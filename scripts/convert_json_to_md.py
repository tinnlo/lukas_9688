#!/usr/bin/env python3
"""Convert tabcut_data.json to human-readable tabcut_data.md.

Supports both legacy layout:
  product_list/<product_id>/tabcut_data.json
and dated batch layout:
  product_list/YYYYMMDD/<product_id>/tabcut_data.json
"""

import argparse
import json
import sys
from pathlib import Path

def _fmt_int(value):
    if value is None or value == "":
        return "N/A"
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)

def json_to_markdown(data):
    """Convert scraped JSON data to markdown format"""
    product_id = data['product_id']
    md = f"""# TikTok Product Data: {product_id}

**Scraped:** {data['scraped_at']}

---

## Product Information

- **Product Name:** {(data.get('product_info') or {}).get('product_name', 'N/A')}
- **Shop Owner:** {(data.get('product_info') or {}).get('shop_owner', 'N/A')}
- **Total Sales:** {_fmt_int((data.get('product_info') or {}).get('total_sales'))} units
- **Total Revenue:** {(data.get('product_info') or {}).get('total_sales_revenue', 'N/A')}
- **Product Rating:** {(data.get('product_info') or {}).get('product_rating', 'N/A')}
- **Category:** {(data.get('product_info') or {}).get('category', 'N/A')}

---

## Sales Data ({data['sales_data']['date_range']})

- **Sales Count:** {_fmt_int((data.get('sales_data') or {}).get('sales_count'))} units
- **Sales Revenue:** {(data.get('sales_data') or {}).get('sales_revenue', 'N/A')}
- **Related Videos:** {(data.get('sales_data') or {}).get('related_videos', 'N/A')}
- **Conversion Rate:** {(data.get('sales_data') or {}).get('conversion_rate', 'N/A')}
- **Click-Through Rate:** {(data.get('sales_data') or {}).get('click_through_rate', 'N/A')}

---

## Video Analysis Metrics

- **Total Videos:** {(data.get('video_analysis') or {}).get('带货视频数', 'N/A')}
- **Total Creators:** {(data.get('video_analysis') or {}).get('带货视频达人数', 'N/A')}
- **Video Sales:** {(data.get('video_analysis') or {}).get('带货视频销量', 'N/A')}
- **Video Revenue:** {(data.get('video_analysis') or {}).get('带货视频销售额', 'N/A')}
- **Ad Revenue:** {(data.get('video_analysis') or {}).get('广告成交金额', 'N/A')}
- **Ad Conversion %:** {(data.get('video_analysis') or {}).get('广告成交占比', 'N/A')}

---

## Top {len(data.get('top_videos') or [])} Performing Videos

"""

    for video in (data.get('top_videos') or []):
        # Handle views as string or int
        views = video.get('total_views', 'N/A')
        if isinstance(views, (int, float)):
            views_formatted = f"{int(views):,}"
        else:
            views_formatted = views

        md += f"""
### Video #{video['rank']}: @{video['creator_username']}

- **Title:** {video['title']}
- **Creator:** @{video['creator_username']} ({video.get('creator_followers', 'N/A')} followers)
- **Published:** {video['publish_date']}
- **Sales:** {video['estimated_sales']} units
- **Revenue:** {video['estimated_revenue']}
- **Views:** {views_formatted}
- **Video URL:** {video.get('video_url', 'N/A')}
- **Video ID:** {video.get('video_id', 'N/A')}
- **Local Path:** `{video.get('local_path', 'Not downloaded')}`

---
"""

    return md

def main():
    parser = argparse.ArgumentParser(description="Convert tabcut_data.json to tabcut_data.md")
    parser.add_argument("--product-id", type=str, help="Product ID to convert")
    parser.add_argument("--batch-file", type=str, help="CSV with header product_id (converts all rows)")
    parser.add_argument("--base", type=str, default=None, help="Base folder that contains product_id subfolders")
    parser.add_argument("--date", type=str, default=None, help="YYYYMMDD under product_list/ (sets base to product_list/YYYYMMDD)")
    args = parser.parse_args()

    if not args.product_id and not args.batch_file:
        print("Usage: python convert_json_to_md.py --product-id <product_id> [--date YYYYMMDD|--base PATH]")
        print("   or: python convert_json_to_md.py --batch-file <csv> [--date YYYYMMDD|--base PATH]")
        sys.exit(1)

    project_root = Path(__file__).parent.parent
    if args.base:
        base = Path(args.base)
    elif args.date:
        base = project_root / "product_list" / args.date
    else:
        base = project_root / "product_list"

    def convert_one(product_id: str) -> bool:
        product_dir = base / product_id
        json_path = product_dir / "tabcut_data.json"
        md_path = product_dir / "tabcut_data.md"

        if not json_path.exists():
            print(f"❌ Error: {json_path} not found")
            return False

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        md_content = json_to_markdown(data)

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        product_name = (data.get('product_info') or {}).get('product_name', 'Unknown')
        total_sales = (data.get('product_info') or {}).get('total_sales')
        print(f"✅ Created: {md_path}")
        print(f"   Product: {product_name}")
        if isinstance(total_sales, int):
            print(f"   Sales: {total_sales:,} units")
        print(f"   Top Videos: {len(data.get('top_videos') or [])}")
        return True

    if args.product_id:
        ok = convert_one(args.product_id)
        sys.exit(0 if ok else 2)

    # Batch file: first column is product_id, allow header.
    ids = []
    with open(args.batch_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            if i == 0 and line.lower().startswith("product_id"):
                continue
            ids.append(line.split(",")[0].strip())

    failures = 0
    for pid in ids:
        if not convert_one(pid):
            failures += 1

    sys.exit(0 if failures == 0 else 2)

if __name__ == "__main__":
    main()
