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

### Voice-related Tags (⭐ = UGC Favorites)

**Laughter:**
- `[laughs]` - Full laugh ⭐
- `[giggles]` - Light laugh ⭐
- `[chuckles]` - Quiet laugh

**Breath:**
- `[whispers]` - Quiet, intimate ⭐
- `[sighs]` - Exhale of frustration/relief ⭐
- `[exhales]` - Sharp breath out
- `[inhales deeply]` - Deep breath in

**Emotions:**
- `[sarcastic]` - Sarcastic tone ⭐
- `[curious]` - Questioning, interested ⭐
- `[excited]` - High enthusiasm ⭐
- `[annoyed]` - Irritated ⭐
- `[surprised]` - Caught off-guard ⭐
- `[frustrated]` - Annoyed ⭐
- `[shocked]` - Stunned ⭐
- `[happy]` - Joyful delivery ⭐
- `[cheerfully]` - Upbeat ⭐
- `[elated]` - Very pleased ⭐
- `[delighted]` - Very happy ⭐
- `[dramatically]` - Theatrical ⭐
- `[mischievously]` - Sly, knowing ⭐

**Special:**
- `[strong X accent]` - Replace X with accent ⭐
- `[sings]` - Melodic delivery ⭐

### UGC Workflow Density Requirements

- **MANDATORY:** 1-2 cues per line (NO uncued lines allowed)
- **FORMAT:** Cues MUST be inline: `[emotion] Text.` NOT on separate lines!
- Hook: 2 cues per line for instant grab
- Middle: 1-2 cues per line for dynamic flow
- CTA: 2 cues for confident close
- Variety: Use diverse emotion chains (Curious → Excited → Happy → Delighted)

**Combination examples:**
- `[excited] [gasps] Das ist WIRKLICH gut!`
- `[shocked] [laughs] Was?!`
- `[curious] [whispers] Schau mal hier.`

---

## Pacing Rules (Official v3 Grammar)

- **FORBIDDEN:** v3 does NOT support SSML `<break time="x.xs" />` tags
- **FORBIDDEN:** Do not use `[pause]` / `[pause 200ms]` cues
- Use **ellipses (`…`)** for pauses instead
- Use **em-dash (`—`)** for interruptions/pivots
- Use **CAPS** for emphasis on key words (official v3 technique)

**UGC Fast Pacing:**
- Avoid "slow list delivery": don't write long ingredient lists as many 1-word lines
- Prefer 1–2 tight lines with commas and em-dash:
  - `[excited] Das ist WIRKLICH gut!`
  - `[shocked] [gasps] Was?! Das gibt's NICHT!`
  - `[curious] Und dazu: BCAA, Ashwagandha, Rhodiola—als Bonus im Stack.`

**Tag Placement:**
- Start of line: `[curious] What is this?`
- End for reactions: `This is amazing! [laughs]`
- Mid-sentence at pauses: `Well, [sighs] I'm not sure what to say.`

---

## Complete Reference

See `doc/ElevenLabs_v3_Alpha_VO_Grammar_Practice.md` for full vocabulary and UGC best practices.
