# TikTok Product Link Resolver

A Python module for resolving TikTok product links to extract numeric product IDs. Handles mobile-only shortened links (vm.tiktok.com) that block desktop browsers.

## Problem Statement

TikTok product links often come in shortened formats like `https://vm.tiktok.com/ZG9abc123/` which are mobile-only. Desktop browsers get blocked with app installation prompts. This module uses a mobile user agent to bypass the restriction and extract the product ID from the redirect chain.

## Features

- **Mobile User Agent**: Bypasses desktop browser blocking
- **Multiple Link Formats**: Handles vm.tiktok.com, direct shop links, etc.
- **Redirect Tracking**: Captures full redirect chain
- **Pattern Matching**: Multiple regex patterns for product ID extraction
- **Error Handling**: Graceful handling of timeouts and failures

## Installation

Dependencies are included in the parent `requirements.txt`.

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
python3 -m pip install -r requirements.txt
playwright install chromium
```

## Usage

### As a CLI Tool

See `resolve_product_link.py` in the parent directory:

```bash
# Single link
python3 resolve_product_link.py --url "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/"

# Multiple links from file
python3 resolve_product_link.py --links-file links.txt --output products.csv
```

### As a Python Module

```python
import asyncio
from link_resolver import LinkResolver, LinkResolverConfig

async def main():
    config = LinkResolverConfig(headless=True, timeout=15000)

    async with LinkResolver(config) as resolver:
        result = await resolver.resolve_link("https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/")

        if result.success:
            print(f"Product ID: {result.product_id}")
        else:
            print(f"Error: {result.error}")

asyncio.run(main())
```

### Batch Processing

```python
import asyncio
from link_resolver import LinkResolver, LinkResolverConfig

async def main():
    config = LinkResolverConfig(headless=True)

    urls = [
        "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/",
        "https://www.tiktok.com/view/product/1729536030472509561",
    ]

    async with LinkResolver(config) as resolver:
        results = await resolver.resolve_multiple_links(urls)

        for result in results:
            if result.success:
                print(f"{result.original_url} → {result.product_id}")
            else:
                print(f"{result.original_url} → ERROR: {result.error}")

asyncio.run(main())
```

## Architecture

### Module Structure

```
link_resolver/
├── __init__.py          # Package exports
├── models.py            # Data models (LinkResolverConfig, ResolvedProduct)
├── resolver.py          # Core resolver implementation
└── README.md            # This file
```

### Product ID Extraction Patterns

The resolver uses multiple regex patterns to extract product IDs:

1. `/view/product/{id}` - Primary pattern in redirect URLs
2. `/product/{id}` - Alternative URL pattern
3. `?product_id={id}` - Query parameter format
4. `"product_id":"{id}"` - JSON data attributes in page content
5. `productId:"{id}"` - Alternative JSON key
6. `item_id:"{id}"` - Another common key in TikTok data

### Mobile User Agent

The resolver uses an iPhone user agent to bypass desktop blocking:

```
Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)
AppleWebKit/605.1.15 (KHTML, like Gecko)
Version/16.6 Mobile/15E148 Safari/604.1
```

### Redirect Tracking

The resolver tracks all navigation requests to capture the full redirect chain. Product IDs are extracted from:
1. Each redirect URL in the chain
2. The final destination URL
3. Page content (as fallback)

## Configuration

### LinkResolverConfig

```python
@dataclass
class LinkResolverConfig:
    headless: bool = True              # Run browser headless
    timeout: int = 15000               # Navigation timeout (ms)
    user_agent: str = '...'            # Mobile user agent string
    log_level: str = 'INFO'            # Logging level
```

### ResolvedProduct

```python
@dataclass
class ResolvedProduct:
    original_url: str                  # Input URL
    product_id: str                    # Extracted product ID
    final_url: str                     # Final redirect destination
    redirect_chain: List[str]          # Full redirect chain
    success: bool                      # Whether extraction succeeded
    error: Optional[str] = None        # Error message if failed
```

## Error Handling

### Timeout Handling

The resolver uses `domcontentloaded` instead of `networkidle` to avoid unnecessary waits. Product IDs are usually captured from redirects before full page load completes.

### Graceful Degradation

If navigation times out but redirects were captured, the resolver will still attempt to extract the product ID from the redirect URLs.

### Pattern Matching

Multiple regex patterns ensure product IDs can be extracted from various URL formats and page content structures.

## Integration with Product Scraper

The link resolver is designed as a pre-step to the product scraper:

```bash
# Step 0: Resolve links to product IDs
python3 resolve_product_link.py \
  --links-file links.txt \
  --output products.csv

# Step 1: Scrape product data
python3 run_scraper.py \
  --batch-file products.csv \
  --download-videos \
  --output-dir "../product_list/YYYYMMDD"
```

## Testing

### Test with Sample Link

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts

python3 resolve_product_link.py \
  --url "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/" \
  --headed
```

### Test with Known Product ID

```bash
python3 resolve_product_link.py \
  --url "https://www.tiktok.com/view/product/1729536030472509561"
```

## Troubleshooting

### Browser Fails to Launch

```bash
playwright install chromium
```

### Product ID Not Found

1. Verify the link manually in a mobile browser
2. Run with `--headed` to see browser behavior
3. Check logs with `--log-level DEBUG`

### Timeout Errors

Product IDs are usually captured from redirects even if the page times out. Check if the result still contains a valid product ID despite the timeout error.

## Performance

- **Single link**: ~2-5 seconds
- **Batch (10 links)**: ~20-50 seconds
- **Network dependent**: Slower on poor connections

## Version History

**v1.0.0** (2025-02-10)
- Initial release
- Mobile user agent support
- Multiple product ID extraction patterns
- Batch processing capability
- CSV and JSON output formats
