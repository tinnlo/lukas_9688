---
name: tiktok-workflow-e2e
description: End-to-end orchestration of TikTok content creation. Single entry point for batch processing multiple products from scraping to production-ready scripts.
version: 1.2.0
author: Claude
updated: 2026-01-07 (parallel image+synthesis execution)
---

# TikTok E2E Workflow

**Single command to process products from start to finish.**

---

## Quick Start

```bash
# Process single product
/workflow 1729607303430380470

# Process batch from CSV
/workflow --batch products.csv

# Resume from specific phase
/workflow --batch products.csv --start-phase analysis
```

---

## Workflow Phases

```
┌────────────────────────────────────────────────────────────────┐
│  PHASE 1: SCRAPING (Python)                                    │
│  Skill: tiktok_product_scraper.md                              │
│  Agent: Python script                                          │
│  Parallel: Yes (across products)                               │
│  Output: tabcut_data.json, product_images/, ref_video/*.mp4    │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  PHASE 2A: VIDEO ANALYSIS (Python Async)                       │
│  Skill: tiktok_ad_analysis.md                                  │
│  Agent: Python (3-phase pipeline: extract → transcribe → API)  │
│  Parallel: 5 videos per product (internal parallelism)         │
│  Output: video_N_analysis.md (5 files)                         │
│  OPTIMIZED v4.3.0: 80-120s (was 4-5 min) - 3-5x faster        │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  PHASE 2B+2C: ANALYSIS + SYNTHESIS (Claude Parallel Reads)     │
│  Skills: tiktok_product_analysis.md + synthesis                │
│  Agent: Claude (parallel tool calls)                           │
│  Parallel: Read all 5 video analyses + glob images at once     │
│  Output: image_analysis.md + video_synthesis.md                │
│  OPTIMIZED v1.2.0: 10-15s (was 60-90s) - 4-6x faster          │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  QUALITY GATE                                                  │
│  Check: video_synthesis.md exists (80+ lines minimum)          │
│  Block: Cannot proceed to Phase 3 if missing                   │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  PHASE 3: SCRIPT GENERATION (Claude)                           │
│  Skill: tiktok_script_generator.md                             │
│  Agent: Claude (direct writing from synthesis)                 │
│  Parallel: No (quality over speed)                             │
│  Output: 3 scripts + Campaign_Summary.md                       │
└────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Scraping

### Output Folder (Dated Batches)

This vault organizes runs under `product_list/YYYYMMDD/<product_id>/` (see existing folders like `product_list/20260103/`).

Set a date folder for the current run:

```bash
DATE=YYYYMMDD
OUT="../product_list/$DATE"
mkdir -p "$OUT"
```

**Execute:**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
source venv/bin/activate

# Single product
python run_scraper.py --product-id {product_id} --download-videos --output-dir "$OUT"

# Batch (from products.csv)
python run_scraper.py --batch-file products.csv --download-videos --output-dir "$OUT"
```

**Output per product:**
```
product_list/YYYYMMDD/{product_id}/
├── tabcut_data.json       # Product metadata
├── tabcut_data.md         # Markdown version
├── product_images/        # 5-9 product images
│   └── *.webp
└── ref_video/             # Top 5 videos
    └── *.mp4
```

**Gate:** Check all products have `tabcut_data.json`

---

## Phase 2: Analysis

**⚠️ IMPORTANT:** Video analysis now runs with **internal async parallelism** (Python asyncio + ThreadPoolExecutor), not consuming Gemini MCP slots.

### Concurrency Model (v4.3.0 Optimized)

**Video Analysis (Python async):**
- Uses Python's `asyncio` with `Semaphore(5)` for 5 concurrent Gemini API calls
- Uses `ThreadPoolExecutor(5)` for parallel FFmpeg frame extraction
- **Does NOT consume Gemini MCP async slots** (runs as subprocess)
- Process products **sequentially** (one at a time)
- Within each product: 5 videos analyzed in parallel

**Image + Synthesis (Gemini MCP async):**
- Uses 2 MCP async slots per product (image + synthesis)
- Can be parallelized across products (if desired)

### Model Policy (MANDATORY)

Run analysis prompts with:
- Primary: `-m gemini-3-pro-preview`
- Fallback (only if capacity/quota hit): `-m gemini-3-flash-preview`

### 2A: Video Analysis (Python - Optimized v4.3.0)

**Execute per product:**
```bash
cd scripts
source venv/bin/activate

# Analyze all videos for one product
python analyze_video_batch.py {product_id} --date YYYYMMDD
```

**What happens internally (3-phase pipeline):**
```
📦 PHASE 1: Parallel frame extraction (ThreadPoolExecutor, 5 workers)
  → All 5 videos extract frames simultaneously (~10-15s)

🎤 PHASE 2: Sequential transcription (cached Whisper model)
  → Model loads once, transcribes all 5 videos (~30-50s)

🤖 PHASE 3: Parallel Gemini analysis (asyncio.Semaphore(5))
  → 5 async subprocess calls to gemini-cli (~60-120s)

Total: ~80-120s per product (was ~4-5 min)
```

**Performance (v4.3.0):**
- **Single product (5 videos):** 80-120 seconds (was 4-5 minutes)
- **Speedup:** 3-5x faster
- **Key optimizations:**
  - Whisper model caching (loads once)
  - Parallel frame extraction (ThreadPoolExecutor)
  - Async Gemini calls (asyncio.Semaphore(5))
  - 640px frames (faster, sufficient quality)
  - Tiny Whisper model (4x faster transcription)

**Output:** `ref_video/video_N_analysis.md` (bilingual, per video)

### 2B+2C: Image Analysis + Video Synthesis (Parallel - OPTIMIZED v1.2.0)

**⚡ OPTIMIZATION: Claude reads all files in parallel, generates both analyses immediately.**

**How it works**:
1. In a single message, make parallel tool calls:
   - `Read()` all 5 `video_*_analysis.md` files
   - `Glob()` all product images
2. Generate both outputs:
   - `image_analysis.md`
   - `video_synthesis.md`

**No external scripts needed** - just use Claude's native parallel tool execution.

**Performance**:
- **Old (sequential):** 60-90 seconds (read → generate → read → generate)
- **New (parallel):** 10-15 seconds (read all → generate both)
- **Speedup:** 4-6x faster

**Output per product:**
- `product_images/image_analysis.md`
- `ref_video/video_synthesis.md` (CRITICAL)

---

## Quality Gate

**Before Phase 3, verify:**

```bash
#!/bin/bash
# verify_ready_for_scripts.sh

date="YYYYMMDD"
products="1729607303430380470 1729607478878640746 ..."  # Your product IDs

for pid in $products; do
  echo "=== $pid ==="

  # MANDATORY: Synthesis must exist
  if [ ! -f "product_list/$date/$pid/ref_video/video_synthesis.md" ]; then
    echo "❌ BLOCKED: video_synthesis.md missing"
    exit 1
  fi

  lines=$(wc -l < "product_list/$date/$pid/ref_video/video_synthesis.md" | tr -d ' ')
  if [ "$lines" -lt 150 ]; then
    echo "❌ BLOCKED: synthesis only $lines lines (need 150+)"
    exit 1
  fi

  echo "✅ Ready for scripts"
done

echo ""
echo "=== ALL PRODUCTS READY FOR PHASE 3 ==="
```

### Recommended (Repo Verifier)

Run the repo verifier script (hard gate) instead of maintaining manual lists:

```bash
# Gate analysis + scripts for a date batch folder
bash scripts/verify_gate.sh --date YYYYMMDD --csv scripts/products.csv --phase all
```

---

## Phase 3: Script Generation

**Execute (Claude Code):**

For each product, Claude reads analysis files and writes:
1. `Script_1_[Angle].md` - Hook/Challenge angle
2. `Script_2_[Angle].md` - Feature Demo angle
3. `Script_3_[Angle].md` - Social Proof angle
4. `Campaign_Summary.md` - Executive summary

**Output location:** `product_list/YYYYMMDD/{product_id}/scripts/`

**Key rules:**
- Claude writes ALL scripts (not Gemini)
- Read synthesis first, then write
- Campaign Summary references files (no duplication)

### Retry / Stop Rules

- If the gate fails (missing files or below line thresholds), retry the failed stage **once** with the strict output contract prompts.
- If it fails again, mark that product as **BLOCKED** and continue to the next product (do not generate scripts with incomplete analysis).

---

## Autonomous Batch Execution

**To run the full workflow autonomously:**

```
User prompt to Claude:

"Run the e2e workflow for these products autonomously:
- products.csv contains 8 product IDs
- Don't pause for approval between phases
- If something fails, retry once then skip and continue
- Report failures at the end"
```

**Claude will:**
1. Run Phase 1 (scraping) - wait for completion
2. Run Phase 2A (video analysis) - parallel via Python
3. Run Phase 2B+2C (image + synthesis) - parallel via Gemini async
4. Verify quality gate
5. Run Phase 3 (scripts) - sequential for quality
6. Report completion status

---

## Time Estimates

**Updated for v4.3.0 video analysis optimizations**

| Phase | Single Product | 8 Products (Sequential) | Scaling Notes |
|:------|:---------------|:------------------------|:--------------|
| 1. Scraping | 2-3 min | 5 min | Parallel across products |
| 2. Analysis (per product) | **2-3 min** | **16-24 min** | **Sequential products, optimized** |
|  - Videos (Python async) | **1.5-2 min** | **12-16 min** | **v4.3.0: 3-5x faster** |
|  - Image (Gemini MCP) | 0.5 min | 4 min | 1 MCP task per product |
|  - Synthesis (Gemini MCP) | 0.5 min | 4 min | 1 MCP task per product |
| 3. Scripts | 5-8 min | 40-50 min | Sequential for quality |
| **Total** | **9-14 min** | **~61-79 min** | **Was 77-87 min** |

### Performance Improvement

**Phase 2 Analysis (8 products):**
- **Old (v4.2.0):** 8 × 4 min = 32 min
- **New (v4.3.0):** 8 × 2-3 min = 16-24 min
- **Savings:** ~8-16 minutes per 8-product batch

### Pipeline Strategy (8 Products)

**Phase 2 Analysis (Sequential products, optimized pipeline within each):**

```
Product 1: [Videos: 1.5-2min] → [Image: 0.5min] → [Synthesis: 0.5min] = 2.5-3 min
Product 2: [Videos: 1.5-2min] → [Image: 0.5min] → [Synthesis: 0.5min] = 2.5-3 min
Product 3: [Videos: 1.5-2min] → [Image: 0.5min] → [Synthesis: 0.5min] = 2.5-3 min
...
Product 8: [Videos: 1.5-2min] → [Image: 0.5min] → [Synthesis: 0.5min] = 2.5-3 min
Total: 8 × 2.5-3 min = 20-24 min (was 32 min)
```

**Why this is fast:**
- **Optimized video analysis:** Python async with Semaphore(5) + ThreadPoolExecutor(5)
  - Parallel frame extraction (5 FFmpeg at once)
  - Cached Whisper model (loads once)
  - 5 concurrent Gemini API calls
  - Result: 80-120s for 5 videos (was 4-5 min)
- **Sequential products:** Required to maintain quality and avoid quota issues
- **vs Old sequential:** 8 × 4 min = 32 min → **Now 20-24 min (25-37% faster)**

---

## Error Handling

| Error | Action |
|:------|:-------|
| Scraping fails | Retry once, then skip product |
| No videos downloaded | Skip video analysis, continue with images |
| Video analysis fails | Retry with single video, mark incomplete |
| Image analysis fails | Continue without (not mandatory) |
| Synthesis fails | BLOCK - retry until success or manual intervention |
| Script generation fails | Retry, check for generic placeholders |

---

## Resume Points

**If workflow interrupted:**

```bash
# Check current state
./check_workflow_status.sh products.csv

# Resume from Phase 2
/workflow --batch products.csv --start-phase analysis

# Resume from Phase 3 only
/workflow --batch products.csv --start-phase scripts
```

---

## Skill Dependency Map

```
tiktok_product_scraper.md
         │
         ├──────────────────────────┐
         │                          │
         ▼                          ▼
tiktok_ad_analysis.md    tiktok_product_analysis.md
(video_N_analysis.md)    (image_analysis.md)
         │                          │
         └──────────┬───────────────┘
                    │
                    ▼
         tiktok_product_analysis.md
            (video_synthesis.md)
                    │
                    ▼
         tiktok_script_generator.md
         (Script_1/2/3.md + Campaign_Summary.md)
```

---

## Example: Full Batch Run

```
User: Run e2e workflow for products.csv autonomously

Claude:
1. Starting Phase 1: Scraping 8 products...
   ✅ 8/8 products scraped (5 min)

2. Starting Phase 2: Analysis (sequential products, optimized v4.3.0)...

   === Product 1/8 ===
   - Running Python video analysis (optimized)...
     📦 PHASE 1: Parallel frame extraction (5 workers)
     🎤 PHASE 2: Cached Whisper transcription
     🤖 PHASE 3: Async Gemini analysis (5 concurrent)
   ✅ Videos analyzed (1.5 min)
   - Analyzing product images (Gemini MCP)...
   ✅ Images analyzed (0.5 min)
   - Creating market synthesis (Gemini MCP)...
   ✅ Synthesis complete (0.5 min)
   ✅✅✅ Product 1 COMPLETE (2.5 min)

   === Product 2/8 ===
   - Running Python video analysis (optimized)...
   ✅ Videos analyzed (2 min)
   - Analyzing product images...
   ✅ Images analyzed (0.5 min)
   - Creating market synthesis...
   ✅ Synthesis complete (0.5 min)
   ✅✅✅ Product 2 COMPLETE (3 min)

   ...

   === Product 8/8 ===
   ✅✅✅ Product 8 COMPLETE (2.5 min)

   ✅ All 8 products analyzed (21 min total, was 32 min)

3. Quality Gate...
   ✅ 8/8 products have valid synthesis files

4. Starting Phase 3: Script Generation...
   - Product 1/8: Writing scripts... ✅ (6 min)
   - Product 2/8: Writing scripts... ✅ (5 min)
   ...
   - Product 8/8: Writing scripts... ✅ (5 min)

=== WORKFLOW COMPLETE ===
Total time: 71 minutes (was 83 min - 14% faster with v4.3.0)
Products processed: 8/8
Scripts generated: 24 (3 per product)
Campaign summaries: 8

Ready for video production!
```

---

**Version:** 1.1.0  
**Last Updated:** 2026-01-07  
**Changelog:**
- v1.1.0 (2026-01-07): Updated for v4.3.0 video analysis optimizations
  - 3-5x faster video analysis (Python async + ThreadPoolExecutor)
  - Updated time estimates (8 products: 71 min vs 83 min)
  - Clarified that video analysis uses Python async, not MCP slots
  - Added performance breakdown and optimization details
- v1.0.0 (2026-01-01): Initial e2e workflow documentation
