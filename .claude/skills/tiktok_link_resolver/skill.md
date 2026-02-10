---
name: tiktok-link-resolver
description: Pre-skill for product scraper. Resolves TikTok product links (vm.tiktok.com shortened links) to extract product IDs. Handles mobile-only links that block desktop browsers.
version: 1.0.0
author: User
execution: Python CLI tool
---

# TikTok Link Resolver Skill (Pre-Step 0)

**WHO RUNS THIS:** Manual terminal or n8n workflow (before product scraper)
**PURPOSE:** Extract product IDs from TikTok product links
**INPUT:** TikTok product links (vm.tiktok.com shortened links, direct shop links)
**OUTPUT:** Product IDs (CSV or JSON) that can be fed into the product scraper
**NEXT STEP:** Step 1 - Product Scraper (tiktok_product_scraper)

---

## Core Script Lock (MANDATORY)

This skill is constrained by `.claude/skills/CORE_SCRIPTS.md`.

Execution baseline:
- Use system `python3` for all commands in this skill.
- `venv` activation examples are legacy and should not be required.

---

## Overview

This skill resolves TikTok product links to extract the numeric product IDs needed for the scraping workflow.

### Why This Skill Exists

TikTok product links come in various formats:
- **Shortened links**: `https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/`
- **Direct shop links**: `https://www.tiktok.com/view/product/1729491166267284154`
- **Mobile-only links**: Desktop browsers get blocked with app installation prompts

This skill uses a mobile user agent to bypass desktop blocking and extracts the product ID from the redirect chain.

### Features

- **Mobile user agent**: Bypasses desktop browser blocking
- **Multiple link formats**: Handles shortened, direct, and mobile-only links
- **Batch processing**: Resolve multiple links from a text file
- **CSV output**: Generates products.csv file for product scraper
- **JSON output**: Detailed results with redirect chains for debugging

---

## Prerequisites

✅ **Python 3.8+** (system `python3`)
✅ **Playwright browser** installed (`playwright install chromium`)
✅ **Dependencies installed** (`python3 -m pip install -r requirements.txt`)

**No authentication required** - this tool only follows public redirects.

---

## Quick Start

### Option A: Single Link Resolution

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts

# Resolve single link
python3 resolve_product_link.py --url "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/"

# Output:
# ✅ Successfully resolved product ID: 1729491166267284154
```

### Option B: Batch Links Resolution

**1. Create links file (`links.txt`):**
```txt
https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/
https://vm.tiktok.com/ZG9abc123def456/
https://www.tiktok.com/view/product/1729536030472509561
```

**2. Resolve all links and save to CSV:**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts

python3 resolve_product_link.py \
  --links-file links.txt \
  --output products.csv
```

**3. Use products.csv with product scraper:**
```bash
# Now feed into product scraper (Step 1)
python3 run_scraper.py \
  --batch-file products.csv \
  --download-videos \
  --output-dir "../product_list/YYYYMMDD"
```

---

## Usage Examples

### Single Link with Visible Browser

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts

python3 resolve_product_link.py \
  --url "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/" \
  --headed
```

### Batch with JSON Output (for debugging)

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts

python3 resolve_product_link.py \
  --links-file links.txt \
  --output results.json \
  --format json
```

**JSON output includes:**
- Original URL
- Resolved product ID
- Final redirect URL
- Full redirect chain
- Success status and error messages

### Custom Timeout

```bash
python3 resolve_product_link.py \
  --url "..." \
  --timeout 30000  # 30 seconds
```

---

## Output Structure

### CSV Output (Default)

**Format:**
```csv
product_id
1729491166267284154
1729536030472509561
1729542733703322446
```

**Usage:** Feed directly into `run_scraper.py --batch-file`

### JSON Output (Detailed)

**Format:**
```json
[
  {
    "original_url": "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/",
    "product_id": "1729491166267284154",
    "final_url": "https://www.tiktok.com/view/product/1729491166267284154?...",
    "redirect_chain": [
      "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/",
      "https://www.tiktok.com/view/product/1729491166267284154?..."
    ],
    "success": true,
    "error": null
  }
]
```

---

## n8n Workflow Integration

### Node: Resolve Product Links

**Command:**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts && \
python3 resolve_product_link.py \
  --links-file {{$json.links_file}} \
  --output products.csv
```

**Input:**
- `links_file`: Path to text file with TikTok links (one per line)

**Output:**
- `products.csv`: Product IDs ready for scraper

**Next Node:**
Feed `products.csv` into the product scraper skill.

---

## Technical Details

### How It Works

1. **Browser Setup**
   - Launches Chromium with mobile user agent
   - Viewport: iPhone dimensions (390x844)
   - Touch support enabled

2. **Link Resolution**
   - Navigates to the TikTok link
   - Captures all navigation redirects
   - Extracts product ID from redirect URLs using regex patterns

3. **Product ID Patterns**
   - `/view/product/{id}` (primary pattern)
   - `/product/{id}` (alternative)
   - `?product_id={id}` (query parameter)
   - JSON data attributes in page content

4. **Timeout Handling**
   - Uses `domcontentloaded` instead of `networkidle`
   - Product ID often captured from redirects before full page load
   - Graceful handling of timeouts (redirects are enough)

---

## Error Handling

### Common Issues

**Issue: "Product ID not found"**
- **Cause**: Link doesn't point to a product, or format changed
- **Solution**: Verify the link manually, check with `--headed` mode

**Issue: "Timeout exceeded"**
- **Cause**: Slow network or page loading issues
- **Solution**: Product ID is usually captured from redirects anyway
- **Alternative**: Increase timeout with `--timeout 30000`

**Issue: Browser fails to launch**
- **Cause**: Playwright browsers not installed
- **Solution**: Run `playwright install chromium`

---

## Workflow Integration

### Complete Workflow: Link → Scripts

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
DATE=YYYYMMDD

# Step 0: Resolve product links
python3 resolve_product_link.py \
  --links-file links.txt \
  --output products.csv

# Step 1: Scrape product data
python3 run_scraper.py \
  --batch-file products.csv \
  --download-videos \
  --output-dir "../product_list/$DATE"

# Step 2: Analyze videos (see tiktok_ad_analysis skill)
# Step 3: Generate scripts (see tiktok_script_generator skill)
```

---

## Quality Checklist

Before proceeding to product scraper:

- [ ] All links resolved successfully
- [ ] Product IDs are 19-digit numbers
- [ ] `products.csv` created with proper format
- [ ] Verified at least one product ID manually on TikTok

---

## Troubleshooting

### Verify Product ID Manually

```bash
# Check if product ID is valid (should redirect to product page)
open "https://www.tiktok.com/view/product/1729491166267284154"
```

### Debug Mode

```bash
# Run with DEBUG logging and visible browser
python3 resolve_product_link.py \
  --url "..." \
  --headed \
  --log-level DEBUG
```

### Test with Known Product

```bash
# Use a known working product link to test setup
python3 resolve_product_link.py \
  --url "https://www.tiktok.com/view/product/1729536030472509561"
```

---

## Next Step: Product Scraper (Step 1)

After resolving links:

1. **Review** `products.csv` - verify product IDs look correct
2. **Proceed to** `.skills/tiktok_product_scraper.md`
3. Run product scraper with the generated CSV

**Workflow:**
```
Step 0 (This skill) → products.csv
                    ↓
Step 1 (Product Scraper) → tabcut_data.json + videos
                    ↓
Step 2 (Ad Analysis) → video_analysis.md + image_analysis.md
                    ↓
Step 3 (Script Generator) → 3 TikTok scripts + Campaign_Summary.md
```

---

## Version History

**v1.0.0** (2025-02-10)
- Initial release
- Mobile user agent to bypass desktop blocking
- Batch processing support
- CSV and JSON output formats
- Regex-based product ID extraction from redirect chains
