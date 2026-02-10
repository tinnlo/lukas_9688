# ElevenLabs v3 Voiceover Format

## Critical Format Rules

⚠️ **INLINE CUES ONLY - NO BROKEN LINES ALLOWED**

The most common error is writing emotion cues on separate lines from text.

### ❌ WRONG FORMAT (causes validation failure)

```
[frustrated]
Du kennst das?
Kein Papier mehr.
```

Lines 2-3 are "orphans" without cues!

### ✅ CORRECT FORMAT (passes validation)

```
[frustrated] Du kennst das?
[blunt] Kein Papier mehr.
```

Every line has inline cue!

---

## Template Structure

```markdown
## Voiceover

> with ElevenLabs v3 (alpha) grammar

### DE (ElevenLabs Prompt | 40–50s)

[emotion1] German voiceover line 1.
[emotion2] [action1] German voiceover line 2.
[emotion3] German voiceover line 3.

### ZH (中文翻译 | 40–50s)

[emotion1] Chinese translation line 1.
[emotion2] [action1] Chinese translation line 2.
[emotion3] Chinese translation line 3.
```

---

## Mandatory Rules

- ✅ **INLINE:** Emotion cue MUST be on the SAME LINE as text: `[emotion] Text here.`
- ❌ **NEVER:** Emotion cue on separate line followed by orphan text
- ✅ **EVERY LINE:** Every single line MUST have 1-2 audio tags (emotion + optional action)
- ❌ **NO ORPHANS:** No text lines without emotion cues
- ✅ **CHINESE REQUIRED:** Chinese translation is mandatory for every script

---

## Length Calibration

Target word counts for UGC TikTok Ad style (fast-paced):

| Duration | German Words | Chinese Characters | Notes |
|:---------|:-------------|:-------------------|:------|
| 40s | 100-130 | 130-160 | Fast UGC delivery ⭐ |
| 45s | 110-140 | 140-170 | Fast UGC delivery ⭐ |
| 50s | 120-150 | 150-180 | Fast UGC delivery ⭐ |

**Note:** UGC ads use faster tempo than standard narration.

---

## ElevenLabs v3 Audio Tags

### Credible Emotion Cues (⭐ = Recommended for Authentic TikTok Delivery)

**Natural emotions (use frequently):**
- `[curious]` - Natural interest ⭐
- `[interested]` - Engaged attention ⭐
- `[confident]` - Self-assured without arrogance ⭐
- `[impressed]` - Genuine reaction ⭐
- `[happy]` - Authentic joy ⭐
- `[cheerfully]` - Upbeat energy ⭐
- `[excited]` - Enthusiasm (not over-the-top) ⭐
- `[warm]` - Friendly, approachable ⭐
- `[matter-of-fact]` - Straightforward, credible ⭐
- `[reassured]` - Confident reassurance ⭐
- `[thoughtful]` - Considered opinion ⭐
- `[surprised]` - Natural surprise (not shock) ⭐
- `[frustrated]` - Relatable annoyance ⭐
- `[annoyed]` - Irritated ⭐

**Less common / dramatic (use sparingly):**
- `[delighted]` - Very happy (can feel performed if overused)
- `[elated]` - Very pleased (use rarely)
- `[shocked]` - Stunned (theatrical - prefer `[surprised]`)
- `[dramatically]` - Theatrical (avoid - too performative)
- `[mischievously]` - Sly, knowing (okay for playful moments)
- `[sarcastic]` - Sarcastic tone (okay sparingly)

**Action cues (max 1 per line, selective use):**
- `[laughs]` - Natural laughter (okay)
- `[giggles]` - Light laugh (okay sparingly)
- `[sighs]` - Relief/frustration (okay)
- `[whispers]` - Intimate moments (okay)
- `[chuckles]` - Quiet laugh (okay)
- `[exhales]` - Sharp breath out (okay)
- `[inhales deeply]` - Deep breath in (okay)

**Special:**
- `[strong X accent]` - Replace X with accent
- `[sings]` - Melodic delivery

### UGC Workflow Density Requirements

- **MANDATORY:** 1-2 cues per line (NO uncued lines allowed)
- **FORMAT:** Cues MUST be inline: `[emotion] Text.` NOT on separate lines!
- **PHILOSOPHY:** Natural, convincing delivery over theatrical performance
- Hook: 1-2 cues per line for authentic grab
- Middle: 1-2 cues per line for natural flow
- CTA: 1-2 cues for confident close
- Variety: Use natural emotion progression (Curious → Interested → Impressed → Confident)

**Natural combination examples:**
- `[curious] Kennst du das Problem?`
- `[interested] Schau mal—diese Lösung funktioniert.`
- `[impressed] Das funktioniert wirklich gut.`
- `[confident] Link ist unten.`

**AVOID theatrical stacking:**
- ❌ `[excited] [gasps] Das ist WIRKLICH gut!` (too dramatic)
- ❌ `[shocked] [laughs] Was?!` (over-acted)
- ❌ `[elated] [giggles] Ich bin TOTAL begeistert!` (theatrical)

---

## Pacing Rules (Official v3 Grammar)

- **FORBIDDEN:** v3 does NOT support SSML `<break time="x.xs" />` tags
- **FORBIDDEN:** Do not use `[pause]` / `[pause 200ms]` cues
- Use **ellipses (`…`)** for pauses instead
- Use **em-dash (`—`)** for interruptions/pivots
- Use **CAPS** for emphasis on key words (official v3 technique)

**UGC Natural Pacing:**
- Avoid "slow list delivery": don't write long ingredient lists as many 1-word lines
- Prefer 1–2 tight lines with commas and em-dash:
  - `[impressed] Das funktioniert wirklich gut.`
  - `[curious] Und dazu: BCAA, Ashwagandha, Rhodiola—als Bonus im Stack.`
  - `[confident] Genau das, was ich gebraucht hab.`

**Tag Placement:**
- Start of line: `[curious] What is this?`
- End for reactions: `This is amazing! [laughs]`
- Mid-sentence at pauses: `Well, [sighs] I'm not sure what to say.`

---

## CTA Language (TikTok Shopping Cart)

**CRITICAL:** TikTok now uses orange shopping cart (not external bio/profile links).

**Required CTA format:**
- ✅ **German:** `Link ist unten` (Link is below)
- ✅ **Chinese:** `链接在下面` (Link is below)

**NEVER use:**
- ❌ `Link oben` (Link above)
- ❌ `Link im Profil` (Link in profile)
- ❌ `Link im Bio` (Link in bio)
- ❌ `链接在上面` (Link above)
- ❌ `简介里的链接` (Link in profile)

**CTA examples:**
- `[confident] Link ist unten.`
- `[cheerfully] Link ist unten. Jetzt sichern.`
- `[warm] Hol's dir. Link ist unten.`

---

## Complete Reference

See `doc/ElevenLabs_v3_Alpha_VO_Grammar_Practice.md` for full vocabulary and UGC best practices.
