#!/usr/bin/env python3
"""
Validator for compliance flags in analysis and script files.

Checks for risky claims and proper flagging:
- Analysis files: Risky claims must be flagged in compliance section
- Script files: Risky claims should not appear
- All files: Must cite specific evidence when flagging risks

Usage:
    python3 validate_compliance_flags.py <filepath>

Exit codes:
    0: All checks passed
    1: One or more violations found
"""

import re
import sys
from pathlib import Path


# Risky patterns to detect
RISKY_PATTERNS = {
    "price": [
        r'€\d+', r'\d+€', r'\d+\s*Euro(?:s?)', r'欧元',
        r'\d+%.*(?:Rabatt|Discount|折扣)'
    ],
    "waterproof": [
        r'100%.*wasserdicht', r'komplett wasserdicht',
        r'100%防水', r'完全防水'
    ],
    "medical": [
        r'Schmerz(?:linderung|freiheit)', r'heilt', r'behandelt',
        r'Therapeut', r'Physio(?:therapie)?', r'Tiefengewebe'
    ],
    "tech_ambiguous": [
        r'4K Support(?!\s+\()', r'零延迟', r'instant(?!ly)'
    ]
}


def validate_compliance_flags(filepath: str, is_analysis: bool = True) -> dict:
    """
    Validate compliance flags in the file.

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
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    violations = []

    # Check for risky patterns
    for risk_type, patterns in RISKY_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, content, re.I)
            if matches:
                if is_analysis:
                    # Check if flagged in compliance section
                    compliance_section = re.search(
                        r'##.*(?:Risk|Compliance).*\n(.*?)(?=\n##|\Z)',
                        content,
                        re.S | re.I
                    )
                    if not compliance_section:
                        violations.append(f"{risk_type}: '{matches[0]}' found but no Compliance section")
                    else:
                        # Check if the pattern or risk type is mentioned in compliance section
                        compliance_text = compliance_section.group(1).lower()
                        risk_mentioned = any([
                            matches[0].lower() in compliance_text,
                            risk_type.lower() in compliance_text,
                            pattern.lower().replace(r'\s+', ' ') in compliance_text
                        ])
                        if not risk_mentioned:
                            violations.append(f"{risk_type}: '{matches[0]}' not flagged in Compliance section")
                else:
                    # Scripts should NOT contain risky claims
                    violations.append(f"{risk_type}: '{matches[0]}' appears in final script")

    # For analysis files, check that compliance section exists
    if is_analysis:
        if not re.search(r'##.*(?:Risk|Compliance)', content, re.I):
            violations.append("Missing Compliance/Risk section in analysis file")

    return {
        "violations": violations,
        "passed": len(violations) == 0
    }


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
    status = "✅ PASSED" if result['passed'] else "❌ FAILED"
    print(f"{status} ({file_type}): {filepath.name}")

    if result['violations']:
        print("\nViolations found:")
        for v in result['violations']:
            print(f"  ⚠️ {v}")
    else:
        print("  No compliance violations detected")

    sys.exit(0 if result['passed'] else 1)


if __name__ == "__main__":
    main()
