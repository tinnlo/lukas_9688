# TikTok Content Creation Skills

Complete workflow for TikTok product video script generation with clear agent separation and parallel processing.

**Version:** 2.1.0
**Last Updated:** 2026-01-01

---

## Quick Start: E2E Workflow

**For full end-to-end processing, use:**
```
tiktok_workflow_e2e.md
```

This orchestrates all 4 skills in proper order with quality gates.

---

## Skill Overview

| Skill | Phase | Purpose | Agent |
|:------|:------|:--------|:------|
| `tiktok_workflow_e2e.md` | All | **Master orchestrator** - runs full pipeline | Orchestration |
| `tiktok_product_scraper.md` | 1 | Download product data + videos | Python |
| `tiktok_ad_analysis.md` | 2A | Per-video analysis (frames + transcription) | Python + Gemini |
| `tiktok_product_analysis.md` | 2B | Image analysis + synthesis orchestration | Gemini async MCP |
| `tiktok_script_generator.md` | 3 | Write scripts + Campaign Summary | Claude Code |

### Which skill to use?

| Scenario | Skill to Use |
|:---------|:-------------|
| Full batch processing (e2e) | `tiktok_workflow_e2e.md` |
| Just scraping products | `tiktok_product_scraper.md` |
| Re-analyze videos only | `tiktok_ad_analysis.md` |
| Re-generate synthesis only | `tiktok_product_analysis.md` |
| Re-write scripts only | `tiktok_script_generator.md` |

---

## Workflow Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: DATA COLLECTION (Python)                                 │
│                                                                     │
│  tiktok_product_scraper.md                                          │
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
│  tiktok_ad_analysis.md (per video)                                  │
│  ├── FFmpeg: Extract keyframes + audio                              │
│  ├── Whisper: Transcribe audio                                      │
│  └── Gemini: Generate video_N_analysis.md                           │
│                                                                     │
│  tiktok_product_analysis.md (orchestration)                         │
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
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3: SCRIPT GENERATION (Claude Code - SEQUENTIAL)              │
│                                                                     │
│  tiktok_script_generator.md                                         │
│  ├── Read analysis files (video_synthesis.md, image_analysis.md)    │
│  ├── Write 3 production scripts with:                               │
│  │   ├── Detailed storyboards                                       │
│  │   ├── Bilingual voiceovers (DE + ZH)                             │
│  │   ├── ElevenLabs v3 grammar markers                              │
│  │   └── Visual filming instructions                                │
│  └── Create Campaign Summary (references files, no duplication)     │
│                                                                     │
│  Outputs:                                                           │
│  ├── scripts/Script_1_[Angle].md                                    │
│  ├── scripts/Script_2_[Angle].md                                    │
│  ├── scripts/Script_3_[Angle].md                                    │
│  └── scripts/Campaign_Summary.md                                    │
│                                                                     │
│  Time: ~5-8 min per product (focused quality writing)               │
└─────────────────────────────────────────────────────────────────────┘
```

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
Phase 3 (scripts):    ~40 min (8 products × 5 min, focused quality)
────────────────────────────────────────────────────
Total:               ~77 min (36% faster)
```

### Scaling Benefits

**⚠️ CRITICAL:** Each product has **5 videos**. Analyzing 5 videos in parallel = **all 5 Gemini async slots used**.

| Products | Old (Fully Sequential) | New (Pipeline) | Per Product | Savings |
|:---------|:----------------------|:---------------|:------------|:--------|
| 1 | 15 min | 11 min | 4 min analysis | 27% |
| 5 | 75 min | 45 min | 5 × 4 min = 20 min | 40% |
| 8 | 120 min | 77 min | 8 × 4 min = 32 min | 36% |
| 20 | 300 min | 165 min | 20 × 4 min = 80 min | 45% |
| 50 | 750 min | 405 min | 50 × 4 min = 200 min | 46% |

### Pipeline Strategy

**CRITICAL CONSTRAINT:** 5-task concurrency limit in Gemini async MCP

**Sequential products (one at a time):**
- Product 1: [5 videos in parallel] → [image] → [synthesis] = 4 min
- Product 2: [5 videos in parallel] → [image] → [synthesis] = 4 min
- Product 3: [5 videos in parallel] → [image] → [synthesis] = 4 min
- ...

**Why sequential products:**
- Each product's 5 videos use all 5 concurrent task slots
- Cannot process multiple products simultaneously without exceeding limit
- Trying to parallelize products → 40+ concurrent tasks → **TIMEOUT/FAILURE**

**Why still fast:**
- **Within each product:** 5 videos in parallel (not sequential)
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
# Use tiktok_script_generator.md skill
```

### Batch Processing
```bash
# Step 1: Scrape all products
python run_scraper.py --batch-file products.csv --download-videos

# Step 2: Parallel analysis (use tiktok_product_analysis.md)
# Launch via Gemini async MCP - see skill for details

# Step 3: Verify analysis complete
./verify_analysis.sh

# Step 4: Generate scripts (Claude Code)
# Process each product with tiktok_script_generator.md
```

---

## File Structure After Completion

```
product_list/{product_id}/
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

## Key Changes from v1

| Aspect | v1 (Old) | v2 (New) |
|:-------|:---------|:---------|
| Image analysis | In script generator skill | Separate `tiktok_product_analysis.md` |
| Agent for scripts | Gemini (sometimes) | Claude Code (always) |
| Campaign Summary | Duplicates analysis content | References analysis files |
| Batch processing | Sequential | Parallel analysis, sequential scripts |
| Skill file size | 27k+ tokens | ~11k tokens (simplified) |
| Steps | 13 steps | 5 steps |

---

## Lessons Learned (2026-01-01)

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

---

## Skill Files

| File | Version | Phase | Purpose |
|:-----|:--------|:------|:--------|
| `tiktok_workflow_e2e.md` | 1.0.0 | All | **Master orchestrator** - full pipeline |
| `tiktok_product_scraper.md` | 1.x | 1 | Product data + video download |
| `tiktok_ad_analysis.md` | 4.2.0 | 2A | Per-video analysis (Python + Gemini) |
| `tiktok_product_analysis.md` | 1.0.0 | 2B | Image + synthesis (Gemini async) |
| `tiktok_script_generator.md` | 2.0.0 | 3 | Script writing (Claude Code) |
| `tiktok_quick_directions.md` | 1.x | - | Quick reference for directions |
| `README.md` | 2.1.0 | - | This overview |

**Archived:**
- `tiktok_script_generator_v1.md` - Old 27k+ token version (for reference)
