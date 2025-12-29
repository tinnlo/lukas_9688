#!/usr/bin/env python3
"""Convert tabcut_data.json to human-readable tabcut_data.md"""

import json
import sys
from pathlib import Path

def json_to_markdown(data):
    """Convert scraped JSON data to markdown format"""
    product_id = data['product_id']
    md = f"""# TikTok Product Data: {product_id}

**Scraped:** {data['scraped_at']}

---

## Product Information

- **Product Name:** {data['product_info']['product_name']}
- **Shop Owner:** {data['product_info']['shop_owner']}
- **Total Sales:** {data['product_info']['total_sales']:,} units
- **Total Revenue:** {data['product_info']['total_sales_revenue']}
- **Product Rating:** {data['product_info'].get('product_rating', 'N/A')}
- **Category:** {data['product_info'].get('category', 'N/A')}

---

## Sales Data ({data['sales_data']['date_range']})

- **Sales Count:** {data['sales_data']['sales_count']} units
- **Sales Revenue:** {data['sales_data']['sales_revenue']}
- **Related Videos:** {data['sales_data'].get('related_videos', 'N/A')}
- **Conversion Rate:** {data['sales_data'].get('conversion_rate', 'N/A')}
- **Click-Through Rate:** {data['sales_data'].get('click_through_rate', 'N/A')}

---

## Video Analysis Metrics

- **Total Videos:** {data['video_analysis']['带货视频数']}
- **Total Creators:** {data['video_analysis']['带货视频达人数']}
- **Video Sales:** {data['video_analysis']['带货视频销量']}
- **Video Revenue:** {data['video_analysis']['带货视频销售额']}
- **Ad Revenue:** {data['video_analysis']['广告成交金额']}
- **Ad Conversion %:** {data['video_analysis']['广告成交占比']}

---

## Top {len(data['top_videos'])} Performing Videos

"""

    for video in data['top_videos']:
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
    if len(sys.argv) < 2:
        print("Usage: python convert_json_to_md.py <product_id>")
        sys.exit(1)

    product_id = sys.argv[1]
    base_dir = Path(__file__).parent.parent / "product_list" / product_id
    json_path = base_dir / "tabcut_data.json"
    md_path = base_dir / "tabcut_data.md"

    if not json_path.exists():
        print(f"❌ Error: {json_path} not found")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    md_content = json_to_markdown(data)

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"✅ Created: {md_path}")
    print(f"   Product: {data['product_info']['product_name']}")
    print(f"   Sales: {data['product_info']['total_sales']:,} units")
    print(f"   Top Videos: {len(data['top_videos'])}")

if __name__ == "__main__":
    main()
