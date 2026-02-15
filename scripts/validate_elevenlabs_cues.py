#!/usr/bin/env python3
"""
Validator for ElevenLabs v3 cue density and variety in script files (ALIGNED v2.5).

ALIGNED WITH:
- .claude/skills/tiktok_script_generator/SKILL.md
- .claude/skills/tiktok_script_generator/templates/voiceover_format.md
- doc/ElevenLabs_v3_Alpha_VO_Grammar_Practice.md

NEW RULES (v2.5):
- MANDATORY: 1-2 EMOTION cues per line (every line must have emotion cues)
- OPTIONAL: 0-2 ACTION cues per script (not per line)
- Inline format only (no broken lines)
- NEVER stack emotion + action on same line

Checks:
- ElevenLabs v3 marker present
- EMOTION cue density ≥0.9 (every line must have at least 1 emotion cue)
- Unique emotion cues ≥8 (preferably 10+)
- No invalid cues (all from approved list)
- No excessive repetition of single cue (no emotion used >4 times)
- No stacked cues on same line (e.g., [excited] [gasps])
- Action cues: 0-5 per script (optional, not mandatory)

Usage:
    python3 validate_elevenlabs_cues.py <filepath>

Exit codes:
    0: All checks passed
    1: One or more checks failed
"""

import re
import sys
from pathlib import Path
from collections import Counter


# Approved EMOTION cues (mandatory, 1-2 per line)
APPROVED_EMOTION_CUES = {
    # Natural emotions (recommended for TikTok UGC)
    "curious",
    "interested",
    "confident",
    "impressed",
    "happy",
    "cheerfully",
    "excited",
    "warm",
    "warmly",
    "matter-of-fact",
    "reassured",
    "reassuring",
    "thoughtful",
    "surprised",
    "frustrated",
    "annoyed",
    "professional",
    # Intensity/delivery cues
    "soft",
    "neutral",
    "bright",
    "firm",
    "blunt",
    "understated",
    "casual",
    "casually",
    "direct",
    "emphatic",
    "persuasive",
    # Emotional states
    "amused",
    "reflective",
    "skeptical",
    "playful",
    "mischievously",
    "intrigued",
    "satisfied",
    "cheerful",
    "delighted",
    "proud",
    "amazed",
    "shocked",
    "enthusiastic",
    "sarcastic",
    "defiant",
    "sad",
    "angry",
    "cautiously",
    "quizzically",
    "indecisive",
    "sympathetic",
    "questioning",
    "nervously",
    "sheepishly",
    "deadpan",
    "exhausted",
}

# Approved ACTION cues (optional, 0-2 per script)
APPROVED_ACTION_CUES = {
    "laughs",
    "giggles",
    "chuckles",
    "sighs",
    "whispers",
    "whisper",
    "exhales",
    "inhales deeply",
    "clears throat",
    "gasps",
    "snorts",
    "starts laughing",
    "laughs harder",
    "cracking up",
    "wheezing",
    "exhales sharply",
    "swallows",
    "gulps",
    "crying",
}

# All approved cues combined
APPROVED_CUES = APPROVED_EMOTION_CUES | APPROVED_ACTION_CUES


def validate_elevenlabs_cues(filepath: str) -> dict:
    """
    Validate ElevenLabs v3 cue density and variety (ALIGNED v2.5).

    Args:
        filepath: Path to the script markdown file

    Returns:
        Dictionary with validation results:
        {
            "emotion_cues_total": int,
            "action_cues_total": int,
            "cues_unique": int,
            "emotion_density": float,
            "violations": list[str],
            "passed": bool
        }
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    violations = []

    # Check for ElevenLabs v3 marker
    if not re.search(r">\s*with ElevenLabs v3", content, re.I):
        violations.append("Missing ElevenLabs v3 marker")
        return {
            "emotion_cues_total": 0,
            "action_cues_total": 0,
            "cues_unique": 0,
            "emotion_density": 0.0,
            "violations": violations,
            "passed": False,
        }

    # Extract German voiceover section
    vo_section = re.search(
        r"### DE(?:\s+\(ElevenLabs Prompt|\s+\(中文翻译)?\s*\n(.*?)(?=\n###|\Z)",
        content,
        re.S | re.I,
    )
    if not vo_section:
        violations.append("No German voiceover section found")
        return {
            "emotion_cues_total": 0,
            "action_cues_total": 0,
            "cues_unique": 0,
            "emotion_density": 0.0,
            "violations": violations,
            "passed": False,
        }

    vo_text = vo_section.group(1)

    # Count lines and cues
    lines = [l for l in vo_text.split("\n") if l.strip() and not l.startswith("#")]
    all_cues = re.findall(r"\[(\w+(?:-\w+)?(?:\s+\w+)?)\]", vo_text)

    # Separate emotion and action cues
    emotion_cues = [c for c in all_cues if c in APPROVED_EMOTION_CUES]
    action_cues = [c for c in all_cues if c in APPROVED_ACTION_CUES]

    # Check for stacked cues on same line (FORBIDDEN)
    for line in lines:
        line_cues = re.findall(r"\[(\w+(?:-\w+)?(?:\s+\w+)?)\]", line)
        if len(line_cues) > 1:
            # Check if multiple cues before first sentence-ending punctuation
            # This catches [excited] [gasps] but allows [confident] ... text ... [laughs]
            first_punct = re.search(r"[.!?]", line)
            if first_punct:
                text_before_punct = line[: first_punct.start()]
                cues_before_punct = re.findall(
                    r"\[(\w+(?:-\w+)?(?:\s+\w+)?)\]", text_before_punct
                )
                if len(cues_before_punct) > 1:
                    violations.append(
                        f"Stacked cues forbidden: {' '.join(['[' + c + ']' for c in cues_before_punct])} on same line"
                    )
                    break

    # Validate cues against approved list
    invalid_cues = [c for c in all_cues if c not in APPROVED_CUES]
    if invalid_cues:
        unique_invalid = set(invalid_cues)
        violations.append(f"Invalid cues: {', '.join(unique_invalid)}")

    # Check EMOTION cue density (must be ≥0.9, meaning almost every line has emotion)
    emotion_density = len(emotion_cues) / len(lines) if lines else 0
    if emotion_density < 0.9:
        violations.append(
            f"Low emotion cue density: {emotion_density:.2f} (need ≥0.9, every line needs 1-2 emotion cues)"
        )

    # Check emotion variety
    unique_emotion_cues = len(set(emotion_cues))
    if unique_emotion_cues < 8:
        violations.append(
            f"Low emotion cue variety: {unique_emotion_cues} unique (need ≥8, ideally 10+)"
        )

    # Check action cues (0-5 per script is acceptable)
    if len(action_cues) > 5:
        violations.append(
            f"Too many action cues: {len(action_cues)} (recommended 0-2 per script, max 5)"
        )

    # Check repetition of single emotion cue
    emotion_counts = Counter(emotion_cues)
    excessive = [f"{c}({n}x)" for c, n in emotion_counts.items() if n > 4]
    if excessive:
        violations.append(f"Excessive repetition: {', '.join(excessive)}")

    return {
        "emotion_cues_total": len(emotion_cues),
        "action_cues_total": len(action_cues),
        "cues_unique": len(set(all_cues)),
        "emotion_density": emotion_density,
        "violations": violations,
        "passed": len(violations) == 0,
    }


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) != 2:
        print("Usage: python3 validate_elevenlabs_cues.py <filepath>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    result = validate_elevenlabs_cues(str(filepath))

    # Print results
    status = "✅ PASSED" if result["passed"] else "❌ FAILED"
    print(f"{status}: {filepath.name}")
    print(f"  Emotion cues: {result['emotion_cues_total']}")
    print(f"  Action cues: {result['action_cues_total']} (optional)")
    print(f"  Unique cues: {result['cues_unique']}")
    print(f"  Emotion density: {result['emotion_density']:.2f}")

    if result["violations"]:
        print("\nIssues:")
        for v in result["violations"]:
            print(f"  ⚠️ {v}")

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
