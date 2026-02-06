# Project Guidelines (Obsidian Vault)

This repository is an Obsidian vault for a TikTok affiliate/ad promotion account targeting a German audience. It is content-first (Markdown notes), not a software codebase.

## Core Rule: Reference vs Output

- Treat non-script files inside `product_list/` as **read-only input source** material.
- Create new scripts (and only edit scripts) inside `product_list/YYYYMMDD/{product_id}/scripts/`.

## Folder Structure

- `product_list/` — reference materials per product; scripts live under dated batch folders.
- `scripts_dashboard.base` — Obsidian Base view for listing scripts (do not edit unless requested).
- `.obsidian/` — local Obsidian settings (avoid editing unless necessary).

## Automation Environment (Python/Playwright)

- Use the system `python3` (global environment) for all scripts under `scripts/`.
- Playwright browser binaries are pinned to a fixed location to avoid cleanup tools deleting them:
  - `/Users/lxt/.local/share/ms-playwright/`
  - `/Users/lxt/Library/Caches/ms-playwright` is a symlink to that folder
  - `scripts/config/.env` sets `PLAYWRIGHT_BROWSERS_PATH=/Users/lxt/.local/share/ms-playwright`

## Script Note Naming

- Filenames: `Product_Model_KeyAngle.md` (use underscores, keep it short and descriptive).
  - Example: `HTC_NE20_AI_Uebersetzer_Earbuds.md`

## Required Frontmatter (YAML)

Every script note in `product_list/YYYYMMDD/{product_id}/scripts/` must start with YAML frontmatter.

Required keys:

```yaml
---
cover: ""
caption: ""
published: YYYY-MM-DD
duration: "MM:SS"   # target 00:30–00:40
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

Rules:
- `duration` should be a best estimate for VO read time; default to a value in **00:30–00:50**.
- `tags` maximum **5**; prefer meaningful commerce/interest tags (avoid vague tags like `#deutsch`).
- `caption` should be short, punchy, and production-ready for TikTok.
- `caption` must append the same hashtags as `tags` (space-separated), with **no commas** and **no quote marks**; use `caption: >-` block scalar to avoid YAML issues.

## Note Sections (Required)

Use these sections in this order:

- `## Scripts` — structure/beat sheet for the edit (hook → proof → payoff → CTA).
- `## Voiceover` — the final VO text used for TTS/recording.

## Voiceover Style (Workflow Standard)

- Target VO length: **30–40 seconds** (unless a script is already published).
- Language: German is primary. Chinese version is mandatory under a separate heading.
- Avoid medical/legal guarantees; keep claims consistent with source notes.
- Keep sentences short and spoken-word friendly.
- For v3 prompt writing best practices (natural pacing, minimal cues), follow `doc/ElevenLabs_v3_Alpha_VO_Grammar_Practice.md`.

### ElevenLabs Prompt Format

In `## Voiceover`, include:

- A line: `> with ElevenLabs v3 (alpha) grammar`
- Then the VO prompt with delivery cues in **square brackets**, one cue per line.

Allowed cue style:
- Examples: `[bright]`, `[firm]`, `[curious]`, `[soft]`, `[matter-of-fact]`, `[confident]`
- Do **not** use hashtags, pause cues, or custom cue syntaxes.

Example:

```text
> with ElevenLabs v3 (alpha) grammar

### DE (ElevenLabs Prompt | 30–50s)

[bright] ...
[firm] ...
```

## Review Checklist (Before Saving)

- Script is saved under `product_list/YYYYMMDD/{product_id}/scripts/` and source data files in `product_list/` are unchanged.
- Frontmatter exists and parses (date + duration formats valid).
- VO fits **30–50s** read time and has a clear CTA.
- Tags ≤ 5 and meaningful for discovery/commerce.
- `source_notes` links point to the exact reference files used.
