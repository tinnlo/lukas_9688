# ElevenLabs v3 Multi-Speaker Dialogue Examples

**⚠️ IMPORTANT: FEATURE NOT YET AVAILABLE (Feb 2026)**

This file documents the **intended format** for ElevenLabs v3 multi-speaker dialogue based on official documentation. However, **this feature is not currently functional in production**.

**Current Status:**
- ElevenLabs documentation describes "Text to Dialogue API" with multi-speaker support
- In practice, this feature **does not work** as of February 2026
- Use single-speaker workaround with visual markers instead (see below)

---

## Recommended Workaround for UGC TikTok Ads

### Single-Speaker Format with Visual Markers

Use this format until multi-speaker is truly available:

```text
## Voiceover

> with ElevenLabs v3 (alpha) prompting techniques

### DE (ElevenLabs Prompt | 40s)

Woman: [curious] Entschuldigung, mir ist deine Uhr aufgefallen. Die ist richtig stylish!

Woman: [interested] Ist die teuer?

[reassured] Nicht wirklich. Gutes Design, solide gebaut, aber super Preis.

[confident] Schau mal, das Display ist 1,85 Zoll. HD.
[excited] 710 Milliamperestunden Akku. Hält fast eine Woche!

Woman: [delighted] Wo kann man die kaufen?

[enthusiastic] Im TikTok Shop. Einfach Link klicken!
```

**How it works:**
- **`Woman:`** labels = Visual markers for video editing (not spoken by TTS)
- **Regular lines** = Single TTS voice narrates entire script
- **Video production:** Show woman on screen when `Woman:` marker appears
- **Alternative:** Record woman's lines separately with voice actor, mix in post

---

## Future: Multi-Speaker Format (When Available)

**Purpose:** Reference examples for when ElevenLabs Text-to-Dialogue API becomes functional

**Source:** Official ElevenLabs documentation + UGC TikTok workflow customizations

---

## Quick Reference: Multi-Speaker Format

### Basic Syntax

```text
Speaker 1: [emotion] Dialogue text here.

Speaker 2: [emotion] Response text here.

Speaker 1: [emotion] Follow-up text here.
```

**Alternative naming:**
- Use descriptive labels: `Customer:`, `Creator:`, `Woman:`, `Man:`
- Blank lines between speakers optional (but improves readability)
- Assign different voices in ElevenLabs API/UI

---

## UGC TikTok Template (German - Price Question)

**Scenario:** Customer asks about price, Creator explains value, then features, customer asks where to buy

```text
Customer: [curious] Entschuldigung, ist die teuer?

Creator: [reassured] Nicht wirklich. Gutes Design, solide gebaut, aber super Preis.

Creator: [confident] Schau mal, das Display ist 1,85 Zoll. HD.

Creator: [impressed] 710 Milliamperestunden Akku. Hält fast eine Woche!

Creator: [confident] Über 100 Sportmodi direkt am Handgelenk.

Customer: [interested] Wo kann man die kaufen?

Creator: [confident] Im TikTok Shop. Einfach Link klicken!
```

**Duration:** ~40 seconds  
**Emotion arc:** Curious → Reassured → Excited → Interested → Confident  
**Tags:** 1-2 per line (MANDATORY for UGC workflow)

---

## Example 1: Smartwatch Coffee Shop Discovery

**Scenario:** Customer notices smartwatch in café, asks about features, impressed by battery life

```text
Woman: [curious] Entschuldigung, mir ist deine Uhr aufgefallen. Die ist richtig stylisch!

Man: [happy] Danke! [confident] Das ist die neue Smartwatch mit 1,85 Zoll Display.

Woman: [impressed] Wow, das ist riesig!

Man: [impressed] Und der Akku hält fast eine WOCHE!

Woman: [surprised] Eine Woche? Kein Witz?

Man: [confident] Kein Witz! [warm] Und schau mal—zwei Armbänder inklusive!

Woman: [interested] Das ist ja praktisch! Wo gibt's die?

Man: [confident] Im TikTok Shop. Link ist unten!
```

**Duration:** ~30 seconds  
**Key hooks:** Style compliment → Feature reveal → Battery shock → Dual straps bonus → CTA  
**Emotion shifts:** Curious → Happy → Impressed → Excited → Surprised → Delighted → Confident

---

## Example 2: Noise-Canceling Earbuds Demo

**Scenario:** Host tests new earbuds with guest, demonstrates noise canceling, whisper test

```text
Host: [excited] Willkommen zurück! [enthusiastic] Heute testen wir die NEUEN Noise-Canceling Earbuds!

Guest: [curious] Ooh, ich hab davon gehört. Wie gut sind die?

Host: [confident] Pass auf. [whispers] Kannst du mich hören?

Guest: [amazed] [gasps] Kristallklar! Sogar beim Flüstern?

Host: [delighted] [giggles] Und sie blockieren 99% Hintergrundgeräusche!

Guest: [impressed] Das ist WAHNSINN! [excited] Wo krieg ich die?

Host: [cheerfully] Link in der Beschreibung! [playful] Gern geschehen!
```

**Duration:** ~25 seconds  
**Key hooks:** Product announcement → Whisper demo → Noise blocking stat → CTA  
**Action cues:** `[whispers]`, `[gasps]`, `[giggles]` for dramatic effect

---

## Example 3: Air Fryer Kitchen Discovery

**Scenario:** Roommate asks about air fryer, owner demonstrates, reveals price surprise

```text
Roommate: [curious] Was ist das für ein Gerät? Sieht modern aus!

Owner: [proud] Meine neue Air Fryer! [confident] 8 Liter Kapazität.

Roommate: [interested] Acht Liter? Das ist riesig!

Owner: [excited] Und schau mal— [demonstrates] knusprige Pommes in 15 Minuten!

Roommate: [impressed] [gasps] So schnell? Wie teuer war die?

Owner: [playful] Rate mal! [pauses] ...nur 79 Euro!

Roommate: [shocked] [excited] Was?! Das ist ja SUPER günstig!

Owner: [enthusiastic] TikTok Shop! [confident] Link ist unten!
```

**Duration:** ~30 seconds  
**Key hooks:** Visual curiosity → Size reveal → Speed demo → Price shock → CTA  
**Timing:** Uses ellipses `...` for dramatic pause before price

---

## Example 4: LED Mirror Makeup Tutorial

**Scenario:** Friend interrupts makeup tutorial, asks about mirror lighting, buys immediately

```text
Creator: [focused] Also, für diesen Look brauchst du gutes Licht—

Friend: [jumping in] Moment! [curious] Ist das ein LED-Spiegel?

Creator: [cheerfully] Ja! [excited] Drei Lichtmodi: Tageslicht, warm, kalt.

Friend: [impressed] Das erklärt, warum dein Make-up immer perfekt sitzt!

Creator: [giggles] [confident] Und dimmbar! Von 10% bis 100%.

Friend: [delighted] Ich MUSS den haben! Wo gibt's den?

Creator: [enthusiastic] TikTok Shop! [playful] Ich schick dir den Link!
```

**Duration:** ~25 seconds  
**Key hooks:** Interruption (natural conversation) → Feature reveal → Compliment → Dimming feature → CTA  
**Interruption technique:** `[jumping in]` creates authentic dialogue flow

---

## Example 5: Massage Gun Gym Conversation

**Scenario:** Gym buddy asks about recovery tool, demonstrates on sore muscles, immediate relief

```text
GymBuddy: [tired] [sighs] Meine Beine sind total fertig vom Training...

User: [helpful] Probier mal das! [confident] Massage Gun, 20 Stufen.

GymBuddy: [skeptical] Massage Gun? Hilft das wirklich?

User: [demonstrates] Schau— [turns on device] fang mit Stufe 5 an.

GymBuddy: [relieved] [exhales] Oh wow... [impressed] das fühlt sich GUT an!

User: [enthusiastic] Und der Akku hält 6 Stunden! [playful] Perfekt fürs Gym!

GymBuddy: [excited] Ich bestell mir JETZT eine! Wo?

User: [confident] TikTok Shop! [cheerfully] Link ist unten!
```

**Duration:** ~30 seconds  
**Key hooks:** Pain point (sore muscles) → Solution offer → Skepticism → Demonstration → Instant relief → CTA  
**Physical demo:** `[demonstrates]`, `[turns on device]` for immersive experience

---

## Example 6: Portable Blender Office Smoothie

**Scenario:** Coworker asks about desk blender, demonstrates one-button operation, noise surprise

```text
Coworker: [curious] Du machst Smoothies IM Büro?

User: [proud] Ja! [enthusiastic] Tragbarer Mixer, USB-C Aufladung!

Coworker: [impressed] USB-C? Das ist praktisch!

User: [confident] Pass auf— [presses button] ein Knopf, 40 Sekunden.

Coworker: [amazed] Das ist ja leise! [surprised] Ich dachte, das wäre lauter!

User: [giggles] [reassured] Nur 60 Dezibel! Stört niemanden.

Coworker: [delighted] Perfekt fürs Büro! Wo gekauft?

User: [cheerfully] TikTok Shop! [enthusiastic] Super günstig!
```

**Duration:** ~30 seconds  
**Key hooks:** Unusual location (office) → Feature reveal → Demo → Noise surprise → CTA  
**Action cues:** `[presses button]` creates engagement

---

## Example 7: Smart Lamp Reading Session

**Scenario:** Partner asks about bedside light, demonstrates color modes, reveals app control

```text
Partner: [sleepy] [yawns] Kannst du das Licht dimmen?

User: [softly] Klar— [adjusts light] schau mal, 16 Millionen Farben!

Partner: [surprised] Was?! [curious] Wie funktioniert das?

User: [demonstrates] App-Steuerung! [confident] Farbe, Helligkeit, Zeitplan...

Partner: [impressed] Du kannst einen Zeitplan einstellen?

User: [enthusiastic] Ja! [playful] Weckfunktion mit Sonnenaufgang-Simulation!

Partner: [delighted] [giggles] Das ist ja genial! Wo kaufen?

User: [whispers] TikTok Shop... [cheerfully] ich zeig's dir morgen!
```

**Duration:** ~30 seconds  
**Key hooks:** Practical need (dimming) → Color reveal → App demo → Schedule feature → Wake-up simulation → CTA  
**Mood matching:** `[softly]`, `[whispers]` matches bedtime setting

---

## Technical Notes

### Tag Placement Options

**Before dialogue:**
```text
Creator: [excited] Das ist UNGLAUBLICH!
```

**After dialogue:**
```text
Creator: Das ist UNGLAUBLICH! [laughs]
```

**Mid-sentence at natural pause:**
```text
Creator: Das ist, [sighs] wie soll ich sagen... PERFEKT!
```

### Interruption Techniques

**Em-dash for cutoff:**
```text
Speaker 1: [starting to speak] Ich wollte gerade—

Speaker 2: [jumping in] —sagen, dass ich das auch will!
```

**Ellipses for trailing off:**
```text
Customer: [indecisive] Ich bin mir nicht sicher...

Creator: [reassured] Kein Problem! 30 Tage Rückgaberecht!
```

**Overlapping (mark explicitly):**
```text
Speaker 1: [overlapping] Das ist doch—

Speaker 2: [overlapping] —genau was ich meinte!
```

---

## Voice Assignment Strategy

**For UGC TikTok Ads:**

### Voice Selection
- **Customer/Guest:** Neutral, curious tone (use Natural stability)
- **Creator/Host:** Expressive, enthusiastic tone (use Creative stability)
- Choose voices from [ElevenLabs V3 Voice Library](https://elevenlabs.io/app/voice-library/collections/aF6JALq9R6tXwCczjhKH)

### Stability Settings
- **Creative:** More emotional, prone to hallucinations (use for Creator)
- **Natural:** Balanced, closest to original (use for Customer)
- **Robust:** Highly stable, less responsive to tags (avoid for UGC)

### Voice Contrast Tips
- Use different genders for clear distinction
- Choose voices with distinct tonal characteristics
- Match voice character to role (neutral vs. expressive)

---

## Common Mistakes to Avoid

❌ **Missing emotion tags:**
```text
Customer: Ist das teuer?  # NO emotion tag
```

✅ **Correct:**
```text
Customer: [curious] Ist das teuer?
```

---

❌ **No speaker labels:**
```text
[curious] Ist das teuer?  # Missing "Customer:"
```

✅ **Correct:**
```text
Customer: [curious] Ist das teuer?
```

---

❌ **Contradictory tags:**
```text
Creator: [whispers] [shouting] Das ist laut!  # Conflicting emotions
```

✅ **Correct:**
```text
Creator: [excited] [shouting] Das ist LAUT!
```

---

❌ **Too many tags:**
```text
Creator: [excited] [happy] [enthusiastic] [delighted] Check this out!
```

✅ **Correct:**
```text
Creator: [excited] [giggles] Check this out!
```

---

## Duration Guidelines

**For UGC TikTok Ads:**
- **30-40 seconds:** Sweet spot for engagement
- **~100-130 words:** Achieves 40s at fast-paced delivery
- **~75-100 words:** Achieves 30s at fast-paced delivery

**Word count per role:**
- Customer: ~3-5 lines (20-30 words)
- Creator: ~5-7 lines (60-90 words)
- Total: ~8-12 lines for 30-40s ad

---

## API Implementation

### Text-to-Dialogue API Request Format

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key="YOUR_API_KEY")

dialogue_text = """
Customer: [curious] Entschuldigung, ist die teuer?

Creator: [reassured] Nicht wirklich. Gutes Design, solide gebaut, super Preis.

Customer: [interested] Wo kann man die kaufen?

Creator: [enthusiastic] Im TikTok Shop. Einfach Link klicken!
"""

# Assign voices to speakers
voices = {
    "Customer": "voice_id_1",  # Neutral female voice
    "Creator": "voice_id_2"    # Expressive male voice
}

# Generate audio
audio = client.text_to_dialogue.convert(
    text=dialogue_text,
    model_id="eleven_v3",
    voices=voices,
    output_format="mp3_44100_128"
)

# Save to file
with open("dialogue.mp3", "wb") as f:
    f.write(audio)
```

### Multiple Generations (Non-Deterministic)

Text-to-Dialogue is **not deterministic**. Generate 2-3 versions and select best:

```python
# Generate 3 versions
for i in range(3):
    audio = client.text_to_dialogue.convert(
        text=dialogue_text,
        model_id="eleven_v3",
        voices=voices
    )
    with open(f"dialogue_v{i+1}.mp3", "wb") as f:
        f.write(audio)

# Listen to all 3, pick the best one for production
```

---

## Workflow Integration

**When to use multi-speaker dialogue in TikTok scripts:**

1. **Product Discovery Scenarios:**
   - Coffee shop / gym / office / home
   - Stranger asks about product
   - Creator demonstrates features
   - CTA at end

2. **Before-After Testimonials:**
   - Friend skeptical at first
   - Creator shows results
   - Friend convinced
   - Both recommend product

3. **Comparison Dialogues:**
   - Customer asks "which one is better?"
   - Creator explains differences
   - Customer chooses
   - CTA for TikTok Shop link

**NOT recommended for:**
- Solo product demonstrations (use single speaker)
- Narrative storytelling (use single speaker with emotion shifts)
- Technical tutorials (use single speaker)

---

## Quality Checklist

Before sending dialogue to ElevenLabs API:

- [ ] Every line has speaker label (`Customer:`, `Creator:`)
- [ ] Every line has 1-2 emotion/action tags
- [ ] Total duration ~30-40 seconds (test word count)
- [ ] Emotion arc flows naturally (Curious → Excited → Delighted)
- [ ] CTA included at end
- [ ] No conflicting emotion tags on same line
- [ ] Interruptions/overlaps marked with `—` or `[overlapping]`
- [ ] Voice assignments planned (neutral vs. expressive)

---

## ⚠️ Production Reminder

**As of February 2026:**

✅ **USE THIS:** Single-speaker format with visual markers  
❌ **DON'T USE:** Multi-speaker format (not functional yet)

**When multi-speaker becomes available:**
1. Monitor ElevenLabs changelog/announcements
2. Test with simple dialogue first
3. Verify voice switching works correctly
4. Then adopt for production workflows

**For now:** Use the single-speaker workaround shown at the top of this file.

---

**Version:** 1.1.0  
**Last Updated:** 2026-02-07  
**Author:** Claude (based on official ElevenLabs v3 documentation)  
**Status:** REFERENCE ONLY - Feature not yet functional
