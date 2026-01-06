# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an Obsidian vault for creating TikTok short-form video scripts (German-language affiliate/ad promotion content). It is **content-first**, not a software codebase.

## Core Workflow Rule

**Directory Structure:**
- `product_list/YYYYMMDD/{product_id}/` — Product source materials (data, images, analysis)
  - Source data files are **READ-ONLY**
  - `scripts/` subfolder — **WRITE HERE** generated/edited video scripts for each product

**Workflow:**
1. Source materials in `product_list/YYYYMMDD/{product_id}/` (tabcut_data.json, image_analysis.md, etc.)
2. Generated scripts go into `product_list/YYYYMMDD/{product_id}/scripts/`
3. Never edit source data files directly

## Automation: TikTok Shop Product Scraper

**Location**: `scripts/` directory (NEW automation workflow)

### Purpose
Automated scraper for extracting TikTok shop product data from tabcut.com, including:
- Product information and shop owner data
- 7-day sales analytics (with 30-day fallback)
- Video analysis metrics
- Top 5 performing video downloads

### Setup & Usage

**Prerequisites:**
1. Valid tabcut.com account credentials in `scripts/config/.env`
2. Python 3.8+ with virtual environment

**Quick Start:**
```bash
cd scripts
source venv/bin/activate
DATE=YYYYMMDD

# Single product
python run_scraper.py --product-id 1729630936525936882 --output-dir "../product_list/$DATE"

# Batch scraping
python run_scraper.py --batch-file products.csv --download-videos --output-dir "../product_list/$DATE"

# Resume interrupted batch
python run_scraper.py --batch-file products.csv --resume --output-dir "../product_list/$DATE"
```

**Output Structure:**
```
product_list/
└── YYYYMMDD/
    └── {product_id}/               # e.g., "1729630936525936882"
        ├── tabcut_data.json        # All scraped metadata
        ├── image_analysis.md       # Product image analysis (if available)
        ├── ref_video/              # Top 5 downloaded reference videos
        │   ├── video_1_{creator}.mp4
        │   └── ...
        └── scripts/                # Generated scripts for this product
            ├── Script1_Angle1.md
            ├── Script2_Angle2.md
            └── Campaign_Summary.md
```

See `scripts/README.md` for complete documentation.

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
caption: ""
published: YYYY-MM-DD
duration: "MM:SS"   # target 00:30–00:50
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

**Frontmatter rules:**
- `duration`: Best estimate for VO read time, default to 00:30–00:50
- `tags`: Maximum **5** tags; prefer meaningful commerce/interest tags
- `caption`: Short, punchy, production-ready for TikTok
- `source_notes`: Link to exact reference files used from `product_list/`

### Required Content Sections

Use these sections in order:

1. `## Scripts` — Structure/beat sheet (hook → proof → payoff → CTA)
2. `## Voiceover` — Final VO text for TTS/recording

## Voiceover Standards

### Length & Language
- Target: **30–40 seconds** (unless script is already published)
- Primary language: German
- Chinese version is mandatory under a separate heading

### ElevenLabs v3 (alpha) Format

Must include this marker line:
```
> with ElevenLabs v3 (alpha) grammar
```

Then use delivery cues in **square brackets**, one cue per line:

**Allowed cue examples:**
- Intensity: `[bright]`, `[firm]`, `[soft]`, `[neutral]`
- Emotion: `[curious]`, `[warm]`, `[confident]`, `[reflective]`, `[amused]`, `[skeptical]`
- Delivery: `[matter-of-fact]`, `[understated]`, `[whisper]`

**Do NOT use:**
- Hashtags, pause cues, or custom cue syntax
- Over-direction (too many cues feel synthetic)

### Writing Style (See doc/ElevenLabs_v3_Alpha_VO_Grammar_Practice.md)

**Best practices:**
- One idea per line (short "micro-lines" for natural breaths)
- Periods create confidence; use more than in normal writing
- Use dashes (`—`) and ellipses (`…`) sparingly (1–3 per script)
- Irregular pacing through line breaks, not pause cues
- Avoid feature dumps; include human reactions, asides, stakes
- Keep sentences short and spoken-word friendly
- No medical/legal guarantees; stay consistent with source notes

**Anti-AI flavor checklist:**
- Vary sentence lengths (short hits + medium sentences)
- Include 2+ human beats (reactions, asides, self-corrections)
- Avoid repeated cadence patterns
- Short, confident CTA (no over-selling)

### Timing Estimates
- 30s: ~65–90 words
- 35s: ~80–105 words
- 40s: ~90–115 words

## Pre-Save Review Checklist

- [ ] Script saved under `product_list/YYYYMMDD/{product_id}/scripts/`
- [ ] Non-script data files in `product_list/` unchanged (read-only)
- [ ] Frontmatter exists and parses correctly (valid date + duration formats)
- [ ] VO fits 30–50s read time with clear CTA
- [ ] Tags ≤ 5 and meaningful for discovery/commerce
- [ ] `source_notes` links point to exact reference files used
- [ ] ElevenLabs v3 grammar marker present
- [ ] Delivery cues are valid and minimal (not over-directed)

## Reference Materials

- `AGENTS.md` — Complete workflow guidelines and rules
- `doc/ElevenLabs_v3_Alpha_VO_Grammar_Practice.md` — Detailed v3 prompting best practices
- `doc/Tiktok_Golden_3_seconds.md` — 8 core hook patterns for German TikTok
- `Account_Description.md` — Account purpose/audience
- `scripts_dashboard.base` — Obsidian Base view (avoid editing unless requested)
- `.obsidian/` — Local Obsidian settings (avoid editing)

## Content Organization

**Product folders** (in `product_list/`):
- Dated batch folders under `product_list/YYYYMMDD/` contain product ID subfolders
- Contains: `.md` transcripts, `.mp4` videos, `.png` screenshots
- Transcripts typically include both German and Chinese versions

**Script naming** follows product structure but focuses on specific angles/features for different videos.
