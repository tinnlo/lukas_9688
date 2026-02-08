# ElevenLabs v3 (alpha) — Prompting Techniques for UGC TikTok Ads

Goal: make German TikTok UGC ads sound **energetic, engaging, and attention-grabbing** (fast-paced, dynamic emotions, infectious delivery) using **ElevenLabs v3 (alpha)**.

This is a practical writing guide for the text you feed into ElevenLabs (not a linguistics primer).

**Source**: Official ElevenLabs v3 documentation (Updated Feb 2026) + UGC TikTok workflow customizations

---

## ⚠️ CRITICAL: v3 Does NOT Support "Grammar" Parameter

**Key Differences from v2 Models:**

ElevenLabs' Eleven v3 model **does not support** the traditional "grammar" parameter used in Turbo v2 or Flash v2 models for phonetic control or pronunciation rules. Instead, v3 relies on:

- **Audio tags** (e.g., `[whispers]`, `[laughs]`, `[excited]`)
- **Punctuation** (ellipses `…`, em-dashes `—`)
- **Capitalization** for emphasis (CAPS)
- **Precise prompting** for delivery, emotion, and pronunciation

| Feature | Turbo/Flash v2 | Eleven v3 |
|---------|----------------|-----------|
| **Grammar Parameter** | ✅ Yes (phonetic control) | ❌ No |
| **SSML Support** | ✅ Phoneme tags, break tags | ❌ No SSML |
| **Control Method** | SSML phonemes, aliases | Audio tags, punctuation |
| **Multi-Speaker** | ❌ No | ❌ No (despite API docs claiming yes)* |
| **Best For** | Precise pronunciation | Emotional dialogue |

**\*Multi-Speaker Status (Feb 2026):** While ElevenLabs documentation mentions "Text to Dialogue API" with multi-speaker support, **this feature is not yet functional in practice**. Use single-speaker format with visual markers instead.

### What "v3 Grammar" Actually Means

When this guide refers to "ElevenLabs v3 (alpha) grammar," it means **prompting style and text formatting techniques** (not an API parameter). Think of it as the "grammar" of how you write prompts for v3's emotional engine.

For v3, use:
- Ellipses `…` for pauses (instead of SSML `<break>` tags)
- CAPS for stress/emphasis (instead of phoneme tags)
- Audio tags for emotion (instead of SSML prosody)

---

## What v3 (alpha) is great at (UGC TikTok style)

v3 (alpha) is optimized for **emotionally rich, expressive delivery** and performance.

For UGC TikTok ads, aim for authentic emotional impact:
- **Every line MUST have 1-2 emotion/action cues** (mandatory for this workflow)
- Use **natural, convincing delivery** for credible TikTok engagement
- Energetic tempo with authentic emotion progression
- **Action cues selectively** (max 1 per line, used strategically)

Critical rules:
- NEVER leave a line without emotion cues
- Prefer convincing energy over theatrical performance
- Use natural emotion progression to maintain engagement (Curious → Interested → Impressed → Confident)

---

## Natural emotion cueing (UGC ad philosophy)

**MANDATORY**: Every line must have 1-2 emotion/action cues.

Distribution:
- Hook: 1-2 cues per line for authentic grab
- Middle: 1-2 cues per line for natural flow
- CTA: 1-2 cues for confident close

**Key principle:** Keep emotion curves for engagement, but avoid theatrical stacking and over-acting.

---

## Punctuation & line breaks (the real "grammar")

### Line breaks = beat changes

One idea per line. Use short "micro-lines" to force natural breaths:
- "Ganz kurz."
- "Pass auf."
- "Und jetzt kommt's."

### Periods create confidence

German VO becomes more human when you use more periods than in writing:
- "Das ist keine Spielerei."
- "Das funktioniert."

### Capitalization for emphasis

Capitalize words to increase emphasis (official v3 technique):
- "Das ist SEHR wichtig."
- "UNGLAUBLICH gut."

### Dashes and ellipses for pauses

Use for "thinking out loud" (v3 does not support SSML break tags):
- `—` for pivots/interruptions: "Ich dachte erst—ne."
- `…` for suspense/soft landing: "Und das Beste ist…"

---

## Fast pacing & dramatic timing

**CRITICAL**: v3 does NOT support SSML break tags. Explicit pause cues are FORBIDDEN.

Create dynamic timing with:
1) **Audio tags** (emotion + action cues)
2) **Ellipses** (`…`) for pauses
3) **Micro-lines** (fast cuts)
4) **Self-correction** ("Also—nicht das Case. Die Earbuds.")
5) **Punctuation** (`…` / `—`)

Target: Fast, energetic pace for TikTok UGC ads.

---

## Complete Audio Tags Vocabulary (Official ElevenLabs v3)

**Source: ElevenLabs official documentation**

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
- `[warmly]` - Kind/friendly ⭐
- `[matter-of-fact]` - Straightforward, credible ⭐
- `[reassuring]` - Confident reassurance ⭐
- `[thoughtful]` - Considered opinion ⭐
- `[surprised]` - Natural surprise ⭐
- `[frustrated]` - Relatable annoyance ⭐
- `[annoyed]` - Irritated ⭐
- `[professional]` - Formal tone ⭐

**Less common / dramatic (use sparingly):**
- `[delighted]` - Very happy (can feel performed if overused)
- `[elated]` - Very pleased (use rarely)
- `[shocked]` - Stunned (theatrical - prefer `[surprised]`)
- `[dramatically]` - Theatrical (avoid - too performative)
- `[mischievously]` - Playful/sly (okay for playful moments)
- `[sarcastic]` - Sarcastic tone (okay sparingly)
- `[appalled]` - Shocked/disgusted (dramatic)
- `[desperately]` - Urgent (dramatic)
- `[panicking]` - Frantic (dramatic)
- `[alarmed]` - Startled (dramatic)

**Action cues (max 1 per line, selective use):**
- `[laughs]` - Natural laughter (okay) ⭐
- `[giggles]` - Light laugh (okay sparingly)
- `[chuckles]` - Quiet laugh (okay)
- `[sighs]` - Relief/frustration (okay) ⭐
- `[whispers]` - Intimate moments (okay) ⭐
- `[exhales]` - Sharp breath out (okay)
- `[inhales deeply]` - Deep breath in (okay)
- `[clears throat]` - Throat clearing (okay)
- `[laughs harder]` - Intensified laughter (use rarely)
- `[starts laughing]` - Gradual laughter (use rarely)
- `[wheezing]` - Breathless laughter (dramatic)
- `[exhales sharply]` - Quick breath out (okay)
- `[snorts]` - Dismissive sound (use rarely)
- `[crying]` - Tearful delivery (dramatic)
- `[cracking up]` - Breaking into laughter (use rarely)

**Additional validated emotion/delivery tags:**
- `[sad]` - Melancholy tone
- `[angry]` - Frustrated/upset
- `[cautiously]` - Careful delivery
- `[quizzically]` - Puzzled
- `[indecisive]` - Uncertain
- `[jumping in]` - Interrupting
- `[stuttering]` - Hesitant speech
- `[sympathetic]` - Understanding
- `[questioning]` - Asking
- `[nervously]` - Anxious
- `[sheepishly]` - Embarrassed
- `[deadpan]` - Flat delivery

### Sound Effects Tags

**Official from ElevenLabs:**
- `[gunshot]` - Gunshot sound
- `[applause]` - Clapping sound
- `[clapping]` - Hand clapping
- `[explosion]` - Explosion sound
- `[swallows]` - Swallowing sound
- `[gulps]` - Gulping sound

**Environmental audio (experimental):**
- `[leaves rustling]`
- `[gentle footsteps]`
- `[football]` - Football match ambiance
- `[wrestling match]` - Wrestling ambiance
- `[auctioneer]` - Auction style delivery

### Special/Experimental Tags

**Official from ElevenLabs:**
- `[strong X accent]` - Replace X with desired accent (e.g., `[strong French accent]`, `[strong Russian accent]`) ⭐
- `[sings]` - Melodic delivery ⭐
- `[woo]` - Exclamation
- `[screams]` - Excited yell (use strategically)

### Pause/Timing Tags (Non-Speech)

**Official from ElevenLabs:**
- `[short pause]` - Brief silence
- `[long pause]` - Extended silence

**Note**: Use ellipses (`…`) for pauses in text instead when possible.

---

## UGC TikTok Usage Guidelines

**For this workflow:**
- 1-2 cues per line (MANDATORY)
- Prioritize natural, convincing delivery over theatrical performance
- Natural emotion progression = believability (Curious → Interested → Impressed → Confident)
- Variety > Repetition (use diverse emotion curves)
- **UGC TikTok ads prefer authentic energy over flat delivery**
- Action cues: Max 1 per line, used selectively (no stacking like `[excited] [gasps]`)
- ⭐ = Recommended for credible delivery

**Tag placement** (official best practice):
- Place tags at the start of the line: `[curious] What is this?`
- Or immediately after for reactions: `This is amazing. [laughs]`
- Or mid-sentence at natural pauses: `Well, [sighs] I'm not sure what to say.`

**AVOID theatrical stacking:**
- ❌ `[excited] [gasps]` - Over-acted
- ❌ `[shocked] [dramatically]` - Theatrical
- ❌ `[elated] [giggles]` - Too performative

---

## "Anti‑AI flavor" checklist (fast QA)

- Sentence lengths vary (short hits + medium sentences)
- At least 2 human beats (reaction, aside, or self-correction)
- No repeated cadence (don't start every line with "Und…")
- Feature list has rhythm (mini-lines, not one long enumeration)
- CTA is short and confident (no over-selling)
- Use CAPS for emphasis on key words

---

## Recommended house template for this vault

In `product_list/{vendor}/{product_id}/script/*.md`:

```text
## Voiceover

> with ElevenLabs v3 (alpha) prompting techniques

### DE (ElevenLabs Prompt | 40–50s)

[curious] …
[interested] …
[impressed] …
[confident] …
```

**Every line MUST have 1-2 cues.**

**Note:** "v3 grammar" refers to prompting style (audio tags + punctuation), not an API parameter.

---

## Multi-Speaker Dialogue: Current Status

**⚠️ NOT SUPPORTED (Feb 2026)**

Despite ElevenLabs documentation mentioning "Text to Dialogue API" with multi-speaker support using speaker labels (`Woman:`, `Man:`), **this feature is not yet functional in production**.

### Workaround for UGC TikTok Ads

Use **single-speaker voiceover** with **visual markers** for dialogue scenes:

```text
## Voiceover

> with ElevenLabs v3 (alpha) prompting techniques

### DE (ElevenLabs Prompt | 40s)

Woman: [curious] Entschuldigung, mir ist deine Uhr aufgefallen. Die ist richtig stylisch!

Woman: [interested] Ist die teuer?

[reassured] Nicht wirklich. Gutes Design, solide gebaut, aber super Preis.

[confident] Schau mal, das Display ist 1,85 Zoll. HD.
[impressed] Massiv groß und super klar.
[excited] 710 Milliamperestunden Akku. Hält fast eine Woche!

[enthusiastic] Über 100 Sportmodi direkt am Handgelenk.

Woman: [delighted] Wo kann man die kaufen?

[enthusiastic] Im TikTok Shop. Einfach Link klicken!
```

**How this works:**
- **`Woman:`** = Visual marker for video editing (shows when woman speaks on screen)
- **Regular lines** = Single TTS voice speaks entire script
- **Production:** Show woman's face when `Woman:` marker appears, show product/hands for other lines

### Alternative: Voice Acting

For true dialogue effect:
1. Generate TTS for main voice (creator/narrator)
2. Record woman's lines separately (voice actor or different TTS session)
3. Mix in post-production with video

### When Multi-Speaker Might Work (Future)

Monitor ElevenLabs changelog for "Text to Dialogue API" availability. If/when functional:
- Format: `Speaker: [emotion] Text`
- Voice assignment in API/UI
- Non-deterministic (generate 2-3 versions)

---

## Practical timing guide (40–50s UGC ads)

Fast-paced UGC delivery (energetic tempo):
- 40s: ~100–130 words ⭐
- 45s: ~110–140 words ⭐
- 50s: ~120–150 words ⭐

**Target range:** 40–50s scripts (sweet spot for TikTok UGC ads)

If it sounds too slow:
- add emotion cues, shorten sentences, remove filler

If it sounds flat:
- add 2-3 action cues + exaggerate emotion shifts + more exclamations

---

## Natural Delivery Checklist (for Credible TikTok Scripts)

**TARGET:** Convincing energy with authentic emotion curve (not theatrical)

**Balance check:**
- ❌ **NOT this (too flat):** All `[matter-of-fact]` with no emotion variety
- ❌ **NOT this (theatrical):** Stacked action cues, `[shocked] [gasps]`, excessive `[elated]`
- ✅ **YES this (credible curve):** Natural progression like `[curious] → [interested] → [impressed] → [confident]`

**Rewrite moves for authentic energy:**
1) Use natural reactions: `[curious] Kennst du das Problem?`
2) Add relatable contrast: `Sieht billig aus—aber funktioniert richtig gut.`
3) Selective action cues (max 1 per line): `[impressed] Ich hab's getestet. [confident] Überzeugt.`
4) Natural emphasis: `Das funktioniert wirklich gut!`
5) Emotion progression (not whiplash): Curious → Interested → Impressed → Confident (natural flow)
6) Use CAPS for emphasis: `Das ist WIRKLICH gut!`
7) Confident CTA: `[confident] Link ist unten.`

**Examples showing the difference:**

**Theatrical (AVOID):**
```
[shocked] [gasps] Oh mein GOTT!
[excited] [dramatically] Das ist UNGLAUBLICH!
[elated] [giggles] Ich bin TOTAL begeistert!
```

**Credible (TARGET):**
```
[curious] Kennst du das Problem? [frustrated] Nie findest du, was du suchst.
[interested] Schau mal—diese Box hat ein Sichtfenster.
[impressed] Ein Blick, und du weißt sofort, was drin ist.
[confident] Das ist genau, was ich gebraucht hab. [warm] Link ist unten.
```

---

## Official ElevenLabs v3 Best Practices

### Voice Selection
- Choose voices with emotional range for v3
- Neutral voices are more stable across languages
- IVC (Instant Voice Clone) recommended over PVC for v3

### Stability Settings
- **Creative**: More emotional, prone to hallucinations
- **Natural**: Balanced, closest to original (RECOMMENDED for UGC)
- **Robust**: Highly stable, less responsive to tags

### Tag Effectiveness
- Tags work differently per voice and training samples
- Don't expect contradictory results (whispering voice won't shout)
- Experiment with combinations for complex delivery
- Text structure strongly influences output

---

## Examples from Official Docs

### Expressive UGC-style:
```
[laughs] Alright...guys - guys. Seriously.
[exhales] Can you believe just how - realistic - this sounds now?
[laughing hysterically] I mean OH MY GOD...it's so good.
```

### Emotional delivery:
```
[cheerfully] Hello, how are you?
[stuttering] I'm... I'm doing well, thank you
```

### Multi-emotion flow:
```
[giggling] That's really funny!
[groaning] That was awful.
Well, [sighs] I'm not sure what to say.
```
