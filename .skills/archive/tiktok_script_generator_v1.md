---
name: tiktok-script-generator
description: Generates 3 TikTok short video scripts (30-40s) for product campaigns with comprehensive bilingual campaign summary. Uses proven "Golden 3 Seconds" hook patterns for German market. Analyzes reference videos, product data, and images (comprehensive bilingual v1.5 format with inline translations via async Gemini CLI MCP + OUTPUT VALIDATION). INTEGRATES VISUAL HOOKS from image analysis directly into scripts with filming instructions. Creates bilingual (DE/ZH) scripts AND bilingual Campaign Summary with inline Chinese translations. Optimized for parallel batch workflows. INCLUDES MANDATORY STEPS (validated bilingual image analysis with Visual Hooks section, hook extraction & integration, bilingual Campaign Summary with image insights, Final Quality Gate with bilingual verification) with explicit batch execution checklist and quality verification to prevent incomplete deliverables.
version: 1.7.0
author: Claude
---

# TikTok Script Generator Skill

Generates 3 production-ready TikTok ad scripts based on reference video analysis, product data, visual analysis, and official product descriptions.

## Overview

**Input:** Product ID + Category
**Output:** 3 distinct angle scripts (30-40s each) + Bilingual Campaign Summary in `product_list/{product_id}/scripts/`

**Key Features:**
- **Golden 3 Seconds Hook Patterns:** 8 proven opening strategies for German TikTok
- Multi-source analysis (videos, data, images, official description)
- Category-specific compliance verification
- Bilingual output (German + Chinese translation) for scripts AND Campaign Summary
- ElevenLabs v3 (alpha) grammar formatting
- Visual hook integration from packaging
- 3 different marketing angles per product
- Comprehensive bilingual campaign summary with inline Chinese translations and performance predictions

---

## Workflow Steps

**Complete workflow (13 steps):**

0. **Pre-Check Verification** ⚠️ **MANDATORY - BLOCKS IF FAILS** - Verify all required source files exist before starting
1. **Gather Source Materials** - Collect all reference files
2. **Product Image Analysis** ⚠️ **MANDATORY IF IMAGES EXIST** - Analyze using async Gemini CLI MCP (v1.5 format)
3. **Official Description Verification** - Cross-reference product claims
4. **Determine Product Category** - Identify compliance rules
5. **Script Angle Planning** - Map 3 distinct marketing angles
5.5. **Golden 3 Seconds Hook Selection** - Choose proven hook patterns
5.7. **Extract Visual Hooks from Image Analysis** - Map Section 10 hooks to script angles (if Step 2 completed)
6. **Script Writing** - Create 3 scripts with visual hook integration
7. **ElevenLabs v3 Grammar** - Format voiceover cues
8. **Bilingual Translation** - Add Chinese (ZH) versions
9. **Compliance Verification** - Check category-specific rules
10. **Campaign Summary Creation** ⚠️ **MANDATORY** - Comprehensive campaign overview with image insights
11. **Final Quality Gate** ⚠️ **MANDATORY** - Verification checkpoint including image analysis check

**🚨 CRITICAL MANDATORY STEPS (Cannot be skipped):**
- **Step 2:** Image analysis (if `product_images/` folder exists with images)
- **Step 10:** Campaign Summary creation
- **Step 11:** Final Quality Gate verification

**⚠️ BATCH EXECUTION WARNING:**
When processing multiple products in batch mode, these mandatory steps are frequently missed. You MUST explicitly verify before marking any product complete:
- [ ] Image analysis completed (if images exist)
- [ ] Campaign Summary created
- [ ] Final Quality Gate passed

---

## Batch Execution Checklist (CRITICAL)

When processing multiple products from `products.csv` or a batch list:

### Pre-Execution Setup
```bash
# Verify all products have required source materials
for product_id in {list}; do
  echo "=== Checking $product_id ==="
  ls -lh product_list/$product_id/
  # Must have: tabcut_data.md or fastmoss_data.json
  # Optional: video_analysis.md, product_images/, ref_video/
done
```

### Per-Product Execution Order

**For EACH product, execute ALL 12 steps in sequence:**

1. ✅ Gather source materials
2. ⚠️ **STOP:** Check if `product_images/` exists and has files
   - **IF YES:** Run async Gemini CLI MCP image analysis (v1.5 format) → Save to `image_analysis.md`
   - **IF NO:** Skip to Step 3
3. ✅ Verify official description
4. ✅ Determine category
5. ✅ Plan 3 angles
5.5. ✅ Select Golden 3 Seconds hooks
5.7. ✅ **IF Step 2 completed:** Extract Visual Hooks from Section 10, map to 3 script angles
   - **IF Step 2 skipped:** Skip to Step 6
6. ✅ Write 3 scripts (integrate visual hooks if available)
7. ✅ Format ElevenLabs v3 grammar
8. ✅ Add bilingual (DE/ZH)
9. ✅ Verify compliance
10. ⚠️ **MANDATORY:** Create Campaign Summary (include image insights if Step 2 completed)
11. ⚠️ **MANDATORY:** Run Final Quality Gate verification

**🛑 DO NOT proceed to next product until Step 11 PASSES for current product.**

### Common Batch Failure Modes

**❌ Mistake 1: Skipping image analysis**
- **Why it happens:** Rushing to script writing
- **Fix:** Add explicit check at Step 2 - if images exist, MUST analyze

**❌ Mistake 2: Forgetting Campaign Summary**
- **Why it happens:** Scripts feel "complete" without it
- **Fix:** Step 10 is NOT optional - always create Campaign_Summary.md

**❌ Mistake 3: Skipping Final Quality Gate**
- **Why it happens:** Assuming scripts are correct
- **Fix:** ALWAYS run Step 11 verification commands before marking complete

**❌ Mistake 4: Batch processing too fast**
- **Why it happens:** Trying to parallelize steps that must be sequential
- **Fix:** Complete ALL 11 steps for Product A before starting Product B

### Batch Verification Command

After processing N products, verify completeness:

```bash
# Run this after completing batch
for product_id in {list}; do
  echo "=== Verifying $product_id ==="

  # Check scripts folder exists
  if [ ! -d "product_list/$product_id/scripts" ]; then
    echo "❌ MISSING: product_list/$product_id/scripts/"
    continue
  fi

  # Count files (must be 4: 3 scripts + Campaign Summary)
  file_count=$(ls -1 product_list/$product_id/scripts/*.md 2>/dev/null | wc -l)
  if [ $file_count -lt 4 ]; then
    echo "❌ INCOMPLETE: Only $file_count files (expected 4)"
  else
    echo "✅ COMPLETE: $file_count files"
  fi

  # Check Campaign Summary exists
  if [ ! -f "product_list/$product_id/scripts/Campaign_Summary.md" ]; then
    echo "❌ MISSING: Campaign_Summary.md"
  fi

  # Check image analysis (if images exist)
  if [ -d "product_list/$product_id/product_images" ]; then
    img_count=$(find "product_list/$product_id/product_images" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) | wc -l)
    if [ $img_count -gt 0 ] && [ ! -f "product_list/$product_id/image_analysis.md" ]; then
      echo "⚠️ WARNING: $img_count images but no image_analysis.md"
    fi
  fi

  echo ""
done
```

**Expected Output (all products complete):**
```
=== Verifying 1729571650514622666 ===
✅ COMPLETE: 4 files

=== Verifying 1729625207544715402 ===
✅ COMPLETE: 4 files

=== Verifying 1729480021523209013 ===
✅ COMPLETE: 4 files
```

---

### Step 0: Pre-Check Verification ⚠️ MANDATORY - BLOCKS IF FAILS

**🛑 CRITICAL:** Before starting script generation, verify all required source files exist. This prevents wasted effort on incomplete data.

**Purpose:** Ensure the campaign is built on complete foundation data (product info, images, videos).

#### Pre-Check Command

```bash
# Run this verification BEFORE Step 1
product_id="{product_id}"

echo "=== PRE-CHECK VERIFICATION FOR PRODUCT: $product_id ==="
echo ""

# Check 1: Product data file (MANDATORY - at least one must exist)
echo "1. Checking product data files..."
has_tabcut=false
has_fastmoss=false

if [ -f "product_list/$product_id/tabcut_data.md" ]; then
  echo "   ✅ tabcut_data.md exists"
  has_tabcut=true
elif [ -f "product_list/$product_id/fastmoss_data.json" ]; then
  echo "   ✅ fastmoss_data.json exists"
  has_fastmoss=true
fi

if [ "$has_tabcut" = false ] && [ "$has_fastmoss" = false ]; then
  echo "   ❌ BLOCKER: No product data file found"
  echo "   Required: tabcut_data.md OR fastmoss_data.json"
  exit 1
fi

# Check 2: Image analysis (MANDATORY if images exist)
echo ""
echo "2. Checking image analysis..."
if [ -d "product_list/$product_id/product_images" ]; then
  img_count=$(find "product_list/$product_id/product_images" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) 2>/dev/null | wc -l)
  if [ $img_count -gt 0 ]; then
    echo "   Found $img_count product images"
    if [ -f "product_list/$product_id/image_analysis.md" ]; then
      line_count=$(wc -l < "product_list/$product_id/image_analysis.md")
      echo "   ✅ image_analysis.md exists ($line_count lines)"
      if [ $line_count -lt 250 ]; then
        echo "   ⚠️  WARNING: Analysis seems incomplete ($line_count < 250 lines)"
      fi
    else
      echo "   ❌ BLOCKER: image_analysis.md MISSING"
      echo "   Required: Run Step 2 (Image Analysis) first"
      exit 1
    fi
  else
    echo "   ⏭️  No images found - image analysis not required"
  fi
else
  echo "   ⏭️  No product_images folder - image analysis not required"
fi

# Check 3: Video analysis (MANDATORY if videos exist)
echo ""
echo "3. Checking video analysis..."
if [ -d "product_list/$product_id/ref_video" ]; then
  video_count=$(find "product_list/$product_id/ref_video" -type f -name "*.mp4" 2>/dev/null | wc -l)
  if [ $video_count -gt 0 ]; then
    echo "   Found $video_count reference videos"

    # Check individual video analyses
    analysis_count=$(find "product_list/$product_id/ref_video" -type f -name "video_*_analysis.md" 2>/dev/null | wc -l)
    echo "   Found $analysis_count individual video analyses"

    if [ $analysis_count -eq 0 ]; then
      echo "   ❌ BLOCKER: No video_*_analysis.md files found"
      echo "   Required: Run Step 2 (Video Analysis) first"
      exit 1
    fi

    # Check video synthesis (market summary)
    if [ -f "product_list/$product_id/ref_video/video_synthesis.md" ]; then
      synth_lines=$(wc -l < "product_list/$product_id/ref_video/video_synthesis.md")
      echo "   ✅ video_synthesis.md exists ($synth_lines lines)"
      if [ $synth_lines -lt 200 ]; then
        echo "   ⚠️  WARNING: Synthesis seems incomplete ($synth_lines < 200 lines)"
      fi
    else
      echo "   ❌ BLOCKER: video_synthesis.md MISSING"
      echo "   Required: Market summary is mandatory when videos exist"
      exit 1
    fi
  else
    echo "   ⏭️  No videos found - video analysis not required"
  fi
else
  echo "   ⏭️  No ref_video folder - video analysis not required"
fi

# Summary
echo ""
echo "=== PRE-CHECK COMPLETE ==="
echo "✅ All required source files verified"
echo "Ready to proceed with script generation"
```

#### Pre-Check Criteria

**✅ PASS Conditions:**
- At least ONE of: `tabcut_data.md` OR `fastmoss_data.json` exists
- IF `product_images/` has files → `image_analysis.md` exists (250+ lines)
- IF `ref_video/` has .mp4 files → ALL of:
  - `video_*_analysis.md` files exist (one per video)
  - `video_synthesis.md` exists (200+ lines)

**❌ BLOCKER Conditions (STOP - Do NOT proceed):**
- No product data file (neither tabcut nor fastmoss)
- Images exist BUT no `image_analysis.md`
- Videos exist BUT no `video_*_analysis.md` files
- Videos exist BUT no `video_synthesis.md`

#### Failure Handling

**If pre-check fails, DO NOT proceed. Instead:**

1. **Missing product data:**
   ```bash
   # Re-run Step 1 (scraping)
   cd scripts && source venv/bin/activate
   python run_scraper.py --product-id {product_id}
   ```

2. **Missing image analysis (but images exist):**
   ```bash
   # Image analysis should auto-run in Step 1 of script generation
   # But if missing, this indicates Step 1 was skipped
   # Go back to Step 1 (Gather Source Materials) and run image analysis
   ```

3. **Missing video analysis (but videos exist):**
   ```bash
   # Re-run Step 2 (video analysis) - should have auto-triggered
   cd scripts && source venv/bin/activate
   python analyze_video_batch.py {product_id}
   ```

4. **Incomplete analysis files (line count too low):**
   - Regenerate analysis using complete v1.5 template
   - Verify output quality before proceeding

#### Integration with Workflow

**Before Step 1 "Gather Source Materials":**
```
[Step 0: Pre-Check] → PASS → [Step 1: Gather Source Materials] → ...
                    ↓
                   FAIL → [Fix missing files] → [Re-run Step 0]
```

**🚨 ENFORCEMENT:** If you encounter missing files during Step 1, STOP and run Pre-Check verification. Do NOT attempt to generate scripts with incomplete data.

---

### Step 1: Gather Source Materials

**Required files:**
```
product_list/{product_id}/
├── video_analysis.md          # Reference video insights
├── tabcut_data.md             # Performance metrics, top videos
├── ref_video/                 # Downloaded reference videos (may differ from tabcut)
│   ├── video_1_xxx.mp4
│   └── ...
├── product_images/            # Package photos (if available)
│   ├── product_image_1.webp
│   └── ...
└── product_description.png    # Official TikTok Shop description (screenshot)
```

**Actions:**
1. **Verify local video files** - Check if `ref_video/` matches `tabcut_data.md` listings
   - User may have curated videos (deleted bad ones, added better ones)
   - If mismatch detected, prioritize analyzing ACTUAL local video files
2. Read `video_analysis.md` to understand successful angles
   - **⚠️ CRITICAL:** Verify analysis is based on actual local videos, not hallucinated
   - Check video durations mentioned match actual file durations
3. Read `tabcut_data.md` for product details and top video data
4. Analyze `product_images/` using Gemini MCP for visual hooks
5. Read official product description (screenshot or text file)

**Video Analysis Verification:**

If `video_analysis.md` seems inaccurate or missing:
- Check actual video durations using ffmpeg:
  ```bash
  ffmpeg -i video_file.mp4 2>&1 | grep Duration
  ```
- If durations don't match analysis → **analysis is hallucinated, needs regeneration**

---

### Step 1.5: Video Analysis Best Practices (If Regenerating)

**⚠️ Important: Gemini MCP Limitations**

**Gemini MCP CANNOT directly access local .mp4 files.** It will hallucinate content based on:
- Filenames
- Existing analysis files
- Tabcut data

**Recommended Approaches:**

**Option A: Direct gemini-cli (Most Reliable)**
```bash
gemini "Analyze these 5 videos in [path/to/ref_video/] and report what you actually see"
```
- Run this OUTSIDE of MCP (user runs directly in terminal)
- Provides most accurate results

**Option B: Extract Video Frames (Works via Claude)**
```bash
# Extract opening frame from each video
ffmpeg -i video_1.mp4 -ss 00:00:01 -frames:v 1 -update 1 frame1.jpg -y
ffmpeg -i video_2.mp4 -ss 00:00:01 -frames:v 1 -update 1 frame2.jpg -y
# ... repeat for all videos
```
- Then analyze extracted frames using Read tool (multimodal)
- Provides visual hooks and text overlays
- Cannot capture audio/voiceover

**Option C: Manual User Input**
- Ask user to describe each video's hook, visuals, and key messages
- Most time-consuming but perfectly accurate

**Red Flags Indicating Hallucinated Analysis:**
- Video durations don't match ffmpeg output
- Claims about voiceover content without audio analysis
- Generic descriptions that could apply to any video
- Details not visible in extracted frames

---

### Step 2: Product Image Analysis ⚠️ MANDATORY IF IMAGES EXIST

**🚨 CRITICAL CHECK:** Before proceeding, verify if images exist:

```bash
# Check if product has images
if [ -d "product_list/{product_id}/product_images" ]; then
  img_count=$(find "product_list/{product_id}/product_images" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) 2>/dev/null | wc -l)
  if [ $img_count -gt 0 ]; then
    echo "⚠️ MANDATORY: Found $img_count images - MUST run image analysis"
  else
    echo "✅ No images found - safe to skip Step 2"
  fi
fi
```

**If images exist:** This step is **MANDATORY**. Do not skip.

**Use Async Gemini CLI MCP to analyze product images:**

**Why Gemini CLI MCP instead of Claude Read tool:**
- ✅ **Parallel execution** - Analyze multiple products simultaneously
- ✅ **Token-efficient** - Doesn't consume Claude Code context/tokens
- ✅ **Faster processing** - Async background execution
- ✅ **Better for batch workflows** - Launch all analyses, retrieve when needed

**Tool:** `mcp__gemini-cli-mcp-async__gemini_cli_execute` or `mcp__gemini-cli-mcp-async__gemini_cli_execute_async`

**🚨 CRITICAL REQUIREMENTS:**
- **Bilingual output** (German + Chinese) - MANDATORY
- **Synthesized insights** - not just descriptions, but actionable script elements
- **Exact German text** - copy verbatim from packaging (for compliance)
- **Structured data** - organized for easy reference during script writing

**Example Usage:**

```javascript
// For single product (synchronous):
mcp__gemini-cli-mcp-async__gemini_cli_execute({
  query: `[See detailed prompt template below - use complete template for best results]`
})

// For batch workflow (asynchronous - RECOMMENDED):
const task1 = mcp__gemini-cli-mcp-async__gemini_cli_execute_async({
  query: `[Complete prompt template here]`
})
```

---

### Enhanced Prompt Template v1.5 (Comprehensive Bilingual Format)

**Use this COMPLETE template for image analysis (based on proven Cat Tree format):**

```
Analyze all product images in /path/to/product_list/{product_id}/product_images/

Create a COMPREHENSIVE BILINGUAL product intelligence report for TikTok script writing.

**OUTPUT FORMAT:**
- Use bilingual section headers: ## Section Name | 中文节名
- Provide inline translations for key content (German with Chinese in parentheses)
- Include 10+ sections with actionable script elements
- Minimum 250+ lines for comprehensive coverage

**REFERENCE FORMAT:** See product_list/1729600227153779322/product_images/image_analysis.md for example structure.

---
## REQUIRED SECTIONS (Minimum 10)

### Header Template
```markdown
# [Product Name] - Product Image Analysis
# [Product Name Chinese] - 产品图像分析

**Product ID:** {product_id}
**Analysis Date:** YYYY-MM-DD
**Images Analyzed:** X product images
```

---

## 1. Product Design & Aesthetics | 产品设计与美学

**Style:** [Modern/Traditional/Luxus/Minimalistisch/etc.]
**风格:** [现代化/传统/奢华/简约等]

**Materials:**
- [Material 1 with details]
- [Material 2 with details]

**材料:**
- [材料1及细节]
- [材料2及细节]

**Colors Available:**
- **[Color Name (German)]:** [Description, use case]
- **[颜色名称（中文）]:** [描述、使用场景]

**Vibe:** [Overall aesthetic impression]

---

## 2. [Product-Specific Features] | [产品特定功能]

*Adapt this section to product category:*
- **Electronics:** Technical specs, display, ports, buttons
- **Health/Supplements:** Bottle design, capsule count, ingredients
- **Furniture:** Dimensions, assembly, materials
- **Pet Products:** Size options, features, use cases

**Subsections (as needed):**
### [Feature Category 1] ([中文名称])
- Details with inline Chinese translations

### [Feature Category 2] ([中文名称])
- Details with inline Chinese translations

---

## 3. Size & Scale Indicators | 尺寸与规模指标

**Total Dimensions:** [Length x Width x Height] (KEY SELLING POINT if notable)
**总尺寸:** [长 x 宽 x 高]（如果显著则为关键卖点）

**[Component] Size:** [Specific measurements]
**[组件]尺寸:** [具体测量值]

**Capacity/Scale:** [Usage capacity, weight limits, servings, etc.]
**容量/规模:** [使用容量、重量限制、份量等]

---

## 4. Text & Labels (German) | 文字与标签（德语）

**Note:** [Indicate if text is in German, English, or other languages]

**German Terms (EXACT from packaging):**
- **[Term 1]:** "[Exact German text in quotes]"
- **[Term 2]:** "[Exact German text in quotes]"
- **[Term 3]:** "[Exact German text in quotes]"

**Marketing Copy (if English/other):**
- "[Exact text 1]"
- "[Exact text 2]"

**Key Feature Descriptions:** [How product describes itself]
**关键功能描述:** [产品如何描述自己]

---

## 5. Quality Signals | 质量信号

**Visible Quality Indicators:**

1. **[Quality Aspect 1] ([中文])**
   - [Details showing quality]
   - [具体质量体现]

2. **[Quality Aspect 2] ([中文])**
   - [Details showing quality]
   - [具体质量体现]

3. **Construction Details (构造细节)**
   - [Finishing, edges, materials]
   - [完工、边缘、材料]

4. **Certifications/Badges (认证/徽章)**
   - [CE, GS, TÜV, Bio, Vegan, etc. - exact names]
   - [具体认证名称]

---

## 6. [Variations/Options] | [变体/选项]

**[Color/Size/Version] Variations:**

**[Option 1]:**
- [Description and use case]
- [描述和使用场景]

**[Option 2]:**
- [Description and use case]
- [描述和使用场景]

---

## 7. Key Differentiators (vs. Competitors) | 关键差异化（与竞争对手相比）

### UNIQUE FEATURES (独特功能)

1. **[Unique Feature 1] ([中文名称])**
   - [Why it's unique, advantage over competitors]
   - [为何独特、相比竞争对手的优势]

2. **[Unique Feature 2 - STAR FEATURE] ([中文名称 - 明星功能])**
   - [Detailed explanation of standout feature]
   - [突出功能的详细说明]

3. **[Unique Feature 3] ([中文名称])**
   - [Advantage and market positioning]
   - [优势和市场定位]

---

## 8. Usage Context | 使用场景

**Room Setting / Use Environment:**
- [Where product is shown being used]
- [产品展示使用的地方]

**Target Use Cases:**
- [Use case 1 with target audience]
- [Use case 2 with target audience]
- [使用场景1及目标受众]
- [使用场景2及目标受众]

**Target Audience Indicators:**
- [Who this product is for based on visuals]
- [基于视觉效果的目标用户]

---

## 9. Packaging/Presentation | 包装/展示

**Visible Packaging Elements:**
- [Packaging type, design, certifications]
- [包装类型、设计、认证]

**Brand Presentation:**
- [Photography style, lifestyle integration]
- [摄影风格、生活方式融合]

---

## 10. Visual Hooks for TikTok Scripts | TikTok 脚本的视觉钩子

### Priority Visual Elements (按优先级排序)

1. **"[Hook Name]" ([中文钩子名])**
   - **How to film:** [Specific filming instruction]
   - **Why it works:** [Psychological/attention reason]
   - **Script hook:** "[Exact German hook line for script]"
   - **如何拍摄:** [具体拍摄指导]

2. **"[Hook Name]" ([中文钩子名])**
   - **How to film:** [Specific filming instruction]
   - **Why it works:** [Psychological/attention reason]
   - **Script hook:** "[Exact German hook line for script]"
   - **如何拍摄:** [具体拍摄指导]

3. **"[Hook Name]" ([中文钩子名])**
   - **How to film:** [Specific filming instruction]
   - **Why it works:** [Psychological/attention reason]
   - **Script hook:** "[Exact German hook line for script]"
   - **如何拍摄:** [具体拍摄指导]

[Include 5-6 visual hooks minimum]

---

## Visual Hook Recommendations by Script Angle | 按脚本角度的视觉钩子推荐

**Angle 1: [Urgency/Price/Deal]**
- **Primary Visual:** [Main visual element]
- **Secondary Visual:** [Supporting visual]
- **主要视觉:** [主要视觉元素]
- **次要视觉:** [辅助视觉]

**Angle 2: [Problem-Solution]**
- **Primary Visual:** [Main visual element]
- **Secondary Visual:** [Supporting visual]
- **主要视觉:** [主要视觉元素]
- **次要视觉:** [辅助视觉]

**Angle 3: [Lifestyle/Gift/Transformation]**
- **Primary Visual:** [Main visual element]
- **Secondary Visual:** [Supporting visual]
- **主要视觉:** [主要视觉元素]
- **次要视觉:** [辅助视觉]

---

## [Color/Version] Choice for Scripts | 脚本的[颜色/版本]选择

**[Option 1]:**
- Better for [aesthetic/angle type]
- Recommended for [script angle]
- 更适合[美学/角度类型]
- 推荐用于[脚本角度]

**[Option 2]:**
- Better for [aesthetic/angle type]
- Recommended for [script angle]
- 更适合[美学/角度类型]
- 推荐用于[脚本角度]

---

## German Text Elements for Scripts | 脚本的德语文字元素

**Product Name Variations:**
- [Variation 1]
- [Variation 2]
- [Variation 3]

**Feature Callouts (EXACT German from packaging):**
- "[German term 1]" ([English translation])
- "[German term 2]" ([English translation])
- "[German term 3]" ([English translation])

**Quality Claims (Safe for Scripts):**
- "[Safe claim 1]" ([Translation])
- "[Safe claim 2]" ([Translation])
- "[Safe claim 3]" ([Translation])

---

## Next Step: Script Generation | 下一步：脚本生成

**Ready to use:**
- ✅ Product specifications from tabcut_data.md
- ✅ Market insights from video_analysis.md (if available)
- ✅ Visual hooks from this image_analysis.md
- ✅ German terminology and feature descriptions

**Generate 3 scripts using:**
1. **Angle 1:** [Recommended angle] → Hook Type: [Golden 3 Seconds pattern]
2. **Angle 2:** [Recommended angle] → Hook Type: [Golden 3 Seconds pattern]
3. **Angle 3:** [Recommended angle] → Hook Type: [Golden 3 Seconds pattern]

---

**Analysis completed:** YYYY-MM-DD
**Ready for:** Script Generation (Step 3)

**OUTPUT FORMAT:**
Save as `product_list/{product_id}/image_analysis.md`
```

---

### What Makes Good v1.5 Image Analysis

**✅ GOOD (Comprehensive + Bilingual):**
```
## 1. Product Design & Aesthetics | 产品设计与美学
Style: Modern, floor-to-ceiling tower style (skyscraper for cats)
风格: 现代化，落地到天花板的塔式设计（猫的摩天大楼）

Materials:
- Soft plush fabric covering (velvety/dense texture)
- Natural sisal rope wrapping on posts (segmented design)

材料:
- 柔软的毛绒布料覆盖（天鹅绒般/密集质地）
- 天然剑麻绳缠绕在抓柱上（分段设计）

## 10. Visual Hooks for TikTok Scripts | TikTok 脚本的视觉钩子

1. **"The Penthouse View" (顶层视角)**
   - **How to film:** Slow pan UP the 210cm height to reveal cat looking down
   - **Why it works:** Emphasizes impressive height, shows scale dramatically
   - **Script hook:** "Deine Katze verdient eine Penthouse-Wohnung, kein einfaches Bett."
```

**❌ BAD (Generic + Monolingual):**
```
## 1. Packaging Design
- Color Scheme: White background with blue accent
- Aesthetic: Minimalist
- Visual Impression: Simple cardboard box
```

---

**Save Analysis:**
ALWAYS save comprehensive bilingual analysis to:
```
product_list/{product_id}/image_analysis.md
```

This becomes a critical reference document for script writing.

---

### Output Validation & Quality Check ⚠️ MANDATORY

**After Gemini completes image analysis, you MUST verify output quality:**

#### Minimum Requirements (PASS/FAIL)

```bash
# Verify image analysis meets requirements
wc -l product_list/{product_id}/image_analysis.md
# Expected: 250+ lines minimum for v1.5 comprehensive format
```

**✅ PASS Criteria (All must be true):**
- [ ] **File size:** 250+ lines (good examples: 300-400 lines)
- [ ] **Bilingual headers:** All major sections use "## Name | 中文名" format
- [ ] **Inline translations:** Key content has Chinese translations in parentheses or separate lines
- [ ] **Section 10 present:** "Visual Hooks for TikTok Scripts" with 5-6 hooks
- [ ] **Exact German text:** Verbatim quotes from packaging (in quotes)
- [ ] **Actionable hooks:** "How to film" + "Script hook" for each visual element
- [ ] **Script recommendations:** "Visual Hook Recommendations by Script Angle" section exists

**❌ FAIL Indicators (Requires retry):**
- **Too short:** <200 lines = incomplete analysis
- **No inline bilingual:** Headers bilingual but body content only in one language
- **No Section 10:** Missing "Visual Hooks for TikTok Scripts" = not actionable
- **Generic hooks:** "Show the product" without specific filming instructions
- **No script lines:** Missing ready-to-use German hook formulations

#### Verification Command

```bash
# Quick quality check (v1.5 format)
echo "=== IMAGE ANALYSIS QUALITY CHECK (v1.5) ==="
echo "Line count: $(wc -l < product_list/{product_id}/image_analysis.md)"
echo ""
echo "Required sections check:"
grep -c "## 1.*|" product_list/{product_id}/image_analysis.md && echo "✓ Section 1 (Bilingual)" || echo "✗ MISSING bilingual section 1"
grep -c "## 10.*Visual Hooks" product_list/{product_id}/image_analysis.md && echo "✓ Section 10 (Visual Hooks)" || echo "✗ MISSING Visual Hooks section"
grep -c "How to film:" product_list/{product_id}/image_analysis.md && echo "✓ Filming instructions present" || echo "✗ MISSING filming instructions"
grep -c "Script hook:" product_list/{product_id}/image_analysis.md && echo "✓ Script hooks present" || echo "✗ MISSING script hooks"
```

**Expected output (PASS):**
```
=== IMAGE ANALYSIS QUALITY CHECK (v1.5) ===
Line count: 362

Required sections check:
✓ Section 1 (Bilingual)
✓ Section 10 (Visual Hooks)
✓ Filming instructions present
✓ Script hooks present
```

#### If Output FAILS Validation

**🔄 RETRY REQUIRED - Reference the complete v1.5 template:**

```javascript
mcp__gemini-cli-mcp-async__gemini_cli_execute({
  query: `CRITICAL: Previous analysis was incomplete. You MUST follow the v1.5 comprehensive bilingual format.

REFERENCE EXAMPLE: product_list/1729600227153779322/product_images/image_analysis.md
(This is the gold standard - 362 lines, fully bilingual, actionable visual hooks)

[Paste complete template from lines 314-584 above]

MANDATORY v1.5 REQUIREMENTS:
1. Minimum 250+ lines total
2. All major sections use bilingual headers: ## Name | 中文名
3. Inline Chinese translations for key content
4. Section 10 "Visual Hooks for TikTok Scripts" with 5-6 detailed hooks
5. Each hook must have:
   - **How to film:** Specific camera instruction
   - **Why it works:** Psychological reason
   - **Script hook:** Ready-to-use German line
6. Exact German text from packaging in quotes
7. "Visual Hook Recommendations by Script Angle" section
8. "Next Step: Script Generation" section with angle recommendations

DO NOT output shortened analysis. Follow the Cat Tree example structure exactly.`
})
```

**🚨 CRITICAL:** Do NOT proceed to script writing with failed image analysis. Scripts will be low-quality without comprehensive bilingual input.

---

### Step 3: Official Description Verification

**Read official TikTok Shop product description** (screenshot or saved file).

**Cross-reference:**
- Ingredient/component lists
- Benefit claims (CRITICAL for compliance)
- Technical specifications
- Usage instructions
- Certifications and quality claims

**Purpose:** Ensure script claims align EXACTLY with official product listing to avoid TikTok violations.

---

### Step 4: Determine Product Category & Compliance Rules

**Product Categories:**

### Category 1: Health & Supplements

**Strict Compliance Required:**

**NEVER use:**
- Medical claims: "heilt" (heals), "behandelt" (treats), "verhindert" (prevents), "therapiert"
- Guaranteed results: "wirst X kg verlieren" (will lose X kg), "garantiert"
- Disease treatment language: "gegen Diabetes", "heilt Krebs"
- Exaggerated health claims

**SAFE language patterns:**
- "kann unterstützen" (can support)
- "hilft dabei" (helps with)
- "natürliche Inhaltsstoffe" (natural ingredients)
- "traditionell eingesetzt" (traditionally used)
- User experience, not medical effects
- Focus on feelings, not diagnoses
- Personal observations: "sah aus", "fühlte mich" (appeared, felt)

### Category 2: Electronics & Tech

**Compliance Focus:**
- Accurate technical specifications (battery life, memory, etc.)
- No exaggerated performance claims
- Proper comparison language (if comparing to competitors)
- Safety certifications mentioned accurately

**SAFE language patterns:**
- "unterstützt bis zu X Stunden" (supports up to X hours)
- "mit X GB Speicher" (with X GB memory)
- "kompatibel mit" (compatible with)
- Specific feature descriptions from official specs

### Category 3: Beauty & Skincare

**Compliance Focus:**
- No medical/therapeutic claims
- Age-appropriate language
- Allergy/sensitivity warnings if applicable
- Ingredient transparency

**SAFE language patterns:**
- "kann das Hautbild unterstützen" (can support skin appearance)
- "spendet Feuchtigkeit" (provides moisture)
- "sieht X aus" (looks X) - observation, not claim
- "für X Hauttyp geeignet" (suitable for X skin type)

### Category 4: General Products (Household, Fashion, etc.)

**Compliance Focus:**
- Accurate material/fabric descriptions
- Honest durability claims
- Clear usage instructions
- Size/fit information

**SAFE language patterns:**
- "besteht aus X Material" (made of X material)
- "für X geeignet" (suitable for X)
- "einfach zu verwenden" (easy to use)

---

### Step 5: Script Angle Planning

**Generate 3 distinct angles based on reference video analysis:**

**Common Successful Angles:**

1. **Problem-Solution** (highest conversion)
   - Hook: Relatable pain point
   - Solution: Product as answer
   - Proof: User experience or specs
   - CTA: Link below

2. **Lifestyle Integration / Glow Up** (high engagement)
   - Hook: Daily routine scenario
   - Integration: How product fits seamlessly
   - Result: Observable improvement
   - CTA: Link below

3. **Educational / Value Proposition** (trust building)
   - Hook: "Did you know" or comparison
   - Education: Product science/features
   - Value: Why this product is better
   - CTA: Link below

**Map angles to reference videos:**
- If reference videos show "Deal/Discount" → Use urgency angle
- If reference videos show "Testimonial" → Use personal experience
- If reference videos show "Before/After" → Use transformation angle

**Select 3 complementary angles** that don't overlap.

---

### Step 5.5: Golden 3 Seconds Hook Patterns

**Critical Success Factor:** The first 3 seconds determine 80%+ of video performance.

**8 Proven Hook Types for German TikTok:**

#### 1. The Urgency Type (Highest Retention)
**Keywords:** Last / Only remaining / Now / Heute / Nur noch

**Examples:**
- "Heute ist der letzte Tag." (Today is the last day.)
- "Nur noch heute." (Only today left.)

**Best For:** Coupons, flash sales, limited inventory, countdowns

**Pro Tip:** Keep tone calm and matter-of-fact. Avoid shouting or over-excitement (reduces trust in German market).

**Implementation:**
```
[matter-of-fact] Heute ist der letzte Tag für diesen Preis.
[soft] Morgen ist es vorbei.
```

---

#### 2. Pain Point Resonance Type (Most Stable)
**Keywords:** Every day / Always / Constantly / Jeden Tag / Immer / Ständig

**Examples:**
- "Jeden Tag das gleiche Problem." (The same problem every day.)
- "Das nervt mich schon lange." (This has been annoying me for a long time.)

**Best For:** Household items, kitchen products, daily necessities, health supplements

**Why It Works:** Creates immediate emotional identification. Viewer thinks "That's ME!"

**Implementation:**
```
[soft] Kennst du das? Jeden Tag müde, ohne Grund.
[reflective] Morgens aufgewacht… und die Beine fühlen sich schwer an.
```

---

#### 3. Counter-Intuitive Type (Strong Curiosity)
**Keywords:** No / Never / No longer / Nicht mehr / Nie wieder / Eigentlich nicht

**Examples:**
- "Ich mache das nicht mehr." (I don't do this anymore.)
- "Das braucht man eigentlich nicht dachte ich." (I thought you didn't actually need this.)

**Best For:** Functional products, problem-solving tools, innovative solutions

**Why It Works:** Creates pattern interrupt. Challenges viewer's assumptions.

**Implementation:**
```
[curious] Ich dachte, das braucht man eigentlich nicht.
[matter-of-fact] Aber dann hab ich's ausprobiert.
```

---

#### 4. Documentary Type (Safest for Organic Reach)
**Keywords:** Today / Just now / Now / Heute / Gerade / Jetzt

**Examples:**
- "Heute habe ich das erste Mal..." (Today is the first time I...)
- "Ich wollte das einfach festhalten." (I just wanted to record/capture this.)

**Best For:** Product unboxings, first impressions, testing videos

**German Market Insight:** German users HIGHLY trust "recording/documenting" authenticity. This feels less "salesy" than direct pitch.

**Implementation:**
```
[warm] Heute zeige ich euch, was ich gerade bekommen habe.
[curious] Ich wollte das einfach festhalten.
```

---

#### 5. Wrong Demonstration Type (High Retention)
**Keywords:** Many people / Almost everyone / Fast alle / Die meisten

**Examples:**
- "Das machen fast alle falsch." (Almost everyone is doing this wrong.)
- "Ich habe das viel zu lange falsch gemacht." (I did this the wrong way for way too long.)

**Best For:** Tutorials, tools, how-to content, product usage tips

**Why It Works:** Nobody wants to be "doing it wrong." Creates immediate attention.

**Implementation:**
```
[matter-of-fact] Die meisten nehmen das falsch ein.
[confident] Ich zeig dir, wie es richtig geht.
```

---

#### 6. Result-First Type (Direct)
**Keywords:** Now / Finally / Finally no longer / Jetzt / Endlich / Seitdem

**Examples:**
- "Jetzt ist es endlich gelöst." (It's finally solved now.)
- "Seitdem habe ich das Problem nicht mehr." (I haven't had that problem since.)

**Best For:** Before & After content, transformation stories, problem resolution

**Why It Works:** Shows the end result first, making viewers want to know "how?"

**Implementation:**
```
[bright] Endlich keine Muskelkrämpfe mehr.
[reflective] Seitdem nehme ich das hier.
```

---

#### 7. Emotional Whisper Type (Germany Special)
**Keywords:** To be honest / Honestly speaking / Ehrlich gesagt / Ich war skeptisch

**Examples:**
- "Ehrlich gesagt..." (To be honest...)
- "Ich war wirklich skeptisch." (I was really skeptical.)

**German Market Insight:** German audiences respond VERY WELL to "low emotion" (understated) delivery. Over-enthusiasm = suspicious.

**Why It Works:** Creates trust through vulnerability and skepticism-to-belief journey.

**Implementation:**
```
[soft] Ehrlich gesagt, war ich skeptisch.
[reflective] Aber nach ein paar Tagen… hat's mich überrascht.
```

---

#### 8. Visual-First Type (No Voiceover)
**Method:** Lead with strong visual conflict or relatable problem.

**Visual Examples:**
- Cold feet stepping on hard floor
- Messy, disorganized kitchen drawer
- Frosted windows during winter
- Bloated stomach in mirror
- Heavy, tired legs

**On-Screen Text (0-2s):** "Kennt das jemand?" (Does anyone relate to this?)

**Why It Works:** Visual hooks process faster than audio. Universal recognition across language barriers.

**Implementation:**
- Open with problem visual (no voiceover)
- Add text overlay asking "Kennst das?"
- Then introduce product solution at 3-5s mark

---

### Hook Selection Strategy

**For each script, select ONE Golden 3 Seconds pattern as the primary hook:**

**High Conversion Products (supplements, health):**
- Primary: Pain Point Resonance (#2)
- Secondary: Result-First (#6)
- Tertiary: Emotional Whisper (#7)

**Deal/Flash Sale Products:**
- Primary: Urgency (#1)
- Secondary: Counter-Intuitive (#3)
- Tertiary: Pain Point Resonance (#2)

**Functional/Tool Products:**
- Primary: Wrong Demonstration (#5)
- Secondary: Counter-Intuitive (#3)
- Tertiary: Documentary (#4)

**Beauty/Lifestyle Products:**
- Primary: Visual-First (#8)
- Secondary: Result-First (#6)
- Tertiary: Documentary (#4)

**When in doubt:** Use Documentary Type (#4) - safest for organic reach in German market.

---

### Step 5.7: Extract Visual Hooks from Image Analysis v1.5

**🎯 CRITICAL:** If you completed Step 2 (Image Analysis), you now have ready-to-use visual hooks in Section 10 of `image_analysis.md`.

**Purpose:** Map visual hooks from image analysis to your 3 script angles.

#### How to Extract Visual Hooks

**1. Read Section 10 from image analysis:**
```bash
# Extract Visual Hooks section
sed -n '/## 10. Visual Hooks for TikTok Scripts/,/## Visual Hook Recommendations/p' product_list/{product_id}/image_analysis.md
```

**Expected output:** 5-6 detailed visual hooks, each with:
- **How to film:** Specific camera/filming instruction
- **Why it works:** Psychological appeal
- **Script hook:** Ready-to-use German line
- **如何拍摄:** Chinese translation

**2. Map hooks to your 3 script angles:**

| Script Angle | Primary Visual Hook | Script Hook Line (from analysis) |
|:-------------|:-------------------|:--------------------------------|
| Angle 1: [Problem-Solution] | Hook #X: "[Name]" | "[Exact German line from analysis]" |
| Angle 2: [Lifestyle/Glow Up] | Hook #Y: "[Name]" | "[Exact German line from analysis]" |
| Angle 3: [Educational/Value] | Hook #Z: "[Name]" | "[Exact German line from analysis]" |

**3. Review "Visual Hook Recommendations by Script Angle" section:**

The image analysis already suggests which visual hooks work best for each angle type. Use these recommendations.

#### Decision Framework: Which Hook for Which Script?

**Problem-Solution Scripts (Angle 1):**
- Look for hooks showing "before/after" transformations
- Example hook types: "The Transformation", "The Clutter to Clean", "The Messy to Organized"

**Lifestyle/Glow Up Scripts (Angle 2):**
- Look for hooks showing usage context or aesthetic appeal
- Example hook types: "The Cozy Setup", "The Aesthetic Reveal", "The Daily Ritual"

**Educational/Value Scripts (Angle 3):**
- Look for hooks highlighting unique features or quality signals
- Example hook types: "The Hidden Feature", "The Quality Proof", "The Size Comparison"

#### Integration Checklist

Before moving to Step 6 (Script Writing), verify:

- [ ] Read Section 10 "Visual Hooks for TikTok Scripts" from image_analysis.md
- [ ] Identified 3 visual hooks (one per script angle)
- [ ] Copied exact German "Script hook" lines for each
- [ ] Noted specific "How to film" instructions for production team
- [ ] Reviewed "Visual Hook Recommendations by Script Angle" section

**If you skipped Step 2 (no images):** Skip this step, proceed directly to Step 6.

---

### Step 6: Script Writing

**Create 3 scripts following this structure:**

#### Using Visual Hooks from Image Analysis (v1.5)

**🎯 NEW REQUIREMENT:** If image analysis was completed (Step 2), each script MUST integrate visual hooks from Section 10.

**How to integrate:**

1. **Opening Hook (0-3s):** Use the "Script hook" line from image_analysis.md directly
   - Example from Cat Tree analysis: *"Deine Katze verdient eine Penthouse-Wohnung, kein einfaches Bett."*
   - These lines are pre-tested for German market appeal

2. **Product Introduction (3-8s):** Reference visual elements from analysis
   - Use exact German terms from Section 4 "Text & Labels"
   - Reference distinctive design elements from Section 1 "Product Design & Aesthetics"

3. **Trust Signals (15-25s):** Use quality signals from Section 5
   - Certifications mentioned in analysis (GS, CE, TÜV, Bio, etc.)
   - Quality construction details identified

4. **CTA (28-35s):** Reference visual recognition elements
   - Color/design elements that make product recognizable
   - Packaging features from Section 9

**Example Integration (using Cat Tree analysis):**

```markdown
## Voiceover

> with ElevenLabs v3 (alpha) grammar

### DE (ElevenLabs Prompt | 35s)

[bright] Deine Katze verdient eine Penthouse-Wohnung, kein einfaches Bett.  # ← From Section 10, Hook #1
[curious] Das ist der XXL Katzenbaum. 210cm hoch.  # ← From Section 3, Size & Scale
[matter-of-fact] Sisal-Kratzsäulen, Plüsch-Höhlen, und ganz oben—  # ← From Section 2, Features
[soft] die Aussichtsplattform.  # ← From Section 10, "The Penthouse View" hook
[reflective] Meine Katze liegt jetzt nur noch da oben.
[confident] Made in Germany, stabil bis 15kg.  # ← From Section 5, Quality Signals
[firm] Link ist unten.
```

**Benefits of this integration:**
- ✅ **Pre-tested language:** Visual hook lines are based on product analysis
- ✅ **Compliance-safe:** German text extracted from official packaging
- ✅ **Market-tested:** Hooks designed for German TikTok psychology
- ✅ **Production-ready:** "How to film" instructions guide video creation

#### File Naming
```
product_list/{product_id}/scripts/
├── {Product}_{Angle1}_Keyword.md
├── {Product}_{Angle2}_Keyword.md
└── {Product}_{Angle3}_Keyword.md
```

**Example:**
- `Brennnessel_Komplex_Bloating_Loesung.md`
- `Brennnessel_Komplex_Glow_Up.md`
- `Brennnessel_Komplex_Detox_Wellness.md`

#### Script Template

```yaml
---
cover: ""
caption: "[Punchy German caption - 1 sentence] #tag1 #tag2 #tag3 #tag4 #tag5"
published: YYYY-MM-DD
duration: "00:XX"   # 30-40s target
sales:
  - yes
link: ""
tags:
  - "#tag1"
  - "#tag2"
  - "#tag3"
  - "#tag4"
  - "#tag5"         # Max 5 tags
product: "[Full Product Name]"
source_notes:
  - "product_list/{product_id}/video_analysis.md"
  - "product_list/{product_id}/tabcut_data.md"
  - "product_list/{product_id}/product_images/"  # if used
---
## Scripts

Structure (30–40s):
- Hook: [Hook strategy]
- Product: [Product name + key feature]
- Benefit: [Main value proposition]
- Proof: [Trust signal or user experience]
- Feature: [Optional - standout feature]
- CTA: Link below

## Voiceover

> with ElevenLabs v3 (alpha) grammar

### DE (ElevenLabs Prompt | 30–40s)

[cue] Line 1.
[cue] Line 2.
[cue] Line 3.
...
[cue] CTA.

### ZH (中文翻译)

[cue] 中文翻译第1句。
[cue] 中文翻译第2句。
[cue] 中文翻译第3句。
...
[cue] CTA中文。
```

---

### Step 7: ElevenLabs v3 Grammar Rules

**Critical formatting rules:**

**Marker Line (Required):**
```
> with ElevenLabs v3 (alpha) grammar
```

**Cue Usage:**
- **Hook:** 0-2 cues
- **Middle:** 1-3 cues
- **CTA:** 1 cue
- **Total:** 6-8 cues per script maximum

**Safe Cue Vocabulary:**
- Intensity: `[soft]`, `[neutral]`, `[bright]`, `[firm]`
- Emotion: `[warm]`, `[curious]`, `[amused]`, `[reflective]`, `[skeptical]`, `[confident]`
- Delivery: `[understated]`, `[matter-of-fact]`, `[whisper]`

**Pacing:**
- One idea per line (micro-lines for natural breaths)
- Use periods (`.`) for confident statements
- Use `…` sparingly (1-3 per script) for suspense
- Use `—` sparingly (1-3 per script) for pivots
- Explicit `[pause XXms]` cues: 0-2 maximum

**Anti-AI Checklist:**
- Varied sentence lengths (short hits + medium sentences)
- 2+ human beats (reactions, asides, self-corrections)
- No repeated cadence patterns
- Short, confident CTA (no over-selling)

**Word Count Guidelines:**
- 30s: ~65-90 words
- 35s: ~80-105 words
- 40s: ~90-115 words

---

### Step 8: Bilingual Translation (DE → ZH)

**For each script, provide Chinese translation:**

**Purpose:** Internal reference for non-German-speaking team members, NOT production.

**Translation Guidelines:**
- Keep cues identical: `[soft]` → `[soft]`
- Translate content naturally (not word-for-word)
- Maintain tone and intent
- Keep product names in original language with Chinese explanation if needed
  - Example: "Wasserbalance（水平衡）"

---

### Step 9: Compliance Verification Checklist

**Before finalizing, verify each script:**

#### General Compliance
- [ ] All claims match official product description
- [ ] No exaggerations beyond official listing
- [ ] Technical specs accurate (quantity, dosage, dimensions)
- [ ] Trust signals accurate (certifications, origin)
- [ ] Source notes correctly linked

#### Category-Specific Compliance
- [ ] **Health Products:** No medical claims, no guarantees, safe language only
- [ ] **Electronics:** Accurate specs, no exaggerated performance
- [ ] **Beauty:** No therapeutic claims, ingredient transparency
- [ ] **General:** Honest material/quality descriptions

#### Format Compliance
- [ ] YAML frontmatter complete and valid
- [ ] Exactly 5 tags (no more, no less)
- [ ] **Caption includes hashtags** in TikTok format: "Text here #tag1 #tag2 #tag3"
- [ ] Duration estimate realistic (word count check)
- [ ] ElevenLabs v3 marker present
- [ ] Cues valid and minimal (6-8 total)
- [ ] Both DE and ZH sections present
- [ ] Caption punchy and production-ready

---

### Step 10: Create Bilingual Campaign Summary

**After all 3 scripts are complete, create a comprehensive bilingual campaign summary file.**

**Purpose:**
- Provides strategic overview of all 3 scripts as a unified campaign
- Documents performance data and predictions
- Serves as production brief for video team (accessible to both German and Chinese-speaking team members)
- Enables data-driven optimization decisions

**File Location:**
```
product_list/{product_id}/scripts/Campaign_Summary.md
```

**⚠️ BILINGUAL FORMAT REQUIREMENT:**

The Campaign Summary MUST be bilingual with inline Chinese translations throughout. Use the following format:

**Headers:**
```markdown
## Section Title | 章节标题
### Subsection Title | 子章节标题
```

**Content:**
- Bullet points: `English content | 中文翻译`
- Key terms: `**Term | 术语:** Description | 描述`
- Paragraphs: English paragraph followed by Chinese paragraph

**Example:**
```markdown
## 2. Campaign Strategy | 活动策略

### Overall Strategic Approach | 整体战略方法
- **Viral Wow Factor | 病毒式惊艳因素** - Lead with transformation | 以变形开场
- **Gift-Giving Urgency | 送礼紧迫感** - Seasonal shopping | 季节性购物

**Key Insight | 关键洞察:** "The transformation IS the product."

与传统遥控玩具将变形作为次要功能不同，该产品的核心价值主张是瞬间变形。
```

**Reference Example:**
See `product_list/1729655828988926782/scripts/Campaign_Summary.md` for complete bilingual format reference.

---

**Required Content Sections:**

#### 1. Header Metadata
```yaml
---
product_id: "{product_id}"
product_name: "{Full Product Name}"
product_name_zh: "{产品全名}"
campaign_date: YYYY-MM-DD
scripts_count: 3
total_duration: "~XXXs (Xm XXs)"
target_audience: "{Primary demographic}"
target_audience_zh: "{主要人群}"
---
```

**Note:** Include both English and Chinese versions in frontmatter for key fields.

#### 2. Product Overview | 产品概述
- Full product name and shop | 完整产品名称和店铺
- Key features and USPs | 核心特性和独特卖点
- Supply details (quantity, duration) | 供应详情（数量、时长）
- Quality certifications | 质量认证
- Main ingredients/components list | 主要成分/组件清单

**Format:** Use bilingual bullet points: `- **Feature | 特性:** Description | 描述`

#### 3. Campaign Strategy | 活动策略
- Overall strategic approach | 整体战略方法
- Psychological triggers used (Fear/Urgency, Validation, Education, etc.) | 使用的心理触发器（恐惧/紧迫感、验证、教育等）
- Key insight statement | 关键洞察陈述

**Format:** Include both English and Chinese paragraphs for key insights.

#### 4. Scripts Overview (All 3) | 脚本概览（全部3个）
For each script:
- **File name | 文件名** and duration | 时长
- **Effectiveness rating | 有效性评分** (X/10) based on video analysis or prediction
- **Hook | 钩子** (exact opening line | 确切的开场白)
- **Strategy | 策略** (what makes this angle work | 为何这个角度有效)
- **Tags | 标签** (hashtag list | 标签列表)
- **Best For | 最适合** (specific audience segment | 特定受众群体)
- **Why It Works | 为何有效** or **Based On | 基于** (reference to video analysis insights | 参考视频分析洞察)

**Format:** Use bilingual headers and inline translations for each script summary.

#### 5. Audience Segmentation Table | 受众细分表
```markdown
| Audience Segment | 受众群体 | Primary Script | 主要脚本 | Secondary Script | 次要脚本 | Targeting Strategy | 定位策略 |
|:-----------------|:---------|:---------------|:---------|:-----------------|:---------|:-------------------|:---------|
| {Segment 1} | {群体1} | Script X ({Angle}) | 脚本X（{角度}） | Script Y ({Angle}) | 脚本Y（{角度}） | {Strategy} | {策略} |
...
```

**Format:** Full bilingual table with columns for both English and Chinese.

#### 6. Key Selling Points Across Campaign | 整个活动的关键卖点
Organize by trigger type:
- **Rational Triggers (Left Brain) | 理性触发器（左脑）:** Specs, certifications, value | 规格、认证、价值
- **Emotional Triggers (Right Brain) | 情感触发器（右脑）:** Feelings, relief, transformation | 情感、解脱、转变
- **Trust Signals | 信任信号:** Quality badges, origin, testing | 质量徽章、来源、测试

**Format:** Use bilingual headers and inline translations for each trigger.

#### 7. Performance Data (Actual Market Results) | 表现数据（实际市场结果）
From `tabcut_data.md`:
- Total Sales & Revenue | 总销量和收入
- 7-Day Sales & Revenue | 7天销量和收入
- Conversion Rate | 转化率
- Video Performance metrics | 视频表现指标
- Top Performing Video details (creator, hook, views, sales) | 最佳表现视频详情（创作者、钩子、观看、销量）
- **Key Insight | 关键洞察** statement interpreting the data | 解读数据的陈述

**Format:** Include both English and Chinese for key metrics and insights.

#### 8. Performance Predictions | 表现预测
- **Expected Best Performers | 预期最佳表现者** (rank all 3 scripts with reasoning) | （对所有3个脚本排名并说明理由）
- **Optimization Strategy | 优化策略** (week-by-week scaling plan) | （逐周扩展计划）

**Format:** Use bilingual headers and inline translations for predictions and strategies.

#### 9. Content Production Notes
- **Visual Requirements** for each script (what to film)
- **Voiceover Style** (tone, delivery, language notes)

#### 9.5. Image Analysis Insights (v1.5) - **IF STEP 2 COMPLETED**

**⚠️ CRITICAL:** If image analysis was performed (Step 2), this section is MANDATORY.

**Purpose:** Document visual intelligence from product images for video production team.

**Include:**

**A. Visual Hooks Used in Scripts**
List which visual hooks from image_analysis.md Section 10 were integrated into each script:

```markdown
**Script 1: [Filename]**
- Primary Visual Hook: "[Hook Name]" (from Section 10, Hook #X)
  - How to film: [Copy exact filming instruction from analysis]
  - German line used: "[Exact line from script]"

**Script 2: [Filename]**
- Primary Visual Hook: "[Hook Name]" (from Section 10, Hook #Y)
  - How to film: [Copy exact filming instruction from analysis]
  - German line used: "[Exact line from script]"

**Script 3: [Filename]**
- Primary Visual Hook: "[Hook Name]" (from Section 10, Hook #Z)
  - How to film: [Copy exact filming instruction from analysis]
  - German line used: "[Exact line from script]"
```

**B. Key Visual Elements from Analysis**
Summarize critical visual elements identified in image_analysis.md:

- **Product Design (Section 1):** [Style, materials, aesthetic vibe]
- **Distinctive Features (Section 2):** [Star features that must be shown]
- **Size & Scale (Section 3):** [Key dimensions, capacity - if selling point]
- **German Text Elements (Section 4):** [Exact terms from packaging to show on screen]
- **Quality Signals (Section 5):** [Certifications, construction details to highlight]
- **Color/Variations (Section 6):** [Which version to film, why]
- **Usage Context (Section 8):** [Room setting, target use cases for B-roll]
- **Packaging Elements (Section 9):** [Recognition features for final frame]

**C. Production Team Reference**
Direct production team to full analysis for comprehensive details:
```markdown
**Full Image Analysis:** `product_list/{product_id}/image_analysis.md`
- 10+ sections with bilingual details
- Section 10 has 5-6 additional visual hooks not used in these scripts
- "Visual Hook Recommendations by Script Angle" section suggests alternatives for A/B testing
```

**If Step 2 was skipped (no images):**
```markdown
#### 9.5. Image Analysis Insights
**N/A** - No product images available for this product.
Visual direction based on video analysis and product description only.
```

#### 10. Recommendations for Future Creatives
- **High Priority:** 3-4 immediate next steps
- **Medium Priority:** 3-4 testing opportunities
- **Testing Opportunities:** New angles, demographics, seasonal hooks

#### 11. Top Video Analysis Insights (if applicable)
From `video_analysis.md`:
- Winning hook patterns
- Visual elements that work
- Creator success factors

#### 12. Source Materials | 源材料
List all reference files:
```markdown
### Product Data | 产品数据
- **Product Data | 产品数据:** `product_list/{product_id}/tabcut_data.md`
- **Video Analysis | 视频分析:** `product_list/{product_id}/video_analysis.md` (if available)
- **Image Analysis (v1.5) | 图像分析（v1.5）:** `product_list/{product_id}/image_analysis.md` (if Step 2 completed)

### Reference Videos | 参考视频
- **Reference Videos | 参考视频:** `product_list/{product_id}/ref_video/` (if available)

### Product Images | 产品图片
- **Product Images | 产品图片:** `product_list/{product_id}/product_images/` (if available)

### Generated Scripts | 生成的脚本
- **Script 1 | 脚本1:** `product_list/{product_id}/scripts/Script_1.md`
- **Script 2 | 脚本2:** `product_list/{product_id}/scripts/Script_2.md`
- **Script 3 | 脚本3:** `product_list/{product_id}/scripts/Script_3.md`
```

**Format:** Use bilingual headers for all source material sections.

#### 13. Compliance Notes | 合规说明
- **Product Category | 产品类别:** {Category} | {类别}
- **Safe Language Used | 使用的安全语言:** List exact phrases used | 列出使用的确切短语
- **Avoided Claims | 避免的声明:** What was intentionally not said | 有意避免说的内容
- **Important Notes | 重要说明:** Category-specific warnings or disclaimers | 特定类别的警告或免责声明

**Format:** Use bilingual headers and inline translations for compliance items.

#### 14. Footer | 页脚
```markdown
---

**Campaign created | 活动创建日期:** YYYY-MM-DD

**Based on proven market performance | 基于已验证的市场表现:**
- X total sales | 总销量X件
- €X total revenue | 总收入€X
- X% conversion rate | X%转化率

**Scripts ready for production | 准备制作的脚本:**
- 3 unique angles (XXs, XXs, XXs) | 3个独特角度（XX秒、XX秒、XX秒）
- Based on Video Analysis insights | 基于视频分析洞察
- ElevenLabs v3 (alpha) voiceover compatible | 兼容ElevenLabs v3（alpha）配音
- Bilingual (DE/ZH) internal reference | 双语（德语/中文）内部参考

---
```

**Format:** Include bilingual headers and inline translations in footer.

**Optional Additions:**
- **TOP PERFORMER** or **PRIORITY FOR SCALING** tags for high-performing products
- Portfolio comparison table (if creating multiple campaign summaries)
- Competitive analysis (if available)

**Example Bilingual Summary File:**
See `product_list/1729655828988926782/scripts/Campaign_Summary.md` for complete bilingual format reference with:
- Inline Chinese translations throughout all sections
- Bilingual headers (## Section Title | 章节标题)
- Bilingual bullet points (English | 中文)
- Bilingual tables with both language columns
- Bilingual frontmatter metadata

---

### Step 11: Final Quality Gate ⚠️ MANDATORY CHECKPOINT

**🛑 STOP: Do NOT mark this task as complete until ALL criteria below are verified.**

This is the **final verification checkpoint** before delivery. All previous steps may have been completed, but this gate ensures **nothing was missed**.

---

#### Deliverables Verification

**Run this command to verify all files exist:**

```bash
# Verify all required files for product {product_id}
ls -lh product_list/{product_id}/scripts/

# Expected output (4 files minimum):
# - Script_1.md (1.5-2.5KB typical size)
# - Script_2.md (1.5-2.5KB typical size)
# - Script_3.md (1.5-2.5KB typical size)
# - Campaign_Summary.md (15-25KB typical size)
```

**Verification Checklist:**

- [ ] **Script 1 file exists** at `product_list/{product_id}/scripts/{Product}_{Angle1}.md`
- [ ] **Script 2 file exists** at `product_list/{product_id}/scripts/{Product}_{Angle2}.md`
- [ ] **Script 3 file exists** at `product_list/{product_id}/scripts/{Product}_{Angle3}.md`
- [ ] **Campaign Summary exists** at `product_list/{product_id}/scripts/Campaign_Summary.md`

**🚨 CRITICAL:** If ANY file is missing, the task is **INCOMPLETE**. Do NOT proceed.

---

#### Content Quality Verification

**For EACH of the 3 scripts, verify:**

```bash
# Quick verification command
for file in product_list/{product_id}/scripts/*.md; do
  echo "=== $file ==="
  head -20 "$file" | grep -E "(cover:|caption:|duration:|product:|tags:)"
  echo "---"
done
```

**Script Quality Checklist (verify ALL 3 scripts):**

- [ ] **YAML frontmatter present** (starts with `---`)
- [ ] **Caption field populated** (not empty "")
- [ ] **Duration field valid** (format: "00:XX" between 00:30-00:50)
- [ ] **Exactly 5 tags** (count them - no more, no less)
- [ ] **Tags include hashtags in caption** (e.g., "Text #tag1 #tag2...")
- [ ] **Product name matches** official product name from tabcut_data.md
- [ ] **Source notes linked** to actual files used
- [ ] **ElevenLabs v3 marker present** (`> with ElevenLabs v3 (alpha) grammar`)
- [ ] **DE section exists** with voiceover cues
- [ ] **ZH section exists** with Chinese translation
- [ ] **Cue count reasonable** (6-8 cues per script, not 15+)
- [ ] **Word count appropriate** (~65-115 words for 30-40s duration)

**🚨 CRITICAL:** If ANY script fails these checks, **FIX IT** before proceeding.

---

#### Image Analysis Verification (If Step 2 Was Performed)

**🎯 Check if image analysis was required and completed:**

```bash
# Check if product has images
if [ -d "product_list/{product_id}/product_images" ]; then
  img_count=$(find "product_list/{product_id}/product_images" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.webp" \) 2>/dev/null | wc -l)
  if [ $img_count -gt 0 ]; then
    echo "⚠️ Product has $img_count images - image analysis is MANDATORY"
    if [ -f "product_list/{product_id}/image_analysis.md" ]; then
      echo "✓ image_analysis.md exists"
      echo "Line count: $(wc -l < product_list/{product_id}/image_analysis.md)"
    else
      echo "❌ MISSING: image_analysis.md - MUST be completed"
    fi
  else
    echo "✓ No images - image analysis not required"
  fi
else
  echo "✓ No product_images folder - image analysis not required"
fi
```

**Image Analysis Quality Checklist (v1.5 Format):**

**IF images exist and analysis was performed:**

- [ ] **File exists** at `product_list/{product_id}/image_analysis.md`
- [ ] **Minimum line count** (250+ lines for v1.5 comprehensive format)
- [ ] **Bilingual headers** present (## Section Name | 中文节名)
- [ ] **Section 10 exists** "Visual Hooks for TikTok Scripts | TikTok 脚本的视觉钩子"
- [ ] **Visual hooks complete** (5-6 hooks with "How to film", "Script hook", "如何拍摄")
- [ ] **German text extracted** (Section 4 has exact packaging text in quotes)
- [ ] **Quality signals documented** (Section 5 has certifications, construction details)
- [ ] **Visual Hook Recommendations section** exists
- [ ] **Scripts reference visual hooks** (each script uses at least one hook from Section 10)

**Verification command (v1.5):**
```bash
# Run comprehensive image analysis check
if [ -f "product_list/{product_id}/image_analysis.md" ]; then
  echo "=== IMAGE ANALYSIS QUALITY CHECK (v1.5) ==="
  line_count=$(wc -l < product_list/{product_id}/image_analysis.md)
  echo "Line count: $line_count (minimum 250 required)"

  grep -c "## 1.*|" product_list/{product_id}/image_analysis.md && echo "✓ Bilingual headers present"
  grep -c "## 10.*Visual Hooks" product_list/{product_id}/image_analysis.md && echo "✓ Section 10 present"
  hook_count=$(grep -c "How to film:" product_list/{product_id}/image_analysis.md)
  echo "Visual hooks: $hook_count (minimum 5 required)"
  script_hook_count=$(grep -c "Script hook:" product_list/{product_id}/image_analysis.md)
  echo "Script hook lines: $script_hook_count"

  if [ $line_count -lt 250 ]; then
    echo "❌ FAIL: Analysis too short ($line_count lines < 250 minimum)"
  elif [ $hook_count -lt 5 ]; then
    echo "❌ FAIL: Not enough visual hooks ($hook_count < 5 minimum)"
  else
    echo "✅ PASS: Image analysis meets v1.5 standards"
  fi
fi
```

**🚨 CRITICAL FAILURE MODES:**

1. **Image analysis missing when images exist**
   - Fix: Go back to Step 2, run async Gemini CLI MCP analysis
   - Use v1.5 comprehensive template

2. **Image analysis too short (<250 lines)**
   - Fix: Regenerate with explicit v1.5 template reference
   - Reference Cat Tree example: `product_list/1729600227153779322/product_images/image_analysis.md`

3. **Scripts don't reference visual hooks**
   - Fix: Go back to Step 5.7 and 6
   - Extract hooks from Section 10, integrate into script opening lines

**IF no images exist:** Skip this verification - proceed to Campaign Summary Verification.

---

#### Campaign Summary Verification (Bilingual Format Required)

**Verify Campaign Summary completeness and bilingual format:**

```bash
# Check Campaign Summary structure (bilingual headers)
grep -E "^#{1,2} " product_list/{product_id}/scripts/Campaign_Summary.md
# Should show all 14 section headers with " | " pattern for bilingual format

# Check for bilingual format indicators
grep -c " | " product_list/{product_id}/scripts/Campaign_Summary.md
# Should show 50+ occurrences (bilingual headers, bullets, and content)
```

**Campaign Summary Checklist:**

- [ ] **Header metadata present** (YAML frontmatter with product_id, product_name_zh, target_audience_zh, etc.)
- [ ] **Bilingual format throughout** (headers use "Section Title | 章节标题" format)
- [ ] **Product Overview section | 产品概述** (features, USPs, use cases with inline translations)
- [ ] **Campaign Strategy section | 活动策略** (psychological triggers, key insight with Chinese paragraphs)
- [ ] **Scripts Overview | 脚本概览** (all 3 scripts with bilingual headers and inline translations)
- [ ] **Audience Segmentation Table | 受众细分表** (bilingual table with both language columns)
- [ ] **Key Selling Points | 关键卖点** (Rational/Emotional triggers, Trust signals with inline Chinese)
- [ ] **Performance Data section | 表现数据** (actual sales, conversion rate with bilingual headers)
- [ ] **Performance Predictions | 表现预测** (ranked 1-3 with reasoning, bilingual)
- [ ] **Content Production Notes** (visual requirements, VO style)
- [ ] **Image Analysis Insights (Section 9.5)** - **IF image analysis was performed (Step 2)**
  - [ ] Visual hooks used in each script documented
  - [ ] Key visual elements summarized from analysis
  - [ ] Production team reference to full image_analysis.md included
  - [ ] **IF Step 2 skipped:** Section 9.5 marked as "N/A"
- [ ] **Recommendations section** (High/Medium priority, testing opportunities)
- [ ] **Source Materials | 源材料** (all reference files with bilingual headers)
- [ ] **Compliance Notes | 合规说明** (safe claims, avoided claims with bilingual headers)
- [ ] **Footer | 页脚** (campaign date, performance summary with bilingual format)
- [ ] **File size reasonable** (20-35KB typical with bilingual content - if <15KB, likely incomplete)

**Bilingual Format Verification:**
```bash
# Check key bilingual markers
echo "=== Bilingual Format Check ==="
echo "Section headers with |: $(grep -c '^## .* | ' product_list/{product_id}/scripts/Campaign_Summary.md)"
echo "Frontmatter bilingual fields: $(grep -c '_zh:' product_list/{product_id}/scripts/Campaign_Summary.md)"
echo "Inline translations: $(grep -c ' | ' product_list/{product_id}/scripts/Campaign_Summary.md)"

# Expected results:
# Section headers: 14+ (all major sections)
# Frontmatter bilingual fields: 2+ (product_name_zh, target_audience_zh)
# Inline translations: 100+ (throughout content)
```

**🚨 CRITICAL:** Campaign Summary MUST be bilingual. If monolingual or missing, **CREATE/FIX IT** now.

**Reference:** See `product_list/1729655828988926782/scripts/Campaign_Summary.md` for complete bilingual format example.

---

#### Compliance Verification (Category-Specific)

**Health & Supplements Products:**
- [ ] No medical claims ("heilt", "behandelt", "therapiert", "garantiert")
- [ ] Only safe language ("kann unterstützen", "hilft dabei", "traditionell eingesetzt")
- [ ] Personal experience framing ("hab ich gefühlt", "bei mir", "sah aus")
- [ ] All ingredient claims match official product description

**Electronics & Tech Products:**
- [ ] Technical specs accurate (match official listing)
- [ ] No exaggerated performance claims
- [ ] Safety certifications mentioned accurately

**Beauty & Skincare Products:**
- [ ] No medical/therapeutic claims
- [ ] Ingredient transparency maintained
- [ ] Observation language ("sieht aus", "spendet Feuchtigkeit")

**General Products:**
- [ ] Material/quality descriptions honest
- [ ] No unverified durability claims

---

#### Angle Differentiation Verification

**Verify scripts have DISTINCT angles (no overlap):**

```bash
# Quick check: read first 5 lines of each script's voiceover
grep -A 5 "### DE (ElevenLabs" product_list/{product_id}/scripts/*.md
```

**Angle Differentiation Checklist:**

- [ ] **Script 1 hook** is DIFFERENT from Script 2 and 3
- [ ] **Script 2 hook** is DIFFERENT from Script 1 and 3
- [ ] **Script 3 hook** is DIFFERENT from Script 1 and 2
- [ ] Each script targets **different psychological trigger** or **audience segment**
- [ ] No repetitive content across scripts (each angle is unique)

**Common Failure:** All 3 scripts sound the same with minor word changes. If this happens, **REWRITE** to create true differentiation.

---

#### Common Failure Modes - Check These

**🔍 Most Common Mistakes:**

1. **Missing Campaign Summary** ← Most frequent failure
   - Solution: Always create Step 10, never skip it

2. **Caption missing hashtags**
   - Wrong: `caption: "Great product"`
   - Correct: `caption: "Great product #tag1 #tag2 #tag3 #tag4 #tag5"`

3. **More or fewer than 5 tags**
   - Must be EXACTLY 5 tags in the tags array

4. **Scripts too long** (>40s / >115 words)
   - Count words, ensure 65-115 range for 30-40s

5. **Over-cued voiceover** (15+ cues)
   - Keep to 6-8 cues maximum per script

6. **Identical scripts with different filenames**
   - Each script must have distinct hook, angle, and content

7. **Chinese translation missing**
   - Every script needs both DE and ZH sections

8. **Compliance violations**
   - Health products: Check for medical claims
   - All products: Verify claims match official description

---

#### Final Verification Command

**Run this comprehensive check:**

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/product_list/{product_id}/scripts

echo "=== FILE COUNT CHECK ==="
file_count=$(ls -1 *.md | wc -l)
echo "Files found: $file_count (Expected: 4 minimum)"

echo -e "\n=== CAMPAIGN SUMMARY CHECK ==="
if [ -f "Campaign_Summary.md" ]; then
  size=$(ls -lh Campaign_Summary.md | awk '{print $5}')
  echo "✓ Campaign_Summary.md exists (Size: $size)"
else
  echo "✗ MISSING: Campaign_Summary.md"
fi

echo -e "\n=== SCRIPT FILES CHECK ==="
ls -1 *.md | grep -v Campaign_Summary

echo -e "\n=== TAG COUNT VERIFICATION ==="
for file in *.md; do
  if [[ "$file" != "Campaign_Summary.md" ]]; then
    tag_count=$(grep -A 6 "^tags:" "$file" | grep "#" | wc -l)
    echo "$file: $tag_count tags (Expected: 5)"
  fi
done

echo -e "\n=== ELEVENLABS MARKER CHECK ==="
for file in *.md; do
  if [[ "$file" != "Campaign_Summary.md" ]]; then
    if grep -q "> with ElevenLabs v3 (alpha) grammar" "$file"; then
      echo "✓ $file has ElevenLabs marker"
    else
      echo "✗ $file MISSING ElevenLabs marker"
    fi
  fi
done
```

---

#### PASS/FAIL Criteria

**✅ PASS - Task Complete:**
- All 4 files exist (3 scripts + Campaign Summary)
- All scripts have valid YAML frontmatter
- All scripts have exactly 5 tags
- All scripts have both DE and ZH sections
- All scripts have ElevenLabs v3 marker
- Campaign Summary has all 14 sections
- No compliance violations detected
- Scripts have distinct angles (no overlap)

**❌ FAIL - Task Incomplete:**
- ANY file missing
- ANY quality check failed
- ANY compliance violation present
- Scripts have overlapping/identical content
- Campaign Summary incomplete or missing

**If FAIL:** Do NOT mark task as complete. Fix issues immediately, then re-run verification.

**If PASS:** Task is complete and ready for production. Update todo list to mark as completed.

---

## Example Usage

### Input Request:

```
Product ID: 1729535919239371775
Category: Health & Supplements
Task: Create 3 TikTok ad scripts
```

### Workflow Execution:

1. **Read source materials:**
   - `product_list/1729535919239371775/video_analysis.md`
   - `product_list/1729535919239371775/tabcut_data.md`

2. **Analyze product images:**
   - Use Gemini MCP to analyze 7 product images
   - Extract visual hooks: Blue orchids, "7-Fach Komplex" badge, German quality seal
   - Extract specific German terms: "Beinschwellung", "Wassereinlagerungen"

3. **Verify official description:**
   - Cross-reference ingredient list (7-Fach Komplex confirmed)
   - Note certifications: Lab tested, GMP-zertifiziert, Made in Germany
   - Extract safe language patterns: "Unterstützt", "natürliche Ausscheidung"

4. **Determine compliance category:** Health & Supplements (strict rules)

5. **Plan 3 angles:**
   - **Angle 1:** Problem-Solution (morning bloating)
   - **Angle 2:** Glow Up (face puffiness → defined look)
   - **Angle 3:** Educational (Brennnessel tradition + modern science)

6. **Write scripts:**
   - `Brennnessel_Komplex_Bloating_Loesung.md` (38s)
   - `Brennnessel_Komplex_Glow_Up.md` (33s)
   - `Brennnessel_Komplex_Detox_Wellness.md` (40s)

7. **Add bilingual content:** DE + ZH for each

8. **Verify compliance:**
   - All scripts use "unterstützt", "kann helfen" (safe language)
   - No medical claims
   - Personal experience language only
   - All product details match official description

### Output:

```
product_list/1729535919239371775/scripts/
├── Brennnessel_Komplex_Bloating_Loesung.md
├── Brennnessel_Komplex_Glow_Up.md
└── Brennnessel_Komplex_Detox_Wellness.md
```

**Result:** 3 production-ready TikTok scripts, fully compliant, bilingual, ready for ElevenLabs voice generation.

---

## Category-Specific Examples

### Health Product Script Pattern

```markdown
[soft] Kennst du das? Morgens aufgedunsen…
[curious] Das sind oft Wassereinlagerungen.
[bright] Ich hab das hier getestet: [Product].
[matter-of-fact] [Key ingredients/formula].
[soft] Unterstützt den Körper dabei, [benefit].
[confident] [Trust signals: Lab tested, Made in Germany].
[warm] Nach ein paar Tagen hab ich mich [feeling] gefühlt.
[firm] Link ist unten.
```

**Compliance:** "Unterstützt", "hab ich mich gefühlt" (personal experience, not medical claim)

### Electronics Product Script Pattern

```markdown
[bright] TikTok hat die Preise gerade komplett verrückt gemacht.
[curious] Und ich musste das testen.
[firm] Das hier sind die [Product]: [Key feature].
[matter-of-fact] [Technical specs].
[soft] [User experience - how it feels/works].
[confident] [Standout feature or comparison].
[reflective] Was mich wirklich überrascht hat: [unique benefit].
[firm] Link ist unten.
```

**Compliance:** Accurate specs, no exaggeration

### Beauty Product Script Pattern

```markdown
[reflective] Morgens in den Spiegel schauen… und [problem].
[curious] Das [cause/reason].
[bright] Ich nehm seit kurzem [Product].
[matter-of-fact] [Key ingredients/formulation].
[soft] [How it supports/helps - not medical claim].
[warm] Nach ein paar Tagen sah [result] aus.
[confident] [Trust signals: vegan, dermatologically tested].
[firm] Link ist unten.
```

**Compliance:** "sah aus" (observation), no therapeutic claims

---

## Tips for Quality Scripts

### Visual Hook Integration

**Always reference specific visual elements from packaging:**
- "Mit den blauen Orchideen erkennst du es sofort" (Blue orchids)
- "Das 7-Fach Komplex Badge siehst du auf der Flasche" (7-Fach badge)
- "Laborgeprüft-Siegel mit deutscher Flagge" (Lab tested seal)

### German Terminology from Packaging

**Use EXACT German terms from official product:**
- Don't invent terms - use what's on the label
- Preserve compound nouns: "Wassereinlagerungen", "Beinschwellung"
- Keep brand-specific language: "Patentierte Rezeptur", "Organische Kombination"

### Compliance Language Patterns

**Safe transition phrases:**
- "kann dabei helfen" (can help with)
- "unterstützt den Körper" (supports the body)
- "traditionell eingesetzt für" (traditionally used for)
- "nach meiner Erfahrung" (in my experience)

**Avoid absolutes:**
- ❌ "Das funktioniert immer" (always works)
- ✅ "Das hat bei mir funktioniert" (worked for me)

### Target Audience Specificity

**Reference use cases from official description:**
- "Für Büroangestellte mit schweren Beinen" (office workers)
- "Für Sportler nach dem Training" (athletes)
- "Für alle Lebensphasen" (all life stages)

---

## Common Issues and Solutions

### Issue 1: Scripts Too Long (>40s)

**Cause:** Too many features listed, verbose language

**Solution:**
- Cut 1 feature
- Use shorter sentences
- Remove filler words
- One idea per line

### Issue 2: Scripts Sound Robotic

**Cause:** Too many cues, no human beats

**Solution:**
- Reduce cues to 6-8 total
- Add 1-2 reactions: "Ganz kurz.", "Pass auf.", "Das war's."
- Use self-corrections: "Also—nicht das. Das hier."

### Issue 3: Compliance Violations

**Cause:** Using language from reference videos without verification

**Solution:**
- ALWAYS cross-reference with official product description
- If official description doesn't claim it, don't say it
- Use safe transition language: "kann unterstützen" instead of "wirkt gegen"

### Issue 4: Missing Visual Hooks

**Cause:** Not analyzing product images

**Solution:**
- Always run Gemini MCP analysis on product images
- Extract distinctive design elements
- Use specific German text from packaging
- Reference certifications visible on label

---

## Quality Gates

### Definition of Done

**🛑 MANDATORY:** Complete Step 11 (Final Quality Gate) before marking task as done.

**Step 11 automatically verifies:**

- [ ] All 4 files exist (3 scripts + Campaign Summary)
- [ ] All scripts have valid YAML frontmatter
- [ ] All scripts have exactly 5 tags
- [ ] Tags are included in caption field with hashtags
- [ ] All scripts have both DE and ZH sections
- [ ] All scripts have ElevenLabs v3 marker
- [ ] Campaign Summary has all 14 required sections
- [ ] Campaign Summary file size is reasonable (15-25KB)
- [ ] No compliance violations detected
- [ ] Scripts have distinct angles (no overlap)
- [ ] Word count appropriate (65-115 words per script)
- [ ] Duration estimates realistic (30-40s)
- [ ] Source notes correctly linked
- [ ] Visual hooks integrated (if images available)
- [ ] Trust signals accurate
- [ ] Category-specific compliance rules followed

**How to verify:** Run the Final Verification Command from Step 11.

**If ANY check fails:** Fix immediately, do NOT mark as complete.

---

## Version History

**v1.7.0** (2026-01-01) - **BILINGUAL CAMPAIGN SUMMARY REQUIREMENT**
- **MANDATORY CHANGE:** Campaign Summary MUST now be bilingual with inline Chinese translations
- **Step 10 Enhanced:** "Create Campaign Summary" → "Create Bilingual Campaign Summary"
  - Added comprehensive bilingual format requirements
  - Headers must use "Section Title | 章节标题" format
  - Content must include inline translations: `English | 中文`
  - Tables must have bilingual columns
  - Frontmatter must include `product_name_zh` and `target_audience_zh` fields
- **Format Documentation:** Added detailed bilingual format examples and guidelines
  - Example headers, bullet points, paragraphs, and tables
  - Reference to `product_list/1729655828988926782/scripts/Campaign_Summary.md`
- **All 14 Sections Updated:** Every required section now has bilingual format specifications
  - Section 1: Header Metadata (bilingual frontmatter)
  - Section 2-14: All sections with Chinese header translations and inline content
- **Final Quality Gate Updated:** Added bilingual format verification checks
  - Verification command checks for " | " pattern (50+ occurrences expected)
  - Checks for bilingual headers (14+ sections)
  - Checks for frontmatter bilingual fields (2+)
  - Checks for inline translations (100+)
  - Updated expected file size: 20-35KB (was 18-30KB)
- **Overview Updated:** Description now mentions "bilingual Campaign Summary" explicitly
- **Why This Matters:** Makes Campaign Summary accessible to both German and Chinese-speaking team members
- **Breaking Change:** All future Campaign Summaries must follow bilingual format
- **Reference Example:** Complete bilingual format example documented in skill file

**v1.6.0** (2026-01-01) - **PRE-CHECK ENFORCEMENT & SOURCE FILE VERIFICATION**
- **NEW STEP 0:** Pre-Check Verification (MANDATORY - blocks if fails)
  - Verifies tabcut_data.md OR fastmoss_data.json exists (at least one required)
  - Verifies image_analysis.md exists IF product_images/ has files
  - Verifies video_*_analysis.md + video_synthesis.md exist IF ref_video/ has .mp4 files
  - Checks file quality (line counts: image ≥250 lines, synthesis ≥200 lines)
  - BLOCKS script generation if required files missing
- **Bash verification command:** Automated pre-check script with clear PASS/FAIL criteria
- **Failure handling:** Documented remediation steps for each missing file type
- **Workflow integration:** Pre-check runs BEFORE Step 1 (Gather Source Materials)
- **Enforcement:** Prevents wasted effort on incomplete data; ensures scripts built on complete foundation
- **Updated workflow:** 12 steps → 13 steps (added Step 0)
- **Updated description:** Added "with comprehensive campaign summary" + pre-check mention
- **Why this matters:** User reported scripts being generated without video analysis when videos existed
- **Target issue:** Scripts missing critical insights because source files weren't verified upfront

**v1.5.1** (2025-12-31) - **VISUAL HOOKS INTEGRATION & WORKFLOW ENHANCEMENT**
- **NEW STEP 5.7:** "Extract Visual Hooks from Image Analysis v1.5"
  - Maps Section 10 visual hooks to 3 script angles
  - Decision framework for hook selection (Problem-Solution, Lifestyle, Educational)
  - Integration checklist before script writing
- **ENHANCED STEP 6:** "Script Writing with Visual Hook Integration"
  - NEW REQUIREMENT: Scripts MUST integrate visual hooks from Section 10 if Step 2 completed
  - Added example integration showing exact placement of hooks (Opening, Product, Trust, CTA)
  - Benefits documented: Pre-tested language, compliance-safe, market-tested, production-ready
- **ENHANCED STEP 10:** Campaign Summary now includes Section 9.5 "Image Analysis Insights (v1.5)"
  - **NEW MANDATORY SECTION** if Step 2 completed
  - Documents visual hooks used in each script
  - Summarizes key visual elements from all 10 sections of image analysis
  - Production team reference to full analysis for comprehensive details
- **ENHANCED STEP 11:** Final Quality Gate now verifies image analysis
  - NEW Image Analysis Verification section
  - Checks if analysis exists when images present
  - Validates v1.5 format quality (250+ lines, Section 10, visual hooks)
  - Automated verification command for image analysis
  - Critical failure modes documented with fixes
- **WORKFLOW UPDATES:**
  - Updated workflow from 11 to 12 steps (added Step 5.7)
  - Updated Batch Execution Checklist to include Step 5.7
  - Updated Campaign Summary checklist to verify Section 9.5
  - Updated Source Materials section to include image_analysis.md reference
- **WHY THIS MATTERS:**
  - Bridges v1.5 comprehensive image analysis to actual script production
  - Ensures visual hooks aren't wasted - they MUST be used in scripts
  - Production teams get clear filming instructions from analysis
  - Quality gate prevents incomplete deliverables

**v1.5.0** (2025-12-31) - **COMPREHENSIVE BILINGUAL FORMAT (Cat Tree Standard)**
- **MAJOR REWRITE:** New template based on proven Cat Tree example format
- **Format change:** From PART 1-6 structure → 10+ section comprehensive format
- **Bilingual approach:** Inline translations (## Name | 中文名) instead of separate DE/ZH blocks
- **Section structure (minimum 10):**
  1. Product Design & Aesthetics | 产品设计与美学
  2. [Product-Specific Features] (adapts to category)
  3. Size & Scale Indicators | 尺寸与规模指标
  4. Text & Labels (German) | 文字与标签（德语）
  5. Quality Signals | 质量信号
  6. Variations/Options | 变体/选项
  7. Key Differentiators (vs. Competitors) | 关键差异化
  8. Usage Context | 使用场景
  9. Packaging/Presentation | 包装/展示
  10. **Visual Hooks for TikTok Scripts** | TikTok 脚本的视觉钩子 (CRITICAL)
- **Enhanced Visual Hooks section:** Each hook includes:
  - "How to film" (specific camera instructions)
  - "Why it works" (psychological appeal)
  - "Script hook" (ready-to-use German line)
- **Additional sections:** Visual Hook Recommendations by Script Angle, German Text Elements for Scripts, Next Step: Script Generation
- **Quality standard:** 250-400 lines (vs old 44-100 lines)
- **Reference example:** product_list/1729600227153779322/product_images/image_analysis.md (362 lines)
- **Updated validation:** New v1.5 verification command checks for bilingual headers, Section 10, filming instructions, script hooks
- **Why this matters:** User feedback - "This one is good" (Cat Tree format), requested v1.5 based on this comprehensive structure

**v1.4.3** (2025-12-31) - **OUTPUT VALIDATION REQUIREMENT**
- **CRITICAL ADDITION:** Output Validation & Quality Check section after Step 2
- **Mandatory verification:** Must check image analysis output before proceeding
- **PASS/FAIL criteria:** Clear checklist (150+ lines, all 6 parts, bilingual, synthesized)
- **Verification command:** Bash script to automatically check output quality
- **Retry instructions:** If output fails, explicit template to retry with complete requirements
- **Why this matters:** Prevents proceeding with incomplete/generic image analysis (user reported issue: some analyses were concise with no translation)
- **Quality gate:** Do NOT proceed to script writing if image analysis fails validation
- **Example comparison:** Good example (362 lines, bilingual, synthesized) vs Bad example (44 lines, no Chinese, no synthesis)
- **Enforcement:** Added "🚨 CRITICAL: Do NOT proceed to script writing with failed image analysis"

**v1.4.2** (2025-12-31) - **IMAGE ANALYSIS ENHANCEMENT (Bilingual + Synthesized)**
- **CRITICAL IMPROVEMENT:** Complete rewrite of image analysis prompt template
- **New bilingual format:** German (Parts 1-3) + Chinese (Parts 4-6) - MANDATORY
- **Synthesized insights:** Part 2 (DE) and Part 5 (ZH) provide actionable script elements
- **6-Part structure:**
  - Part 1/4: Visual Intelligence (DE/ZH) - raw observations
  - Part 2/5: Synthesized Script Elements (DE/ZH) - hook ideas, core features, trust signals
  - Part 3/6: Compliance Check (DE/ZH) - safe vs problematic claims
- **Script-ready outputs:**
  - "Für Hook (Erste 3 Sekunden)" - ready-to-use hook formulations
  - "Für Produktvorstellung" - core features with exact German terms
  - "Für Trust-Building" - compliance-safe trust signals
  - "Für CTA" - visual recognition elements
- **Exact German text requirement:** Copy verbatim from packaging (critical for compliance)
- **Good vs Bad examples:** Added comparison showing generic vs synthesized analysis
- **Why this matters:** Previous image analysis was too generic/descriptive; new format provides actionable data directly usable in script writing
- **Token efficiency:** Structured format reduces back-and-forth, one analysis provides everything needed

**v1.4.1** (2025-12-31) - **BATCH EXECUTION CLARITY UPDATE**
- **CRITICAL ADDITION:** Batch Execution Checklist section (lines 59-163)
- **Enhanced workflow steps** with explicit mandatory markers (⚠️)
- **New pre-execution setup** commands to verify source materials
- **Per-product execution order** with stop points at mandatory steps
- **Common batch failure modes** documented with fixes:
  - Skipping image analysis (Mistake #1)
  - Forgetting Campaign Summary (Mistake #2 - most common)
  - Skipping Final Quality Gate (Mistake #3)
  - Batch processing too fast (Mistake #4)
- **Batch verification command** to check completeness after processing N products
- **Step 2 enhancement:** Added critical check to verify if images exist before proceeding
- **Why this matters:** Prevents incomplete deliverables in batch workflows
- **Target issue:** Image analysis and Campaign Summary frequently missed in batch mode

**v1.4.0** (2025-12-31) - **STABILITY RELEASE**
- **MAJOR FEATURE:** Added Step 11 - Final Quality Gate (Mandatory Verification Checkpoint)
- **Why this matters:** Prevents incomplete deliverables (missing Campaign Summary was #1 failure mode)
- **What it includes:**
  - Deliverables verification (all 4 files must exist)
  - Content quality verification (YAML, tags, cues, word count)
  - Campaign Summary completeness check (all 14 sections)
  - Category-specific compliance verification
  - Angle differentiation verification (no script overlap)
  - Common failure modes checklist (8 most frequent mistakes)
  - Final verification command (automated bash check)
  - Clear PASS/FAIL criteria (cannot mark complete until all pass)
- **Added workflow steps overview** at beginning (all 11 steps listed)
- **Updated Quality Gates section** to reference Step 11
- **Critical requirement:** Step 11 CANNOT be skipped - enforced with 🛑 warnings

**v1.3.1** (2025-12-31)
- **PERFORMANCE OPTIMIZATION:** Updated Step 2 (Product Image Analysis) to use Async Gemini CLI MCP
- **Benefits:**
  - Parallel execution for batch workflows (analyze multiple products simultaneously)
  - Token-efficient (doesn't consume Claude Code context)
  - Faster processing with async background execution
  - Better suited for automated e2e workflows
- **Tool Change:** `mcp__gemini-cli-mcp-async__gemini_cli_execute` replaces Claude Read tool for image analysis
- Added example usage for both synchronous and asynchronous workflows
- Added recommendation to save analysis to `image_analysis.md` for reference

**v1.3.0** (2025-12-27)
- **MAJOR FEATURE:** Added Step 5.5 - Golden 3 Seconds Hook Patterns
- **8 Proven Hook Types** for German TikTok market with implementation examples:
  1. Urgency Type (highest retention)
  2. Pain Point Resonance Type (most stable)
  3. Counter-Intuitive Type (strong curiosity)
  4. Documentary Type (safest for organic reach)
  5. Wrong Demonstration Type (high retention)
  6. Result-First Type (direct conversion)
  7. Emotional Whisper Type (Germany special - understated delivery)
  8. Visual-First Type (no voiceover needed)
- **Hook Selection Strategy** by product category (supplements, deals, tools, beauty)
- **German Market Insights** integrated throughout (e.g., low emotion delivery, documentary authenticity)
- Updated description to highlight Golden 3 Seconds methodology

**v1.2.0** (2025-12-27)
- **NEW FEATURE:** Added Step 10 - Campaign Summary creation
- **Campaign Summary includes:**
  - Strategic overview of all 3 scripts as unified campaign
  - Performance data analysis and predictions
  - Audience segmentation matrix
  - Content production notes and recommendations
  - Future creative optimization strategies
- **Purpose:** Serves as production brief and enables data-driven decisions
- Updated description to reflect comprehensive campaign output

**v1.1.0** (2025-12-27)
- **CRITICAL FIX:** Added video analysis verification step
- **Gemini MCP limitation documented:** Cannot directly access local video files
- **New workflow:** Direct gemini-cli or frame extraction for accurate video analysis
- **Caption format updated:** Hashtags now included in caption field for TikTok
- Added red flags checklist for identifying hallucinated analysis
- Added local video file verification (user may curate ref_video folder)

**v1.0.0** (2025-12-26)
- Initial release
- Generalized from health product workflow
- Added category-specific compliance rules (Health, Electronics, Beauty, General)
- Integrated product image analysis step
- Added official description verification step
- Bilingual output (DE/ZH) as standard
- ElevenLabs v3 (alpha) grammar integration
