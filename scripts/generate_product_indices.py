#!/usr/bin/env python3
"""
Product Index Generator for TikTok Shop Scraper

Generates index files (product_index.md) for all products with YAML frontmatter
containing sales metrics, video analytics, and script status. Designed for use
with Obsidian Database views.

Usage:
    python generate_product_indices.py                           # Generate all
    python generate_product_indices.py --dry-run                 # Preview only
    python generate_product_indices.py --force                   # Overwrite existing
    python generate_product_indices.py --date 20260205           # Dated batch
    python generate_product_indices.py --date 20260205 --csv scripts/products.csv  # Batch from CSV
    python generate_product_indices.py --product-id ID --date YYYYMMDD  # Single product in dated folder
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root is parent of scripts directory
REPO_ROOT = Path(__file__).parent.parent
PRODUCT_LIST_DIR = REPO_ROOT / "product_list"


def parse_revenue(revenue_str: str) -> float:
    """
    Parse revenue from multiple formats to USD float.

    Examples:
        '€ 7.27万($ 8.46万)' → 84600.00
        '$ 4429.33' → 4429.33
        '-' → 0.0
        '-(-)'→ 0.0
        '-(-))'→ 0.0
        null → 0.0

    Args:
        revenue_str: Revenue string from tabcut_data.json

    Returns:
        Float value in USD
    """
    if not revenue_str or revenue_str in ["-", "-(-)", "-(-))"]:
        return 0.0

    # Extract USD value with optional 万 (10,000) multiplier
    usd_match = re.search(r"\$\s*([\d.]+)万?", str(revenue_str))
    if usd_match:
        value = float(usd_match.group(1))
        if "万" in str(revenue_str) and "$" in str(revenue_str):
            # Check if 万 is after the USD amount
            usd_pos = str(revenue_str).find("$")
            wan_pos = str(revenue_str).find("万", usd_pos)
            if wan_pos > usd_pos:
                value *= 10000
        return value

    return 0.0


def parse_percentage(pct_str: str) -> float:
    """
    Parse percentage string to float.

    Examples:
        '5.26%' → 5.26
        '-' → 0.0
        null → 0.0

    Args:
        pct_str: Percentage string

    Returns:
        Float percentage value
    """
    if not pct_str or pct_str == "-":
        return 0.0

    # Extract numeric value before %
    match = re.search(r"([\d.]+)%", str(pct_str))
    if match:
        return float(match.group(1))

    return 0.0


def parse_view_count(view_str: str) -> int:
    """
    Parse view count from Chinese numeric format.

    Examples:
        '31.63万' → 316300
        '7100' → 7100
        null → 0

    Args:
        view_str: View count string

    Returns:
        Integer view count
    """
    if not view_str:
        return 0

    # Handle 万 (10,000) multiplier
    if "万" in str(view_str):
        match = re.search(r"([\d.]+)万", str(view_str))
        if match:
            return int(float(match.group(1)) * 10000)

    # Extract plain integer
    cleaned = re.sub(r"[^\d]", "", str(view_str))
    return int(cleaned) if cleaned else 0


def count_scripts(product_path: Path) -> Tuple[int, bool, Optional[str]]:
    """
    Count scripts in product's scripts/ folder.

    Args:
        product_path: Path to product folder

    Returns:
        Tuple of (script_count, has_campaign_summary, last_script_date)
        - script_count: Number of .md files excluding Campaign_Summary.md
        - has_campaign_summary: True if Campaign_Summary.md exists
        - last_script_date: ISO date of most recent script (YYYY-MM-DD) or None
    """
    scripts_dir = product_path / "scripts"
    if not scripts_dir.exists():
        return (0, False, None)

    # Count scripts (exclude Campaign_Summary.md)
    scripts = [f for f in scripts_dir.glob("*.md") if f.name != "Campaign_Summary.md"]

    has_campaign = (scripts_dir / "Campaign_Summary.md").exists()

    # Get most recent script modification date
    last_date = None
    if scripts:
        most_recent = max(scripts, key=lambda f: f.stat().st_mtime)
        last_date = datetime.fromtimestamp(most_recent.stat().st_mtime).strftime(
            "%Y-%m-%d"
        )

    return (len(scripts), has_campaign, last_date)


def get_product_category(product_path: Path) -> str:
    """
    Extract category from product path.

    Examples:
        product_list/htc/1729... → 'htc'
        product_list/20260104/1729... → '20260104'

    Args:
        product_path: Path to product folder

    Returns:
        Category string (folder name before product_id)
    """
    # Product path is: product_list/{category}/{product_id}
    # We want the {category} part
    parts = product_path.parts
    if "product_list" in parts:
        category_index = parts.index("product_list") + 1
        if category_index < len(parts):
            return parts[category_index]

    return "unknown"


def generate_performance_tags(metadata: dict) -> List[str]:
    """
    Auto-generate performance tags based on metrics.

    Rules:
        - #bestseller: total_sales > 1000
        - #high-conversion: conversion_rate > 5.0
        - #viral-videos: top_video_views > 100000
        - #no-sales-data: total_sales == 0 or null

    Args:
        metadata: Product metadata dict

    Returns:
        List of performance tag strings (with # prefix)
    """
    tags = []

    total_sales = metadata.get("total_sales", 0) or 0
    conversion_rate = metadata.get("conversion_rate", 0.0) or 0.0
    top_video_views = metadata.get("top_video_views", 0) or 0

    if total_sales > 1000:
        tags.append("#bestseller")

    if conversion_rate > 5.0:
        tags.append("#high-conversion")

    if top_video_views > 100000:
        tags.append("#viral-videos")

    if total_sales == 0:
        tags.append("#no-sales-data")

    return tags


def extract_product_metadata(json_path: Path, product_path: Path) -> dict:
    """
    Extract structured metadata from tabcut_data.json.

    Args:
        json_path: Path to tabcut_data.json
        product_path: Path to product folder

    Returns:
        Dict with structured metadata including:
        - product_id, product_name, shop_owner, scraped_at
        - total_sales, sales_revenue_usd (parsed float)
        - sales_7day, sales_7day_revenue_usd, conversion_rate (float)
        - video_count, creator_count, video_sales, video_revenue_usd
        - top_video_* (first valid video from top_videos array)
        - scripts_generated, has_campaign_summary, last_script_date
        - cover_image (relative path or empty)
        - category, performance_tags
    """
    # Read JSON data
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract basic info
    product_info = data.get("product_info", {})
    sales_data = data.get("sales_data", {})
    video_analysis = data.get("video_analysis", {})
    top_videos = data.get("top_videos", [])

    # Parse product info
    product_id = data.get("product_id", "unknown")
    product_name = product_info.get("product_name") or "Unknown Product"
    shop_owner = product_info.get("shop_owner") or "Unknown Shop"

    # Parse scraped date
    scraped_at_raw = data.get("scraped_at", "")
    try:
        scraped_at = datetime.fromisoformat(scraped_at_raw).strftime("%Y-%m-%d")
    except:
        scraped_at = datetime.now().strftime("%Y-%m-%d")

    # Parse sales metrics
    total_sales = product_info.get("total_sales") or 0
    sales_revenue_usd = parse_revenue(product_info.get("total_sales_revenue"))

    sales_7day = sales_data.get("sales_count") or 0
    sales_7day_revenue_usd = parse_revenue(sales_data.get("sales_revenue"))
    conversion_rate = parse_percentage(sales_data.get("conversion_rate"))

    # Parse video analytics
    video_count = video_analysis.get("带货视频数") or 0
    creator_count = video_analysis.get("带货视频达人数") or 0
    video_sales = video_analysis.get("带货视频销量") or 0
    video_revenue_usd = parse_revenue(video_analysis.get("带货视频销售额"))
    ad_revenue_percentage = parse_percentage(video_analysis.get("广告成交占比"))

    # Find first valid top video (skip placeholders)
    top_video_views = 0
    top_video_sales = 0
    top_video_creator = ""
    top_video_url = ""

    placeholder_titles = ["●直播", "●其它", "●商家自营账号", "●达人账号"]
    for video in top_videos:
        if (
            video.get("creator_username") != "unknown"
            and video.get("title", "").strip() not in placeholder_titles
            and video.get("video_url")
        ):
            # Found valid video
            top_video_views = parse_view_count(video.get("total_views"))
            top_video_sales = video.get("estimated_sales", 0) or 0
            top_video_creator = video.get("creator_username", "")
            top_video_url = video.get("video_url", "")
            break

    # Count scripts
    scripts_generated, has_campaign_summary, last_script_date = count_scripts(
        product_path
    )

    # Get cover image (project-level path)
    cover_image = ""
    img_path = product_path / "product_images" / "product_image_1.webp"
    if img_path.exists():
        # Store path relative to repo root (unique per product)
        cover_image = str(img_path.relative_to(REPO_ROOT))

    # Get category
    category = get_product_category(product_path)

    # Build metadata dict
    metadata = {
        "product_id": product_id,
        "product_name": product_name,
        "shop_owner": shop_owner,
        "category": category,
        "scraped_at": scraped_at,
        "total_sales": total_sales,
        "sales_revenue_usd": sales_revenue_usd,
        "sales_7day": sales_7day,
        "sales_7day_revenue_usd": sales_7day_revenue_usd,
        "conversion_rate": conversion_rate,
        "video_count": video_count,
        "creator_count": creator_count,
        "video_sales": video_sales,
        "video_revenue_usd": video_revenue_usd,
        "ad_revenue_percentage": ad_revenue_percentage,
        "top_video_views": top_video_views,
        "top_video_sales": top_video_sales,
        "top_video_creator": top_video_creator,
        "top_video_url": top_video_url,
        "scripts_generated": scripts_generated,
        "has_campaign_summary": has_campaign_summary,
        "last_script_date": last_script_date or "",
        "cover_image": cover_image,
    }

    # Generate performance tags
    metadata["performance_tags"] = generate_performance_tags(metadata)

    return metadata


def escape_yaml_string(value: str) -> str:
    """
    Escape string for YAML double-quoted strings (YAML 1.2 spec).

    In YAML double-quoted strings, backslash is the escape character:
    - Backslash: \\
    - Double quote: \"
    - Newline: \\n
    - Tab: \\t

    Examples:
        'Mini "Pro" Blender' → 'Mini \\"Pro\\" Blender'
        'Path\\to\\file' → 'Path\\\\to\\\\file'
        'Line1\nLine2' → 'Line1\\nLine2'

    Args:
        value: String to escape

    Returns:
        Escaped string safe for YAML double-quoted strings
    """
    if not value:
        return ""

    value = str(value)

    # CRITICAL: Escape backslashes FIRST (before other escapes add backslashes)
    value = value.replace("\\", "\\\\")

    # Escape double quotes
    value = value.replace('"', '\\"')

    # Escape newlines and carriage returns (preserve literal whitespace)
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    value = value.replace("\t", "\\t")

    return value


def generate_frontmatter(metadata: dict) -> str:
    """
    Generate YAML frontmatter from metadata.

    Args:
        metadata: Product metadata dict

    Returns:
        YAML frontmatter string with --- delimiters
    """
    tags = metadata["performance_tags"]
    tags_yaml = (
        "\n".join(f'  - "{escape_yaml_string(tag)}"' for tag in tags)
        if tags
        else '  - ""'
    )

    return f"""---
cover: "{escape_yaml_string(metadata["cover_image"])}"
product_id: "{escape_yaml_string(metadata["product_id"])}"
product_name: "{escape_yaml_string(metadata["product_name"])}"
shop_owner: "{escape_yaml_string(metadata["shop_owner"])}"
category: "{escape_yaml_string(metadata["category"])}"
scraped_at: "{escape_yaml_string(metadata["scraped_at"])}"

total_sales: {metadata["total_sales"]}
sales_revenue_usd: {metadata["sales_revenue_usd"]:.2f}
sales_7day: {metadata["sales_7day"]}
sales_7day_revenue_usd: {metadata["sales_7day_revenue_usd"]:.2f}
conversion_rate: {metadata["conversion_rate"]:.2f}

video_count: {metadata["video_count"]}
creator_count: {metadata["creator_count"]}
video_sales: {metadata["video_sales"]}
video_revenue_usd: {metadata["video_revenue_usd"]:.2f}
ad_revenue_percentage: {metadata["ad_revenue_percentage"]:.2f}

top_video_views: {metadata["top_video_views"]}
top_video_sales: {metadata["top_video_sales"]}
top_video_creator: "{escape_yaml_string(metadata["top_video_creator"])}"
top_video_url: "{escape_yaml_string(metadata["top_video_url"])}"

scripts_generated: {metadata["scripts_generated"]}
has_campaign_summary: {str(metadata["has_campaign_summary"]).lower()}
last_script_date: "{escape_yaml_string(metadata["last_script_date"])}"

tags:
{tags_yaml}
link: ""
---
"""


def generate_markdown_content(metadata: dict) -> str:
    """
    Generate markdown content sections.

    Args:
        metadata: Product metadata dict

    Returns:
        Markdown content string
    """
    content = []

    # Product Overview
    content.append("## Product Overview\n")
    content.append(f"**{metadata['product_name']}**\n")
    content.append(
        f"**Shop**: {metadata['shop_owner']} | **Category**: {metadata['category']} | **ID**: `{metadata['product_id']}`\n"
    )

    # Sales Performance
    content.append("\n## Sales Performance\n")
    content.append(
        f"- **Total Sales**: {metadata['total_sales']:,} units | ${metadata['sales_revenue_usd']:,.2f}\n"
    )
    content.append(
        f"- **7-Day Performance**: {metadata['sales_7day']:,} units | ${metadata['sales_7day_revenue_usd']:,.2f}\n"
    )
    content.append(f"- **Conversion Rate**: {metadata['conversion_rate']:.2f}%\n")

    # Video Analytics
    content.append("\n## Video Analytics\n")
    content.append(
        f"- **Active Videos**: {metadata['video_count']:,} videos by {metadata['creator_count']:,} creators\n"
    )
    content.append(
        f"- **Video Sales**: {metadata['video_sales']:,} units | ${metadata['video_revenue_usd']:,.2f}\n"
    )
    content.append(
        f"- **Ad Revenue**: {metadata['ad_revenue_percentage']:.2f}% of total\n"
    )

    # Top Performing Video (if exists)
    if metadata["top_video_creator"] and metadata["top_video_url"]:
        content.append("\n## Top Performing Video\n")
        content.append(
            f"**Creator**: @{metadata['top_video_creator']} | **Views**: {metadata['top_video_views']:,} | **Sales**: {metadata['top_video_sales']:,}\n"
        )
        content.append(f"\n[Watch Video]({metadata['top_video_url']})\n")
    else:
        content.append("\n## Top Performing Video\n")
        content.append("*No top performing videos available*\n")

    # Script Status
    content.append("\n## Script Status\n")
    content.append(f"- **Scripts Generated**: {metadata['scripts_generated']}\n")
    content.append(
        f"- **Campaign Summary**: {'✓' if metadata['has_campaign_summary'] else '✗'}\n"
    )
    if metadata["last_script_date"]:
        content.append(f"- **Latest Script**: {metadata['last_script_date']}\n")

    # Source Files
    content.append("\n## Source Files\n")
    content.append("- [Product Data](./tabcut_data.json)\n")
    content.append("- [Product Images](./product_images/)\n")
    content.append("- [Reference Videos](./ref_video/)\n")
    content.append("- [Scripts](./scripts/)\n")

    # Footer
    content.append(f"\n---\n*Last updated: {metadata['scraped_at']}*\n")

    return "".join(content)


def generate_index_file(product_path: Path, metadata: dict) -> str:
    """
    Generate complete product_index.md content.

    Args:
        product_path: Path to product folder
        metadata: Product metadata dict

    Returns:
        Complete markdown file content
    """
    frontmatter = generate_frontmatter(metadata)
    content = generate_markdown_content(metadata)

    return frontmatter + "\n" + content


def load_product_ids_from_csv(csv_path: Path) -> List[str]:
    """
    Load product IDs from CSV file.

    Args:
        csv_path: Path to CSV file with 'product_id' header

    Returns:
        List of product ID strings
    """
    product_ids = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            # Skip header row
            if i == 0 and row[0].lower() == "product_id":
                continue

            if row and row[0].strip():
                product_ids.append(row[0].strip())

    return product_ids


def check_scripts_gate(product_path: Path) -> bool:
    """
    Check if product passes scripts gate (3+ scripts + Campaign Summary).

    Args:
        product_path: Path to product folder

    Returns:
        True if product has complete scripts, False otherwise
    """
    scripts_dir = product_path / "scripts"
    if not scripts_dir.exists():
        return False

    # Check for Campaign_Summary.md
    if not (scripts_dir / "Campaign_Summary.md").exists():
        return False

    # Count script files (exclude Campaign_Summary.md)
    scripts = [f for f in scripts_dir.glob("*.md") if f.name != "Campaign_Summary.md"]

    return len(scripts) >= 3


def find_product_folders(
    base_path: Optional[Path] = None, product_ids: Optional[List[str]] = None
) -> List[Path]:
    """
    Find product folders (17-digit Snowflake IDs) in product_list/.

    Args:
        base_path: If provided, search only in this base directory
                   (e.g., product_list/20260205)
        product_ids: If provided, filter to only these product IDs

    Returns:
        List of Path objects to product folders
    """
    products = []

    # Pattern: 17-digit number
    product_id_pattern = re.compile(r"17\d{16}")

    # Determine search root
    search_root = base_path if base_path else PRODUCT_LIST_DIR

    # Search in all subdirectories of search_root
    if base_path and base_path.is_dir():
        # Direct children of base_path (e.g., product_list/20260205/{product_id})
        for product_dir in base_path.iterdir():
            if not product_dir.is_dir():
                continue

            # Check if folder name matches product ID pattern
            if product_id_pattern.match(product_dir.name):
                # Filter by product_ids if provided
                if product_ids is None or product_dir.name in product_ids:
                    products.append(product_dir)
    else:
        # Search all category dirs (legacy behavior)
        for category_dir in search_root.iterdir():
            if not category_dir.is_dir():
                continue

            for product_dir in category_dir.iterdir():
                if not product_dir.is_dir():
                    continue

                # Check if folder name matches product ID pattern
                if product_id_pattern.match(product_dir.name):
                    # Filter by product_ids if provided
                    if product_ids is None or product_dir.name in product_ids:
                        products.append(product_dir)

    return sorted(products)


def needs_index_update(product_path: Path, metadata: dict) -> bool:
    """
    Check if product_index.md needs updating (is stale or missing).

    Args:
        product_path: Path to product folder
        metadata: Freshly extracted metadata

    Returns:
        True if index needs update, False if current
    """
    index_path = product_path / "product_index.md"

    if not index_path.exists():
        return True  # Missing, needs creation

    # Read existing frontmatter to check staleness
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract YAML frontmatter
        if not content.startswith("---\n"):
            return True  # Malformed, needs rewrite

        # Simple check: compare key fields
        # (scripts_generated, has_campaign_summary, last_script_date, cover)
        lines = content.split("\n")

        # Extract current values from frontmatter
        current_scripts = None
        current_campaign = None
        current_date = None
        current_cover = None

        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith("scripts_generated:"):
                current_scripts = int(line.split(":", 1)[1].strip())
            elif line.startswith("has_campaign_summary:"):
                current_campaign = line.split(":", 1)[1].strip() == "true"
            elif line.startswith("last_script_date:"):
                current_date = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("cover:"):
                current_cover = line.split(":", 1)[1].strip().strip('"')

        # Compare with fresh metadata
        if (
            current_scripts != metadata["scripts_generated"]
            or current_campaign != metadata["has_campaign_summary"]
            or current_date != metadata["last_script_date"]
            or current_cover != metadata["cover_image"]
        ):
            return True  # Stale

        return False  # Current

    except Exception:
        return True  # Read error, needs rewrite


def process_product(
    product_path: Path,
    force: bool = False,
    dry_run: bool = False,
    incremental: bool = True,
    require_scripts: bool = False,
) -> dict:
    """
    Process a single product and generate index file.

    Args:
        product_path: Path to product folder
        force: If True, overwrite existing index file
        dry_run: If True, don't write file
        incremental: If True, skip if index is current
        require_scripts: If True, skip if product doesn't pass scripts gate

    Returns:
        Dict with keys: 'status' ('success'|'skipped'|'failed'),
                       'product_id', 'message', 'warnings'
    """
    result = {
        "status": "failed",
        "product_id": product_path.name,
        "message": "",
        "warnings": [],
    }

    # Check for tabcut_data.json
    json_path = product_path / "tabcut_data.json"
    if not json_path.exists():
        result["message"] = "tabcut_data.json not found"
        return result

    # Check scripts gate if required
    if require_scripts and not check_scripts_gate(product_path):
        result["status"] = "skipped"
        result["message"] = "Scripts incomplete (need 3+ scripts + Campaign Summary)"
        return result

    try:
        # Extract metadata
        metadata = extract_product_metadata(json_path, product_path)

        # Check if update needed (incremental mode)
        index_path = product_path / "product_index.md"
        if incremental and not force:
            if not needs_index_update(product_path, metadata):
                result["status"] = "skipped"
                result["message"] = "Index current (no update needed)"
                return result
        elif index_path.exists() and not force:
            result["status"] = "skipped"
            result["message"] = "Index already exists (use --force to overwrite)"
            return result

        # Generate index content
        index_content = generate_index_file(product_path, metadata)

        # Collect warnings
        if not metadata["cover_image"]:
            result["warnings"].append("No product_image_1.webp found")

        if metadata["scripts_generated"] == 0:
            result["warnings"].append("No scripts generated yet")

        if metadata["total_sales"] == 0:
            result["warnings"].append("No sales data available")

        # Write file (unless dry-run)
        if not dry_run:
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index_content)

        result["status"] = "success"
        result["message"] = f"Generated index ({len(index_content)} bytes)"

    except json.JSONDecodeError as e:
        result["message"] = f"Invalid JSON: {str(e)}"
    except Exception as e:
        result["message"] = f"Error: {str(e)}"

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate product index files for Obsidian Database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                          # Generate all indices
  %(prog)s --dry-run                                # Preview without writing
  %(prog)s --force                                  # Overwrite existing indices
  %(prog)s --date 20260205 --csv scripts/products.csv  # Batch from CSV (dated)
  %(prog)s --date 20260205 --csv scripts/products.csv --require-scripts  # Only successful products
  %(prog)s --product-id 1729630... --date 20260205  # Single product in dated folder
        """,
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without writing files"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing index files"
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        default=True,
        help="Only update stale indices (default: True)",
    )
    parser.add_argument(
        "--no-incremental",
        dest="incremental",
        action="store_false",
        help="Disable incremental mode",
    )
    parser.add_argument(
        "--require-scripts",
        action="store_true",
        help="Only generate index for products with 3+ scripts + Campaign Summary",
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Date folder (YYYYMMDD) under product_list/ (e.g., 20260205)",
    )
    parser.add_argument(
        "--base",
        type=str,
        help="Base folder containing product_id subfolders (overrides --date)",
    )
    parser.add_argument(
        "--csv",
        type=str,
        help="CSV file with product_id column (e.g., scripts/products.csv)",
    )
    parser.add_argument(
        "--product-ids", type=str, help="Space-separated product IDs (overrides --csv)"
    )
    parser.add_argument(
        "--product-id",
        type=str,
        help="Generate for single product ID (requires --date or --base)",
    )

    args = parser.parse_args()

    # Header
    print("=" * 70)
    print("Product Index Generator")
    print("=" * 70)

    if args.dry_run:
        print("DRY RUN MODE - No files will be written\n")

    # Determine base path
    base_path = None
    if args.base:
        base_path = Path(args.base).resolve()
        if not base_path.is_dir():
            print(f"Error: Base folder does not exist: {base_path}")
            sys.exit(1)
    elif args.date:
        base_path = (PRODUCT_LIST_DIR / args.date).resolve()
        if not base_path.is_dir():
            print(f"Error: Date folder does not exist: {base_path}")
            sys.exit(1)

    # Load product IDs
    product_ids = None
    if args.product_id:
        # Single product mode - require base/date
        if not base_path:
            print("Error: --product-id requires --date or --base")
            sys.exit(1)
        product_ids = [args.product_id]
    elif args.product_ids:
        # Manual list
        product_ids = args.product_ids.split()
    elif args.csv:
        # Load from CSV
        csv_path = Path(args.csv)
        if not csv_path.exists():
            print(f"Error: CSV file not found: {args.csv}")
            sys.exit(1)
        product_ids = load_product_ids_from_csv(csv_path)
        print(f"Loaded {len(product_ids)} product IDs from {args.csv}\n")

    # Find products
    product_folders = find_product_folders(base_path=base_path, product_ids=product_ids)

    if not product_folders:
        print("Error: No products found matching criteria")
        sys.exit(1)

    print(f"Found {len(product_folders)} product(s)\n")

    if args.require_scripts:
        print("Mode: Only generating indices for products with complete scripts\n")
    if args.incremental and not args.force:
        print("Mode: Incremental (skip if current)\n")

    # Process products
    results = {
        "successful": [],
        "skipped": [],
        "failed": [],
        "warnings": [],
    }

    for i, product_path in enumerate(product_folders, 1):
        print(
            f"[{i}/{len(product_folders)}] Processing {product_path.name}...", end=" "
        )

        result = process_product(
            product_path,
            force=args.force,
            dry_run=args.dry_run,
            incremental=args.incremental,
            require_scripts=args.require_scripts,
        )

        if result["status"] == "success":
            print(f"✓ {result['message']}")
            results["successful"].append(result)

            # Show warnings
            for warning in result["warnings"]:
                print(f"    ⚠  {warning}")
                results["warnings"].append(
                    {"product_id": result["product_id"], "warning": warning}
                )

        elif result["status"] == "skipped":
            print(f"⊘ {result['message']}")
            results["skipped"].append(result)

        else:  # failed
            print(f"✗ {result['message']}")
            results["failed"].append(result)

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total: {len(product_folders)}")
    print(f"✓ Successful: {len(results['successful'])}")
    print(f"⊘ Skipped: {len(results['skipped'])}")
    print(f"✗ Failed: {len(results['failed'])}")
    print(f"⚠  Warnings: {len(results['warnings'])}")

    # Show failures
    if results["failed"]:
        print("\nFailed Products:")
        for result in results["failed"]:
            print(f"  - {result['product_id']}: {result['message']}")

    # Exit code
    sys.exit(0 if not results["failed"] else 1)


if __name__ == "__main__":
    main()
