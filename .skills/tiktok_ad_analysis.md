---
name: tiktok-ad-analysis
description: Analyzes TikTok product videos using Gemini multimodal vision. Extracts key frames per shot, generates storyboard breakdown with VO/transcript, creates AI image prompts, and provides bilingual (EN/CN) output.
version: 1.2.0
author: Claude
---

# TikTok Ad Analysis Skill

Analyzes TikTok product videos to extract marketing insights, generate storyboards with voiceover transcripts, create AI image prompts, and provide bilingual documentation.

## Overview

This skill processes TikTok product videos through a complete analysis pipeline:
1. **Shot Detection**: Identifies scene boundaries and shot count
2. **Key Frame Extraction**: Extracts ONE representative frame per shot
3. **Voiceover Extraction**: Extracts audio transcript from video
4. **Multimodal Analysis**: Uses Gemini vision to analyze video and frames
5. **Report Generation**: Creates breakdown report with VO and storyboard
6. **Translation**: Bilingual (English/Chinese) version of all content
7. **Image Prompts**: AI generation prompts for recreating visuals

## Prerequisites

- **ffmpeg**: For video processing, frame extraction, and audio extraction
- **Gemini CLI**: With multimodal vision capabilities
- **Local video files**: MP4 format

## Workflow

### Step 1: Detect Shot Boundaries

Use Gemini to analyze video and identify shot transitions:

```
Analyze this TikTok video and return shot boundaries as JSON:
Video: [path to video]

Return format:
[
  {"shot": 1, "start": 0, "end": 5, "type": "hook", "description": "..."},
  {"shot": 2, "start": 5, "end": 20, "type": "benefit", "description": "..."},
  ...
]
```

### Step 2: Extract Key Frames Per Shot

Extract ONE representative frame from the middle of each shot:

```bash
# Calculate midpoint of each shot and extract
ffmpeg -i input.mp4 -ss 2.5 -frames:v 1 shot_01_hook.jpg -y
ffmpeg -i input.mp4 -ss 12.5 -frames:v 1 shot_02_benefit.jpg -y
ffmpeg -i input.mp4 -ss 27.5 -frames:v 1 shot_03_reveal.jpg -y
# ... continue for all shots
```

### Step 3: Extract Voiceover/Transcript

Extract audio and get transcript using Gemini:

```bash
# Extract audio
ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3 -y
```

Then use Gemini to transcribe and translate:

```
Transcribe this TikTok video audio to text.
Provide ONLY the spoken words, line by line, in the original language.

Also provide Chinese translation of the transcript.

Video: [path to video or audio]

Format:
VO:
[original language transcript line by line]

中文翻译 (Chinese Translation):
[chinese translation line by line]
```

### Step 4: Generate Complete Breakdown Report

Create comprehensive markdown report: `tiktok_breakdown_[VIDEO_ID].md`

```markdown
# TikTok Ad Analysis: [Product Name] | [产品名称]

## 1. Overview | 概述
**Product | 产品:** [Name]
**Hook Type | 钩子类型:** [Type]
**Hook | 钩子:** [Description]

---

## 2. Viral Hook / Meme Strategy | 病毒式钩子策略
[Strategy explanation - English]

**策略说明 (Chinese):**
[Strategy explanation - Chinese]

**Key Viral Elements | 关键病毒元素:**
- [Element 1]
- [Element 2]

---

## 3. Voiceover / Transcript | 语音/转录

**Original | 原文:**
```
[Original transcript line by line]
```

**中文翻译 | Chinese Translation:**
```
[Chinese translation line by line]
```

---

## 4. Video Script & Storyboard | 视频脚本与分镜

| Shot | Time | Visual Action | Voiceover | 语音 | Asset |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | 0-5s | **[Description]** | **[VO text]** | **[中文]** | `shot_01.jpg` |
| **02** | 5-15s | **[Description]** | **[VO text]** | **[中文]** | `shot_02.jpg` |

---

## 5. Production Notes | 制作备注
*   [Production style - English]
*   [制作风格 - Chinese]
```

### Step 5: Translate All Content to Chinese

Use Gemini to translate the entire breakdown report while preserving English:

```
Translate this TikTok ad analysis to Chinese.
Keep the original English content, then add Chinese translation below each section.

Maintain this bilingual format throughout.

[paste the markdown content]
```

Save as: `tiktok_breakdown_[VIDEO_ID]_bilingual.md`

### Step 6: Generate Image Prompts

Generate AI image prompts for recreating visuals: `image_prompts_[VIDEO_ID].md`

```markdown
# Image Generation Prompts: [Product] | [产品]

**Objective | 目标:** Generate consistent visual assets

---

## Unified Scenario | 统一场景

**Style | 风格:** [UGC description]
**Lighting | 灯光:** [Warm soft lighting]
**Background | 背景:** [Cozy home interior]
**Creator | 创作者:** [Description]

---

## Shot 01: Hook | 钩子

**Reference | 参考:** shot_01_hook.jpg

**Prompt:**
> [English prompt]

**提示 (Chinese):**
> [Chinese translation]

---

[Continue for all shots]
```

### Step 7: Create Bilingual Image Prompts

Create bilingual version: `image_prompts_[VIDEO_ID]_bilingual.md`

(Use same format as Step 6, with Chinese translations below each prompt)

### Step 8: Cleanup

Remove temporary files:
```bash
rm -rf .tmp_analysis preview_*.jpg audio.mp3
```

## Input Format

- **Video file path**: Local MP4 file
- **Output directory**: Where to save reports and key frames

## Output Format

**Directory structure:**
```
[ref_video_dir]/
├── video_1_[creator].mp4
├── video_2_[creator].mp4
├── ...
├── video_1_analysis/
│   ├── tiktok_breakdown_[VIDEO_ID]_bilingual.md
│   ├── image_prompts_[VIDEO_ID]_bilingual.md
│   ├── shot_01_[type].jpg
│   ├── shot_02_[type].jpg
│   └── ...
├── video_2_analysis/
│   ├── tiktok_breakdown_[VIDEO_ID]_bilingual.md
│   ├── image_prompts_[VIDEO_ID]_bilingual.md
│   └── ...
└── ...
```

**Important:** Each video gets its own `video_N_analysis/` sub-folder to prevent overwrites.

## Breakdown Report Template

```markdown
# TikTok Ad Analysis: [Product Name] | [产品名称]

## 1. Overview | 概述
**Product | 产品:** Wasserbalance 7 fach Brennnessel Komplex
**Hook Type | 钩子类型:** Testimonial/Problem-Solution
**Hook | 钩子:** Creator discusses water weight struggles

---

## 2. Viral Hook / Meme Strategy | 病毒式钩子策略
This video leverages a high-trust UGC approach...

**策略说明:**
该视频采用高信任度的UGC（用户生成内容）策略...

---

## 3. Voiceover / Transcript | 语音/转录

**Original | 原文:**
```
gerade gibt es darauf einen Rabatt von 88 Prozent.
falls du diese Teile noch nicht kennst,
das sind die HTC NE20 ihr Earbuds.
```

**中文翻译 | Chinese Translation:**
```
现在这款耳机正在进行88%的折扣促销。
如果您还不了解这款耳机，
它就是HTC NE20耳机。
```

---

## 4. Video Script & Storyboard | 视频脚本与分镜

| Shot | Time | Visual Action | Voiceover | 语音 | Asset |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | 0-5s | **Hook shot** | **VO text** | **中文** | `shot_01.jpg` |
```

## Shot Types

Common TikTok ad shot types:
- **hook**: Opening grabber
- **reveal**: Product unboxing
- **demo**: Product demonstration
- **benefit**: Showing results
- **cta**: Call-to-action
- **testimonial**: Creator speaking

## Hook Strategies

- **pricing_error**: "88% off!", "Pricing mistake!"
- **problem_solution**: "Bloated? Here's the solution."
- **unboxing**: Classic product opening
- **testimonial**: Personal recommendation

## Example Usage

```
Analyze the video at:
/Users/lxt/Movies/TikTok/WZ/lukas_9688/product_list/1729535919239371775/ref_video/video_1__hayleymarshall__.mp4

Save output to:
/Users/lxt/Movies/TikTok/WZ/lukas_9688/product_list/1729535919239371775/ref_video/analysis/
```

## Tips for Quality Analysis

1. **Shot Detection**: Use Gemini vision for accurate shot boundary detection
2. **Key Frame Timing**: Extract from middle of each shot
3. **Frame Naming**: Use descriptive names (shot_01_hook.jpg)
4. **VO Extraction**: Extract audio, use Gemini for transcription + translation
5. **Bilingual Format**: Always preserve English content, add Chinese below
6. **Unified Scenario**: Image prompts should maintain visual consistency
