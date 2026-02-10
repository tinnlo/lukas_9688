# TikTok Product Link Resolver - Setup & Usage Guide

## Overview

The **TikTok Product Link Resolver** is a new pre-skill that extracts product IDs from TikTok product links. This is especially useful for shortened links (vm.tiktok.com) and mobile-only links that block desktop browsers.

### Problem It Solves

TikTok product links come in various formats:
- **Shortened links**: `https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/`
- **Direct shop links**: `https://www.tiktok.com/view/product/1729491166267284154`
- **Mobile-only links**: Desktop browsers get blocked with app installation prompts

This tool uses a mobile user agent to bypass desktop blocking and extracts the product ID from the redirect chain.

---

## What Was Built

### 1. Core Module: `scripts/link_resolver/`

```
link_resolver/
├── __init__.py          # Package exports
├── models.py            # Data models (LinkResolverConfig, ResolvedProduct)
├── resolver.py          # Core resolver implementation
└── README.md            # Technical documentation
```

**Key Features:**
- Mobile user agent to bypass desktop blocking
- Multiple regex patterns for product ID extraction
- Redirect chain tracking
- Batch processing support

### 2. CLI Tool: `scripts/resolve_product_link.py`

Command-line interface for resolving links:

```bash
# Single link
python3 resolve_product_link.py --url "https://vm.tiktok.com/..."

# Batch from file
python3 resolve_product_link.py --links-file links.txt --output products.csv
```

**Outputs:**
- CSV format: Product IDs ready for scraper
- JSON format: Detailed results with redirect chains
- Rich terminal UI with tables and progress bars

### 3. Skill Definition: `.claude/skills/tiktok_link_resolver/`

Claude Code skill for easy invocation:

```bash
/tiktok-link-resolver
```

### 4. Documentation

- `scripts/link_resolver/README.md` - Technical module documentation
- `.claude/skills/tiktok_link_resolver/skill.md` - Skill usage guide
- `scripts/README.md` - Updated with link resolver section
- `scripts/examples/links.txt` - Example links file

---

## Quick Start

### Test with Sample Link

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts

# Resolve the sample link
python3 resolve_product_link.py --url "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/"
```

**Expected Output:**
```
✅ Product ID: 1729491166267284154
```

### Batch Processing Workflow

**1. Create links file:**

```bash
cat > my_links.txt << EOF
https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/
https://vm.tiktok.com/ZG9abc123def456/
EOF
```

**2. Resolve links:**

```bash
python3 resolve_product_link.py \
  --links-file my_links.txt \
  --output products.csv
```

**3. Feed into product scraper:**

```bash
DATE=$(date +%Y%m%d)

python3 run_scraper.py \
  --batch-file products.csv \
  --download-videos \
  --output-dir "../product_list/$DATE"
```

---

## Usage Examples

### Example 1: Single Link with Visible Browser

```bash
# See the browser in action
python3 resolve_product_link.py \
  --url "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/" \
  --headed
```

### Example 2: Batch with JSON Output (Debugging)

```bash
# Get detailed results including redirect chains
python3 resolve_product_link.py \
  --links-file links.txt \
  --output results.json \
  --format json
```

**JSON includes:**
- Original URL
- Resolved product ID
- Final redirect URL
- Full redirect chain
- Success status and error messages

### Example 3: Custom Timeout

```bash
# Increase timeout for slow connections
python3 resolve_product_link.py \
  --url "..." \
  --timeout 30000  # 30 seconds
```

---

## Integration Points

### With Product Scraper

The link resolver outputs CSV files that can be directly used with `run_scraper.py`:

```bash
# Complete workflow
python3 resolve_product_link.py --links-file links.txt --output products.csv
python3 run_scraper.py --batch-file products.csv --download-videos
```

### With n8n Workflow

Add a new node before the product scraper:

**Node: Resolve Product Links**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts && \
python3 resolve_product_link.py \
  --links-file {{$json.links_file}} \
  --output products.csv
```

**Output:** `products.csv` → Feed to product scraper node

### With Claude Code Skills

```bash
# Use the skill
/tiktok-link-resolver

# Follow prompts to resolve links
```

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
   - Extracts product ID using regex patterns

3. **Product ID Patterns**
   ```regex
   /view/product/(\d{19})      # Primary pattern
   /product/(\d{19})            # Alternative
   ?product_id=(\d{19})         # Query parameter
   "product_id":"(\d{19})"      # JSON data
   ```

4. **Timeout Handling**
   - Uses `domcontentloaded` instead of `networkidle`
   - Product ID often captured from redirects before full page load
   - Graceful handling of timeouts

### Mobile User Agent

```
Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)
AppleWebKit/605.1.15 (KHTML, like Gecko)
Version/16.6 Mobile/15E148 Safari/604.1
```

### Performance

- **Single link**: ~2-5 seconds
- **Batch (10 links)**: ~20-50 seconds
- Network dependent

---

## Testing Results

### Tested Sample Link

**Input:**
```
https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/
```

**Redirect Chain:**
```
1. https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/
2. https://www.tiktok.com/view/product/1729491166267284154?...
```

**Output:**
```
Product ID: 1729491166267284154
```

**Status:** ✅ Successful

### CSV Output Format

```csv
product_id
1729491166267284154
```

This format is identical to the existing `products.csv` used by the product scraper.

---

## Troubleshooting

### Issue: "Product ID not found"

**Causes:**
- Link doesn't point to a product
- TikTok changed their URL format

**Solutions:**
1. Verify the link manually in a mobile browser
2. Run with `--headed` to see browser behavior
3. Check logs with `--log-level DEBUG`

### Issue: "Timeout exceeded"

**Causes:**
- Slow network or page loading issues

**Solutions:**
- Product ID is usually captured from redirects anyway (check result)
- Increase timeout: `--timeout 30000`
- Run with `--headed` to see what's happening

### Issue: Browser fails to launch

**Cause:** Playwright browsers not installed

**Solution:**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
playwright install chromium
```

---

## Workflow Diagram

```
┌─────────────────────────┐
│   TikTok Product Links  │
│  (vm.tiktok.com, etc.)  │
└───────────┬─────────────┘
            │
            ▼
    ┌───────────────────┐
    │  Link Resolver    │
    │  (Pre-Step 0)     │
    └─────────┬─────────┘
              │
              ▼ products.csv
    ┌───────────────────┐
    │  Product Scraper  │
    │  (Step 1)         │
    └─────────┬─────────┘
              │
              ▼ tabcut_data.json + videos
    ┌───────────────────┐
    │  Ad Analysis      │
    │  (Step 2)         │
    └─────────┬─────────┘
              │
              ▼ analysis.md files
    ┌───────────────────┐
    │ Script Generator  │
    │  (Step 3)         │
    └─────────┬─────────┘
              │
              ▼ TikTok Scripts
```

---

## Files Structure

```
scripts/
├── resolve_product_link.py       # CLI tool (NEW)
├── link_resolver/                # Module (NEW)
│   ├── __init__.py
│   ├── models.py
│   ├── resolver.py
│   └── README.md
├── examples/                     # Example files (NEW)
│   └── links.txt
├── run_scraper.py               # Existing product scraper
├── tabcut_scraper/              # Existing
├── fastmoss_scraper/            # Existing
└── README.md                    # Updated with link resolver

.claude/skills/
└── tiktok_link_resolver/         # Skill definition (NEW)
    └── skill.md
```

---

## Next Steps

### 1. Test with Your Links

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts

# Add your links to the example file
nano examples/links.txt

# Resolve them
python3 resolve_product_link.py \
  --links-file examples/links.txt \
  --output products.csv
```

### 2. Integrate with Existing Workflow

Use the generated `products.csv` with your existing scraper:

```bash
python3 run_scraper.py \
  --batch-file products.csv \
  --download-videos \
  --output-dir "../product_list/$(date +%Y%m%d)"
```

### 3. Update n8n Workflow (Optional)

Add the link resolver as a new node before the product scraper node.

---

## Support

- **Module Documentation**: `scripts/link_resolver/README.md`
- **Skill Documentation**: `.claude/skills/tiktok_link_resolver/skill.md`
- **Main README**: `scripts/README.md`
- **Sample Links**: `scripts/examples/links.txt`

---

## Version

**v1.0.0** (2025-02-10)
- Initial release
- Mobile user agent support
- Batch processing
- CSV and JSON output formats
