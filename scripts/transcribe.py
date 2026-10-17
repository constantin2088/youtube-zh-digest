#!/usr/bin/env python3
"""Download audio when needed and transcribe original Chinese speech."""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from faster_whisper import WhisperModel


def seconds(value: str) -> float:
    parts = value.split(":")
    if not 1 <= len(parts) <= 3 or not all(p.isdigit() for p in parts):
        raise argparse.ArgumentTypeError("Use seconds, MM:SS, or HH:MM:SS")
    result = 0
    for part in parts:
        result = result * 60 + int(part)
    return float(result)


def stamp(value: float) -> str:
    total = round(value)
    return f"{total // 3600:02d}:{(total // 60) % 60:02d}:{total % 60:02d}"


def run(args: list[str]) -> None:
    subprocess.run(args, check=True)


def download_audio(url: str, target: Path) -> Path:
    cmd = [sys.executable, "-m", "yt_dlp", "--no-playlist"]
    if shutil.which("node"):
        cmd += ["--js-runtimes", "node"]
    cmd += ["-f", "bestaudio", "-o", str(target / "source.%(ext)s"), url]
    run(cmd)
    matches = [p for p in target.glob("source.*") if p.is_file() and not p.name.endswith(".part")]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one downloaded audio file, found {len(matches)}")
    return matches[0]


def decode(source: Path, start: float, end: float | None) -> np.ndarray:
    cmd = ["ffmpeg", "-v", "error", "-i", str(source)]
    if start:
        cmd += ["-ss", str(start)]
    if end is not None:
        cmd += ["-t", str(end - start)]
    cmd += ["-vn", "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
    # Feed samples directly: avoids PyAV version conflicts in some installations.
    result = subprocess.run(cmd, capture_output=True, check=True)
    samples = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    if not samples.size:
        raise RuntimeError("FFmpeg decoded no audio; check the requested time range")
    return samples


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="YouTube URL or local audio/video path")
    parser.add_argument("--output", type=Path, default=Path("digest-output"))
    parser.add_argument("--model", default="small", help="Whisper model; small or medium recommended")
    parser.add_argument("--start", type=seconds, default=0.0)
    parser.add_argument("--end", type=seconds)
    args = parser.parse_args()
    if args.end is not None and args.end <= args.start:
        parser.error("--end must be greater than --start")
    if not shutil.which("ffmpeg"):
        parser.error("FFmpeg must be installed and on PATH")

    args.output.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(args.source)
    is_url = parsed.scheme in ("https", "http")
    if is_url and not (parsed.hostname or "").lower().removeprefix("www.") in {
        "youtube.com", "m.youtube.com", "youtu.be", "music.youtube.com"
    }:
        parser.error("Only YouTube URLs or local media files are supported")
    if not is_url and not Path(args.source).expanduser().is_file():
        parser.error(f"Media file does not exist: {args.source}")

    with tempfile.TemporaryDirectory(prefix="youtube-zh-", dir=args.output) as temp:
        source = download_audio(args.source, Path(temp)) if is_url else Path(args.source).expanduser()
        samples = decode(source, args.start, args.end)

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        samples, language="zh", task="transcribe", beam_size=5, vad_filter=True
    )
    transcript = args.output / "transcript.zh.txt"
    metadata = args.output / "segments.json"
    rows = []
    with transcript.open("w", encoding="utf-8") as file:
        for segment in segments:
            row = {
                "start": round(args.start + segment.start, 3),
                "end": round(args.start + segment.end, 3),
                "text": segment.text.strip(),
            }
            rows.append(row)
            file.write(f"[{stamp(row['start'])}] {row['text']}\n")
            file.flush()
            print(f"{stamp(row['start'])} transcribed", file=sys.stderr, flush=True)
    metadata.write_text(json.dumps({"source": args.source, "language": "zh", "model": args.model, "segments": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    if not rows:
        raise RuntimeError("No speech was detected in the selected range")
    print(transcript.resolve())
    print(metadata.resolve())


if __name__ == "__main__":
    main()
