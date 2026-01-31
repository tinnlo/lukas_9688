# YAML Frontmatter Hardening - Potential Issues & Fixes

## Summary

Based on `scripts/fix_yaml_frontmatter.sh` analysis and TikTok product data patterns, here are all potential YAML frontmatter issues and their fixes.

---

## Issues Identified & Fixed

### ✅ 1. Empty Lines in Frontmatter (FIXED: scripts/fix_yaml_frontmatter.sh)

**Problem:** Empty lines between `---` delimiters break YAML parsing
```yaml
---
product_name: "Test"

total_sales: 100
---
```

**Fix:** `scripts/fix_yaml_frontmatter.sh` removes empty lines within YAML section

**Status:** ✅ Fixed by `scripts/fix_yaml_frontmatter.sh`

---

### ✅ 2. Unescaped Double Quotes (FIXED: generate_product_indices.py v2)

**Problem:** Product names with quotes break YAML parsing
```yaml
product_name: "Mini "Pro" Blender"  # ✗ Parse error
```

**Fix:** Backslash-escape quotes per YAML 1.2 spec
```yaml
product_name: "Mini \"Pro\" Blender"  # ✓ Correct
```

**Status:** ✅ Fixed in `generate_product_indices.py` (escape_yaml_string function)

**Common in TikTok data:**
- Product names: `Mini "Pro" Blender`
- Shop names: `Mike's "Best" Shop`
- URLs with query params containing quotes

---

### ✅ 3. Unescaped Backslashes (FIXED: generate_product_indices.py v2)

**Problem:** Windows paths or escaped characters
```yaml
cover: "product_list\20260104\product.webp"  # ✗ Interprets \2 as escape
```

**Fix:** Escape backslashes FIRST (before other escapes)
```yaml
cover: "product_list\\20260104\\product.webp"  # ✓ Correct
```

**Status:** ✅ Fixed in `generate_product_indices.py`

---

### ✅ 4. Newlines in Field Values (FIXED: generate_product_indices.py v2)

**Problem:** Literal newlines break single-line YAML values
```yaml
product_name: "Line1
Line2"  # ✗ Multi-line without proper syntax
```

**Fix:** Escape newlines as `\n`
```yaml
product_name: "Line1\nLine2"  # ✓ Correct
```

**Status:** ✅ Fixed in `generate_product_indices.py` (handles \n, \r, \t)

**Likelihood in TikTok data:** Low (rare but possible in scraped text)

---

## Additional Potential Issues (Not Currently Handled)

### ⚠️ 5. Colons in Unquoted Strings

**Problem:** Colons have special meaning in YAML (key-value separator)
```yaml
product_name: Product: Premium Edition  # ✗ Ambiguous parsing
```

**Fix:** Always quote strings with colons (already done in our code)
```yaml
product_name: "Product: Premium Edition"  # ✓ Correct
```

**Status:** ✅ Safe (we quote all string fields)

---

### ⚠️ 6. Leading/Trailing Whitespace

**Problem:** Whitespace affects YAML parsing
```yaml
product_name: " Product "  # May preserve or trim depending on parser
```

**Current behavior:** Preserved in double-quoted strings (correct)

**Recommendation:** No change needed unless we want to normalize whitespace

**Status:** ✅ Acceptable as-is

---

### ⚠️ 7. Very Long Lines (>1024 characters)

**Problem:** Some YAML parsers have line length limits

**Current risk:** URLs could be very long
- YouTube URLs: ~100 chars
- TikTok URLs with tracking: 200-500 chars
- Data URIs: Could exceed 1024 chars

**Fix options:**
1. Keep as-is (most modern parsers handle long lines)
2. Use YAML block scalars for URLs >500 chars
3. Truncate URLs (not recommended)

**Status:** ⚠️ Monitor (unlikely to be an issue with modern parsers)

---

### ⚠️ 8. Control Characters (ASCII 0-31)

**Problem:** Non-printable characters could break parsing

**Examples:**
- Null byte (`\0`)
- Bell (`\x07`)
- Backspace (`\x08`)

**Likelihood in TikTok data:** Very low (scraped text is usually clean)

**Fix:** Add control character stripping if needed
```python
def strip_control_chars(value: str) -> str:
    return ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
```

**Status:** ⚠️ Not implemented (add if issues arise)

---

### ⚠️ 9. Unicode Issues

**Problem:** Byte Order Mark (BOM), invalid UTF-8

**Current handling:** Python 3 handles UTF-8 correctly, write with `encoding='utf-8'`

**Status:** ✅ Safe (handled by Python 3 defaults)

---

### ⚠️ 10. YAML Reserved Words as Values

**Problem:** Unquoted boolean/null literals
```yaml
product_name: true   # ✗ Parsed as boolean, not string
product_name: null   # ✗ Parsed as null
product_name: yes    # ✗ Parsed as boolean in some parsers
```

**Fix:** Always quote string fields (already done)
```yaml
product_name: "true"   # ✓ String
product_name: "null"   # ✓ String
product_name: "yes"    # ✓ String
```

**Status:** ✅ Safe (we quote all string fields)

---

### ⚠️ 11. Hash/Pound Signs (#)

**Problem:** Unquoted `#` starts a comment
```yaml
product_name: Product #1  # ✗ Everything after # is a comment
```

**Fix:** Quote strings with `#` (already done)
```yaml
product_name: "Product #1"  # ✓ Correct
tags:
  - "#bestseller"           # ✓ Correct
```

**Status:** ✅ Safe (we quote all string fields)

---

### ⚠️ 12. Emojis and Special Unicode

**Problem:** Some parsers struggle with emojis

**Common in TikTok data:**
- Product names: `🔥 Hot Deal 💯`
- Shop names: `⭐ Premium Shop ⭐`

**Current handling:** UTF-8 encoding handles emojis correctly

**Status:** ✅ Safe (verified in tests)

---

## Testing Recommendations

### Test Data Generation

Create test cases for:
```python
edge_cases = [
    'Mini "Pro" Blender',           # Quotes
    'Path\\to\\file',                # Backslashes
    'Product: Premium',              # Colons
    'Tag #1',                        # Hash marks
    '🔥 Hot Deal 💯',                # Emojis
    'Product\nName',                 # Newlines
    'true',                          # YAML keywords
    'null',                          # YAML keywords
    'yes',                           # YAML keywords
    '  Product  ',                   # Leading/trailing spaces
    'Very ' + 'long ' * 200,        # Long strings
]
```

### Validation Script

Run on all generated `product_index.md` files:
```bash
#!/bin/bash
for file in product_list/*/*/product_index.md; do
    python3 -c "
import yaml
with open('$file', 'r') as f:
    content = f.read()
    frontmatter = content.split('---')[1]
    try:
        yaml.safe_load(frontmatter)
        print('✓ $file')
    except Exception as e:
        print('✗ $file: {e}')
        exit(1)
    "
done
```

---

## Current Protection Summary

| Issue | Protected | How |
|:------|:----------|:----|
| Empty lines in YAML | ✅ | `scripts/fix_yaml_frontmatter.sh` |
| Unescaped quotes | ✅ | Backslash escaping |
| Unescaped backslashes | ✅ | Double backslash |
| Newlines in values | ✅ | `\n` escaping |
| Tabs in values | ✅ | `\t` escaping |
| Carriage returns | ✅ | `\r` escaping |
| Colons in values | ✅ | Always quote strings |
| Hash marks | ✅ | Always quote strings |
| YAML keywords | ✅ | Always quote strings |
| Emojis/Unicode | ✅ | UTF-8 encoding |
| Control characters | ⚠️ | Not filtered (low risk) |
| Very long lines | ⚠️ | Not limited (acceptable) |

---

## Regeneration Required?

After fixing `escape_yaml_string()`, **all existing `product_index.md` files need regeneration** if they contain:
- Product names with quotes: `Mini "Pro" Blender`
- Paths with backslashes (Windows users)
- Any field with literal newlines

**Regeneration command:**
```bash
cd scripts
python3 generate_product_indices.py --force
```

**Or use fix script for YAML-specific issues:**
```bash
bash scripts/fix_yaml_frontmatter.sh
```

---

## Summary

**Critical fixes applied:**
1. ✅ Proper backslash escaping (YAML 1.2 compliant)
2. ✅ Quote escaping fixed (was using wrong method)
3. ✅ Newline/tab/CR escaping added
4. ✅ Empty line removal (existing script)

**Risk assessment:**
- High-risk issues: **All fixed**
- Medium-risk issues: **Handled**
- Low-risk issues: **Acceptable as-is**

**Recommendation:** Regenerate all `product_index.md` files with updated script.
