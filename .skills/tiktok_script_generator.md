---
name: tiktok-script-generator
description: Generates 3 TikTok short video scripts (45–50s) in German with MANDATORY Chinese translation, plus a bilingual Campaign Summary. References pre-existing analysis files (does NOT duplicate content). Outputs Obsidian-ready notes to product_list/YYYYMMDD/{product_id}/scripts/ with required frontmatter and sections.
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
# Use the correct dated batch folder:
date="YYYYMMDD"
base="product_list/$date/$product_id"

echo "=== PRE-CHECK: $product_id ==="

# MANDATORY: Video synthesis must exist
if [ ! -f "$base/ref_video/video_synthesis.md" ]; then
    echo "❌ BLOCKED: video_synthesis.md missing"
    echo "Run tiktok_product_analysis.md first"
    exit 1
fi

lines=$(wc -l < "$base/ref_video/video_synthesis.md" | tr -d ' ')
if [ "$lines" -lt 150 ]; then
    echo "❌ BLOCKED: video_synthesis.md too short ($lines lines, need 150+)"
    exit 1
fi

echo "✅ Pre-check passed. Ready for script generation."
```

**If blocked:** Run `tiktok_product_analysis.md` skill first.

### Recommended (Repo Verifier)

```bash
bash scripts/verify_gate.sh --date YYYYMMDD --csv scripts/products.csv --phase analysis
```

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
caption: >-
  Short, punchy TikTok caption in German WITH hashtags appended (space-separated, no commas, no quote marks)
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
  - "product_list/YYYYMMDD/{product_id}/ref_video/video_synthesis.md"
  - "product_list/YYYYMMDD/{product_id}/product_images/image_analysis.md"
  - "product_list/YYYYMMDD/{product_id}/tabcut_data.json"
---
```
**Rules:**
- `duration` target: 00:30–00:50
- `tags` max 5 and meaningful for commerce/interest
- `caption` uses TikTok caption format: include the same hashtags as `tags` appended at the end (space-separated), with no commas and no quote marks
- Use YAML block scalar `caption: >-` so `:` and `#` don't break frontmatter parsing
- Always include `source_notes` to exact files used (use fastmoss_data.json if applicable)

### Compliance & Policy Wording (DE Market)

These rules reduce avoidable ad/policy rejections and “false advertising” complaints.

**1) Price / Discount Claims**
- Avoid exact prices and exact discount math in scripts and captions (e.g. `"10€"`, `"€5.49"`, `"40€ → 15€"`, `"10€ vs 100€"`). Prices change too often.
- Prefer relative wording:
  - German: `"super günstig"`, `"preiswert"`, `"für kleines Geld"`, `"fairer Preis"`
  - Chinese: `"价格很友好"`, `"很划算"`, `"不贵"`
- If a price is absolutely required: only use what’s explicitly present in `tabcut_data.json`, and treat it as “current at time of recording” (still risky).

**2) Waterproof / Water-Resistance Claims**
- Do **not** say `"100% wasserdicht"` / `"komplett wasserdicht"` / `"完全防水"` unless an IP rating is clearly documented in `tabcut_data.json` or packaging text from `product_images/image_analysis.md`.
- Safe defaults:
  - German: `"spritzwassergeschützt"` (shower splash), `"wasserabweisend"` (rain)
  - Chinese: `"防溅水"` / `"防泼水"`
- If an IP rating exists, be precise:
  - `IP67` / `IPX7` is okay **only if sourced**, and keep wording practical (e.g., “regen/shower ok”)—avoid implying “swimming”.

**3) Medical / Therapeutic Claims**
- Avoid medical promises or therapy framing:
  - Don’t use: `"Schmerzlinderung"`, `"Schmerzfreiheit"`, `"heilt"`, `"behandelt"`, `"Therapeut"`, `"Physio"`, `"Tiefengewebe-Behandlung"`
- Use wellness language:
  - German: `"Entspannung"`, `"Wohlbefinden"`, `"lockert Verspannungen"` (no guarantees)
  - Chinese: `"放松"`, `"缓解紧绷感"` (avoid medical certainty)

**4) Tech Specs & Capability Claims**
- Match the strongest claim to the strongest source.
- Especially for projectors:
  - `"4K Support"` is ambiguous; prefer `"unterstützt 4K Dekodierung"` unless you can prove native 4K.
  - Avoid “instant/no lag/zero buffering” absolutes; use “läuft flüssig” / “keine spürbare Verzögerung” (still be careful).

### Quick Post-Gen Scan (recommended)

Run these after generating scripts to catch compliance issues fast:

```bash
scripts_dir="product_list/YYYYMMDD/{product_id}/scripts"

# Prices / currency
rg -n "€|\\bEuro\\b|欧元" "$scripts_dir" --glob '!Campaign_Summary.md' || true

# Waterproof absolutes
rg -n "100% wasserdicht|komplett wasserdicht|100%防水|完全防水" "$scripts_dir" --glob '!Campaign_Summary.md' || true

# Medical claims
rg -n "Schmerz|Physio|Therapeut|Tiefengewebe|heilt|behandelt" "$scripts_dir" --glob '!Campaign_Summary.md' || true
```

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

### VO Pacing Rules (Important)
- **FORBIDDEN:** Do not use `[pause]` / `[pause 200ms]` / `[pause: 200ms]` cues.
- Avoid “slow list delivery”: don’t write long ingredient lists as many 1-word lines ending in `.`.
  - Prefer 1–2 tight lines with commas and an em-dash, e.g.:
    - `[matter-of-fact] Cyanotis Arachnoidea Extrakt: 1200 mg.`
    - `[excited] Und dazu: BCAA, Ashwagandha, Rhodiola, Schwarzer Pfeffer‑Extrakt—als Bonus im Stack.`

### Script Naming Convention
```
Product_Model_KeyAngle.md   # e.g., HTC_NE20_AI_Uebersetzer_Earbuds.md
```

---

## Step 3: Campaign Summary (Reference-Based)

**Key Change from v1:** DO NOT duplicate content from analysis files. REFERENCE them.

### Campaign Summary Template (Comprehensive Inline Chinese)

MANDATORY: use inline Chinese throughout (English text (中文翻译)), not just headings.

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

**Product (产品):** Product Name | 产品名称  
**Shop (店铺):** Shop Name  
**Price (价格):** €XX.XX (from sales data | 基于销售数据)  

> For detailed analysis, see (详细分析请参考):
> - `product_images/image_analysis.md`
> - `ref_video/video_synthesis.md`

## 2. Campaign Strategy | 活动策略

Based on video synthesis insights (基于视频综合洞察), we selected 3 angles (选择3个角度) to cover different pain points (覆盖不同痛点):

| Script (脚本) | Angle (角度) | Duration (时长) | Hook Type (钩子类型) |
|:-------|:------|:---------|:----------|
| Script 1 | Angle name (角度中文) | 35s | Hook type (钩子中文) |
| Script 2 | Angle name (角度中文) | 35s | Hook type (钩子中文) |
| Script 3 | Angle name (角度中文) | 35s | Hook type (钩子中文) |

**Why these angles work (为什么有效):**
- Angle 1 reason (角度1原因)
- Angle 2 reason (角度2原因)
- Angle 3 reason (角度3原因)

## 3. Key Selling Points | 核心卖点

Extracted from `ref_video/video_synthesis.md` (提取自视频综合):

1. Selling point (卖点) — why it converts (转化原因)
2. Selling point (卖点) — why it converts (转化原因)
3. Selling point (卖点) — why it converts (转化原因)
4. Selling point (卖点) — why it converts (转化原因)
5. Selling point (卖点) — why it converts (转化原因)

## 4. Target Audience | 目标受众

- Primary audience (主要受众): description (中文描述)
- Secondary audience (次要受众): description (中文描述)

**Pain Points → Solutions (痛点→解决方案):**
- "Pain point" (中文痛点) → solution (中文解决方案)
- "Pain point" (中文痛点) → solution (中文解决方案)

## 5. Scripts Summary | 脚本摘要

### Script 1 (脚本1): Script_File_Name.md
- File (文件): `scripts/Script_File_Name.md`
- Hook (钩子): description (中文描述)
- Key Message (核心信息): description (中文描述)
- Proof Mechanic (证据机制): description (中文描述)

### Script 2 (脚本2): Script_File_Name.md
- File (文件): `scripts/Script_File_Name.md`
- Hook (钩子): description (中文描述)
- Key Message (核心信息): description (中文描述)
- Proof Mechanic (证据机制): description (中文描述)

### Script 3 (脚本3): Script_File_Name.md
- File (文件): `scripts/Script_File_Name.md`
- Hook (钩子): description (中文描述)
- Key Message (核心信息): description (中文描述)
- Proof Mechanic (证据机制): description (中文描述)

## 6. Production Notes | 制作说明

From image analysis (来自图片分析):
- Primary visual hook (主要视觉钩子): description (中文描述)
- Props (道具): list (中文)

## 7. Source Files | 源文件

| File (文件) | Purpose (用途) | Status (状态) |
|:-----|:--------|:-------|
| `tabcut_data.json` | Product metadata (产品元数据) | ✅ |
| `ref_video/video_synthesis.md` | Market synthesis (市场综合) | ✅ |
| `product_images/image_analysis.md` | Visual analysis (视觉分析) | ✅/⏭️ |
| `scripts/*.md` | 3 scripts + summary (三条脚本+总结) | ✅ |

---
Generated (生成): YYYY-MM-DD  
Ready for (用于): Video Production (视频制作)
```

### Optional: Simplified Summary

If you need a super short internal note, you can use a simplified variant, but keep `| 中文` headings and inline Chinese for key bullets.

---

## Step 4: Quality Gate

```bash
product_id="{product_id}"
date="YYYYMMDD"
scripts_dir="product_list/$date/$product_id/scripts"

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

    # Caption should use YAML block scalar so hashtags don't break YAML parsing
    if ! awk 'BEGIN{in=0} /^---$/{in=!in} in && /^caption: >-/{ok=1} END{exit !ok}' "$script"; then
        echo "⚠️ WARNING: $(basename $script) caption is not using 'caption: >-' (hashtags may break YAML)"
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
product_list/YYYYMMDD/{product_id}/
├── tabcut_data.json                    # From scraper
├── product_images/
│   ├── *.webp
│   └── image_analysis.md               # From analysis skill
├── ref_video/
│   ├── video_*.mp4
│   ├── video_*_analysis.md             # From analysis skill
│   └── video_synthesis.md              # From analysis skill (CRITICAL)
└── scripts/                            # FROM THIS SKILL (new workflow)
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
date="YYYYMMDD"
ls product_list/$date/$product_id/ref_video/video_synthesis.md  # Must exist
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
