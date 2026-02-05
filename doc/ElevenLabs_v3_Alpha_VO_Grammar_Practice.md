# ElevenLabs v3 (alpha) — VO Grammar & Prompting Practice (UGC TikTok Ads)

Goal: make German TikTok UGC ads sound **energetic, engaging, and attention-grabbing** (fast-paced, dynamic emotions, infectious delivery) using **ElevenLabs v3 (alpha)**.

This is a practical writing guide for the text you feed into ElevenLabs (not a linguistics primer).

**Source**: Official ElevenLabs v3 documentation (Updated Feb 2026) + UGC TikTok workflow customizations

---

## What v3 (alpha) is great at (UGC TikTok style)

v3 (alpha) is optimized for **emotionally rich, expressive delivery** and performance.

For UGC TikTok ads, maximize emotional impact:
- **Every line MUST have 1-2 emotion/action cues** (mandatory for this workflow)
- Use **dynamic, engaging emotion chains** for attention-grabbing delivery
- Fast-paced, energetic tempo (no slow pacing)
- **Action cues for drama** (laughs, giggles, gasps, sighs, whispers)

Critical rules:
- NEVER leave a line without emotion cues
- Prefer infectious and dynamic over flat delivery
- Use rapid emotion shifts to maintain engagement

---

## Maximum emotion cueing (UGC ad philosophy)

**MANDATORY**: Every line must have 1-2 emotion/action cues.

Distribution:
- Hook: 2 cues per line for instant grab
- Middle: 1-2 cues per line for dynamic flow
- CTA: 2 cues for confident close

Never remove cues - add more for energy if needed.

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

### Voice-related Tags (Delivery & Emotion)

**Official tags from ElevenLabs:**
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

**Additional validated emotion/delivery tags:**
- `[happy]` - Joyful delivery ⭐
- `[sad]` - Melancholy tone
- `[angry]` - Frustrated/upset
- `[annoyed]` - Irritated ⭐
- `[appalled]` - Shocked/disgusted
- `[thoughtful]` - Reflective
- `[surprised]` - Caught off-guard ⭐
- `[elated]` - Very pleased ⭐
- `[cautiously]` - Careful delivery
- `[cheerfully]` - Upbeat ⭐
- `[quizzically]` - Puzzled
- `[indecisive]` - Uncertain
- `[jumping in]` - Interrupting
- `[stuttering]` - Hesitant speech
- `[professional]` - Formal tone
- `[sympathetic]` - Understanding
- `[questioning]` - Asking
- `[reassuring]` - Comforting
- `[nervously]` - Anxious
- `[alarmed]` - Startled
- `[sheepishly]` - Embarrassed
- `[frustrated]` - Annoyed ⭐
- `[desperately]` - Urgent
- `[cracking up]` - Breaking into laughter
- `[deadpan]` - Flat delivery
- `[panicking]` - Frantic
- `[mischievously]` - Playful/sly
- `[warmly]` - Kind/friendly
- `[impressed]` - Admiring
- `[dramatically]` - Theatrical ⭐
- `[delighted]` - Very happy ⭐

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
- Combine emotion + action cues for maximum impact: `[excited] [gasps]`
- Fast emotion shifts = high engagement
- Variety > Repetition (but maximize emotional range)
- Match engaging emotional arc (Surprised → Excited → Curious → Delighted → Confident)
- **UGC TikTok ads prefer engaging and dynamic over flat delivery**
- Use action cues generously for dramatic effect
- ⭐ = High-impact cues for UGC

**Tag placement** (official best practice):
- Place tags at the start of the line: `[curious] What is this?`
- Or immediately after for reactions: `This is amazing! [laughs]`
- Or mid-sentence at natural pauses: `Well, [sighs] I'm not sure what to say.`

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

> with ElevenLabs v3 (alpha) grammar

### DE (ElevenLabs Prompt | 40–50s)

[excited] [gasps] …
[curious] …
[playful] [giggles] …
[shocked] …
[confident] [emphatic] …
```

**Every line MUST have 1-2 cues.**

---

## Multi-Speaker Dialogue (NEW in v3)

ElevenLabs v3 supports multi-speaker dialogue using **Speaker labels**.

### Format:

```text
Speaker 1: [excited] First speaker's line here.

Speaker 2: [curious] Second speaker's line here.

Speaker 1: [happy] First speaker responds.
```

### Key Rules:

- Use `Speaker 1:`, `Speaker 2:`, etc. (can also use character names like `Woman:`, `Man:`)
- Each speaker can have their own voice assigned in the ElevenLabs interface
- Audio tags work the same as single-speaker format
- Leave blank lines between speakers for clarity (optional but recommended)
- You can have unlimited speakers in one dialogue

### Example (UGC TikTok Dialogue):

```text
Customer: [curious] Entschuldigung, die Uhr ist richtig stylisch. Welche Marke ist das?

Creator: [confident] Danke! Schau mal, das Display ist 1,85 Zoll. HD.

Creator: [excited] 710 Milliamperestunden Akku. Hält fast eine Woche!

Creator: [enthusiastic] Link ist unten. Schnapp sie dir!
```

**Important**: In the ElevenLabs UI or API, you assign different voices to each speaker. The format tells the system WHEN to switch voices.

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

## Rewrite moves to maximize UGC energy (use ALL)

1) Add engaging reactions: "[shocked] [gasps] Was?! Das gibt's NICHT!"
2) Add dramatic contrast: "Sieht billig aus—aber kostet 200 Euro!"
3) Inject action cues: "[giggles] Ich hab's getestet—"
4) Add exclamations: "Krass! Kein Witz!"
5) Fast emotion shifts: Shocked → Excited → Confident (within 10s)
6) Use CAPS for emphasis: "Das ist WIRKLICH gut!"
7) Crisp, punchy CTA: "[confident] [emphatic] Link. Jetzt."

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
