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

**Execute:**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
source venv/bin/activate

# Single product
python run_scraper.py --product-id {product_id} --download-videos

# Batch (from products.csv)
python run_scraper.py --batch-file products.csv --download-videos
```

**Output per product:**
```
product_list/{product_id}/
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

**Sub-phases (can run in parallel):**

### 2A: Video Analysis (Python + Gemini)
```bash
# For each product with videos
python analyze_video_batch.py {product_id}
```

**Output:** `ref_video/video_N_analysis.md` (per video)

### 2B: Image Analysis (Gemini async MCP)
```javascript
// Launch all image analyses in parallel
for (product_id of products) {
  mcp__gemini-cli-mcp-async__gemini_cli_execute_async({
    query: `Analyze images in product_list/${product_id}/product_images/
            Create bilingual image_analysis.md with 10+ sections.
            Save to product_list/${product_id}/product_images/image_analysis.md`,
    yolo: true
  })
}
```

**Output:** `product_images/image_analysis.md`

### 2C: Video Synthesis (Gemini async MCP)
**Requires:** 2A complete (video analyses exist)

```javascript
// After video analyses complete, launch synthesis in parallel
for (product_id of products) {
  mcp__gemini-cli-mcp-async__gemini_cli_execute_async({
    query: `Create market synthesis from video analyses in
            product_list/${product_id}/ref_video/video_*_analysis.md
            Include: hook patterns, selling points, replication strategy.
            Save to product_list/${product_id}/ref_video/video_synthesis.md`,
    yolo: true
  })
}
```

**Output:** `ref_video/video_synthesis.md` (CRITICAL)

---

## Quality Gate

**Before Phase 3, verify:**

```bash
#!/bin/bash
# verify_ready_for_scripts.sh

products="1729607303430380470 1729607478878640746 ..."  # Your product IDs

for pid in $products; do
  echo "=== $pid ==="

  # MANDATORY: Synthesis must exist
  if [ ! -f "product_list/$pid/ref_video/video_synthesis.md" ]; then
    echo "❌ BLOCKED: video_synthesis.md missing"
    exit 1
  fi

  lines=$(wc -l < "product_list/$pid/ref_video/video_synthesis.md" | tr -d ' ')
  if [ "$lines" -lt 100 ]; then
    echo "⚠️ WARNING: synthesis only $lines lines"
  fi

  echo "✅ Ready for scripts"
done

echo ""
echo "=== ALL PRODUCTS READY FOR PHASE 3 ==="
```

---

## Phase 3: Script Generation

**Execute (Claude Code):**

For each product, Claude reads analysis files and writes:
1. `Script_1_[Angle].md` - Hook/Challenge angle
2. `Script_2_[Angle].md` - Feature Demo angle
3. `Script_3_[Angle].md` - Social Proof angle
4. `Campaign_Summary.md` - Executive summary

**Key rules:**
- Claude writes ALL scripts (not Gemini)
- Read synthesis first, then write
- Campaign Summary references files (no duplication)

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

| Phase | Single Product | 8 Products (Parallel) |
|:------|:---------------|:----------------------|
| 1. Scraping | 2-3 min | 5 min |
| 2A. Video Analysis | 3-5 min | 8 min |
| 2B. Image Analysis | 1-2 min | 3 min |
| 2C. Synthesis | 2-3 min | 4 min |
| 3. Scripts | 5-8 min | 40-50 min |
| **Total** | **13-21 min** | **~60-70 min** |

**vs Sequential:** 8 × 20 min = 160 min (saves 55-60%)

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

2. Starting Phase 2: Analysis...
   - Launching 8 video batch analyses (Python)
   - Launching 8 image analyses (Gemini async)
   ...waiting for video analyses...
   ✅ Video analyses complete (8 min)
   - Launching 8 synthesis tasks (Gemini async)
   ...waiting for synthesis...
   ✅ All synthesis complete (4 min)

3. Quality Gate...
   ✅ 8/8 products have valid synthesis files

4. Starting Phase 3: Script Generation...
   - Product 1/8: Writing scripts... ✅ (6 min)
   - Product 2/8: Writing scripts... ✅ (5 min)
   ...
   - Product 8/8: Writing scripts... ✅ (5 min)

=== WORKFLOW COMPLETE ===
Total time: 62 minutes
Products processed: 8/8
Scripts generated: 24 (3 per product)
Campaign summaries: 8

Ready for video production!
```

---

**Version:** 1.0.0
**Last Updated:** 2026-01-01
