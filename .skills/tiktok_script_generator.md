---
name: tiktok-script-generator
description: Generates 3 TikTok short video scripts (30-40s) for product campaigns with comprehensive campaign summary. Uses proven "Golden 3 Seconds" hook patterns for German market. Analyzes reference videos, product data, images, and official descriptions. Creates bilingual (DE/ZH) scripts with category-specific compliance.
version: 1.3.0
author: Claude
---

# TikTok Script Generator Skill

Generates 3 production-ready TikTok ad scripts based on reference video analysis, product data, visual analysis, and official product descriptions.

## Overview

**Input:** Product ID + Category
**Output:** 3 distinct angle scripts (30-40s each) + Campaign Summary in `shorts_scripts/{product_id}/`

**Key Features:**
- **Golden 3 Seconds Hook Patterns:** 8 proven opening strategies for German TikTok
- Multi-source analysis (videos, data, images, official description)
- Category-specific compliance verification
- Bilingual output (German + Chinese translation)
- ElevenLabs v3 (alpha) grammar formatting
- Visual hook integration from packaging
- 3 different marketing angles per product
- Comprehensive campaign summary with performance predictions

---

## Workflow Steps

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

### Step 2: Product Image Analysis (If Available)

**Use Gemini MCP to analyze product images:**

```
Analyze these product images for [Product Name]:

[List all image paths]

Please provide:
1. **Packaging Design:** Bottle/box color, label design, aesthetic
2. **Label Text:** Product name, key ingredients/features, certifications
3. **Visual Highlights:** Prominently displayed text (badges, seals, counts)
4. **Marketing Messages:** Benefit claims visible on packaging
5. **Product Details:** Quantity, dosage/specs, usage recommendations
6. **Trust Signals:** Lab tested, certifications, quality seals, origin
7. **Brand:** Manufacturer/brand name and logo

Format as a structured report for script writing.
```

**Extract:**
- **Visual hooks** (distinctive design elements for scripts)
- **Specific terminology** (exact German text from packaging)
- **Trust signals** (certifications, origin, quality badges)
- **Product specs** (quantity, dosage, dimensions)

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

### Step 6: Script Writing

**Create 3 scripts following this structure:**

#### File Naming
```
shorts_scripts/{product_id}/
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

### Step 10: Create Campaign Summary

**After all 3 scripts are complete, create a comprehensive campaign summary file.**

**Purpose:**
- Provides strategic overview of all 3 scripts as a unified campaign
- Documents performance data and predictions
- Serves as production brief for video team
- Enables data-driven optimization decisions

**File Location:**
```
shorts_scripts/{product_id}/Campaign_Summary.md
```

**Required Content Sections:**

#### 1. Header Metadata
```yaml
---
product_id: "{product_id}"
product_name: "{Full Product Name}"
campaign_date: YYYY-MM-DD
scripts_count: 3
total_duration: "~XXXs (Xm XXs)"
target_audience: "{Primary demographic}"
---
```

#### 2. Product Overview
- Full product name and shop
- Key features and USPs
- Supply details (quantity, duration)
- Quality certifications
- Main ingredients/components list

#### 3. Campaign Strategy
- Overall strategic approach
- Psychological triggers used (Fear/Urgency, Validation, Education, etc.)
- Key insight statement

#### 4. Scripts Overview (All 3)
For each script:
- **File name** and duration
- **Effectiveness rating** (X/10) based on video analysis or prediction
- **Hook** (exact opening line)
- **Strategy** (what makes this angle work)
- **Tags** (hashtag list)
- **Best For** (specific audience segment)
- **Why It Works** or **Based On** (reference to video analysis insights)

#### 5. Audience Segmentation Table
```markdown
| Audience Segment | Primary Script | Secondary Script |
|:-----------------|:---------------|:-----------------|
| {Segment 1} | Script X ({Angle}) | Script Y ({Angle}) |
| {Segment 2} | Script Y ({Angle}) | Script X ({Angle}) |
...
```

#### 6. Key Selling Points Across Campaign
Organize by trigger type:
- **Rational Triggers (Left Brain):** Specs, certifications, value
- **Emotional Triggers (Right Brain):** Feelings, relief, transformation
- **Trust Signals:** Quality badges, origin, testing

#### 7. Performance Data (Actual Market Results)
From `tabcut_data.md`:
- Total Sales & Revenue
- 7-Day Sales & Revenue
- Conversion Rate
- Video Performance metrics
- Top Performing Video details (creator, hook, views, sales)
- **Key Insight** statement interpreting the data

#### 8. Performance Predictions
- **Expected Best Performers** (rank all 3 scripts with reasoning)
- **Optimization Strategy** (week-by-week scaling plan)

#### 9. Content Production Notes
- **Visual Requirements** for each script (what to film)
- **Voiceover Style** (tone, delivery, language notes)

#### 10. Recommendations for Future Creatives
- **High Priority:** 3-4 immediate next steps
- **Medium Priority:** 3-4 testing opportunities
- **Testing Opportunities:** New angles, demographics, seasonal hooks

#### 11. Top Video Analysis Insights (if applicable)
From `video_analysis.md`:
- Winning hook patterns
- Visual elements that work
- Creator success factors

#### 12. Source Materials
List all reference files:
```markdown
- **Product Data:** `product_list/{product_id}/tabcut_data.md`
- **Video Analysis:** `product_list/{product_id}/video_analysis.md`
- **Product Images:** `product_list/{product_id}/product_images/`
- **Reference Videos:** `product_list/{product_id}/ref_video/`
```

#### 13. Compliance Notes
- **Health Claims Used (Safe):** List exact phrases used
- **Avoided Claims:** What was intentionally not said
- **Important Notes:** Category-specific warnings or disclaimers

#### 14. Footer
```markdown
---
*Campaign created: YYYY-MM-DD*
*Based on proven market performance: X sales, €X revenue, X% conversion*
*Scripts ready for production with ElevenLabs v3 (alpha) voiceover*
```

**Optional Additions:**
- **TOP PERFORMER** or **PRIORITY FOR SCALING** tags for high-performing products
- Portfolio comparison table (if creating multiple campaign summaries)
- Competitive analysis (if available)

**Example Summary File:** See `shorts_scripts/1729535917392698367/Campaign_Summary.md` for reference.

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
shorts_scripts/1729535919239371775/
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

Before delivering scripts:

- [ ] All 3 scripts created in correct directory
- [ ] Each script has unique angle (no overlap)
- [ ] All frontmatter complete and valid
- [ ] Target duration met (30-40s)
- [ ] Word count appropriate (65-115 words)
- [ ] ElevenLabs v3 grammar correct
- [ ] Both DE and ZH versions present
- [ ] Category compliance verified
- [ ] Official product description cross-referenced
- [ ] Visual hooks integrated (if images available)
- [ ] Trust signals accurate
- [ ] No medical/therapeutic claims (for health products)
- [ ] Tags relevant and max 5
- [ ] Source notes correctly linked
- [ ] **Campaign Summary created** with all required sections
- [ ] Performance data analyzed and insights documented
- [ ] Optimization strategy included

---

## Version History

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
