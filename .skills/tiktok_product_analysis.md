---
name: tiktok-product-analysis
description: Parallel analysis pipeline for TikTok product campaigns. Handles image analysis, video analysis, and market synthesis using Gemini async MCP. Prepares all foundation data before script generation. Designed for batch processing multiple products simultaneously.
version: 1.0.0
author: Claude
execution_agent: Gemini CLI MCP (async)
---

# TikTok Product Analysis Skill

**PURPOSE:** Prepare all analysis foundation before script generation
**EXECUTOR:** Gemini CLI MCP (async for parallelism)
**OUTPUT:** Analysis files that script generator will reference (not duplicate)

---

## Agent Assignment

| Task | Agent | Tool | Parallelizable |
|:-----|:------|:-----|:---------------|
| Image Analysis | Gemini | `gemini_cli_execute_async` | Yes - per product |
| Video Analysis | Gemini | `gemini_cli_execute_async` | Yes - per video |
| Video Synthesis | Gemini | `gemini_cli_execute_async` | Yes - per product (after videos) |
| Script Generation | Claude | Direct writing | No - sequential quality focus |
| Campaign Summary | Claude | Direct writing | No - needs scripts first |

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: PARALLEL ANALYSIS (Gemini Async MCP)              │
│                                                             │
│  Product A ──┬── Image Analysis ──┐                         │
│              └── Video 1-5 Analysis ── Video Synthesis      │
│                                                             │
│  Product B ──┬── Image Analysis ──┐     (all parallel)      │
│              └── Video 1-5 Analysis ── Video Synthesis      │
│                                                             │
│  Product C ──┬── Image Analysis ──┐                         │
│              └── Video 1-5 Analysis ── Video Synthesis      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  QUALITY GATE: Verify all analysis files exist              │
│  - image_analysis.md (if images exist)                      │
│  - video_N_analysis.md (for each video)                     │
│  - video_synthesis.md (MANDATORY)                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: SCRIPT GENERATION (Claude Code)                   │
│  → Uses tiktok_script_generator.md skill                    │
│  → References analysis files (does NOT duplicate content)   │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Parallel Analysis Execution

### Step 1.1: Launch All Image Analyses (Parallel)

**For each product with images, launch async:**

```python
# Launch image analysis for all products in parallel
tasks = {}
for product_id in product_ids:
    if has_images(product_id):
        task = mcp__gemini-cli-mcp-async__gemini_cli_execute_async({
            "query": IMAGE_ANALYSIS_PROMPT.format(product_id=product_id),
            "working_dir": PROJECT_ROOT,
            "yolo": True
        })
        tasks[product_id] = {"image": task}
```

### Step 1.2: Launch All Video Analyses (Parallel)

**For each video in each product, launch async:**

```python
# Launch video analysis for all videos in parallel
for product_id in product_ids:
    videos = get_videos(product_id)
    for i, video in enumerate(videos, 1):
        task = mcp__gemini-cli-mcp-async__gemini_cli_execute_async({
            "query": VIDEO_ANALYSIS_PROMPT.format(
                product_id=product_id,
                video_num=i,
                video_path=video
            ),
            "working_dir": PROJECT_ROOT,
            "yolo": True
        })
        tasks[product_id][f"video_{i}"] = task
```

### Step 1.3: Wait for Video Analyses, Then Launch Synthesis

**Synthesis depends on video analyses completing first:**

```python
# Check video analysis completion, then launch synthesis
for product_id in product_ids:
    # Wait for all video analyses to complete
    video_tasks = [t for k, t in tasks[product_id].items() if k.startswith("video_")]
    wait_for_all(video_tasks)

    # Now launch synthesis (can run in parallel across products)
    task = mcp__gemini-cli-mcp-async__gemini_cli_execute_async({
        "query": SYNTHESIS_PROMPT.format(product_id=product_id),
        "working_dir": PROJECT_ROOT,
        "yolo": True
    })
    tasks[product_id]["synthesis"] = task
```

---

## Quality Gate: Analysis Verification

**Run BEFORE proceeding to script generation:**

```bash
#!/bin/bash
# verify_analysis.sh

product_id=$1
status="PASS"

echo "=== Analysis Verification: $product_id ==="

# Check 1: Image analysis (if images exist)
if [ -d "product_list/$product_id/product_images" ]; then
    img_count=$(find "product_list/$product_id/product_images" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) 2>/dev/null | wc -l | tr -d ' ')
    if [ "$img_count" -gt 0 ]; then
        if [ -f "product_list/$product_id/product_images/image_analysis.md" ]; then
            lines=$(wc -l < "product_list/$product_id/product_images/image_analysis.md" | tr -d ' ')
            if [ "$lines" -ge 200 ]; then
                echo "✅ Image analysis: $lines lines"
            else
                echo "⚠️ Image analysis incomplete: $lines lines (need 200+)"
                status="WARN"
            fi
        else
            echo "❌ Image analysis MISSING (found $img_count images)"
            status="FAIL"
        fi
    fi
fi

# Check 2: Video synthesis (MANDATORY if videos exist)
if [ -d "product_list/$product_id/ref_video" ]; then
    video_count=$(find "product_list/$product_id/ref_video" -type f -name "*.mp4" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$video_count" -gt 0 ]; then
        if [ -f "product_list/$product_id/ref_video/video_synthesis.md" ]; then
            lines=$(wc -l < "product_list/$product_id/ref_video/video_synthesis.md" | tr -d ' ')
            if [ "$lines" -ge 150 ]; then
                echo "✅ Video synthesis: $lines lines"
            else
                echo "⚠️ Video synthesis incomplete: $lines lines (need 150+)"
                status="WARN"
            fi
        else
            echo "❌ Video synthesis MISSING (found $video_count videos)"
            status="FAIL"
        fi

        # Check individual video analyses
        analysis_count=$(find "product_list/$product_id/ref_video" -type f -name "video_*_analysis.md" 2>/dev/null | wc -l | tr -d ' ')
        echo "   Video analyses: $analysis_count/$video_count"
    fi
fi

echo ""
echo "Status: $status"
[ "$status" = "FAIL" ] && exit 1
exit 0
```

---

## Prompt Templates

### Image Analysis Prompt (Bilingual)

```
Analyze all product images in product_list/{product_id}/product_images/

Create a BILINGUAL product analysis for TikTok script writing.

**OUTPUT FILE:** Save as product_list/{product_id}/product_images/image_analysis.md

**FORMAT:**
- Bilingual headers: ## Section | 中文标题
- Inline translations for key terms
- 10+ sections, 200+ lines minimum

**REQUIRED SECTIONS:**
1. Product Design & Aesthetics | 产品设计与美学
2. Key Features | 核心功能
3. Size & Specifications | 尺寸与规格
4. Text & Labels (German) | 文字与标签
5. Quality Signals | 质量信号
6. Color/Variant Options | 颜色/变体选项
7. Key Differentiators | 关键差异化
8. Usage Context | 使用场景
9. Packaging | 包装展示
10. Visual Hooks for Scripts | 脚本视觉钩子

**CRITICAL - Section 10 Must Include:**
- 5+ specific visual hook ideas
- Filming instructions for each
- German hook lines for scripts
- Priority ranking for script angles
```

### Video Analysis Prompt (Per Video)

```
Analyze video: product_list/{product_id}/ref_video/video_{video_num}_*.mp4

**OUTPUT FILE:** Save as product_list/{product_id}/ref_video/video_{video_num}_analysis.md

**REQUIRED SECTIONS:**
1. Video Metadata (duration, creator, views)
2. Hook Analysis (first 3 seconds)
3. Voiceover/Dialogue Transcript (German + Chinese translation)
4. Visual Storyboard (shot-by-shot)
5. Key Selling Points (ranked)
6. Music/Audio Analysis
7. CTA Analysis
8. Target Audience Inference
9. Effectiveness Rating (1-10)
10. Replication Insights

**FORMAT:**
- Bilingual: German/English content with Chinese translations
- Specific timestamps for each section
- Actionable insights for script writers
```

### Video Synthesis Prompt (Market Summary)

```
Create a COMPREHENSIVE market synthesis from all video analyses in:
product_list/{product_id}/ref_video/video_*_analysis.md

**OUTPUT FILE:** Save as product_list/{product_id}/ref_video/video_synthesis.md

**REQUIRED SECTIONS (14 minimum):**
1. Executive Summary | 执行摘要
2. Common Winning Patterns | 共同获胜模式
   - Hook Types (ranked by effectiveness)
   - Visual Strategy
   - Key Selling Points (ranked by emphasis)
3. Duration Sweet Spot | 时长最佳点
4. Language & Voice Strategy | 语言与声音策略
5. Target Audience Profile | 目标受众画像
6. Creative Production Patterns | 创意制作模式
7. Seasonal Context | 季节性背景
8. Compliance & Trust Signals | 合规与信任信号
9. Competitive Differentiation | 竞争差异化
10. Replication Strategy | 复制策略
    - 3+ specific script angles with estimated effectiveness
11. Performance Predictions | 效果预测
12. Recommendations (DO's and DON'Ts) | 建议
13. Source Materials | 源材料

**FORMAT:**
- Bilingual headers and inline translations
- 150+ lines minimum (comprehensive analysis)
- Actionable insights for script generation
```

---

## Batch Processing Example

**For 8 products with 5 videos each = 48 parallel tasks:**

```python
# Time comparison:
# Sequential: 8 products × (5 videos × 2min + synthesis 3min + image 2min) = 8 × 15min = 120min
# Parallel:   All 40 videos parallel (2min) + 8 synthesis parallel (3min) + 8 images parallel (2min) = 7min

# Launch all tasks
all_tasks = {}
for product_id in products:
    all_tasks[product_id] = {}

    # Image analysis (parallel)
    if has_images(product_id):
        all_tasks[product_id]['image'] = launch_image_analysis(product_id)

    # Video analyses (parallel)
    for i in range(1, 6):
        all_tasks[product_id][f'video_{i}'] = launch_video_analysis(product_id, i)

# Wait for all video analyses, then launch synthesis (parallel)
for product_id in products:
    wait_for_videos(all_tasks[product_id])
    all_tasks[product_id]['synthesis'] = launch_synthesis(product_id)

# Wait for all synthesis to complete
wait_for_all_synthesis(all_tasks)

# Quality gate verification
for product_id in products:
    verify_analysis(product_id)

# Now proceed to script generation (Claude Code)
print("✅ All analysis complete. Ready for script generation.")
```

---

## Handoff to Script Generator

**After Phase 1 completes, the following files exist:**

```
product_list/{product_id}/
├── tabcut_data.json           # Product metadata (from scraper)
├── product_images/
│   ├── *.webp                 # Product images
│   └── image_analysis.md      # Gemini analysis (bilingual)
└── ref_video/
    ├── video_1_*.mp4          # Reference videos
    ├── video_1_analysis.md    # Per-video analysis
    ├── video_2_analysis.md
    ├── ...
    └── video_synthesis.md     # Market summary (CRITICAL)
```

**Script generator (Claude Code) will:**
1. Read these files (not regenerate them)
2. Extract key insights for scripts
3. Reference files in Campaign Summary (not duplicate content)

---

## Error Handling

**If analysis fails:**

1. **Retry once** with same prompt
2. **If retry fails:** Mark product as "analysis_incomplete"
3. **Continue with other products** (don't block batch)
4. **Report failures** at end for manual review

```python
# Error handling pattern
try:
    result = await check_task(task_id)
    if result.status == "failed":
        # Retry once
        retry_task = launch_retry(product_id, task_type)
        result = await check_task(retry_task)
        if result.status == "failed":
            failed_products.append(product_id)
            continue
except TimeoutError:
    failed_products.append(product_id)
    continue

# At end of batch
if failed_products:
    print(f"⚠️ Failed products: {failed_products}")
    print("Run manually or skip for now")
```

---

## Integration with Existing Skills

**This skill replaces image analysis from `tiktok_script_generator.md`**

**Workflow order:**
1. `tiktok_product_scraper.md` → Downloads product data + videos
2. `tiktok_product_analysis.md` → Analyzes images + videos (THIS SKILL)
3. `tiktok_script_generator.md` → Generates scripts using analysis files

---

**Version:** 1.0.0
**Last Updated:** 2026-01-01
