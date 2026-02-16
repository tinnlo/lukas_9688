# AGENTS.md

This file provides guidance to coding agents working in this repository.

## Repository Overview

This is an Obsidian vault for creating TikTok short-form video scripts (German-language affiliate/ad promotion content). It is content-first, not a software codebase.

## Core Workflow Rule

Directory structure:
- `product_list/YYYYMMDD/{product_id}/` - Product source materials (data, images, analysis)
- Source data files are read-only
- `scripts/` subfolder - Write generated/edited video scripts here

Workflow:
1. Source materials in `product_list/YYYYMMDD/{product_id}/` (for example: `tabcut_data.json`, `image_analysis.md`).
2. Generated scripts go into `product_list/YYYYMMDD/{product_id}/scripts/`.
3. Never edit source data files directly.

## Skills Memory (Current)

Skills are now maintained under `.claude/skills/<skill-name>/SKILL.md`.

Current skill set and versions:
- `tiktok-workflow-e2e` - `1.7.0` (master orchestrator)
- `tiktok-product-scraper` - `2.0.0` (tabcut/fastmoss scraping)
- `tiktok-ad-analysis` - `4.4.0` (parallel video analysis)
- `tiktok-product-analysis` - `1.0.0` (image + synthesis orchestration)
- `tiktok-script-generator` - `2.4.0` (script writing + campaign summary)
- `tiktok-targeted-analysis` - `1.0.0` (URL-targeted breakdowns)

Preferred full workflow entry point:
- `/tiktok-workflow-e2e`

## Automation: TikTok Shop Product Scraper

Location: `scripts/` directory.

### Purpose

Automated scraper for extracting TikTok shop product data from tabcut.com, including:
- Product information and shop owner data
- 7-day sales analytics (with 30-day fallback)
- Video analysis metrics
- Top 5 performing video downloads

### Setup and Usage

Prerequisites:
1. Valid tabcut.com account credentials in `.env` (repository root)
2. Python 3.8+ (use system/global Python environment)
3. Required packages installed globally (see `scripts/requirements.txt`)

### Playwright Browsers (Important)

This project uses system Python + Playwright. Browser binaries are stored in a fixed location to avoid accidental cache cleanup.

- Fixed browsers dir: `/Users/lxt/.local/share/ms-playwright/`
- Compatibility symlink: `/Users/lxt/Library/Caches/ms-playwright` -> `/Users/lxt/.local/share/ms-playwright`

If Playwright errors with missing executables, reinstall to the fixed dir:

```bash
PLAYWRIGHT_BROWSERS_PATH="/Users/lxt/.local/share/ms-playwright" python3 -m playwright install chromium
```

Quick start:

```bash
cd scripts
DATE=YYYYMMDD

# Single product
python3 run_scraper.py --product-id 1729630936525936882 --output-dir "../product_list/$DATE"

# Batch scraping
python3 run_scraper.py --batch-file products.csv --download-videos --output-dir "../product_list/$DATE"

# Resume interrupted batch
python3 run_scraper.py --batch-file products.csv --resume --output-dir "../product_list/$DATE"
```

This project uses system Python. Install dependencies globally with:

```bash
pip3 install -r scripts/requirements.txt
```

Output structure:

```text
product_list/
└── YYYYMMDD/
    └── {product_id}/
        ├── tabcut_data.json
        ├── image_analysis.md
        ├── ref_video/
        │   ├── video_1_{creator}.mp4
        │   └── ...
        └── scripts/
            ├── Script1_Angle1.md
            ├── Script2_Angle2.md
            └── Campaign_Summary.md
```

See `scripts/README.md` for complete scraper documentation.

## Script File Structure

### Naming Convention

Files in `product_list/YYYYMMDD/{product_id}/scripts/`: `Product_Model_KeyAngle.md`
- Use underscores, keep concise and descriptive
- Example: `HTC_NE20_AI_Uebersetzer_Earbuds.md`

### Required YAML Frontmatter

Every script note must start with:

```yaml
---
cover: ""
caption: >-
  Short, punchy TikTok caption in German WITH hashtags appended (space-separated, no commas, no quote marks)
published: YYYY-MM-DD
duration: "MM:SS"   # target 00:30-00:50
sales:
  - yes            # or: no
link: ""
tags:
  - "#tag1"
  - "#tag2"
  - "#tag3"
  - "#tag4"
  - "#tag5"
product: "Brand Model"
source_notes:
  - "product_list/Path/To/Source1.md"
  - "product_list/Path/To/Source2.md"
---
```

Frontmatter rules:
- `duration`: best estimate for VO read time, default to `00:30-00:50`
- `tags`: maximum 5 tags; prefer meaningful commerce/interest tags
- `caption`: short, punchy, production-ready for TikTok
- `source_notes`: link to exact reference files used from `product_list/`

### Required Content Sections

Use these sections in order:

1. `## Scripts` - Structure/beat sheet (hook -> proof -> payoff -> CTA)
2. `## On-Screen Text` - Bilingual (DE/ZH) text overlay table with strategy rationale (max 3 overlays, hook overlay <=10 words, timed to video beats)
3. `## Voiceover` - Final VO text for TTS/recording

## Voiceover Standards

### Length and Language

- Target: 30-40 seconds (unless script is already published)
- Primary language: German
- Chinese version is mandatory under a separate heading

### ElevenLabs v3 (alpha) Format

Must include this marker line:

```text
> with ElevenLabs v3 (alpha) grammar
```

Then use delivery cues in square brackets, one cue per line.

Allowed cue examples:
- Intensity: `[bright]`, `[firm]`, `[soft]`, `[neutral]`
- Emotion: `[curious]`, `[warm]`, `[confident]`, `[reflective]`, `[amused]`, `[skeptical]`
- Delivery: `[matter-of-fact]`, `[understated]`, `[whisper]`

Do not use:
- hashtags, pause cues, or custom cue syntax
- over-direction (too many cues sounds synthetic)

### Writing Style

Follow `doc/ElevenLabs_v3_Alpha_VO_Grammar_Practice.md`.

Best practices:
- One idea per line (micro-lines for natural breath)
- Periods create confidence; use more than in normal writing
- Use dashes and ellipses sparingly (1-3 per script)
- Irregular pacing through line breaks, not pause cues
- Avoid feature dumps; include human reactions, asides, stakes
- Keep sentences short and spoken-word friendly
- No medical/legal guarantees; stay consistent with source notes

Anti-AI flavor checklist:
- Vary sentence lengths (short hits + medium lines)
- Include 2+ human beats (reactions, asides, self-corrections)
- Avoid repeated cadence patterns
- End with short, confident CTA (no over-selling)

### Timing Estimates

- 30s: ~65-90 words
- 35s: ~80-105 words
- 40s: ~90-115 words

## Pre-Save Review Checklist

- [ ] Script saved under `product_list/YYYYMMDD/{product_id}/scripts/`
- [ ] Non-script data files in `product_list/` unchanged (read-only)
- [ ] Frontmatter exists and parses correctly (valid date + duration formats)
- [ ] VO fits 30-50s read time with clear CTA
- [ ] Tags <= 5 and meaningful for discovery/commerce
- [ ] `source_notes` links point to exact reference files used
- [ ] On-Screen Text section present with strategy rationale
- [ ] ElevenLabs v3 grammar marker present
- [ ] Delivery cues are valid and minimal (not over-directed)

## Reference Materials

- `CLAUDE.md` - Canonical workflow memory for this repository
- `doc/ElevenLabs_v3_Alpha_VO_Grammar_Practice.md` - Detailed v3 prompting best practices
- `doc/Tiktok_Golden_3_seconds.md` - 8 core hook patterns for German TikTok
- `Account_Description.md` - Account purpose/audience
- `scripts_dashboard.base` - Obsidian Base view (avoid editing unless requested)
- `.obsidian/` - Local Obsidian settings (avoid editing)

## Content Organization

Product folders in `product_list/`:
- Dated batch folders under `product_list/YYYYMMDD/` contain product ID subfolders
- Typical contents: markdown transcripts, mp4 videos, png screenshots
- Transcripts commonly include both German and Chinese versions

Script naming follows product context but focuses on specific angles/features per video.
