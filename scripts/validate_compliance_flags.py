#!/usr/bin/env python3
"""
Validator for compliance flags in analysis and script files.

Checks for risky claims and proper flagging:
- Analysis files: Risky claims must be flagged in compliance section
- Script files: Risky claims should not appear
- All files: Must cite specific evidence when flagging risks

TikTok Policies (DE Market):
1. No Exact Low Price Bait - Avoid specific € amounts with urgency/comparison
2. No Absolute Effect Claims - Avoid "100%", "pure", "perfect", "genauso gut"
3. No Exaggerated Promotions - Avoid "unbezahlbar", false urgency, superlatives

Usage:
    python3 validate_compliance_flags.py <filepath>

Exit codes:
    0: All checks passed
    1: One or more violations found
"""

import re
import sys
from pathlib import Path


# Risky patterns to detect - TikTok Policy Compliance v2.0
# Categories: Price Bait | Absolute Claims | Exaggerated Promotions

RISKY_PATTERNS = {
    # === 1. EXACT LOW PRICE BAIT (TikTok Policy) ===
    # Specific amounts with urgency/comparative framing
    "price": [
        r"€\d+",
        r"\d+€",
        r"\d+\s*Euro(?:s?)",
        r"欧元",
        r"\d+%.*(?:Rabatt|Discount|折扣)",
        r"(?:nur|nur noch|only)\s+(?:€|\d+\s*Euro)",  # "nur 9€"
        r"(?:statt|anstatt|instead of)\s+(?:€|\d+)",  # "statt 150€"
        r"(?:vs\.?|versus|gegenüber)\s+(?:€|\d+)",  # "vs. 150€"
        r"\d+\s*(?:€|Euro).*\b(?:statt|anstatt|vs)\b",  # "9€ statt 150€"
    ],
    # === 2. ABSOLUTE EFFECT CLAIMS (TikTok Policy) ===
    # "100%", "completely", "never", "always", "pure", "perfect"
    "absolute_claims": [
        r"100%.*wasserdicht",
        r"komplett wasserdicht",
        r"100%防水",
        r"完全防水",
        r"\b(?:rein|pure)\s+(?:Freude|Vergnügen|Spaß)",  # "pure Freude"
        r"\b(?:perfekt|perfektes|perfekte|ideal|beste)\s+(?:Geschenk|Lösung|Wahl)",  # "perfektes Geschenk"
        r"\bgenauso\s+(?:gut|stark|schnell|gut wie)",  # "genauso gut"
        r"\bbesser\s+(?:als|wie)\b",  # "besser als"
        r"\b(?:immer|nie|jederzeit|sofort|instant)\b",  # absolutes
        r"\b(?:vollständig|komplett|total|absolut)\b(?=\s+(?:schützt|hält|funktioniert|wirkt))",
    ],
    # === 3. EXAGGERATED PROMOTIONS (TikTok Policy) ===
    # Unverifiable claims, false urgency, superlatives without proof
    "exaggerated": [
        r"\bunbezahlbar\b",  # "unbezahlbar"
        r"\b(?:genial|unglaublich|wahnsinnig|irre)\b",  # hyperboles
        r"(?:bevor|bevor es|solange).*\b(?:weg|ausverkauft|vorbei)",  # "bevor es weg ist"
        r"\b(?:letzte|letzter|letztes)\s+(?:Chance|Möglichkeit|Tag|Stunde)",  # "letzte Chance"
        r"\b(?:nur noch|nur|limited)\s+\d+",  # "nur noch 3"
        r"\b(?:unbedingt|müssen Sie|darf nicht verpassen)",  # pressure language
    ],
    # === 4. MEDICAL CLAIMS (Existing - High Risk) ===
    "medical": [
        r"Schmerz(?:linderung|freiheit)",
        r"heilt",
        r"behandelt",
        r"Therapeut",
        r"Physio(?:therapie)?",
        r"Tiefengewebe",
        r"(?:治愈|治疗|止痛|疗效|医生推荐|医疗级)",  # Chinese medical
    ],
    # === 5. TECH SPECS AMBIGUITY (Existing) ===
    "tech_ambiguous": [
        r"4K Support(?!\s+\()",
        r"4K\s+Support",
        r"零延迟",
        r"keine\s+Verzögerung",  # "zero lag"
        r"instant(?!ly)",
        r"(?:sofort|instantan)\s+(?:ohne|kein)",
    ],
}


def validate_compliance_flags(filepath: str, is_analysis: bool = True) -> dict:
    """
    Validate TikTok policy compliance flags in the file.

    TikTok Policies:
    1. No Exact Low Price Bait - Avoid specific € + urgency/comparison
    2. No Absolute Effect Claims - Avoid "100%", "pure", "perfect", "genauso gut"
    3. No Exaggerated Promotions - Avoid "unbezahlbar", false urgency, superlatives

    Args:
        filepath: Path to the markdown file
        is_analysis: True if this is an analysis file, False if script file

    Returns:
        Dictionary with validation results:
        {
            "violations": list[str],
            "passed": bool
        }
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    violations = []

    # Check for risky patterns
    for risk_type, patterns in RISKY_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, content, re.I | re.MULTILINE)
            if matches:
                if is_analysis:
                    # Check if flagged in compliance section
                    compliance_section = re.search(
                        r"##.*(?:Risk|Compliance|Trust Signal).*\n(.*?)(?=\n##|\Z)",
                        content,
                        re.S | re.I,
                    )
                    if not compliance_section:
                        violations.append(
                            f"[{risk_type}] '{matches[0]}' found but no Compliance section"
                        )
                    else:
                        # Check if the pattern or risk type is mentioned in compliance section
                        compliance_text = compliance_section.group(1).lower()
                        risk_mentioned = any(
                            [
                                matches[0].lower() in compliance_text,
                                risk_type.lower().replace("_", " ") in compliance_text,
                                pattern.lower().replace(r"\s+", " ") in compliance_text,
                            ]
                        )
                        if not risk_mentioned:
                            violations.append(
                                f"[{risk_type}] '{matches[0]}' not flagged in Compliance section"
                            )
                else:
                    # Scripts should NOT contain risky claims
                    # Provide specific TikTok policy reference
                    policy_map = {
                        "price": "TikTok Policy: No Exact Low Price Bait",
                        "absolute_claims": "TikTok Policy: No Absolute Effect Claims",
                        "exaggerated": "TikTok Policy: No Exaggerated Promotions",
                        "medical": "High Risk: Medical Claims",
                        "tech_ambiguous": "Risk: Ambiguous Tech Specs",
                    }
                    policy = policy_map.get(risk_type, risk_type)
                    violations.append(f"[{policy}] '{matches[0]}' appears in script")

    # For analysis files, check that compliance section exists
    if is_analysis:
        if not re.search(r"##.*(?:Risk|Compliance|Trust Signal)", content, re.I):
            violations.append("Missing Compliance/Risk section in analysis file")

    return {"violations": violations, "passed": len(violations) == 0}


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) != 2:
        print("Usage: python3 validate_compliance_flags.py <filepath>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    # Determine if this is an analysis file or script file
    # Scripts are in "scripts/" subdirectory
    is_analysis = filepath.parent.name != "scripts"

    result = validate_compliance_flags(str(filepath), is_analysis)

    # Print results
    file_type = "Analysis" if is_analysis else "Script"
    status = "✅ PASSED" if result["passed"] else "❌ FAILED"
    print(f"{status} ({file_type}): {filepath.name}")

    if result["violations"]:
        print("\nViolations found:")
        for v in result["violations"]:
            print(f"  ⚠️ {v}")
    else:
        print("  No compliance violations detected")

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
