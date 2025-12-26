---
name: tiktok-ad-analysis
description: Analyzes TikTok product videos using Gemini multimodal vision. Supports deep-dive (single video storyboard) and bulk analysis (marketing insights for multiple videos). Generates bilingual (EN/CN) reports.
version: 2.0.0
author: Claude
---

# TikTok Ad Analysis Skill

Analyzes TikTok product videos with two modes: **Deep-Dive** (detailed shot-by-shot) and **Bulk Marketing** (insights for multiple videos).

## Analysis Modes

### Mode 1: Deep-Dive Analysis (Single Video)
**Use when:** You need detailed storyboard, frame extraction, and VO transcript for ONE video

**Output:** Shot-by-shot breakdown, key frames, voiceover transcript, image prompts, bilingual report

### Mode 2: Bulk Marketing Insights (Multiple Videos)
**Use when:** You need marketing insights for ALL videos in a directory/product

**Output:** Consolidated marketing analysis with hooks, selling points, effectiveness ratings

---

## Mode 1: Deep-Dive Analysis

### Overview
Complete technical and creative breakdown of a single video:
1. **Shot Detection**: Identifies scene boundaries and shot count
2. **Key Frame Extraction**: Extracts ONE representative frame per shot
3. **Voiceover Extraction**: Extracts audio transcript from video
4. **Multimodal Analysis**: Uses Gemini vision to analyze video and frames
5. **Report Generation**: Creates breakdown report with VO and storyboard
6. **Translation**: Bilingual (English/Chinese) version of all content
7. **Image Prompts**: AI generation prompts for recreating visuals

### Prerequisites

- **ffmpeg**: For video processing, frame extraction, and audio extraction
- **Gemini CLI**: With multimodal vision capabilities
- **Local video files**: MP4 format

### Workflow

#### Step 1: Detect Shot Boundaries

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

#### Step 2: Extract Key Frames Per Shot

Extract ONE representative frame from the middle of each shot:

```bash
# Calculate midpoint of each shot and extract
ffmpeg -i input.mp4 -ss 2.5 -frames:v 1 shot_01_hook.jpg -y
ffmpeg -i input.mp4 -ss 12.5 -frames:v 1 shot_02_benefit.jpg -y
ffmpeg -i input.mp4 -ss 27.5 -frames:v 1 shot_03_reveal.jpg -y
# ... continue for all shots
```

#### Step 3: Extract Voiceover/Transcript

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

#### Step 4: Generate Complete Breakdown Report

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

#### Step 5: Translate All Content to Chinese

Use Gemini to translate the entire breakdown report while preserving English:

```
Translate this TikTok ad analysis to Chinese.
Keep the original English content, then add Chinese translation below each section.

Maintain this bilingual format throughout.

[paste the markdown content]
```

Save as: `tiktok_breakdown_[VIDEO_ID]_bilingual.md`

#### Step 6: Generate Image Prompts

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

#### Step 7: Cleanup

Remove temporary files:
```bash
rm -rf .tmp_analysis preview_*.jpg audio.mp3
```

### Deep-Dive Output Structure

```
[ref_video_dir]/
├── video_1_[creator].mp4
├── video_1_analysis/
│   ├── tiktok_breakdown_[VIDEO_ID]_bilingual.md
│   ├── image_prompts_[VIDEO_ID]_bilingual.md
│   ├── shot_01_[type].jpg
│   ├── shot_02_[type].jpg
│   └── ...
```

---

## Mode 2: Bulk Marketing Insights

### Overview

Analyzes ALL videos in a product directory to extract marketing insights, creative strategies, and effectiveness ratings.

**Key difference from Deep-Dive:** No frame extraction, no shot breakdown, focuses on marketing strategy and campaign-level insights.

### Workflow

#### Step 1: Enumerate All Video Files

**CRITICAL:** Always explicitly list all video files before analysis to prevent missing videos.

```bash
# List all MP4 files in directory
ls -1 /path/to/product/ref_video/*.mp4

# Example output:
# video_1-Product_Feature@creator1.mp4
# video_2-Product_Value@creator2.mp4
# video_3_creator3.mp4
# video_4_creator3.mp4
# video_5_creator3.mp4
```

**Store this list** to pass to Gemini explicitly.

#### Step 2: Launch Gemini Analysis with Explicit File List

**DO NOT** use vague prompts like "analyze all videos in this directory"

**DO** use explicit enumeration:

```
Analyze ALL [N] TikTok ad videos in this directory: /path/to/product/ref_video

The directory contains exactly these [N] video files:
1. video_1-Product_Feature@creator1.mp4
2. video_2-Product_Value@creator2.mp4
3. video_3_creator3.mp4
4. video_4_creator3.mp4
5. video_5_creator3.mp4

For EACH of these [N] videos, provide:
1. Video content summary (what's shown, product features highlighted)
2. Hook/opening strategy (first 3 seconds)
3. Key selling points emphasized
4. Visual elements and editing style
5. Call-to-action approach
6. Target audience inference
7. Effectiveness rating (1-10) with reasoning

Format as a detailed markdown report with separate sections for each video.
```

**Why this works:**
- Gemini can't miss videos when they're explicitly listed
- Count validation ([N] videos expected)
- Clear structure requirements

#### Step 3: Parse and Validate Results

Check that Gemini analyzed all videos:
- Count sections in output
- Verify each filename appears
- Flag missing analyses

#### Step 4: Save Bulk Analysis Report

Save as: `video_analysis.md` in the product directory

```
product_list/
└── [product_id]/
    ├── ref_video/
    │   ├── video_1.mp4
    │   ├── video_2.mp4
    │   └── ...
    ├── video_analysis.md  ← Bulk marketing insights
    └── tabcut_data.json
```

### Bulk Analysis Report Template

```markdown
# TikTok Ad Video Analysis Report

**Product:** [Product Name]
**Product ID:** [ID]
**Analysis Date:** YYYY-MM-DD
**Videos Analyzed:** [N]

---

## Executive Summary

[Campaign overview, overall strategy, effectiveness]

---

## Video-by-Video Analysis

### Video 1: [Title/Description]

**Filename:** `video_1_creator.mp4`
**Creator:** @creator

#### 1. Video Content Summary
[What's shown, product features highlighted]

#### 2. Hook / Opening Strategy (First 3 Seconds)
**Strategy:** [Hook type]
**Description:** [Details]

#### 3. Key Selling Points Emphasized
- [Point 1]
- [Point 2]
- [Point 3]

#### 4. Visual Elements and Editing Style
**Style:** [UGC, professional, etc.]
**Elements:** [Specific visual choices]

#### 5. Call-to-Action Approach
[CTA strategy and messaging]

#### 6. Target Audience Inference
[Demographics, psychographics]

#### 7. Effectiveness Rating: X/10
**Reasoning:** [Why this rating]

---

[Repeat for all videos]

---

## Overall Campaign Strategy

### Creative Mix Framework
[How videos work together]

### Key Success Factors
1. [Factor 1]
2. [Factor 2]

### Recommendations for Future Creatives
1. [Recommendation 1]
2. [Recommendation 2]
```

---

## Parallel Bulk Analysis (Multiple Products)

To analyze multiple products efficiently, use **async Gemini CLI** to run analyses in parallel:

```bash
# Launch 5 parallel analyses (one per product)
# Each returns a task_id

gemini_cli_execute_async(
  query="[bulk analysis prompt with explicit file list]",
  working_dir="/path/to/project"
)

# Monitor progress
gemini_cli_check_result(task_id="...")

# Retrieve completed results
# Save to each product's video_analysis.md
```

**Benefits:**
- Analyze 20+ videos in ~2-3 minutes total
- No timeouts
- Efficient resource usage

---

## Common Issues and Solutions

### Issue 1: Gemini Only Analyzes 1 Video

**Cause:** Vague directory prompt without explicit file enumeration

**Solution:** Always use Step 1 (enumerate files) and Step 2 (explicit list in prompt)

### Issue 2: Missing Videos in Analysis

**Cause:** Gemini file discovery incomplete

**Solution:**
1. List files with `ls -1 *.mp4`
2. Pass exact filenames in prompt
3. Validate output has all videos

### Issue 3: Analysis Timeout

**Cause:** Too many videos, synchronous execution

**Solution:** Use `gemini_cli_execute_async` for parallel processing

### Issue 4: Inference-Only Analysis (No Direct Video Access)

**Situation:** Gemini cannot directly process video binary

**Approach:** Infer from metadata (filenames, titles, existing data)

**Best Practice:**
- Check for `tabcut_data.json` first
- Use creator names, video titles from filenames
- Cross-reference with existing product data

---

## Shot Types (Deep-Dive Mode)

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
- **pattern_interrupt**: Unexpected/humorous opening
- **unboxing**: Classic product opening
- **testimonial**: Personal recommendation
- **educational**: "Did you know...?"
- **urgency**: "Limited time!", "Black Friday!"

---

## Example Usage

### Deep-Dive Single Video

```
Analyze this video in detail:
/Users/lxt/Movies/TikTok/WZ/lukas_9688/product_list/1729535919239371775/ref_video/video_1_creator.mp4

Generate:
- Shot breakdown
- Key frames
- VO transcript (bilingual)
- Image prompts

Save to: product_list/1729535919239371775/ref_video/video_1_analysis/
```

### Bulk Marketing Insights

```
Analyze ALL 5 videos for product 1729535917392698367:

Files:
1. video_1-Magnesium Komplex mit guter Qualität@produkt.tester_131514.mp4
2. video_2-Magnesium Komplex zum fairen Preis@produkt.tester_131613.mp4
3. video_3_zs.carmen_1406.mp4
4. video_4_zs.carmen_1406.mp4
5. video_5_zs.carmen_1406.mp4

Save consolidated report to: product_list/1729535917392698367/video_analysis.md
```

---

## Tips for Quality Analysis

### Deep-Dive Mode
1. **Shot Detection**: Use Gemini vision for accurate shot boundary detection
2. **Key Frame Timing**: Extract from middle of each shot
3. **Frame Naming**: Use descriptive names (shot_01_hook.jpg)
4. **VO Extraction**: Extract audio, use Gemini for transcription + translation
5. **Bilingual Format**: Always preserve English content, add Chinese below
6. **Unified Scenario**: Image prompts should maintain visual consistency

### Bulk Marketing Mode
1. **File Enumeration**: ALWAYS list files explicitly first
2. **Count Validation**: Verify [N] videos in prompt matches directory
3. **Async Execution**: Use parallel processing for multiple products
4. **Metadata Fallback**: If video access fails, use tabcut_data.json
5. **Campaign-Level Insights**: Group videos by creator, hook type, strategy
6. **Cross-Product Patterns**: Identify winning patterns across products
