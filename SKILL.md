---
name: youtube-zh-digest
description: Turn Chinese-spoken YouTube videos, livestream replays, or local audio/video into a readable Chinese digest with timestamped source links. Use when captions are missing, mistranslated, or unreliable, or when the user wants the main points of a long Chinese video organized by topic.
---

# Chinese YouTube digest

## Workflow

1. Inspect the video URL, duration, and available caption languages. Do not assume a translated caption track is the original speech. Prefer genuine Chinese captions only if a short spot check against the audio is accurate.
2. For missing or poor Chinese captions, run `scripts/transcribe.py` on the YouTube URL or a local media file. It downloads audio only and transcribes the **Chinese speech**, not a translation. Install dependencies with `python -m pip install -r requirements.txt`; also install FFmpeg and make `ffmpeg` available on `PATH`. The first run downloads the selected model. No paid transcription API is required.
3. For a trial, use `--start 00:03:37 --end 00:13:37` or another representative 5–10 minute passage. For a full digest, transcribe the whole video. On a CPU, `small` is faster; `medium` can improve difficult speech but may be much slower. The script writes UTF-8 text with absolute video timestamps and JSON segment data. It may take many minutes for a long replay.
4. Read the **whole** transcript before writing a full-video digest. Group by subject, not fixed time windows. Remove greetings, filler, ads, and repetition while retaining reasoning, examples, numbers, qualifications, and disagreements. Do not turn a speaker's claims into facts.
5. Produce an overview, thematic sections, key takeaways, an optional audience Q&A section when present, and timestamp links. Use `[MM:SS](https://www.youtube.com/watch?v=VIDEO_ID&t=SECONDSs)` for YouTube. For local media, cite timestamps without inventing a URL.
6. Review named entities, amounts, dates, financial/legal terms, and any internally inconsistent passage. Mark uncertain recognition as `待核实` and refer to the audio if available. For allegations about identifiable people or organizations, attribute them explicitly to the speaker; distinguish transcript evidence from independent verification. If the user asks for fact-checking, use independent sources separately.

## Commands

```bash
python scripts/transcribe.py "https://www.youtube.com/watch?v=VIDEO_ID" --output digest-output --model small
python scripts/transcribe.py "https://www.youtube.com/watch?v=VIDEO_ID" --start 00:03:37 --end 00:13:37 --output trial-output
python scripts/transcribe.py ./recording.mp3 --output digest-output --model medium
```

The tool prints the transcript and JSON paths. It does not perform the final editorial digest; an agent uses those files to write it. If download access is blocked, ask for a local audio/video file and run the same command on that file. Do not silently fall back to English auto-translation.

## Digest format

```markdown
# 视频标题｜内容纪要
来源：视频链接 · 时长 · 转写方式：中文原声识别

## 内容概览
200–300字，点明主要问题、讲述者的结论及适用边界。

## 分主题整理
### 主题一（时间范围）
观点、论证、例子，以及能定位原声的时间戳链接。

## 关键观点
3–7条，避免重复正文。

## 观众问答
仅在视频确有问答时加入。

## 待核实
识别不清的人名、数字、术语，以及尚无独立证据的重大事实主张。
```

Do not present automated transcription as a verbatim certified record. Keep the raw transcript available for audit, and scale the digest length to the information density rather than a fixed number of bullets.
