# 中文直播太长，先读纪要。

**YouTube 中文视频与直播回放 → 中文原声转写 → 带时间戳的主题纪要。**

博主讲了近一小时，视频却没有中文字幕？自动字幕只有英文，翻译又把人名、金额和术语弄错？`youtube-zh-digest` 从**原始音频直接识别中文**，再引导 AI 将口语整理成清楚、可回听的文字。它特别适合访谈、讲座、时事分析和长直播回放。

> 先听中文，再写中文。视频里的观点归视频作者；有争议的事实和识别不清的数字，留给读者核对。

## 你会得到什么

- **中文原声文字稿**：每段保留原视频时间戳，不经过英文字幕转译。
- **好读的内容纪要**：概览、分主题正文、关键观点、观众问答（如有）和待核实项。
- **可回听的出处**：纪要中的重要观点链接到 YouTube 对应时刻。
- **清楚的事实边界**：把“博主称”与已核实事实分开；不擅自补全听不清的人名、金额或规则。

转写脚本在本地运行，无需付费转写 API。写纪要需要你所使用的 AI agent；它的模型费用或订阅规则取决于你的运行环境。

## 快速开始

准备 Python 3.10+、[FFmpeg](https://ffmpeg.org/download.html)，并确认 `ffmpeg -version` 可运行。下载 YouTube 音频时还需可访问 YouTube。Node.js 可帮助 `yt-dlp` 处理部分 YouTube 格式，但本地音视频文件不需要它。

```bash
git clone https://github.com/constantin2088/youtube-zh-digest.git
cd youtube-zh-digest
python -m pip install -r requirements.txt
python scripts/transcribe.py "https://www.youtube.com/watch?v=VIDEO_ID" --output output
```

生成的 `output/transcript.zh.txt` 是带时间戳的中文稿，`output/segments.json` 保存每段的起止时间。将这两个文件交给支持 Agent Skills 的助手，并要求它使用仓库根目录的 `SKILL.md` 撰写完整纪要。若你的 agent 支持 [skills.sh](https://skills.sh/) 的安装方式，也可以尝试：

```bash
npx skills add constantin2088/youtube-zh-digest
```

### 先试听十分钟

```bash
python scripts/transcribe.py "https://www.youtube.com/watch?v=VIDEO_ID" \
  --start 00:03:37 --end 00:13:37 --output trial-output
```

在 Windows PowerShell 中把上面的两行合成一行即可。时间戳仍指向**原视频**，从 `03:37` 开始，而不是从 `00:00` 重新计时。

### 已有本地音频或视频

```bash
python scripts/transcribe.py ./recording.mp3 --output output --model medium
```

默认 `small` 模型在 CPU 上较省时；`medium` 对复杂语音可能更准，但处理长直播会慢很多。首次运行会下载模型。下载 YouTube 失败时，先取得你有权处理的本地音频，再使用同一命令。

## 让助手写纪要

你可以这样说：

> 使用 `$youtube-zh-digest` 阅读完整中文转写稿，把这期直播整理成适合阅读的中文纪要。按主题重组，保留观点、依据和例子，删去寒暄与重复内容；关键处给出时间戳链接。将无法听清的人名、数字、专业术语列入“待核实”，将未经独立证实的指控明确归于讲述者。

**质量提醒：**语音识别不是逐字认证。尤其是人名、股票名称、金额、法律或交易规则，应回听原音频；若需要判断观点真假，再查独立资料。此项目只提供整理流程，不为视频中的主张背书。

## 项目结构

| 文件 | 作用 |
| --- | --- |
| `SKILL.md` | Agent 的完整工作流程与纪要格式 |
| `scripts/transcribe.py` | 下载音频、识别中文、输出时间戳 |
| `requirements.txt` | Python 依赖 |
| `agents/openai.yaml` | 技能展示信息 |

基于一次没有可靠中文字幕的中文直播回放整理实践制作。公开仓库不包含该视频的音频、转写稿或内容纪要。
