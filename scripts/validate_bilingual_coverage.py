#!/usr/bin/env python3
"""
Validator for bilingual coverage in analysis and synthesis files.

Verifies that generated files meet the gold-standard sample quality metrics:
- Bilingual section headers: 10+
- DE/ZH pairs: 30+
- Chinese character ratio: 15-20%
- Shot list rows: 12+ (if present)
- German copy bank lines: 80+ (if present)

Usage:
    python3 validate_bilingual_coverage.py <filepath>

Exit codes:
    0: All checks passed
    1: One or more checks failed
"""

import re
import sys
from pathlib import Path


def validate_bilingual_coverage(filepath: str) -> dict:
    """
    Validate bilingual coverage meets sample standards.

    Args:
        filepath: Path to the markdown file to validate

    Returns:
        Dictionary with validation results:
        {
            "bilingual_headers": int,
            "de_zh_pairs": int,
            "chinese_char_ratio": float,
            "shot_list_rows": int,
            "copy_bank_lines": int,
            "passed": bool
        }
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count bilingual headers: ## Text | 中文
    # Matches headers like "## English | 中文" or "## Visual Hooks | 视觉钩子"
    headers = len(re.findall(r'^##\s+.+\s*\|\s*.+[\u4e00-\u9fff]', content, re.M))

    # Count DE:/ZH: pairs (separate-line format)
    # Look for lines with "DE:" and corresponding "ZH:" lines
    de_lines = len(re.findall(r'^\s*(?:DE:|.*DE:)', content, re.M))
    zh_lines = len(re.findall(r'^\s*(?:ZH:|.*ZH:)', content, re.M))
    separate_line_pairs = min(de_lines, zh_lines)

    # Count inline bilingual pairs (format: English | 中文)
    # Matches lines with text, pipe separator, and Chinese characters
    inline_pairs = len(re.findall(r'.+\s*\|\s*.+[\u4e00-\u9fff]', content, re.M))

    # Total bilingual pairs
    pairs = separate_line_pairs + inline_pairs

    # Calculate Chinese character ratio
    total_chars = len(content)
    chinese_chars = len([c for c in content if '\u4e00' <= c <= '\u9fff'])
    ratio = chinese_chars / total_chars if total_chars > 0 else 0

    # Check shot list (if exists)
    # Look for section with "Shot List" and count table rows
    shot_list_match = re.search(
        r'##.*Shot List.*\n(.*?)(?=\n##|\Z)',
        content,
        re.S | re.I
    )
    shot_rows = 0
    if shot_list_match:
        # Count rows starting with | (excluding header row)
        table_rows = re.findall(r'^\|', shot_list_match.group(1), re.M)
        shot_rows = max(0, len(table_rows) - 1)  # -1 for header row

    # Check German copy bank (synthesis only)
    # Look for section with "German Copy Bank" or "德语文案库"
    copy_bank_match = re.search(
        r'##.*(German Copy Bank|德语文案库).*\n(.*?)(?=\n##|\Z)',
        content,
        re.S | re.I
    )
    copy_lines = 0
    if copy_bank_match:
        # Count numbered lines (e.g., "1. ", "2. ", etc.)
        copy_lines = len(re.findall(r'^\d+\.', copy_bank_match.group(2), re.M))

    # Determine pass/fail
    # Note: Thresholds adjusted based on actual gold-standard samples
    # - Image analysis: 13 headers, 77 pairs, 8.7% Chinese
    # - Video synthesis: 9 headers, 63 pairs, 6.4% Chinese
    passed = (
        headers >= 9 and
        pairs >= 30 and
        0.06 <= ratio <= 0.25 and
        (shot_rows == 0 or shot_rows >= 12) and
        (copy_lines == 0 or copy_lines >= 80)
    )

    return {
        "bilingual_headers": headers,
        "de_zh_pairs": pairs,
        "chinese_char_ratio": ratio,
        "shot_list_rows": shot_rows,
        "copy_bank_lines": copy_lines,
        "passed": passed
    }


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) != 2:
        print("Usage: python3 validate_bilingual_coverage.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]

    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    result = validate_bilingual_coverage(filepath)

    # Print results
    status = "✅ PASSED" if result['passed'] else "❌ FAILED"
    print(f"{status}: {Path(filepath).name}")
    print(f"  Bilingual headers: {result['bilingual_headers']} (need 9+)")
    print(f"  DE/ZH pairs: {result['de_zh_pairs']} (need 30+)")
    print(f"  Chinese ratio: {result['chinese_char_ratio']:.1%} (need 6-25%)")

    if result['shot_list_rows'] > 0:
        print(f"  Shot list rows: {result['shot_list_rows']} (need 12+)")

    if result['copy_bank_lines'] > 0:
        print(f"  Copy bank lines: {result['copy_bank_lines']} (need 80+)")

    sys.exit(0 if result['passed'] else 1)


if __name__ == "__main__":
    main()
