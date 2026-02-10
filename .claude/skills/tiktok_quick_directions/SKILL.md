# Skill: TikTok Quick Directions (Lightweight Product Analysis)

**Version:** 1.2.0
**Purpose:** Quick analysis of tabcut/fastmoss data + product images to generate 3 short script direction titles
**Last Updated:** 2026-02-08

---

## Overview

This skill provides a fast way to analyze product data and generate 3 TikTok short video direction titles without full video analysis. Useful for:
- Initial product research
- Quick topic ideation
- Script direction planning

**NEW:** Auto-fallback to FastMoss when Tabcut data is insufficient or missing.

---

## ⚠️ Compliance Note

These directions include suggested captions. When expanding into full scripts via `tiktok_script_generator`, ensure captions comply with TikTok advertising policies:

- ❌ No exact € prices or discount percentages
- ❌ No absolute claims ("100%", "perfekt", "komplett", "immer")
- ❌ No exaggerated promotions ("unglaublich", "genial", "Preisglitch")

**These are ideation outputs.** Final scripts must pass `validate_compliance_flags.py` validation.

---

## Core Script Lock (MANDATORY)

Use core scripts and execution rules from `.claude/skills/CORE_SCRIPTS.md`.
Use system `python3` for commands in this skill.


---

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TikTok Quick Directions                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: Product Folder                                           │
│  ├── tabcut_data.json OR tabcut_data.md (primary)              │
│  ├── fastmoss_data.json OR fastmoss_data.md (fallback) 🆕      │
│  └── product_images/*.webp                                       │
│                                                                  │
│  Data Quality Check: 🆕                                          │
│  ├── Tabcut data sufficient? → Proceed                          │
│  └── Tabcut data insufficient? → Retry with FastMoss            │
│                                                                  │
│  Process: Analysis                                               │
│  1. Read product data (sales, videos, product info)             │
│  2. Read product images (visual analysis)                        │
│  3. Generate 3 script direction titles                           │
│  4. Save to scripts/Quick_Directions.md 🆕                      │
│                                                                  │
│  Output: Quick_Directions.md File 🆕                            │
│  ├── Direction 1: [Angle] - Duration, Target, Caption          │
│  ├── Direction 2: [Angle] - Duration, Target, Caption          │
│  └── Direction 3: [Angle] - Duration, Target, Caption          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Instructions

### Step 1: Analyze Tabcut Data

Read the product's tabcut data file:

```bash
# Check if markdown exists (preferred)
cat product_list/YYYYMMDD/{product_id}/tabcut_data.md

# Or read JSON
cat product_list/YYYYMMDD/{product_id}/tabcut_data.json
```

Extract:
- Product name and description
- Shop info
- Sales data (7-day, 30-day if available)
- Video count and performance metrics
- Top performing video stats

**🆕 Data Quality Check:**
If Tabcut data shows any of these issues, retry with FastMoss:
- Product name or shop owner is missing/placeholder ("Unknown Product", "undefined", empty, or null)
- Sales data missing/unparseable (e.g., total sales or sales count is null)
- `product_images/` missing or empty
- Top videos list is empty or all entries lack a usable video URL
- Fewer than 3 top videos (soft signal of low-quality data)

### Step 1.5: FastMoss Fallback (If Needed)

If Tabcut data is insufficient, retry with FastMoss:

```bash
# Retry scraping with FastMoss source
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
python3 run_scraper.py --product-id {product_id} --source fastmoss --output-dir ../product_list/YYYYMMDD

# Convert to markdown
python3 convert_json_to_md.py --product-id {product_id} --date YYYYMMDD

# Now use fastmoss_data.md instead of tabcut_data.md
cat product_list/YYYYMMDD/{product_id}/fastmoss_data.md
```

**Note:** FastMoss outputs to `fastmoss_data.json` and `fastmoss_data.md` instead of `tabcut_data.*`.

### Step 2: Prepare Image Analysis

Gather product images for analysis:

```bash
ls -la product_list/YYYYMMDD/{product_id}/product_images/
```

### Step 3: Run Gemini Analysis

Use gemini-cli to analyze and generate 3 direction titles:

```bash
cd product_list/YYYYMMDD/{product_id}

# Create a combined prompt for gemini-cli
cat > /tmp/quick_directions_prompt.txt << 'EOF'
You are a TikTok short-form video content strategist for the German market.

Analyze this product data and images, then provide exactly 3 video direction titles.

Format for each title:
**Title [Number]: [German Title]**
- Angle: [Strategy type - Pain Point, Counter-Intuitive, Documentary, etc.]
- Duration: [Target duration 30-40s]
- Target: [Primary audience]
- Caption & Hashtags:
  [German caption 15-25 words with emoji]
  #hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5
- Why: [Brief reasoning based on market data]

**CRITICAL:** Hashtags must be space-separated (NO commas) for direct copy-paste to TikTok.

Focus on:
1. Different angles (don't repeat the same approach)
2. German market preferences
3. Proven hook types that work in DE market
4. Product USPs and differentiators
EOF

# Run analysis with gemini-cli
gemini-cli \
  "Analyze this TikTok product data and suggest 3 short video direction titles.

$(cat tabcut_data.md 2>/dev/null || jq '.' tabcut_data.json)

Product images: $(ls product_images/ | head -5)"
```

### Step 4: Output Format

The final output should be structured as:

```markdown
# 3 Script Directions — [Product Name]

**Product:** [Full product name]
**Shop:** [Shop name]
**Data:** [Sales summary]
**Generated:** YYYY-MM-DD

---

## Direction 1: [German Title]

- **Angle:** [Strategy Type]
- **Hook Type:** [1-8 from Golden 3 Seconds]
- **Duration:** 30–40s
- **Target:** [Audience description]
- **Caption & Hashtags:**
  [German caption 15-25 words with emoji]
  #hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5
- **Why:** [Market-based reasoning]

---

## Direction 2: [German Title]
[Same format...]

---

## Direction 3: [German Title]
[Same format...]
```

**CRITICAL:** Hashtags must be space-separated (NO commas) for direct copy-paste to TikTok.

### Step 5: Save Output to File

**MANDATORY:** After generating directions, save them to a markdown file:

1. **Create scripts directory** if it doesn't exist:
   ```bash
   mkdir -p product_list/YYYYMMDD/{product_id}/scripts
   ```

2. **Write output to file:**
   - Filename: `Quick_Directions.md`
   - Location: `product_list/YYYYMMDD/{product_id}/scripts/Quick_Directions.md`

3. **Confirm file creation:**
   ```bash
   ls -la product_list/YYYYMMDD/{product_id}/scripts/Quick_Directions.md
   ```

**Purpose:** This file serves as a reference for script writers and preserves the research for future use. The user expects MD files to be created automatically, not just chat output.

---

## Quick Command (Terminal Only)

**NOTE:** This bash function is for terminal/manual use only and outputs to stdout. When using this skill through Claude Code, **always save results to `scripts/Quick_Directions.md`** as specified in Step 5.

```bash
# One-liner for quick directions (terminal output only)
quick_directions() {
    local product_id=$1
    local date="YYYYMMDD"
    cd "product_list/$date/$product_id" || exit 1
    gemini-cli "Analyze this TikTok product data and suggest 3 short video direction titles for German market. Format: Title, Angle, Duration, Target, Why. Data: $(cat tabcut_data.md 2>/dev/null || jq '.' tabcut_data.json) Images: $(ls product_images/)"
}

# Usage (outputs to terminal, does NOT create MD file)
quick_directions 1729479916562717270
```

**When invoked as a skill:** Claude Code will automatically save to `scripts/Quick_Directions.md` per Step 5.

---

## Proven Hook Types (German Market)

| Hook Type | Description | Example |
|-----------|-------------|---------|
| **Pain Point Resonance** | Relatable problem statement | "Kennst du das? Im Ausland und niemand versteht dich." |
| **Counter-Intuitive** | Challenge assumptions | "Ich dachte, das braucht man eigentlich nicht." |
| **Documentary** | First impression/unboxing | "Heute zeige ich euch, was ich gerade bekommen habe." |
| **Comparison** | Better than expensive brands | "Besser als [premium brand] aber ein Bruchteil des Preises" |
| **Pattern Interrupt** | Unexpected opener | "Das hier wird das Internet zerstören." |

---

## Tips

- Each title should target a **different audience segment**
- Vary the **emotional triggers** (fear, curiosity, validation)
- Consider **product USPs** - what makes it unique
- Look at **top performing videos** in tabcut data for patterns
- Keep titles **punchy and German-native sounding**

---

## Example Output

```markdown
## 3 Script Directions for MINISO MS156 AI Translator Earbuds

### Direction 1: "Du sprichst kein Englisch? Kein Problem."
- Angle: Pain Point Resonance (Language Barrier)
- Duration: 35s
- Target: Travelers, language learners (18-45)
- Caption & Hashtags:
  Kennst du das? Im Ausland und niemand versteht dich. Diese Kopfhörer übersetzen in 134 Sprachen Echtzeit! 🌍✨
  #übersetzung #reisen #kopfhörer #sprachenlernen #tech
- Why it works: Addresses core frustration of travel; Video 3 shows language barrier hooks resonate despite poor execution

### Direction 2: "Diese Kopfhörer können mehr als du denkst."
- Angle: Counter-Intuitive (Skepticism to Belief)
- Duration: 32s
- Target: Tech enthusiasts, value-conscious buyers
- Caption & Hashtags:
  Ich dachte, das braucht man nicht. Aber 134 Sprachen Echtzeit-Übersetzung? Ich war überrascht! 😲🎧
  #ai #kopfhörer #tech #gadget #tiktokmademebuyitde
- Why it works: Video 1's "Better than AirPods" drove highest sales (2 units, 3,076 views); authentic skepticism works well in DE

### Direction 3: "Heute zeige ich euch meine neuen AI-Kopfhörer."
- Angle: Documentary (First Impression)
- Duration: 38s
- Target: Gen Z, TechTok, unboxing fans
- Caption & Hashtags:
  Heute zeige ich euch, was ich gerade bekommen habe. 5 Modi, 134 Sprachen und komplett kostenlos! 🎁✨
  #unboxing #ai #earbuds #tech #review
- Why it works: German audiences trust "documenting" authenticity (Video 4 analysis); builds trust through genuine discovery
```

**Copy-Paste Format:** Each direction includes caption + space-separated hashtags ready for TikTok.

---

## Version History

**v1.2.0** (2026-02-08)
- **BREAKING CHANGE:** Added mandatory Step 5 - Save Output to File
- Directions must now be saved to `scripts/Quick_Directions.md` (not just chat output)
- Updated workflow diagram to reflect file creation step
- Added Hook Type field to output format (references Golden 3 Seconds doc)
- Clarified that MD file creation is automatic/required, matching user expectations

**v1.1.0** (2025-12-30)
- Added FastMoss fallback when Tabcut data is insufficient
- Added data quality check criteria
- Step 1.5 for FastMoss retry workflow

**v1.0.0** (Initial)
- Quick analysis of product data + images
- 3 direction titles with captions/hashtags
- Gemini-based analysis
