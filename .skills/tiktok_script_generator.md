---
name: tiktok-script-generator
description: Generates 3 TikTok short video scripts (40–50s UGC ad style) in German with MANDATORY Chinese translation, plus a bilingual Campaign Summary. Uses official ElevenLabs v3 audio tags (every line MUST have 1-2 cues). References pre-existing analysis files (does NOT duplicate content). Outputs Obsidian-ready notes to product_list/YYYYMMDD/{product_id}/scripts/ with required frontmatter and sections.
version: 2.2.0
author: Claude
execution_agent: Claude Code (direct writing)
prerequisite: tiktok_product_analysis.md (must complete first)
---

# TikTok Script Generator Skill v2.2

**PURPOSE:** Generate production-ready UGC TikTok ad scripts with official ElevenLabs v3 audio tags (German VO + mandatory Chinese translation)
**EXECUTOR:** Claude Code (for quality creative writing)
**INPUT:** Analysis files from `tiktok_product_analysis.md`
**OUTPUT:** 3 scripts + Campaign Summary (references analysis, no duplication)
**STYLE:** Fast-paced UGC ads with mandatory emotion cues (1-2 per line), engaging delivery, dynamic performance

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
duration: "00:45"
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
- `duration` target: 00:40–00:50
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

### Visual Strategy - ENHANCED TEMPLATE

**Required format:** Seconds | Visual | Purpose (psychological function)

**Sample-quality example (from Blender_Skeptiker_Eiswuerfel_Test.md):**

| Seconds | Visual | Purpose |
|:--------|:-------|:--------|
| 00-03 | Screenshot of negative comment: "Breaks after 1 day" with creator looking annoyed | Hook: Relatable objection creates curiosity |
| 03-07 | Hands dropping LARGE ice cubes + frozen berries into transparent cup | Build tension: "Can it really handle this?" |
| 07-10 | Close-up: LED display showing battery at 95% before starting | Trust: Tech credibility with real data |
| 10-15 | Blender upside down, ice crushing visible through transparent cup | Proof: Visual confirmation of power |
| 20-25 | Final smoothie texture shot (creamy, no chunks) | Result proof: Delivers on promise |

**Purpose categories (choose 1 per shot):**
- **Hook:** Attention/Relatability/Pattern Interrupt
- **Problem:** Pain amplification/Anchoring
- **Proof:** Evidence/Trust building/Demonstration
- **Objection Handling:** Removes barrier (noise, battery, cleaning)
- **Social Proof:** FOMO/Aspiration
- **Conversion:** CTA/Urgency

**Minimum:** 8-10 shots for 40-50s, each with clear psychological purpose

## Voiceover

> with ElevenLabs v3 (alpha) grammar

### DE (ElevenLabs Prompt | 40–50s)

[emotion1] [action1] German voiceover line 1.
[emotion2] German voiceover line 2.
[emotion3] [action2] German voiceover line 3.
...

**MANDATORY:** Every line MUST have 1-2 audio tags (emotion + optional action).

### ZH (中文翻译 | 40–50s)

[emotion1] [action1] Chinese translation line 1.
[emotion2] Chinese translation line 2.
[emotion3] [action2] Chinese translation line 3.
...

**MANDATORY:** Every line MUST have 1-2 audio tags (emotion + optional action).
```
**MANDATORY:** Chinese translation is required for every script. No exceptions.

---

### Voiceover Length Calibration | 配音长度校准

**Target word counts (UGC TikTok Ad style - FAST PACED):**

| Duration | German Words | Chinese Characters | Notes |
|:---------|:-------------|:-------------------|:------|
| 40s | 100-130 | 130-160 | Fast UGC delivery ⭐ |
| 45s | 110-140 | 140-170 | Fast UGC delivery ⭐ |
| 50s | 120-150 | 150-180 | Fast UGC delivery ⭐ |

**Target range:** 40–50s scripts
**Note**: UGC ads use faster tempo than standard narration. Every line MUST have 1-2 emotion/action cues.

---

### ElevenLabs v3 Audio Tags - OFFICIAL VOCABULARY (UGC TikTok Style)

**Source:** Official ElevenLabs v3 documentation + UGC TikTok workflow customizations

**CRITICAL FOR UGC ADS:** Every line MUST have 1-2 audio tags. Combine emotion + action cues for maximum impact.

#### Voice-related Tags (Emotion & Delivery) ⭐ = UGC Favorites

**Official ElevenLabs tags:**
- `[laughs]` - Full laugh ⭐
- `[laughs harder]` - Intensified laughter
- `[starts laughing]` - Gradual laughter
- `[wheezing]` - Breathless laughter
- `[giggles]` - Light laugh ⭐
- `[chuckles]` - Quiet laugh
- `[whispers]` - Quiet, intimate ⭐
- `[sighs]` - Exhale of frustration/relief ⭐
- `[exhales]` - Sharp breath out
- `[inhales deeply]` - Deep breath in
- `[exhales sharply]` - Quick breath out
- `[clears throat]` - Throat clearing
- `[sarcastic]` - Sarcastic tone ⭐
- `[curious]` - Questioning, interested ⭐
- `[excited]` - High enthusiasm ⭐
- `[crying]` - Tearful delivery
- `[snorts]` - Dismissive sound
- `[mischievously]` - Sly, knowing ⭐

**Additional validated emotion tags:**
- `[happy]` - Joyful delivery ⭐
- `[sad]` - Melancholy tone
- `[angry]` - Frustrated/upset
- `[annoyed]` - Irritated ⭐
- `[surprised]` - Caught off-guard ⭐
- `[cheerfully]` - Upbeat ⭐
- `[elated]` - Very pleased ⭐
- `[delighted]` - Very happy ⭐
- `[dramatically]` - Theatrical ⭐
- `[warmly]` - Kind/friendly
- `[impressed]` - Admiring
- `[frustrated]` - Annoyed ⭐
- `[nervously]` - Anxious
- `[shocked]` - Stunned ⭐

#### Special Tags

- `[strong X accent]` - Replace X with accent (e.g., `[strong French accent]`) ⭐
- `[sings]` - Melodic delivery ⭐
- `[screams]` - Excited yell (use strategically)

#### Sound Effects (use sparingly)

- `[applause]` - Clapping sound
- `[clapping]` - Hand clapping
- `[gunshot]` - Gunshot
- `[explosion]` - Explosion

**UGC Workflow Density Requirements:**
- **MANDATORY:** 1-2 cues per line (NO uncued lines allowed)
- Hook: 2 cues per line for instant grab
- Middle: 1-2 cues per line for dynamic flow
- CTA: 2 cues for confident close
- Variety: Use diverse emotion chains (Curious → Excited → Happy → Delighted)
- Combination examples: `[excited] [gasps]`, `[shocked] [laughs]`, `[curious] [whispers]`

**Complete reference:** See `doc/ElevenLabs_v3_Alpha_VO_Grammar_Practice.md` for full vocabulary and UGC best practices.

### VO Pacing Rules (Important)

**CRITICAL - Official v3 Grammar:**
- **FORBIDDEN:** v3 does NOT support SSML `<break time="x.xs" />` tags
- **FORBIDDEN:** Do not use `[pause]` / `[pause 200ms]` / `[pause: 200ms]` cues
- Use **ellipses (`…`)** for pauses instead
- Use **em-dash (`—`)** for interruptions/pivots
- Use **CAPS** for emphasis on key words (official v3 technique)

**UGC Fast Pacing:**
- Avoid "slow list delivery": don't write long ingredient lists as many 1-word lines ending in `.`
- Prefer 1–2 tight lines with commas and an em-dash, e.g.:
  - `[excited] Das ist WIRKLICH gut!`
  - `[shocked] [gasps] Was?! Das gibt's NICHT!`
  - `[curious] Und dazu: BCAA, Ashwagandha, Rhodiola—als Bonus im Stack.`

**Tag Placement (official best practice):**
- Start of line: `[curious] What is this?`
- End for reactions: `This is amazing! [laughs]`
- Mid-sentence at pauses: `Well, [sighs] I'm not sure what to say.`

### Script Naming Convention
```
Product_Model_KeyAngle.md   # e.g., HTC_NE20_AI_Uebersetzer_Earbuds.md
```

---

## Step 3: Campaign Summary (Reference-Based)

**Key Change from v1:** DO NOT duplicate content from analysis files. REFERENCE them.

### Campaign Summary Template (Comprehensive Inline Chinese)

**MANDATORY:** Use inline Chinese throughout (English text (中文翻译)) following the template format below.
EVERY section header must have `| 中文翻译`. Every key bullet must have inline Chinese.

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
**Price (价格):** ~€XX.XX (based on sales data | 基于销售数据)
**Model (型号):** Model Number (if applicable | 如适用)
**Total Sales (总销量):** X,XXX units | X,XXX 件
**Total Revenue (总营收):** €XXX.XK ($ XXX.XK)

> For detailed product analysis, see (详细产品分析请参考):
> - `product_images/image_analysis.md` (图片分析 - XXX lines | XXX行)
> - `ref_video/video_synthesis.md` (视频综合分析 - XXX lines | XXX行)

## 2. Campaign Strategy | 活动策略

Based on video synthesis analysis (基于视频综合分析), we identified 3 winning angles (获胜角度) targeting different audience pain points (针对不同受众痛点):

| Script (脚本) | Angle (角度) | Duration (时长) | Hook Type (钩子类型) |
|:-------|:------|:---------|:----------|
| Script_File_1.md | Angle Name (角度名称) | XXs | Hook description (钩子描述) |
| Script_File_2.md | Angle Name (角度名称) | XXs | Hook description (钩子描述) |
| Script_File_3.md | Angle Name (角度名称) | XXs | Hook description (钩子描述) |

**Why these angles work (为什么这些角度有效):**
- **Angle 1 brief (角度1简述)** – Description (描述)
- **Angle 2 brief (角度2简述)** – Description (描述)
- **Angle 3 brief (角度3简述)** – Description (描述)

## 3. Key Selling Points | 核心卖点

*Extracted from video_synthesis.md (提取自视频综合分析):*

1. **Selling Point 1 (卖点1)** – Description (描述). **Conversion Factor (转化因素):** How it overcomes objections (克服异议的方式)

2. **Selling Point 2 (卖点2)** – Description (描述). **Conversion Factor (转化因素):** How it overcomes objections (克服异议的方式)

3. **Selling Point 3 (卖点3)** – Description (描述). **Conversion Factor (转化因素):** How it overcomes objections (克服异议的方式)

4. **Selling Point 4 (卖点4)** – Description (描述). **Conversion Factor (转化因素):** How it overcomes objections (克服异议的方式)

5. **Selling Point 5 (卖点5)** – Description (描述). **Conversion Factor (转化因素):** How it overcomes objections (克服异议的方式)

## 4. Target Audience | 目标受众

*From video_synthesis.md (来自视频综合分析):*

- **Primary 1 (首要受众1):** Audience Segment Name (受众细分名称) – Description (描述). Age (年龄): XX-XX. Key trait (关键特征): trait (特征).

- **Primary 2 (首要受众2):** Audience Segment Name (受众细分名称) – Description (描述). Key trait (关键特征): trait (特征).

- **Secondary (次要受众):** Audience Segment Name (受众细分名称) – Description (描述). Key trait (关键特征): trait (特征).

- **Tertiary (第三受众):** Audience Segment Name (受众细分名称) – Description (描述). Key trait (关键特征): trait (特征).

**Pain Points Addressed (解决的痛点):**
- "Pain point quote" (痛点引用) → Solution (解决方案)
- "Pain point quote" (痛点引用) → Solution (解决方案)
- "Pain point quote" (痛点引用) → Solution (解决方案)
- "Pain point quote" (痛点引用) → Solution (解决方案)

## 5. Scripts Summary | 脚本摘要

### Script 1 (脚本1): Script_File_Name.md
- **File (文件):** `scripts/Script_File_Name.md`
- **Hook (钩子):** Visual + audio description (视觉+音频描述)
- **Key Message (核心信息):** Description (描述)
- **Proof Mechanic (证据机制):** Description (描述)
- **Best For (最适合):** Target audience (目标受众), use case (使用场景)
- **Emotional Arc (情感弧线):** Emotion → Emotion → Emotion → Emotion (情感→情感→情感→情感)

### Script 2 (脚本2): Script_File_Name.md
- **File (文件):** `scripts/Script_File_Name.md`
- **Hook (钩子):** Visual + audio description (视觉+音频描述)
- **Key Message (核心信息):** Description (描述)
- **Proof Mechanic (证据机制):** Description (描述)
- **Best For (最适合):** Target audience (目标受众), use case (使用场景)
- **Emotional Arc (情感弧线):** Emotion → Emotion → Emotion → Emotion (情感→情感→情感→情感)

### Script 3 (脚本3): Script_File_Name.md
- **File (文件):** `scripts/Script_File_Name.md`
- **Hook (钩子):** Visual + audio description (视觉+音频描述)
- **Key Message (核心信息):** Description (描述)
- **Proof Mechanic (证据机制):** Description (描述)
- **Best For (最适合):** Target audience (目标受众), use case (使用场景)
- **Emotional Arc (情感弧线):** Emotion → Emotion → Emotion → Emotion (情感→情感→情感→情感)

## 6. Production Notes | 制作说明

*From image_analysis.md Section 10 (来自图片分析第10节 - Visual Hooks | 视觉钩子):*

- **Primary Visual (主要视觉):** Description (描述) – Why it works (为什么有效)
- **Lighting (灯光):** Description (描述)
- **Props Needed (所需道具):**
  - Prop 1 (道具1) –用途/purpose (用途)
  - Prop 2 (道具2) –用途/purpose (用途)
  - Prop 3 (道具3) –用途/purpose (用途) - for Script X (用于脚本X)
- **Audio (音频):** Description (描述) – keep X to emphasize "Y" feature (保持X以强调"Y"特性)

**Filming Tips from synthesis (来自综合分析的拍摄技巧):**
- Tip 1 (技巧1) – Purpose (目的)
- Tip 2 (技巧2) – Purpose (目的)
- Tip 3 (技巧3) – Purpose (目的)

## 7. Source Files | 源文件

| File (文件) | Purpose (用途) | Status (状态) |
|:-----|:--------|:-------|
| `tabcut_data.json` | Product metadata (产品元数据): X.XK sales (销量), €XXK revenue (营收) | ✅ |
| `ref_video/video_synthesis.md` | Market analysis (市场分析): XXX lines (行), X top videos (X个热门视频) | ✅ |
| `product_images/image_analysis.md` | Visual analysis (视觉分析): XXX lines (行), X images (X张图片) | ✅ |
| `scripts/Script_File_1.md` | Script 1 (脚本1) – Angle description (角度描述) | ✅ |
| `scripts/Script_File_2.md` | Script 2 (脚本2) – Angle description (角度描述) | ✅ |
| `scripts/Script_File_3.md` | Script 3 (脚本3) – Angle description (角度描述) | ✅ |

---
**Generated (生成日期):** YYYY-MM-DD
**Ready for (准备用于):** Video Production (视频制作)
**Estimated Performance (预计表现):** Assessment (评估) – addresses top X objections (解决前X大异议): objection list (异议列表) with proof type (证据类型)
```

### Inline Chinese Format Rules

**CRITICAL:** Follow these rules for comprehensive bilingual coverage:

1. **Section Headers:** ALL must have `| 中文翻译`
   - ✅ `## 1. Product Overview | 产品概述`
   - ❌ `## Product Overview`

2. **Bold Labels:** Inline Chinese for ALL bold labels
   - ✅ `**Product (产品):** Product Name | 产品名称`
   - ❌ `**Product:** Product Name`

3. **Table Headers:** ALL columns must have inline Chinese
   - ✅ `| Script (脚本) | Angle (角度) |`
   - ❌ `| Script | Angle |`

4. **Bullet Points:** Key items must have inline Chinese
   - ✅ `- **Primary (主要):** Description (中文描述)`
   - ❌ `- **Primary:** Description`

5. **Value Lists:** Items with `|` separator should be translated
   - ✅ `Product Name | 产品名称`
   - ❌ `Product Name only`

### Optional: Simplified Summary

If you need a super short internal note, you can use a simplified variant, but still keep `| 中文` headings and inline Chinese for key bullets.

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

**Version:** 2.2.0
**Last Updated:** 2026-01-17
**Changes from v2.1:**
- Updated to official ElevenLabs v3 audio tags (verified from docs)
- MANDATORY 1-2 audio tags per line (UGC TikTok workflow)
- Fast-paced UGC delivery style (higher word counts: 50s = 120-150 words)
- Added official v3 grammar rules (no SSML break tags, use ellipses/CAPS)
- Expanded audio tag vocabulary (laughs, gasps, excited, shocked, etc.)
- Action cues for dramatic effect (giggles, sighs, whispers)
- Complete reference to `doc/ElevenLabs_v3_Alpha_VO_Grammar_Practice.md`
- Tag combination examples for maximum impact

**Changes from v2.0:**
- Separated analysis from script generation
- Reference-based Campaign Summary (no duplication)
- Clear agent assignment (Claude for scripts)
- Simplified workflow (5 steps vs 13)
- Removed image analysis template (moved to tiktok_product_analysis.md)
- Mandatory Chinese translation in every script
- Output paths and naming aligned to Obsidian vault rules
