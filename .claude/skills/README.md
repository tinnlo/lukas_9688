# TikTok Content Creation Skills

Complete workflow for TikTok product video script generation with clear agent separation and parallel processing.

**Version:** 2.2.0
**Last Updated:** 2026-01-31

---

## ⚠️ Migration Note (v2.2.0)

Skills migrated from `.skills/` to `.claude/skills/<skill-name>/SKILL.md` following official Claude Code conventions.

**Key Changes:**
- Each skill now in dedicated directory with supporting files
- Templates extracted for complex skills (script_generator, product_analysis)
- Skill invocation: `/tiktok-workflow-e2e`, `/tiktok-script-generator`, etc.

---

## Quick Start: E2E Workflow

**For full end-to-end processing, use:**
```
/tiktok-workflow-e2e
```

This orchestrates all 4 skills in proper order with quality gates.

---

## Skill Overview

| Skill | Phase | Purpose | Agent |
|:------|:------|:--------|:------|
| `/tiktok-workflow-e2e` | All | **Master orchestrator** - runs full pipeline | Orchestration |
| `/tiktok-product-scraper` | 1 | Download product data + videos | Python |
| `/tiktok-ad-analysis` | 2A | Per-video analysis (frames + transcription) | Python + Gemini |
| `/tiktok-product-analysis` | 2B | Image analysis + synthesis orchestration | Gemini async MCP |
| `/tiktok-script-generator` | 3 | Write scripts + Campaign Summary | Claude Code |

### Which skill to use?

| Scenario | Skill to Use |
|:---------|:-------------|
| Full batch processing (e2e) | `/tiktok-workflow-e2e` |
| Just scraping products | `/tiktok-product-scraper` |
| Re-analyze videos only | `/tiktok-ad-analysis` |
| Re-generate synthesis only | `/tiktok-product-analysis` |
| Re-write scripts only | `/tiktok-script-generator` |

---

## Workflow Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: DATA COLLECTION (Python)                                 │
│                                                                     │
│  /tiktok-product-scraper                                            │
│  ├── Download product metadata (tabcut_data.json)                   │
│  ├── Download product images (product_images/*.webp)                │
│  └── Download reference videos (ref_video/*.mp4)                    │
│                                                                     │
│  Time: ~2-3 min per product (parallel across products)              │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: ANALYSIS (Gemini - PARALLEL)                              │
│                                                                     │
│  /tiktok-ad-analysis (per video)                                    │
│  ├── FFmpeg: Extract keyframes + audio                              │
│  ├── Whisper: Transcribe audio                                      │
│  └── Gemini: Generate video_N_analysis.md                           │
│                                                                     │
│  /tiktok-product-analysis (orchestration)                           │
│  ├── Launch all image analyses in parallel                          │
│  ├── Launch all video analyses in parallel                          │
│  ├── Wait for video analyses → Launch synthesis in parallel         │
│  └── Quality gate: Verify all files exist                           │
│                                                                     │
│  Outputs:                                                           │
│  ├── product_images/image_analysis.md (bilingual)                   │
│  ├── ref_video/video_N_analysis.md (per video, bilingual)           │
│  └── ref_video/video_synthesis.md (market summary, CRITICAL)        │
│                                                                     │
│  Time: ~5-7 min total (all products in parallel)                    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: Pre-Check (BLOCKS if fails)                          │
│                                                                     │
│  ✓ video_synthesis.md exists (150+ lines)                           │
│  ✓ image_analysis.md exists if images present (200+ lines)          │
│  ✓ All video_N_analysis.md files exist                              │
│  ✓ Compliance risks flagged in analysis (validate_compliance_flags) │
│  ✓ Bilingual coverage meets standards (DE/ZH pairs: 30+)            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3: SCRIPT GENERATION (Claude Code - SEQUENTIAL)              │
│                                                                     │
│  /tiktok-script-generator                                           │
│  ├── Read analysis files (video_synthesis.md, image_analysis.md)    │
│  ├── Write 3 production scripts with:                               │
│  │   ├── Detailed storyboards                                       │
│  │   ├── Bilingual voiceovers (DE + ZH)                             │
│  │   ├── ElevenLabs v3 grammar markers                              │
│  │   └── Visual filming instructions                                │
│  └── Create Campaign Summary (references files, no duplication)     │
│                                                                     │
│  Outputs:                                                           │
│  ├── product_list/YYYYMMDD/{product_id}/scripts/Script_1_[Angle].md │
│  ├── product_list/YYYYMMDD/{product_id}/scripts/Script_2_[Angle].md │
│  ├── product_list/YYYYMMDD/{product_id}/scripts/Script_3_[Angle].md │
│  └── product_list/YYYYMMDD/{product_id}/scripts/Campaign_Summary.md │
│                                                                     │
│  Time: ~2-3 min per product (batched writes, v2.3.0 optimization)   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## TikTok Policy Compliance (DE Market)

All scripts must pass compliance validation before publication to avoid ad rejection:

### 5 Policy Categories

| Policy | Risk | Safe Alternative |
|:-------|:-----|:-----------------|
| **No Exact Low Price Bait** | "Nur 9€!" / "€9 statt €50" | "Super günstig" / "Tolles Preis-Leistungs-Verhältnis" |
| **No Absolute Effect Claims** | "100%", "pure", "perfect", "genauso gut" | "hilft bei", "unterstützt", "stark genug" |
| **No Exaggerated Promotions** | "unbezahlbar", "bevor es weg ist" | "wertvoll", "empfehlenswert", "mehr entdecken" |
| **No Medical Claims** | "heilt", "Schmerzlinderung" | "Entspannung", "Wohlbefinden" |
| **No Ambiguous Tech Specs** | "4K Support", "Zero Lag" | "4K-kompatibel", "flüssige Wiedergabe" |

### Validation Commands

```bash
# Validate all scripts for compliance
bash scripts/verify_gate.sh --date YYYYMMDD --csv scripts/products.csv --phase scripts

# Validate individual file
python3 scripts/validate_compliance_flags.py path/to/script.md

# Full workflow with compliance check
bash scripts/verify_gate.sh --date YYYYMMDD --csv scripts/products.csv --phase all
```

Compliance validation is **automatic** during:
- Analysis phase: Flags risky claims from source videos
- Script phase: Blocks scripts containing violations

See `.claude/skills/tiktok_script_generator/SKILL.md` for detailed policy tables and compliant alternatives.

---

## Agent Assignment Rationale

### Why Gemini for Analysis?
- **Parallel execution:** Async MCP allows launching 40+ tasks simultaneously
- **Token efficiency:** Doesn't consume Claude Code context window
- **Speed:** 8 products × 5 videos = 40 analyses in ~5 min (parallel) vs ~80 min (sequential)

### Why Claude Code for Scripts?
- **Quality:** Claude produces detailed, product-specific content
- **Lesson learned:** Gemini produces generic placeholder scripts ("You won't believe...")
- **Natural language:** Claude writes better German voiceovers with natural flow
- **Storyboards:** Claude creates more detailed visual shooting instructions

---

## Time Efficiency Comparison

### Old Workflow (Fully Sequential)
```
8 products × 15 min/product = 120 minutes total
(Videos sequential: 5 × 2min, Image: 2min, Synthesis: 3min, Scripts: 5min)
```

### New Workflow (Sequential Products, Pipeline Within Each)
```
Phase 1 (scraping):   ~5 min (parallel downloads)
Phase 2 (analysis):   ~32 min (sequential products, parallel videos within)
  └─ Per product:     4 min (5 videos|| 2min + image 1min + synthesis 1min)
Phase 3 (scripts):    ~16-24 min (8 products × 2-3 min, batched writes v2.3.0)
────────────────────────────────────────────────────
Total:               ~53-61 min (50%+ faster)
```

### Scaling Benefits

**⚠️ CRITICAL:** Each product has **5 videos**. Analyzing 5 videos in parallel = **all 5 Gemini async slots used**.

| Products | Old (Fully Sequential) | New (Pipeline) | Per Product | Savings |
|:---------|:----------------------|:---------------|:------------|:--------|
| 1 | 15 min | 9 min | 4 min analysis + 2-3 min scripts | 40% |
| 5 | 75 min | 35 min | 5 × 7 min = 35 min | 53% |
| 8 | 120 min | 57 min | 8 × 7 min = 57 min | 52% |
| 20 | 300 min | 140 min | 20 × 7 min = 140 min | 53% |
| 50 | 750 min | 350 min | 50 × 7 min = 350 min | 53% |

### Pipeline Strategy

**CRITICAL CONSTRAINT:** 5-task concurrency limit in Gemini async MCP

**Sequential products (one at a time):**
- Product 1: [5 videos in parallel] → [image] → [synthesis] → [scripts batched] = 7 min
- Product 2: [5 videos in parallel] → [image] → [synthesis] → [scripts batched] = 7 min
- Product 3: [5 videos in parallel] → [image] → [synthesis] → [scripts batched] = 7 min
- ...

**Why sequential products:**
- Each product's 5 videos use all 5 concurrent task slots
- Cannot process multiple products simultaneously without exceeding limit
- Trying to parallelize products → 40+ concurrent tasks → **TIMEOUT/FAILURE**

**Why still fast:**
- **Within each product:** 5 videos in parallel (not sequential)
- **Script generation optimized:** Batched Write calls in v2.3.0 (2x faster)
- **If videos were sequential:** 5 × 2min = 10min per product = 80min total for 8 products
- **With parallel videos:** 2min per product = 32min total for 8 products
- **Speed gain:** 2.5x faster than fully sequential

---

## Quick Start

### Single Product
```bash
# Step 1: Scrape
cd scripts && source venv/bin/activate
python run_scraper.py --product-id 1729607303430380470 --download-videos

# Step 2: Analyze (auto-triggered or manual)
python analyze_video_batch.py 1729607303430380470

# Step 3: Generate scripts (Claude Code)
/tiktok-script-generator
```

### Batch Processing
```bash
# Step 1: Scrape all products
python run_scraper.py --batch-file products.csv --download-videos

# Step 2: Parallel analysis
/tiktok-product-analysis

# Step 3: Verify analysis complete
./verify_analysis.sh

# Step 4: Generate scripts (Claude Code)
# Process each product with /tiktok-script-generator
```

---

## File Structure After Completion

```
product_list/YYYYMMDD/{product_id}/
├── tabcut_data.json                    # Product metadata
├── tabcut_data.md                      # Markdown version
├── product_images/
│   ├── product_image_1.webp
│   ├── product_image_2.webp
│   └── image_analysis.md               # Gemini analysis (bilingual)
├── ref_video/
│   ├── video_1_creator.mp4
│   ├── video_1_analysis.md             # Per-video analysis
│   ├── video_2_creator.mp4
│   ├── video_2_analysis.md
│   ├── ...
│   └── video_synthesis.md              # Market summary (CRITICAL)
└── scripts/
    ├── Script_1_[Angle].md             # Production script
    ├── Script_2_[Angle].md
    ├── Script_3_[Angle].md
    └── Campaign_Summary.md             # Executive summary
```

---

## Skills Directory Structure

```
.claude/skills/
├── README.md                                    # This file
├── tiktok_workflow_e2e/
│   └── SKILL.md                                 # Master orchestrator
├── tiktok_product_scraper/
│   └── SKILL.md                                 # Product data scraper
├── tiktok_ad_analysis/
│   └── SKILL.md                                 # Per-video analysis
├── tiktok_product_analysis/
│   └── SKILL.md                                 # Image + synthesis
├── tiktok_script_generator/
│   ├── SKILL.md                                 # Script writing
│   ├── templates/
│   │   ├── frontmatter_template.md              # YAML frontmatter spec
│   │   ├── voiceover_format.md                  # ElevenLabs v3 format
│   │   └── campaign_summary_structure.md        # Summary template
│   └── examples/                                # (Reserved for future)
├── tiktok_targeted_analysis/
│   └── SKILL.md                                 # Targeted analysis
└── tiktok_quick_directions/
    └── SKILL.md                                 # Quick reference
```

---

## Key Changes from v2.1

| Aspect | v2.1 (Old) | v2.2 (New) |
|:-------|:---------|:---------|
| Directory structure | `.skills/*.md` | `.claude/skills/<name>/SKILL.md` |
| Templates | Inline in skill files | Separate template files |
| Script generator size | 958 lines | ~520 lines (templates extracted) |
| Skill invocation | File references | Slash commands (`/skill-name`) |
| Organization | Flat file list | Hierarchical with supporting files |
| Template reusability | Copy-paste from skill | Reference template files |

---

## Lessons Learned (2026-01-31)

1. **Gemini for analysis, Claude for creativity**
   - Gemini excels at structured data extraction
   - Claude excels at natural language and detailed storyboards

2. **Don't duplicate content in Campaign Summary**
   - Reference files instead: `> See video_synthesis.md for details`
   - Keeps files smaller and maintains single source of truth

3. **Quality gates prevent wasted work**
   - Pre-check for analysis files before script generation
   - Don't start scripts if synthesis is missing/incomplete

4. **Parallel processing is key for scale**
   - Launch all Gemini tasks async, check results when needed
   - Don't use arbitrary timeouts; check actual file existence

5. **Generic stubs indicate wrong agent**
   - If output has `product: "Product"`, wrong agent was used
   - Claude Code should write all scripts directly

6. **Template extraction improves maintainability**
   - Separate templates from workflow logic
   - Easier to update formats without touching skill code
   - Enables reuse across multiple skills

---

## Skill Files

| Skill | Version | Phase | Purpose | Templates |
|:------|:--------|:------|:--------|:----------|
| `tiktok-workflow-e2e` | 1.0.0 | All | Master orchestrator | - |
| `tiktok-product-scraper` | 1.x | 1 | Product data + video download | - |
| `tiktok-ad-analysis` | 4.2.0 | 2A | Per-video analysis | - |
| `tiktok-product-analysis` | 1.0.0 | 2B | Image + synthesis | - |
| `tiktok-script-generator` | 2.3.0 | 3 | Script writing | 3 templates |
| `tiktok-targeted-analysis` | 1.x | - | Targeted analysis | - |
| `tiktok-quick-directions` | 1.x | - | Quick reference | - |

**Archived:**
- `.skills/` directory (deprecated 2026-01-31)
- Old individual `.md` skill files (migrated to SKILL.md format)
