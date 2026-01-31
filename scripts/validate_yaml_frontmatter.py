#!/usr/bin/env python3
"""
YAML Frontmatter Validator

Validates all product_index.md files for YAML parsing errors.
Reports files with issues and suggests fixes.

Usage:
    python validate_yaml_frontmatter.py           # Check all files
    python validate_yaml_frontmatter.py --fix     # Regenerate broken files
"""

import argparse
import sys
from pathlib import Path
import yaml

# Project root
REPO_ROOT = Path(__file__).parent.parent
PRODUCT_LIST_DIR = REPO_ROOT / "product_list"


def extract_frontmatter(file_path: Path) -> tuple[str, bool]:
    """
    Extract YAML frontmatter from markdown file.

    Args:
        file_path: Path to .md file

    Returns:
        Tuple of (frontmatter_text, success)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find frontmatter between --- delimiters
        parts = content.split('---', 2)
        if len(parts) < 3:
            return ("", False)

        # parts[1] is the frontmatter content
        return (parts[1].strip(), True)

    except Exception as e:
        return (f"File read error: {e}", False)


def validate_yaml(yaml_text: str) -> tuple[bool, str, dict]:
    """
    Validate YAML text.

    Args:
        yaml_text: YAML content to validate

    Returns:
        Tuple of (is_valid, error_message, parsed_data)
    """
    if not yaml_text:
        return (False, "Empty frontmatter", None)

    try:
        data = yaml.safe_load(yaml_text)
        if data is None:
            return (False, "Parsed as null/empty", None)
        return (True, "", data)
    except yaml.YAMLError as e:
        return (False, str(e), None)
    except Exception as e:
        return (False, f"Unexpected error: {e}", None)


def check_common_issues(file_path: Path, yaml_text: str, parsed_data: dict) -> list[str]:
    """
    Check for common YAML issues even if parsing succeeded.

    Args:
        file_path: Path to file
        yaml_text: Raw YAML text
        parsed_data: Parsed YAML data

    Returns:
        List of warning messages
    """
    warnings = []

    # Check for empty lines in frontmatter
    if '\n\n' in yaml_text:
        warnings.append("Empty lines in frontmatter (may cause issues)")

    # Check for unescaped quotes in original (heuristic)
    if parsed_data:
        for key in ['product_name', 'shop_owner', 'top_video_creator']:
            if key in parsed_data:
                value = str(parsed_data[key])
                # If value contains quotes, check if they were properly escaped in source
                if '"' in value:
                    # Look for the field in raw YAML
                    field_pattern = f'{key}: "'
                    if field_pattern in yaml_text:
                        # Extract the quoted value from raw YAML
                        start = yaml_text.find(field_pattern) + len(field_pattern)
                        end = yaml_text.find('"', start)
                        if end > start:
                            raw_value = yaml_text[start:end]
                            # Check if quotes are properly escaped
                            if '""' in raw_value:
                                warnings.append(
                                    f"{key} uses CSV-style quote escaping (\"\") instead of YAML (\\\")"
                                )

    # Check for very long lines (>1024 chars)
    for line_num, line in enumerate(yaml_text.split('\n'), 1):
        if len(line) > 1024:
            warnings.append(f"Line {line_num} exceeds 1024 characters ({len(line)} chars)")

    return warnings


def validate_file(file_path: Path) -> dict:
    """
    Validate a single product_index.md file.

    Args:
        file_path: Path to product_index.md

    Returns:
        Dict with validation results
    """
    result = {
        'file': str(file_path.relative_to(REPO_ROOT)),
        'valid': False,
        'error': None,
        'warnings': []
    }

    # Extract frontmatter
    frontmatter, success = extract_frontmatter(file_path)
    if not success:
        result['error'] = frontmatter  # Error message
        return result

    # Validate YAML
    is_valid, error_msg, parsed_data = validate_yaml(frontmatter)
    result['valid'] = is_valid
    result['error'] = error_msg if not is_valid else None

    # Check for common issues
    if is_valid:
        warnings = check_common_issues(file_path, frontmatter, parsed_data)
        result['warnings'] = warnings

    return result


def find_product_index_files() -> list[Path]:
    """
    Find all product_index.md files.

    Returns:
        List of Path objects
    """
    return sorted(PRODUCT_LIST_DIR.glob("*/*/product_index.md"))


def main():
    parser = argparse.ArgumentParser(
        description='Validate YAML frontmatter in product_index.md files'
    )
    parser.add_argument('--fix', action='store_true',
                       help='Regenerate broken files using generate_product_indices.py')
    args = parser.parse_args()

    print("=" * 70)
    print("YAML Frontmatter Validator")
    print("=" * 70)

    # Find all files
    files = find_product_index_files()
    print(f"\nFound {len(files)} product_index.md file(s)\n")

    if not files:
        print("No files to validate")
        return

    # Validate each file
    results = []
    for i, file_path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Validating {file_path.name}...", end=' ')
        result = validate_file(file_path)
        results.append(result)

        if result['valid']:
            if result['warnings']:
                print(f"⚠ Valid with warnings")
                for warning in result['warnings']:
                    print(f"    ⚠  {warning}")
            else:
                print("✓")
        else:
            print(f"✗ {result['error']}")

    # Summary
    valid_count = sum(1 for r in results if r['valid'])
    invalid_count = len(results) - valid_count
    warning_count = sum(len(r['warnings']) for r in results)

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total files: {len(results)}")
    print(f"✓ Valid: {valid_count}")
    print(f"✗ Invalid: {invalid_count}")
    print(f"⚠  Warnings: {warning_count}")

    # Show invalid files
    if invalid_count > 0:
        print("\nInvalid Files:")
        for result in results:
            if not result['valid']:
                print(f"  ✗ {result['file']}")
                print(f"     Error: {result['error']}")

        if args.fix:
            print("\n" + "=" * 70)
            print("Regenerating broken files...")
            print("=" * 70)

            # Extract product IDs from broken files
            broken_products = []
            for result in results:
                if not result['valid']:
                    # Extract product ID from path: product_list/DATE/PRODUCT_ID/product_index.md
                    parts = Path(result['file']).parts
                    if len(parts) >= 3:
                        product_id = parts[-2]
                        broken_products.append(product_id)

            if broken_products:
                import subprocess
                for product_id in broken_products:
                    print(f"\nRegenerating {product_id}...")
                    cmd = [
                        'python3',
                        str(REPO_ROOT / 'scripts' / 'generate_product_indices.py'),
                        '--product-id', product_id,
                        '--force'
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"  ✓ Successfully regenerated")
                    else:
                        print(f"  ✗ Regeneration failed:")
                        print(f"     {result.stderr}")
            else:
                print("No product IDs could be extracted from broken files")

    # Exit code
    sys.exit(0 if invalid_count == 0 else 1)


if __name__ == '__main__':
    main()
