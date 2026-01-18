#!/usr/bin/env python3
"""
Validator for ElevenLabs v3 cue density and variety in script files.

Checks:
- ElevenLabs v3 marker present
- Cue density ≥0.3 (1 per 3 lines minimum)
- Unique cues ≥8 (preferably 10+)
- No invalid cues (all from approved list)
- No excessive repetition (no cue used >3 times)

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


# Approved cues from gold-standard sample (updated from actual usage)
APPROVED_CUES = {
    # Intensity cues
    'soft', 'neutral', 'bright', 'firm', 'blunt',
    # Emotional cues
    'warm', 'curious', 'amused', 'reflective', 'skeptical',
    'frustrated', 'exhausted', 'annoyed', 'playful', 'mischievously',
    'intrigued', 'satisfied', 'cheerful', 'delighted', 'proud',
    'surprised', 'amazed', 'shocked', 'enthusiastic', 'sarcastic',
    'defiant', 'impressed',
    # Delivery cues
    'matter-of-fact', 'understated', 'whisper', 'confident',
    'persuasive', 'emphatic', 'casual', 'casually', 'direct',
    # Action cues
    'sighs', 'giggles'
}


def validate_elevenlabs_cues(filepath: str) -> dict:
    """
    Validate ElevenLabs v3 cue density and variety.

    Args:
        filepath: Path to the script markdown file

    Returns:
        Dictionary with validation results:
        {
            "cues_total": int,
            "cues_unique": int,
            "density": float,
            "violations": list[str],
            "passed": bool
        }
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    violations = []

    # Check for ElevenLabs v3 marker
    if not re.search(r'>\s*with ElevenLabs v3', content, re.I):
        violations.append("Missing ElevenLabs v3 marker")
        return {
            "cues_total": 0,
            "cues_unique": 0,
            "density": 0.0,
            "violations": violations,
            "passed": False
        }

    # Extract German voiceover section
    vo_section = re.search(
        r'### DE \(ElevenLabs Prompt.*?\n(.*?)(?=\n###|\Z)',
        content,
        re.S | re.I
    )
    if not vo_section:
        violations.append("No German voiceover section found")
        return {
            "cues_total": 0,
            "cues_unique": 0,
            "density": 0.0,
            "violations": violations,
            "passed": False
        }

    vo_text = vo_section.group(1)

    # Count lines and cues
    lines = [l for l in vo_text.split('\n') if l.strip() and not l.startswith('#')]
    cues = re.findall(r'\[(\w+(?:-\w+)?)\]', vo_text)

    # Validate cues against approved list
    invalid_cues = [c for c in cues if c not in APPROVED_CUES]
    if invalid_cues:
        unique_invalid = set(invalid_cues)
        violations.append(f"Invalid cues: {', '.join(unique_invalid)}")

    # Check density
    density = len(cues) / len(lines) if lines else 0
    if density < 0.3:
        violations.append(
            f"Low cue density: {density:.2f} (need ≥0.3, ideally ≥0.5)"
        )

    # Check variety
    unique_cues = len(set(cues))
    if unique_cues < 8:
        violations.append(
            f"Low cue variety: {unique_cues} unique (need ≥8, ideally 10+)"
        )

    # Check repetition
    cue_counts = Counter(cues)
    excessive = [f"{c}({n}x)" for c, n in cue_counts.items() if n > 3]
    if excessive:
        violations.append(f"Excessive repetition: {', '.join(excessive)}")

    return {
        "cues_total": len(cues),
        "cues_unique": unique_cues,
        "density": density,
        "violations": violations,
        "passed": len(violations) == 0
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
    status = "✅ PASSED" if result['passed'] else "❌ FAILED"
    print(f"{status}: {filepath.name}")
    print(f"  Total cues: {result['cues_total']}")
    print(f"  Unique cues: {result['cues_unique']}")
    print(f"  Density: {result['density']:.2f}")

    if result['violations']:
        print("\nIssues:")
        for v in result['violations']:
            print(f"  ⚠️ {v}")

    sys.exit(0 if result['passed'] else 1)


if __name__ == "__main__":
    main()
