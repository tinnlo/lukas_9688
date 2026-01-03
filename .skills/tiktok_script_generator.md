---
name: tiktok-script-generator
description: Generates 3 TikTok short video scripts (30–40s) in German with MANDATORY Chinese translation, plus a bilingual Campaign Summary. References pre-existing analysis files (does NOT duplicate content). Outputs Obsidian-ready notes to product_list/{id}/scripts with required frontmatter and sections.
version: 2.1.0
author: Claude
execution_agent: Claude Code (direct writing)
prerequisite: tiktok_product_analysis.md (must complete first)
---

# TikTok Script Generator Skill v2.1

**PURPOSE:** Generate production-ready scripts from analysis foundation (German VO + mandatory Chinese translation)
**EXECUTOR:** Claude Code (for quality creative writing)
**INPUT:** Analysis files from `tiktok_product_analysis.md`
**OUTPUT:** 3 scripts + Campaign Summary (references analysis, no duplication)

---

## Agent Responsibility

| Task | Agent | Why |
|:-----|:------|:----|
| Image/Video Analysis | Gemini MCP | Parallel processing, token-efficient |
| Script Writing | Claude Code | Better creative quality, detailed storyboards |
| Campaign Summary | Claude Code | Executive synthesis, proper references |

**Key Lesson:** Gemini produces generic placeholder scripts. Claude produces detailed, product-specific content with natural voiceovers.

---

## Workflow (5 Steps)

```
[Step 0: Pre-Check] → GATE
        │
        ▼
[Step 1: Read Analysis Files] → Extract key insights
        │
        ▼
[Step 2: Write 3 Scripts] → Detailed storyboards + bilingual VO
        │
        ▼
[Step 3: Campaign Summary] → Reference files (no duplication)
        │
        ▼
[Step 4: Quality Gate] → Verify completeness
```

---

## Step 0: Pre-Check Gate (MANDATORY)

**DO NOT PROCEED if analysis files are missing.**

```bash
product_id="{product_id}"
base="product_list/$product_id"

echo "=== PRE-CHECK: $product_id ==="

# MANDATORY: Video synthesis must exist
if [ ! -f "$base/ref_video/video_synthesis.md" ]; then
    echo "❌ BLOCKED: video_synthesis.md missing"
    echo "Run tiktok_product_analysis.md first"
    exit 1
fi

lines=$(wc -l < "$base/ref_video/video_synthesis.md" | tr -d ' ')
if [ "$lines" -lt 100 ]; then
    echo "❌ BLOCKED: video_synthesis.md too short ($lines lines)"
    exit 1
fi

echo "✅ Pre-check passed. Ready for script generation."
```

**If blocked:** Run `tiktok_product_analysis.md` skill first.

---

## Step 1: Read Analysis Files

**Files to read (in order of importance):**

1. **`ref_video/video_synthesis.md`** (CRITICAL)
   - Hook patterns, selling points, replication strategy
   - Target audience, production patterns
   - DO's and DON'Ts

2. **`product_images/image_analysis.md`** (if exists)
   - Visual hooks (Section 10)
   - German text from packaging
   - Color/variant recommendations

3. **`tabcut_data.json`** (product metadata)
   - Product name, price, shop
   - Sales data, conversion rate
4. **`fastmoss_data.json`** (fallback if tabcut data is missing/unknown)
   - Use if product_name is "Unknown Product" or key sales metrics are null

**Extract these key elements:**
- Top 3 hook patterns from synthesis
- Top 5 selling points (ranked)
- 3 recommended script angles
- German terminology from packaging
- Visual filming instructions

---

## Step 2: Write 3 Scripts

**Each script must have:**

### Required YAML Frontmatter (Obsidian)
```yaml
---
cover: ""
caption: "Short, punchy German caption (no hashtags)"
published: YYYY-MM-DD
duration: "00:35"
sales:
  - yes
link: ""
tags:
  - "#tag1"
  - "#tag2"
  - "#tag3"
  - "#tag4"
  - "#tag5"
product: "Full Product Name"
source_notes:
  - "product_list/{id}/ref_video/video_synthesis.md"
  - "product_list/{id}/product_images/image_analysis.md"
  - "product_list/{id}/tabcut_data.json"
---
```
**Rules:**
- `duration` target: 00:30–00:50
- `tags` max 5 and meaningful for commerce/interest
- `caption` is short and production-ready (no hashtags)
- Always include `source_notes` to exact files used (use fastmoss_data.json if applicable)

### Required Sections
```markdown
## Scripts

[1–2 sentence concept description]

### Structure (35s)
- Hook: [Description] (0-3s)
- Problem/Reveal: [Description] (3-8s)
- Solution/Demo: [Description] (8-20s)
- Benefits: [Description] (20-30s)
- CTA: [Description] (30-35s)

### Visual Strategy
| Seconds | Visual | Purpose |
|:--------|:-------|:--------|
| 00-03 | [Specific shot] | [Why it works] |
| 03-08 | [Specific shot] | [Why it works] |
| ... | ... | ... |

## Voiceover

> with ElevenLabs v3 (alpha) grammar

### DE (ElevenLabs Prompt | 30–50s)

[tone] German voiceover line 1.
[tone] German voiceover line 2.
[tone] German voiceover line 3.
...

### ZH (中文翻译 | 30–50s)

[tone] Chinese translation line 1.
[tone] Chinese translation line 2.
[tone] Chinese translation line 3.
...
```
**MANDATORY:** Chinese translation is required for every script. No exceptions.

### ElevenLabs v3 Tone Markers
```
[confident] [bright] [warm] [firm] [soft]
[curious] [amused] [matter-of-fact] [concerned]
[enthusiastic] [serious] [whisper] [energetic]
```

### Script Naming Convention
```
Product_Model_KeyAngle.md   # e.g., HTC_NE20_AI_Uebersetzer_Earbuds.md
```

---

## Step 3: Campaign Summary (Reference-Based)

**Key Change from v1:** DO NOT duplicate content from analysis files. REFERENCE them.

### Simplified Campaign Summary Template

```markdown
---
product_id: "{product_id}"
product_name: "Product Name"
product_name_zh: "产品名称"
campaign_date: YYYY-MM-DD
scripts_count: 3
shop_name: "Shop Name"
---

# Campaign Summary | 活动总结

## 1. Product Overview | 产品概述

**Product:** [Name] | [中文名]
**Shop:** [Shop Name]
**Price:** €XX.XX

> For detailed product analysis, see:
> - `product_images/image_analysis.md`
> - `ref_video/video_synthesis.md`

## 2. Campaign Strategy | 活动策略

Based on video synthesis analysis, we identified 3 winning angles:

| Script | Angle | Duration | Hook Type |
|:-------|:------|:---------|:----------|
| Script 1 | [Angle] | 35s | [Hook Type] |
| Script 2 | [Angle] | 35s | [Hook Type] |
| Script 3 | [Angle] | 35s | [Hook Type] |

## 3. Key Selling Points | 核心卖点

*Extracted from video_synthesis.md:*

1. **[Point 1]** | [中文] - [Why it converts]
2. **[Point 2]** | [中文] - [Why it converts]
3. **[Point 3]** | [中文] - [Why it converts]

## 4. Target Audience | 目标受众

*From video_synthesis.md Section 5:*

- **Primary:** [Demographic]
- **Pain Points:** [Key pain points]
- **Values:** [What they care about]

## 5. Scripts Summary | 脚本摘要

### Script 1: [Title]
- **File:** `scripts/[Product_Model_KeyAngle].md`
- **Hook:** [First 3 seconds description]
- **Key Message:** [Core selling point]

### Script 2: [Title]
- **File:** `scripts/[Product_Model_KeyAngle].md`
- **Hook:** [First 3 seconds description]
- **Key Message:** [Core selling point]

### Script 3: [Title]
- **File:** `scripts/[Product_Model_KeyAngle].md`
- **Hook:** [First 3 seconds description]
- **Key Message:** [Core selling point]

## 6. Production Notes | 制作说明

*From image_analysis.md Section 10 (Visual Hooks):*

- **Primary Visual:** [Key visual to capture]
- **Lighting:** [Recommendation]
- **Props Needed:** [List]

## 7. Source Files | 源文件

| File | Purpose | Status |
|:-----|:--------|:-------|
| `tabcut_data.json` | Product metadata | ✅ |
| `ref_video/video_synthesis.md` | Market analysis | ✅ |
| `product_images/image_analysis.md` | Visual analysis | ✅/⏭️ |
| `scripts/Script_1_*.md` | Script 1 | ✅ |
| `scripts/Script_2_*.md` | Script 2 | ✅ |
| `scripts/Script_3_*.md` | Script 3 | ✅ |

---
**Generated:** YYYY-MM-DD
**Ready for:** Video Production
```

**Benefits of Reference-Based Summary:**
- Shorter file (50-80 lines vs 200+ lines)
- No content duplication
- Single source of truth (analysis files)
- Easier to update (change analysis, summary stays valid)
- Faster to generate

---

## Step 4: Quality Gate

```bash
product_id="{product_id}"
scripts_dir="product_list/$product_id/scripts"

echo "=== QUALITY GATE: $product_id ==="

# Check script count (exclude Campaign_Summary.md)
script_count=$(ls -1 "$scripts_dir"/*.md 2>/dev/null | grep -v 'Campaign_Summary.md' | wc -l | tr -d ' ')
if [ "$script_count" -lt 3 ]; then
    echo "❌ FAIL: Only $script_count scripts (need 3)"
    exit 1
fi
echo "✅ Scripts: $script_count"

# Check Campaign Summary
if [ ! -f "$scripts_dir/Campaign_Summary.md" ]; then
    echo "❌ FAIL: Campaign_Summary.md missing"
    exit 1
fi
echo "✅ Campaign Summary exists"

# Check script quality (not stubs)
for script in "$scripts_dir"/*.md; do
    if [ "$(basename "$script")" = "Campaign_Summary.md" ]; then
        continue
    fi
    lines=$(wc -l < "$script" | tr -d ' ')
    if [ "$lines" -lt 40 ]; then
        echo "⚠️ WARNING: $(basename $script) may be a stub ($lines lines)"
    fi

    # Check for placeholder content
    if grep -q 'product: "Product"' "$script"; then
        echo "❌ FAIL: $(basename $script) has placeholder product name"
        exit 1
    fi
    if ! grep -q '### ZH' "$script"; then
        echo "❌ FAIL: $(basename $script) missing Chinese translation section"
        exit 1
    fi
done
echo "✅ Script quality verified"

echo ""
echo "=== QUALITY GATE PASSED ==="
```

---

## Batch Processing

**For multiple products, process sequentially per product but parallel across products:**

```
Product A: [Read Analysis] → [Write Scripts] → [Campaign Summary] → [Gate]
Product B: [Read Analysis] → [Write Scripts] → [Campaign Summary] → [Gate]
Product C: [Read Analysis] → [Write Scripts] → [Campaign Summary] → [Gate]
```

**Why not parallel script writing?**
- Claude Code produces better quality with focused attention
- Scripts require reading analysis files (context window management)
- Quality over speed for creative content

**Time estimate:** ~5-8 minutes per product for script generation

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Starting before analysis complete
**Fix:** Always run Step 0 Pre-Check first

### ❌ Mistake 2: Generic placeholder content
**Symptoms:** "You won't believe...", product="Product"
**Fix:** Read analysis files, use specific product details

### ❌ Mistake 3: Duplicating analysis content in Campaign Summary
**Fix:** Reference files with quotes, don't copy-paste

### ❌ Mistake 4: Missing ElevenLabs v3 markers
**Fix:** Every VO line needs [tone] marker at start

### ❌ Mistake 5: Skipping Chinese translations
**Fix:** Chinese translation is mandatory for every script (DE + ZH sections required)

---

## File Structure After Completion

```
product_list/{product_id}/
├── tabcut_data.json                    # From scraper
├── product_images/
│   ├── *.webp
│   └── image_analysis.md               # From analysis skill
├── ref_video/
│   ├── video_*.mp4
│   ├── video_*_analysis.md             # From analysis skill
│   └── video_synthesis.md              # From analysis skill (CRITICAL)
└── scripts/                            # FROM THIS SKILL
    ├── Product_Model_KeyAngle.md
    ├── Product_Model_KeyAngle.md
    ├── Product_Model_KeyAngle.md
    └── Campaign_Summary.md
```

---

## Integration with Other Skills

**Workflow order:**
1. `tiktok_product_scraper.md` → Product data + videos
2. `tiktok_product_analysis.md` → Image + video analysis (Gemini)
3. **`tiktok_script_generator.md`** → Scripts + summary (THIS SKILL - Claude)

**Handoff verification:**
```bash
# Before running this skill, verify:
ls product_list/$product_id/ref_video/video_synthesis.md  # Must exist
```

---

**Version:** 2.1.0
**Last Updated:** 2026-01-02
**Changes from prior version:**
- Separated analysis from script generation
- Reference-based Campaign Summary (no duplication)
- Clear agent assignment (Claude for scripts)
- Simplified workflow (5 steps vs 13)
- Removed image analysis template (moved to tiktok_product_analysis.md)
- Mandatory Chinese translation in every script
- Output paths and naming aligned to Obsidian vault rules
