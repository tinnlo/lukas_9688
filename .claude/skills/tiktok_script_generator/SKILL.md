---
name: tiktok-script-generator
description: Generates 3 TikTok short video scripts (40–50s UGC ad style) in German with MANDATORY Chinese translation, plus a bilingual Campaign Summary. Uses official ElevenLabs v3 audio tags (every line MUST have 1-2 cues). References pre-existing analysis files (does NOT duplicate content). Outputs Obsidian-ready notes to product_list/YYYYMMDD/{product_id}/scripts/ with required frontmatter and sections. OPTIMIZED with batched Write calls.
version: 2.4.0
author: Claude
execution_agent: Claude Code (direct writing with parallel tool calls)
prerequisite: tiktok-product-analysis
---

# TikTok Script Generator Skill v2.4

**PURPOSE:** Generate production-ready UGC TikTok ad scripts with official ElevenLabs v3 audio tags (German VO + mandatory Chinese translation)
**EXECUTOR:** Claude Code (for quality creative writing)
**INPUT:** Analysis files from `tiktok-product-analysis` skill
**OUTPUT:** 3 scripts + Campaign Summary (references analysis, no duplication)
**STYLE:** Natural UGC ads with mandatory emotion cues (1-2 per line), authentic delivery, convincing tone
**OPTIMIZATION:** Batched Write calls (4 files per product in single message) ⭐ **2x faster**

---

## ⚠️ MANDATORY COMPLIANCE GATE ⚠️

**CRITICAL:** All generated scripts MUST pass TikTok policy compliance validation before workflow completion.

**YOU WILL SKIP THIS AT YOUR PERIL.** This step is NON-NEGOTIABLE.

```bash
# Run IMMEDIATELY after writing scripts (Step 3)
for script in product_list/YYYYMMDD/{product_id}/scripts/*.md; do
  [[ "$(basename "$script")" == "Campaign_Summary.md" ]] && continue
  python3 scripts/validate_compliance_flags.py "$script" || exit 1
done
```

**If ANY script fails:** STOP. Fix violations using the TikTok Policy Compliance tables. Re-validate until ALL scripts pass.

**Common violations to watch for:**
- Exact € prices ("15€", "€9.99")
- Absolute claims ("100%", "perfekt", "immer")
- Exaggerated promotions ("unglaublich", "genial", "Preisglitch")
- Medical claims without qualification

See **Step 3.5: MANDATORY Compliance Validation Gate** for complete process.

---

## Core Script Lock (MANDATORY)

Read inputs only from analysis artifacts produced by core scripts in `.claude/skills/CORE_SCRIPTS.md`.
Do not rely on deprecated wrapper outputs.


⚠️ **CRITICAL FORMAT RULE - READ THIS FIRST:**
- **INLINE CUES ONLY:** `[emotion] Text here.` (cue + text on SAME LINE)
- **NEVER BROKEN LINES:** Do NOT write `[emotion]` on one line followed by text on the next line
- **EVERY LINE NEEDS CUES:** No orphan text without emotion tags
- See `templates/voiceover_format.md` for complete format specification

---

## Agent Responsibility

| Task | Agent | Why |
|:-----|:------|:----|
| Image/Video Analysis | Gemini MCP | Parallel processing, token-efficient |
| Script Writing | Claude Code | Better creative quality, detailed storyboards |
| Campaign Summary | Claude Code | Executive synthesis, proper references |

**Key Lesson:** Gemini produces generic placeholder scripts. Claude produces detailed, product-specific content with natural voiceovers.

---

## Workflow (5 Steps - OPTIMIZED)

```
[Step 0: Pre-Check] → GATE (analysis files exist)
        │
        ▼
[Step 1: Read Analysis Files in Parallel] → Extract key insights
        │                                     (5+ Read calls at once)
        ▼
[Step 2: Generate All Scripts + Summary] → Create all 4 files
        │                                    (in single response)
        ▼
[Step 3: Write All Files in Parallel] → 4 Write calls simultaneously
        │                                ⭐ 2x faster
        ▼
[Step 3.5: 🚨 COMPLIANCE VALIDATION GATE 🚨] → MANDATORY BLOCKING STEP
        │                                       Run validate_compliance_flags.py
        │                                       Fix ALL violations before proceeding
        │                                       ⚠️ DO NOT SKIP THIS STEP ⚠️
        ▼
[Step 4: Quality Gate] → Verify completeness
```

**Key Optimization (v2.3.0):** Steps 2-3 now execute in ONE MESSAGE with parallel Write tool calls, eliminating sequential overhead.

**CRITICAL CHANGE (v2.4.1):** Step 3.5 is a NEW MANDATORY gate that validates TikTok policy compliance. This step is BLOCKING and CANNOT be skipped.

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
    echo "Run tiktok-product-analysis skill first"
    exit 1
fi

lines=$(wc -l < "$base/ref_video/video_synthesis.md" | tr -d ' ')
if [ "$lines" -lt 150 ]; then
    echo "❌ BLOCKED: video_synthesis.md too short ($lines lines, need 150+)"
    exit 1
fi

# CRITICAL: Verify synthesis has properly flagged compliance risks
echo "Checking compliance flagging in analysis..."
if ! python3 scripts/validate_compliance_flags.py "$base/ref_video/video_synthesis.md" >/dev/null 2>&1; then
    echo "⚠️ WARNING: video_synthesis.md has compliance risks not properly flagged"
    echo "   Review and ensure risks are documented in 'Compliance & Trust Signals' section"
    echo "   Run: python3 scripts/validate_compliance_flags.py \"$base/ref_video/video_synthesis.md\""
    # Don't block, but warn - analysis files can have flagged risks
fi

echo "✅ Pre-check passed. Ready for script generation."
```

**If blocked:** Run `tiktok-product-analysis` skill first.

### Recommended (Repo Verifier)

```bash
bash scripts/verify_gate.sh --date YYYYMMDD --csv scripts/products.csv --phase analysis
```

---

## Step 1: Read Analysis Files (PARALLEL v2.3.0)

**CRITICAL OPTIMIZATION:** Use parallel Read tool calls to fetch ALL files in ONE MESSAGE.

**Files to read (make 4-5 parallel Read calls):**

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

5. **Individual `video_N_analysis.md` files** (optional, for deep dive)
   - Use if video_synthesis.md lacks detail

**Example parallel execution:**
```
<Read file_path="product_list/YYYYMMDD/{product_id}/ref_video/video_synthesis.md" />
<Read file_path="product_list/YYYYMMDD/{product_id}/product_images/image_analysis.md" />
<Read file_path="product_list/YYYYMMDD/{product_id}/tabcut_data.json" />
```
All 3 files read simultaneously in ~2-3 seconds (was 6-9 seconds sequential).

**Extract these key elements:**
- Top 3 hook patterns from synthesis
- Top 5 selling points (ranked)
- 3 recommended script angles
- German terminology from packaging
- Visual filming instructions
- **Identify which of the 8 Golden 3 Seconds hook types fits each planned script angle** (needed for OST strategy selection in Step 2-3)

---

## Step 2-3: Generate and Write All Scripts (BATCHED v2.3.0)

**CRITICAL OPTIMIZATION:** Generate all 3 scripts + Campaign Summary in ONE response, then make 4 parallel Write tool calls.

**Old workflow (sequential - SLOW):**
```
Generate Script 1 → Write Script 1 → Generate Script 2 → Write Script 2 → Generate Script 3 → Write Script 3 → Generate Summary → Write Summary
Total: ~5-8 minutes per product
```

**New workflow (batched - FAST):**
```
Generate all 4 files (Scripts 1-3 + Summary) → Write all 4 in parallel
Total: ~2-3 minutes per product ⭐ 2x faster
```

**Implementation:**
1. After reading analysis files, **select OST strategy for each script** (see OST Strategy table below)
2. Generate complete content for all 4 files (each script includes `## On-Screen Text` section)
3. In a SINGLE MESSAGE, make 4 Write tool calls in parallel:
   - Write Script 1
   - Write Script 2
   - Write Script 3
   - Write Campaign Summary

### OST Strategy Selection (NEW v2.4.0)

Before writing each script, map the script's Golden 3 Seconds hook type to an OST strategy:

| Hook Type (Golden 3 Seconds) | OST Strategy |
|:------------------------------|:-------------|
| 1. Urgency | Solution Reveal or Social Proof Tease |
| 2. Pain Point Resonance | Hook Overlay or Bold Claim |
| 3. Counter-Intuitive | Curiosity Question or Bold Claim |
| 4. Documentary / Authentic | Product Label (minimal) |
| 5. Wrong Demonstration | Curiosity Question |
| 6. Result-First | Solution Reveal or Bold Claim |
| 7. Emotional Whisper | Emotional / Lifestyle |
| 8. Visual-First / ASMR | Product Label (minimal) |

**OST Strategy Descriptions:**

| # | Strategy | Description | Hook overlay rules |
|:--|:---------|:------------|:-------------------|
| 1 | **Hook Overlay** | Bold full-frame text mirroring/amplifying the verbal hook | ≤10 words DE, center placement, 0–3s |
| 2 | **Curiosity Question** | On-screen question that triggers scroll-stop curiosity | Question format, center, 0–3s |
| 3 | **Bold Claim** | Strong positioning statement with em-dash or colon | Em-dash or colon structure |
| 4 | **Solution Reveal** | Compact "X = solved" or "[Problem]. [Solved]." | Short declarative format |
| 5 | **Emotional / Lifestyle** | Personal, gifting, or aspirational vibe statement | Warm/aspirational tone |
| 6 | **Product Label** | Minimal product name / category only | No emotion, just label |
| 7 | **Social Proof Tease** | Trending/popularity signal | Viral/trending framing |

**OST Rules (all strategies):**
- Max 3 overlays per video (no clutter)
- Hook overlay text ≤ 10 words (DE); ZH translation follows
- Must work muted-only: if viewer only sees text, they still get hooked
- Emoji: limit 1–2 per overlay for emotional signal
- Hook overlay appears in first 0–3s (golden zone)
- Bilingual table: DE column is production text; ZH column is for creator reference/handoff

**Each script must have:**

### Required YAML Frontmatter (Obsidian)

**See `templates/frontmatter_template.md` for complete specification.**

**Quick reference:**
- `duration` target: 00:40–00:50
- `tags` max 5 and meaningful for commerce/interest
- `caption` uses YAML block scalar `caption: >-` with hashtags appended (space-separated)
- Always include `source_notes` to exact files used

### TikTok Policy Compliance (DE Market) - ENHANCED v2.0

**CRITICAL:** These rules prevent TikTok ad rejection and "false advertising" complaints in the German market. All scripts MUST pass compliance validation before publication.

---

#### **POLICY 1: No Exact Low Price Bait** 🚫

**Prohibited:** Specific € amounts combined with urgency, comparison, or scarcity framing.

| ❌ VIOLATION | ✅ COMPLIANT ALTERNATIVE |
|:-------------|:------------------------|
| "Nur 9€!" | "Super günstig!" / "Tolles Preis-Leistungs-Verhältnis" |
| "€9.99 statt €50" | "Fraktioniert vom Markenpreis" / "Für kleines Geld" |
| "Nur noch 3 Stück!" | "Jetzt verfügbar" / "Schnell bestellen" |
| "Warum 150€ zahlen?" | "Markengeräte oft teurer" / "Ohne Aufpreis" |
| "50% Rabatt" | "Top Angebot" / "Aktionspreis" |
| "Jetzt nur €29,99" | "Aktuell besonders günstig" |

**Safe Price Language:**
- German: `"preiswert"`, `"erschwinglich"`, `"für kleines Geld"`, `"fairer Preis"`, `"gutes Preis-Leistungs-Verhältnis"`
- Chinese: `"价格很友好"`, `"很划算"`, `"性价比高"`, `"不贵"`

**Rule:** Avoid exact €, comparison math ("statt/vs"), or urgency tied to price.

---

#### **POLICY 2: No Absolute Effect Claims** 🚫

**Prohibited:** "100%", "pure", "perfect", "genauso gut", "never", "always", "instant" without qualification.

| ❌ VIOLATION | ✅ COMPLIANT ALTERNATIVE |
|:-------------|:------------------------|
| "100% wasserdicht" | "Wasserabweisend" / "Spritzwassergeschützt" |
| "Pure Freude" | "Richtig schön" / "Tolles Gefühl" |
| "Perfektes Geschenk" | "Schöne Geschenkidee" / "Praktisches Geschenk" |
| "Genauso gut wie [Brand]" | "Vergleichbare Qualität" / "Gute Alternative" |
| "Besser als [Brand]" | "Stark genug" / "Für [use case] geeignet" |
| "Nie wieder [problem]" | "Reduziert [problem]" / "Hilft bei [problem]" |
| "Sofort [result]" | "Schnell [result]" / "In kürzester Zeit" |
| "Komplett schützt" | "Bietet Schutz" / "Schützt vor [specific]" |

**Safe Comparison Language:**
- German: `"hilft bei"`, `"unterstützt"`, `"kann"`, `"für... geeignet"`, `"stark genug"`
- Chinese: `"有助于"`, `"支持"`, `"适合"`, `"功能强大"`, `"能满足需求"`

**Rule:** Use qualified claims with "hilft bei", "unterstützt", or specific context instead of absolutes.

---

#### **POLICY 3: No Exaggerated Promotions** 🚫

**Prohibited:** Unverifiable superlatives, false urgency, hyperbolic claims without proof.

| ❌ VIOLATION | ✅ COMPLIANT ALTERNATIVE |
|:-------------|:------------------------|
| "Unbezahlbar!" | "Unersetzlich" / "Wertvoll" / "Besonders" |
| "Genial!" | "Clevere Lösung" / "Praktisch" / "Wirklich gut" |
| "Unglaublich!" | "Beeindruckend" / "Überzeugend" |
| "Bevor es weg ist!" | "Mehr entdecken" / "Jetzt bestellen" |
| "Letzte Chance!" | "Verfügbar" / "Aktuell auf Lager" |
| "Nur noch 3 Stück!" | "Guter Lagerbestand" / "Jetzt verfügbar" |
| "Sie müssen das haben!" | "Lohnt sich" / "Praktisch für" |
| "Das beste Produkt!" | "Eine gute Wahl" / "Empfehlenswert" |
| "100% empfohlen" | "Wir empfehlen" / "Top Bewertungen" |

**Safe Promotion Language:**
- German: `"praktisch"`, `"clever"`, `"hilfreich"`, `"empfehlenswert"`, `"wertvoll"`, `"besonders"`
- Chinese: `"实用"`, `"方便"`, `"值得推荐"`, `"有价值"`, `"特别"`

**Rule:** Avoid hyperboles without proof. Use descriptive, specific benefits instead.

---

#### **POLICY 4: Medical & Health Claims** 🚫

**Prohibited:** Therapy, healing, pain relief, medical treatment framing.

| ❌ VIOLATION | ✅ COMPLIANT ALTERNATIVE |
|:-------------|:------------------------|
| "Heilt [condition]" | "Unterstützt bei [condition]" / "Hilft bei [condition]" |
| "Schmerzlinderung" | "Entspannung" / "Wohlbefinden" / "Angenehm" |
| "Schmerzfreiheit" | "Lindert" / "Besseres Gefühl" |
| "Physiotherapie" | "Massage-Funktion" / "Entspannungsmodus" |
| "Tiefengewebe-Behandlung" | "Intensive Massage" / "Tiefe Entspannung" |
| "Medizinisch bewährt" | "Beliebt bei" / "Viele nutzen" |

**Safe Wellness Language:**
- German: `"Entspannung"`, `"Wohlbefinden"`, `"lockert Verspannungen"`, `"angenehm"`, `"komfortabel"`, `"entspannend"`
- Chinese: `"放松"`, `"舒适"`, `"缓解紧绷感"`, `"享受"`

**Rule:** Never promise medical outcomes. Use wellness/comfort framing only.

---

#### **POLICY 5: Waterproof & Tech Specs** 🚫

**Prohibited:** Absolutes without IP rating proof, ambiguous tech claims.

| ❌ VIOLATION | ✅ COMPLIANT ALTERNATIVE |
|:-------------|:------------------------|
| "100% wasserdicht" | "Spritzwassergeschützt" (IPX4) / "Wasserabweisend" |
| "Komplett wasserdicht" | "Für Regen geeignet" / "Schützt vor Spritzwasser" |
| "4K Support" (ambiguous) | "Unterstützt 4K Dekodierung" / "4K-kompatibel" |
| "Zero Lag" / "Keine Verzögerung" | "Flüssige Wiedergabe" / "Schnelle Reaktion" |
| "Instant [result]" | "Schnell [result]" / "Kurze Ladezeit" |

**Safe Tech Language:**
- Waterproof: Use IP rating ONLY if sourced (e.g., "IP67" from packaging)
- Performance: Use qualified terms ("flüssig", "schnell", "zuverlässig")
- Avoid: "instant", "zero", "100%", "komplett", "total"

---

#### **Compliance Validation Checklist**

Before finalizing scripts, verify:

```bash
# Run compliance validator on generated scripts
for script in product_list/YYYYMMDD/{product_id}/scripts/*.md; do
  [[ "$(basename "$script")" == "Campaign_Summary.md" ]] && continue
  python3 scripts/validate_compliance_flags.py "$script"
done
```

**Manual Review Points:**
- [ ] No € symbols in captions or voiceovers
- [ ] No "100%", "pure", "perfect", "genauso gut", "besser als"
- [ ] No "unbezahlbar", "genial", false urgency ("weg ist", "letzte Chance")
- [ ] Medical terms replaced with wellness language
- [ ] Tech specs qualified (not absolute)

**If validation fails:**
1. Check the specific violation flagged
2. Find the compliant alternative in the table above
3. Replace and re-validate
4. Never bypass compliance checks

---

#### **CTA Language: TikTok Shopping Cart (NEW)**

**CRITICAL:** TikTok now uses orange shopping cart (not external bio/profile links).

**Required CTA format:**

| ✅ REQUIRED | ❌ NEVER USE |
|:------------|:-------------|
| `Link ist unten` (DE) | `Link oben` |
| `链接在下面` (ZH) | `Link im Profil` |
| | `Link im Bio` |
| | `链接在上面` |
| | `简介里的链接` |

**CTA examples:**
- `[confident] Link ist unten.`
- `[cheerfully] Link ist unten. Jetzt sichern.`
- `[warm] Hol's dir. Link ist unten.`

**Rule:** Always direct users to the TikTok shopping cart below the video, not profile/bio links.

---

## Step 3.5: 🚨 MANDATORY COMPLIANCE VALIDATION GATE 🚨 (BLOCKING)

**THIS STEP IS NON-NEGOTIABLE. DO NOT PROCEED TO STEP 4 UNTIL ALL SCRIPTS PASS.**

After writing all scripts in Step 3, you MUST immediately validate them against TikTok advertising policies.

### Why This Gate Exists

- **Real incident:** In February 2026, scripts were generated with policy violations ("price glitch" narrative, exact € amounts, "unglaublich" exaggerations)
- **User discovery:** User caught violations AFTER script generation completed
- **Root cause:** Compliance validation was embedded in Step 4 but not emphasized enough
- **Solution:** This is now a separate, mandatory gate that BLOCKS workflow completion

### Validation Process

```bash
product_id="{product_id}"
date="YYYYMMDD"
scripts_dir="product_list/$date/$product_id/scripts"

echo "=== 🚨 STEP 3.5: COMPLIANCE VALIDATION GATE 🚨 ==="
echo "Validating all scripts against TikTok advertising policies..."
echo ""

compliance_fail=0
violation_files=()

for script in "$scripts_dir"/*.md; do
    [[ "$(basename "$script")" == "Campaign_Summary.md" ]] && continue
    [[ -e "$script" ]] || continue

    echo "Checking: $(basename "$script")"

    if ! python3 scripts/validate_compliance_flags.py "$script"; then
        echo "❌ VIOLATION DETECTED in $(basename "$script")"
        compliance_fail=1
        violation_files+=("$script")
    else
        echo "✅ PASS: $(basename "$script")"
    fi
    echo ""
done

if [ "$compliance_fail" -eq 1 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️ WORKFLOW BLOCKED: COMPLIANCE VIOLATIONS DETECTED ⚠️"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Files with violations:"
    for file in "${violation_files[@]}"; do
        echo "  - $(basename "$file")"
    done
    echo ""
    echo "REQUIRED ACTIONS:"
    echo "1. Review each violation in the TikTok Policy Compliance section"
    echo "2. Use the compliant alternatives table to fix violations"
    echo "3. Re-run this validation until ALL scripts pass"
    echo "4. DO NOT proceed to Step 4 until this gate is clear"
    echo ""
    echo "Common fixes:"
    echo "  - Exact prices → Remove € amounts, use 'günstig' or 'gutes Angebot'"
    echo "  - 'perfekt', '100%', 'immer' → Use qualified alternatives"
    echo "  - 'unglaublich', 'genial' → Use 'praktisch', 'gut', 'hilfreich'"
    echo "  - 'Preisglitch' → Use 'Deal', 'Angebot', 'Schnäppchen'"
    echo ""
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ COMPLIANCE GATE PASSED: ALL SCRIPTS CLEAN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "You may now proceed to Step 4."
echo ""
```

### Manual Validation (If Automated Script Unavailable)

If `validate_compliance_flags.py` is not available, manually check EVERY script for:

**POLICY 1: No Exact Low Price Bait** 🚫
- [ ] No € symbols anywhere (caption, voiceover, on-screen text)
- [ ] No exact amounts: "9€", "€9.99", "15 Euro", "50% Rabatt"
- [ ] No comparison math: "statt €50", "von €X auf €Y"

**POLICY 2: No Absolute Effect Claims** 🚫
- [ ] No "100%", "komplett", "total", "pure"
- [ ] No "perfekt", "genauso gut", "besser als [Brand]"
- [ ] No "immer", "nie", "sofort", "instant"

**POLICY 3: No Exaggerated Promotions** 🚫
- [ ] No "unglaublich", "unbezahlbar", "genial"
- [ ] No "Preisglitch", "price error", "Fehler im System"
- [ ] No false urgency: "letzte Chance", "nur noch 3 Stück", "bevor es weg ist"

**POLICY 4: Medical & Health Claims** 🚫
- [ ] No "heilt", "Schmerzlinderung", "Therapie"
- [ ] Use wellness language: "Entspannung", "Wohlbefinden", "angenehm"

**POLICY 5: Waterproof & Tech Specs** 🚫
- [ ] No "100% wasserdicht" without IP rating proof
- [ ] Use qualified terms: "spritzwassergeschützt", "wasserabweisend"

### Fixing Violations

When violations are found:

1. **Identify the specific policy violated** (see tables in TikTok Policy Compliance section)
2. **Find the compliant alternative** from the provided tables
3. **Edit the script** using the Edit tool
4. **Re-validate immediately** after each fix
5. **Do not batch fixes** - validate after each script edit to ensure no new violations introduced

**Example fix workflow:**

```
❌ Found: "Nur 15€ im Angebot!"
✅ Fix to: "Super günstig im Angebot!"

❌ Found: "Das ist unglaublich gut!"
✅ Fix to: "Das ist wirklich gut!"

❌ Found: "Perfektes Geschenk für jeden"
✅ Fix to: "Schönes Geschenk für jeden"
```

### Common Mistake: Introducing New Violations While Fixing

**WARNING:** When editing scripts to fix violations, be careful not to introduce NEW violations.

**Example of what NOT to do:**
- Fixing "15€" by changing to "unglaublich günstig" → NEW violation (exaggerated promotion)
- Fixing "100% wasserdicht" by changing to "komplett geschützt" → NEW violation (absolute claim)

**Always re-validate after EVERY edit.**

### When This Gate is Complete

You will see:
```
✅ COMPLIANCE GATE PASSED: ALL SCRIPTS CLEAN
You may now proceed to Step 4.
```

Only then may you continue to Step 4: Quality Gate.

**IF YOU SKIP THIS STEP, YOU HAVE FAILED THE WORKFLOW.**

---

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

**Sample-quality example:**

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

## On-Screen Text

**Strategy:** [Strategy name] — [1-sentence rationale linked to this script's hook type]

| Timing | DE Text | ZH Text | Placement |
|:-------|:--------|:--------|:----------|
| 0–3s | **"[Hook overlay ≤10 words]"** | **"[ZH translation]"** | Center |
| [Xs–Ys] | [Mid-video overlay] | [ZH] | [Top/Center-bottom] |
| [Xs–Ys] | [CTA or product label] | [ZH] | [Center-bottom] |
```

### Voiceover Sections

**See `templates/voiceover_format.md` for complete specification and all audio tags.**

**Critical requirements:**
- INLINE cues: `[emotion] Text.` on SAME LINE
- 1-2 audio tags per line (MANDATORY)
- Both German (DE) and Chinese (ZH) sections required
- Target length: 40-50s (100-150 German words, 130-180 Chinese characters)

### Script Naming Convention
```
Product_Model_KeyAngle.md   # e.g., HTC_NE20_AI_Uebersetzer_Earbuds.md
```

---

## Campaign Summary (Reference-Based - Included in Step 2-3)

**See `templates/campaign_summary_structure.md` for complete template.**

**Key Change from v1:** DO NOT duplicate content from analysis files. REFERENCE them.

**MANDATORY:** Use inline Chinese throughout (English text (中文翻译))

**Required sections:**
1. Product Overview | 产品概述
2. Campaign Strategy | 活动策略
3. Key Selling Points | 核心卖点
4. Target Audience | 目标受众
5. Scripts Summary | 脚本摘要
6. Production Notes | 制作说明
7. Source Files | 源文件

---

## Step 4: Quality Gate (Final Validation)

**PREREQUISITE:** Step 3.5 Compliance Validation Gate MUST be complete and passed.

```bash
product_id="{product_id}"
date="YYYYMMDD"
scripts_dir="product_list/$date/$product_id/scripts"

echo "=== QUALITY GATE: $product_id ==="

# Verify Step 3.5 compliance gate was completed
if [ ! -f "$scripts_dir/.compliance_validated" ]; then
    echo "❌ BLOCKED: Step 3.5 Compliance Validation Gate not completed"
    echo "   You must run compliance validation before this step"
    echo "   Run: Step 3.5 validation commands"
    exit 1
fi

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

    # Check for On-Screen Text section
    if ! grep -q "## On-Screen Text" "$script"; then
        echo "❌ FAIL: $(basename $script) missing ## On-Screen Text section"
        exit 1
    fi
done
echo "✅ Script quality verified"

# NOTE: TikTok Policy Compliance validation is now done in Step 3.5
# This gate focuses on structural quality only

echo ""
echo "=== QUALITY GATE PASSED ==="
```

---

## Batch Processing (v2.3.0 Optimized)

**For multiple products, process sequentially with batched writes:**

```
Product A: [Read all files in parallel] → [Generate + Write 4 files in parallel] → [Gate] = 2-3 min
Product B: [Read all files in parallel] → [Generate + Write 4 files in parallel] → [Gate] = 2-3 min
Product C: [Read all files in parallel] → [Generate + Write 4 files in parallel] → [Gate] = 2-3 min
```

**Performance Improvement:**
- **Old (sequential writes):** 5-8 min per product × 8 products = 40-64 min
- **New (batched writes):** 2-3 min per product × 8 products = 16-24 min
- **Savings:** ~25-40 minutes for 8-product batch ⭐ **2x faster**

**Why sequential across products (not parallel)?**
- Claude Code produces better quality with focused attention
- Each product needs full context window for analysis
- Quality over speed for creative content
- BUT: We optimize WITHIN each product via batched writes

**Time estimate (v2.3.0):** ~2-3 minutes per product for script generation

---

## Common Mistakes to Avoid

### ❌ Mistake 1: **BROKEN LINE FORMAT (Most Common Error)**
**Symptoms:** Writing emotion cues on separate lines from text
```
[frustrated]
Du kennst das?
```
**Why it fails:** Validation script expects `[cue] Text.` on SAME LINE. Separate lines create "orphan" text without cues.
**Fix:** ALWAYS write inline: `[frustrated] Du kennst das?`
**Validation Error:** "Low cue density" / "No German voiceover section found"

### ❌ Mistake 2: Starting before analysis complete
**Fix:** Always run Step 0 Pre-Check first

### ❌ Mistake 3: Generic placeholder content
**Symptoms:** "You won't believe...", product="Product"
**Fix:** Read analysis files, use specific product details

### ❌ Mistake 4: Duplicating analysis content in Campaign Summary
**Fix:** Reference files with quotes, don't copy-paste

### ❌ Mistake 5: Missing ElevenLabs v3 markers
**Fix:** Every VO line needs [tone] marker at start (inline format)

### ❌ Mistake 6: Skipping Chinese translations
**Fix:** Chinese translation is mandatory for every script (DE + ZH sections required)

### ❌ Mistake 7: Missing OST section or wrong strategy for hook type
**Symptoms:** No `## On-Screen Text` section, or using "Product Label" strategy for a Pain Point hook
**Fix:** Always select OST strategy from the hook-type mapping table in Step 2-3. Every script needs an OST section with bilingual table.

### ❌ Mistake 8: **SKIPPING COMPLIANCE VALIDATION (CRITICAL)**
**Symptoms:** Generating scripts, declaring completion, moving to next product WITHOUT running Step 3.5
**Why this happens:** Compliance gate is "one more step" that feels bureaucratic when you're in flow
**Consequences:** Scripts published with policy violations → TikTok ad rejection → wasted production effort
**Fix:**
- Step 3.5 is MANDATORY, not optional
- Run `validate_compliance_flags.py` on ALL scripts immediately after writing
- Fix ALL violations before proceeding to Step 4
- Create a mental checkpoint: "Scripts written → Compliance validated → Quality gate → Done"
**Real incident:** February 2026 - multiple scripts generated with "price glitch" narrative, exact € amounts, "unglaublich" exaggerations. User caught violations after workflow marked complete.

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
1. `tiktok-product-scraper` → Product data + videos
2. `tiktok-product-analysis` → Image + video analysis (Gemini)
3. **`tiktok-script-generator`** → Scripts + summary (THIS SKILL - Claude)

**Handoff verification:**
```bash
# Before running this skill, verify:
date="YYYYMMDD"
ls product_list/$date/$product_id/ref_video/video_synthesis.md  # Must exist
```

---

## Compliance Validation: Lessons Learned

### February 2026 Incident

**What happened:**
- Workflow executed for 3 products, generating 9 scripts total
- Scripts were written with batched Write calls (Step 3)
- User discovered Policy violations AFTER workflow marked complete
- 5/9 scripts failed compliance (exact prices, "Preisglitch", absolute claims)

**Root cause:**
- Compliance validation existed in Step 4 but was not emphasized enough
- Easy to miss when executing workflow quickly
- No separate gate between script generation and completion
- Agent declared workflow complete without running compliance checks

**What we learned:**
- Compliance validation must be a SEPARATE, BLOCKING gate (Step 3.5)
- Visual emphasis is critical (🚨 emojis, all-caps warnings)
- Validation must happen IMMEDIATELY after script generation
- Cannot be buried in a larger "quality gate" step
- Need clear incident documentation so future agents understand WHY this matters

**Changes made (v2.4.1):**
- Created Step 3.5 as dedicated compliance gate
- Updated workflow diagram to show compliance as critical checkpoint
- Added prominent warning at top of skill file
- Documented common violations and fixes in Step 3.5
- Added "Mistake 8: Skipping compliance validation" to common errors
- Changed language from "CRITICAL" to "MANDATORY BLOCKING GATE"

**For future agents:**
If you're reading this, you're generating TikTok scripts. When you finish writing scripts (Step 3), your next action MUST be running compliance validation (Step 3.5). No exceptions. This is not negotiable.

---

**Version:** 2.4.1
**Last Updated:** 2026-02-10
**Changes from v2.4.0:**
- **NEW: Step 3.5 - MANDATORY Compliance Validation Gate** ⚠️
- Separated compliance validation from Step 4 quality gate
- Added prominent compliance warning at top of file
- Updated workflow diagram to show 5 steps (was 4)
- Documented February 2026 incident and lessons learned
- Added Common Mistake 8: Skipping compliance validation
- Enhanced Step 3.5 with detailed validation process and fix workflow
- Moved compliance checks OUT of Step 4 (now prerequisite)

**Changes from v2.3:**
- **NEW: On-Screen Text (OST) section** added to every script ⭐
- OST strategy selection table (7 strategies mapped to 8 Golden 3 Seconds hook types)
- `## On-Screen Text` required section with bilingual DE/ZH table
- Quality gate now checks for `## On-Screen Text` in every script
- Step 1 extract: identify hook type per planned angle
- Common Mistake 7: missing/wrong OST strategy
- Workflow reduced: OST strategy selected before writing, included in batched Write calls
