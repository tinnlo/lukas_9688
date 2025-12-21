# Project Guidelines (Obsidian Vault)

This repository is an Obsidian vault for a TikTok affiliate/ad promotion account targeting a German audience. It is content-first (Markdown notes), not a software codebase.

## Core Rule: Reference vs Output

- **Do not edit** anything inside `product_list/`. Treat it as **read-only input source** material.
- Create new scripts (and only edit scripts) inside `shorts_scripts/`.

## Folder Structure

- `product_list/` — reference materials per product (read-only).
- `shorts_scripts/` — generated/edited short-form video scripts (write here).
- `shorts_dashboard.base` — Obsidian Base view for listing scripts (do not edit unless requested).
- `.obsidian/` — local Obsidian settings (avoid editing unless necessary).

## Script Note Naming

- Filenames: `Product_Model_KeyAngle.md` (use underscores, keep it short and descriptive).
  - Example: `HTC_NE20_AI_Uebersetzer_Earbuds.md`

## Required Frontmatter (YAML)

Every note in `shorts_scripts/` must start with YAML frontmatter.

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

## Note Sections (Required)

Use these sections in this order:

- `## Scripts` — structure/beat sheet for the edit (hook → proof → payoff → CTA).
- `## Voiceover` — the final VO text used for TTS/recording.

## Voiceover Style (Workflow Standard)

- Target VO length: **30–40 seconds** (unless a script is already published).
- Language: German is primary. Optional Chinese version may be included under a separate heading.
- Avoid medical/legal guarantees; keep claims consistent with source notes.
- Keep sentences short and spoken-word friendly.
- For v3 prompt writing best practices (natural pacing, minimal cues), follow `ElevenLabs_v3_Alpha_VO_Grammar_Practice.md`.

### ElevenLabs Prompt Format

In `## Voiceover`, include:

- A line: `> with ElevenLabs v3 (alpha) grammar`
- Then the VO prompt with delivery cues in **square brackets**, one cue per line.

Allowed cue style:
- Examples: `[bright]`, `[firm]`, `[curious]`, `[soft]`, `[matter-of-fact]`, `[confident]`, `[pause 200ms]`
- Do **not** use hashtags or custom cue syntaxes.

Example:

```text
> with ElevenLabs v3 (alpha) grammar

### DE (ElevenLabs Prompt | 30–50s)

[bright] ...
[firm] ...
```

## Review Checklist (Before Saving)

- Script is saved under `shorts_scripts/` and **nothing** in `product_list/` is changed.
- Frontmatter exists and parses (date + duration formats valid).
- VO fits **30–50s** read time and has a clear CTA.
- Tags ≤ 5 and meaningful for discovery/commerce.
- `source_notes` links point to the exact reference files used.
