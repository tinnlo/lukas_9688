---
name: tiktok-workflow-e2e
description: End-to-end orchestration of TikTok content creation. Single entry point for batch processing multiple products from scraping to production-ready scripts.
version: 1.0.0
author: Claude
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
│  PHASE 2: ANALYSIS (Gemini)                                    │
│  Skills: tiktok_ad_analysis.md + tiktok_product_analysis.md    │
│  Agent: Python (video) + Gemini async MCP (image + synthesis)  │
│  Parallel: Yes (all tasks across all products)                 │
│  Output: video_N_analysis.md, image_analysis.md,               │
│          video_synthesis.md                                    │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  QUALITY GATE                                                  │
│  Check: video_synthesis.md exists (150+ lines) for all         │
│  Block: Cannot proceed to Phase 3 if missing                   │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  PHASE 3: SCRIPT GENERATION (Claude)                           │
│  Skill: tiktok_script_generator.md                             │
│  Agent: Claude Code (direct writing)                           │
│  Parallel: No (sequential for quality)                         │
│  Output: Script_1/2/3.md, Campaign_Summary.md                  │
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

**⚠️ CONCURRENCY LIMIT:** Max 5 Gemini async tasks at once.

### Model Policy (MANDATORY)

Run analysis prompts with:
- Primary: `-m gemini-3-pro-preview`
- Fallback (only if capacity/quota hit): `-m gemini-3-flash-preview`

**CRITICAL CONSTRAINT:** Each product has 5 videos. Analyzing 5 videos in parallel = all 5 slots used.
- **Process products SEQUENTIALLY** (one complete pipeline at a time)
- **Within each product:** Videos in parallel → Image → Synthesis (sequential stages)

### 2A: Video Analysis (Python + Gemini - Per Product)
```bash
# For each product with videos
# This script analyzes videos sequentially per product
python analyze_video_batch.py {product_id} --date YYYYMMDD
```

**Output:** `ref_video/video_N_analysis.md` (per video)

### 2B: Complete Product Pipeline (Gemini async MCP)

**Process products sequentially with pipeline stages:**

```javascript
// Process products ONE AT A TIME (sequential)
const date = "YYYYMMDD";
for (const product_id of products) {
  console.log(`\n=== Processing ${product_id} ===`);
  const base = `product_list/${date}/${product_id}`;

  // Stage 1: Launch 5 video analyses in parallel (fills all 5 slots)
  console.log(`Stage 1: Analyzing 5 videos in parallel...`);
  const videoTasks = [];

  for (let i = 1; i <= 5; i++) {
    const task = await mcp__gemini-cli-mcp-async__gemini_cli_execute_async({
      query: `Analyze video ${i} in ${base}/ref_video/
              Create bilingual video_${i}_analysis.md with detailed breakdown.
              Save to ${base}/ref_video/video_${i}_analysis.md`,
      yolo: true
    });
    videoTasks.push(task);
  }

  // Wait for all 5 videos to complete
  await Promise.all(videoTasks.map(t => waitForCompletion(t)));
  console.log(`✅ Videos analyzed`);

  // Stage 2: Image analysis (1 task)
  console.log(`Stage 2: Analyzing product images...`);
  const imageTask = await mcp__gemini-cli-mcp-async__gemini_cli_execute_async({
    query: `Analyze images in ${base}/product_images/
            Create bilingual image_analysis.md with 10+ sections.
            Save to ${base}/product_images/image_analysis.md`,
    yolo: true
  });

  await waitForCompletion(imageTask);
  console.log(`✅ Images analyzed`);

  // Stage 3: Video synthesis (1 task)
  console.log(`Stage 3: Creating market synthesis...`);
  const synthesisTask = await mcp__gemini-cli-mcp-async__gemini_cli_execute_async({
    query: `Create market synthesis from video analyses in
            ${base}/ref_video/video_*_analysis.md
            Include: hook patterns, selling points, replication strategy.
            Save to ${base}/ref_video/video_synthesis.md`,
    yolo: true
  });

  await waitForCompletion(synthesisTask);
  console.log(`✅ Synthesis complete`);
  console.log(`✅✅✅ Product ${product_id} COMPLETE\n`);
}

console.log(`\n=== ALL ${products.length} PRODUCTS ANALYZED ===`);
```

**Output per product:**
- `ref_video/video_N_analysis.md` (5 files)
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

| Phase | Single Product | 8 Products (Sequential Pipeline) | Scaling Notes |
|:------|:---------------|:---------------------------------|:--------------|
| 1. Scraping | 2-3 min | 5 min | Parallel across products |
| 2. Analysis (per product) | 4 min | 32 min | **Sequential products** |
|  - Videos (parallel) | 2 min | 16 min | 5 videos in parallel per product |
|  - Image | 1 min | 8 min | 1 task per product |
|  - Synthesis | 1 min | 8 min | 1 task per product |
| 3. Scripts | 5-8 min | 40-50 min | Sequential for quality |
| **Total** | **11-15 min** | **~77-87 min** | |

### Pipeline Strategy (8 Products)

**Phase 2 Analysis (Sequential products, pipeline within each):**

```
Product 1: [5 videos||] → [image] → [synthesis] = 4 min
Product 2: [5 videos||] → [image] → [synthesis] = 4 min
Product 3: [5 videos||] → [image] → [synthesis] = 4 min
...
Product 8: [5 videos||] → [image] → [synthesis] = 4 min
Total: 8 × 4 min = 32 min
```

**Why this is still fast:**
- **Parallel videos within each product:** 5 videos × 2min = 10min if sequential → 2min with parallel ✅
- **Sequential products:** Required due to 5-task concurrency limit
- **vs Fully sequential:** 8 × (10 + 1 + 1) = 96 min → **3x slower**
- **vs Trying to parallelize (broken):** Would launch 40 video tasks → **TIMEOUT/FAILURE**

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

2. Starting Phase 2: Analysis (sequential products, pipeline within each)...

   === Product 1/8 ===
   - Stage 1: Launching 5 video analyses in parallel...
   ✅ Videos analyzed (2 min)
   - Stage 2: Analyzing product images...
   ✅ Images analyzed (1 min)
   - Stage 3: Creating market synthesis...
   ✅ Synthesis complete (1 min)
   ✅✅✅ Product 1 COMPLETE (4 min)

   === Product 2/8 ===
   - Stage 1: Launching 5 video analyses in parallel...
   ✅ Videos analyzed (2 min)
   - Stage 2: Analyzing product images...
   ✅ Images analyzed (1 min)
   - Stage 3: Creating market synthesis...
   ✅ Synthesis complete (1 min)
   ✅✅✅ Product 2 COMPLETE (4 min)

   ...

   === Product 8/8 ===
   ✅✅✅ Product 8 COMPLETE (4 min)

   ✅ All 8 products analyzed (32 min total)

3. Quality Gate...
   ✅ 8/8 products have valid synthesis files

4. Starting Phase 3: Script Generation...
   - Product 1/8: Writing scripts... ✅ (6 min)
   - Product 2/8: Writing scripts... ✅ (5 min)
   ...
   - Product 8/8: Writing scripts... ✅ (5 min)

=== WORKFLOW COMPLETE ===
Total time: 83 minutes
Products processed: 8/8
Scripts generated: 24 (3 per product)
Campaign summaries: 8

Ready for video production!
```

---

**Version:** 1.0.0
**Last Updated:** 2026-01-01
