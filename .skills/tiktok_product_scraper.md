---
name: tiktok-product-scraper
description: Step 1 of TikTok workflow. Scrapes product data from tabcut.com using Python scraper. Creates JSON + human-readable MD. Optional video downloads. Designed for n8n orchestration.
version: 1.0.0
author: User (via n8n)
execution: n8n workflow node → Bash commands
---

# TikTok Product Scraper Skill (Step 1)

**WHO RUNS THIS:** n8n workflow (or manual terminal)
**PURPOSE:** Scrape product data and optionally download reference videos
**NEXT STEP:** Step 2 - Ad Analysis (gemini-cli)

---

## Overview

This skill scrapes TikTok Shop product data from tabcut.com including:
- Product information and sales metrics
- Top 5 performing videos metadata
- Optional: Download video files for analysis
- **Always:** Convert JSON to human-readable MD for review

---

## Prerequisites

✅ **Python 3.8+** with virtual environment
✅ **Tabcut.com credentials** in `scripts/config/.env`
✅ **Playwright browser** installed (`playwright install chromium`)
✅ **Dependencies installed** (`pip install -r requirements.txt`)

**Setup (one-time):**
```bash
cd scripts/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Configure credentials
cp config/.env.example config/.env
# Edit config/.env with your tabcut.com credentials
```

---

## Quick Start (n8n)

### Option A: Single Product (with videos)

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
source venv/bin/activate
python run_scraper.py \
  --product-id {{$json.product_id}} \
  --download-videos

# Generate human-readable MD
python -c "
import json
import sys
sys.path.append('.')
from tabcut_scraper.utils import json_to_markdown

product_id = '{{$json.product_id}}'
with open(f'../product_list/{product_id}/tabcut_data.json') as f:
    data = json.load(f)
md = json_to_markdown(data)
with open(f'../product_list/{product_id}/tabcut_data.md', 'w') as f:
    f.write(md)
print('✅ Created tabcut_data.md')
"
```

### Option B: Single Product (no videos)

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
source venv/bin/activate
python run_scraper.py --product-id {{$json.product_id}}

# Generate MD (same as above)
python -c "..."
```

### Option C: Batch Products from CSV

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
source venv/bin/activate
python run_scraper.py \
  --batch-file {{$json.csv_file_path}} \
  --download-videos

# Generate MD for all products in batch
python -c "
import json, os, glob
import sys
sys.path.append('.')
from tabcut_scraper.utils import json_to_markdown

for json_file in glob.glob('../product_list/*/tabcut_data.json'):
    product_id = json_file.split('/')[-2]
    with open(json_file) as f:
        data = json.load(f)
    md = json_to_markdown(data)
    md_file = json_file.replace('.json', '.md')
    with open(md_file, 'w') as f:
        f.write(md)
    print(f'✅ Created {md_file}')
"
```

---

## n8n Workflow Node Configuration

### Node 1: Execute Command (Scrape)

**Command:**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts && \
source venv/bin/activate && \
python run_scraper.py --product-id {{$json.product_id}} {{$json.download_videos && '--download-videos' || ''}}
```

**Parameters:**
- `product_id`: String (required) - TikTok product ID
- `download_videos`: Boolean (optional, default: false) - Download video files

**Expected Output:**
```json
{
  "success": true,
  "product_id": "1729630936525936882",
  "files_created": [
    "product_list/1729630936525936882/tabcut_data.json"
  ],
  "videos_downloaded": 5
}
```

### Node 2: Convert JSON to MD (Always)

**Command:**
```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688 && \
python3 -c "
import json
import sys

def json_to_markdown(data):
    product_id = data['product_id']
    md = f'''# TikTok Product Data: {product_id}

**Scraped:** {data['scraped_at']}

---

## Product Information

- **Product Name:** {data['product_info']['product_name']}
- **Shop Owner:** {data['product_info']['shop_owner']}
- **Total Sales:** {data['product_info']['total_sales']:,} units
- **Total Revenue:** {data['product_info']['total_sales_revenue']}
- **Product Rating:** {data['product_info'].get('product_rating', 'N/A')}

---

## Sales Data ({data['sales_data']['date_range']})

- **Sales Count:** {data['sales_data']['sales_count']} units
- **Sales Revenue:** {data['sales_data']['sales_revenue']}
- **Related Videos:** {data['sales_data']['related_videos']}
- **Conversion Rate:** {data['sales_data']['conversion_rate']}

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

'''
    for video in data['top_videos']:
        md += f'''
### Video #{video['rank']}: @{video['creator_username']}

- **Title:** {video['title']}
- **Creator:** @{video['creator_username']} ({video.get('creator_followers', 'N/A')} followers)
- **Published:** {video['publish_date']}
- **Sales:** {video['estimated_sales']} units
- **Revenue:** {video['estimated_revenue']}
- **Views:** {video['total_views']:,}
- **Video URL:** {video.get('video_url', 'N/A')}
- **Local Path:** \`{video.get('local_path', 'Not downloaded')}\`

---
'''
    return md

# Main execution
product_id = '{{$json.product_id}}'
json_path = f'product_list/{product_id}/tabcut_data.json'
md_path = f'product_list/{product_id}/tabcut_data.md'

with open(json_path, 'r') as f:
    data = json.load(f)

md_content = json_to_markdown(data)

with open(md_path, 'w') as f:
    f.write(md_content)

print(json.dumps({
    'success': True,
    'md_file': md_path,
    'product_name': data['product_info']['product_name']
}))
"
```

**Expected Output:**
```json
{
  "success": true,
  "md_file": "product_list/1729630936525936882/tabcut_data.md",
  "product_name": "HTC NE20 Translator Earbuds..."
}
```

---

## Manual Execution (Terminal)

### Single Product with Videos

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
source venv/bin/activate

# Scrape + download videos
python run_scraper.py \
  --product-id 1729630936525936882 \
  --download-videos

# Convert to MD for review
python3 ../scripts/convert_json_to_md.py 1729630936525936882
```

### Single Product WITHOUT Videos

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
source venv/bin/activate

# Scrape metadata only
python run_scraper.py --product-id 1729630936525936882

# Convert to MD
python3 ../scripts/convert_json_to_md.py 1729630936525936882
```

### Batch Processing

```bash
cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
source venv/bin/activate

# Create CSV with product IDs
cat > products.csv << EOF
product_id
1729630936525936882
1729479916562717270
1729535919239371775
EOF

# Scrape all (with videos)
python run_scraper.py \
  --batch-file products.csv \
  --download-videos

# Convert all to MD
for product_dir in ../product_list/*/; do
  product_id=$(basename "$product_dir")
  python3 ../scripts/convert_json_to_md.py "$product_id"
done
```

---

## Output Structure

After running this skill:

```
product_list/{product_id}/
├── tabcut_data.json          # Raw scraped data
├── tabcut_data.md            # ← Human-readable review file (ALWAYS created)
└── ref_video/                # ← Optional (if --download-videos used)
    ├── video_1_{creator}.mp4
    ├── video_2_{creator}.mp4
    ├── video_3_{creator}.mp4
    ├── video_4_{creator}.mp4
    └── video_5_{creator}.mp4
```

---

## Helper Script: convert_json_to_md.py

**Create this utility script:**

```bash
cat > /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts/convert_json_to_md.py << 'EOF'
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
        md += f"""
### Video #{video['rank']}: @{video['creator_username']}

- **Title:** {video['title']}
- **Creator:** @{video['creator_username']} ({video.get('creator_followers', 'N/A')} followers)
- **Published:** {video['publish_date']}
- **Sales:** {video['estimated_sales']} units
- **Revenue:** {video['estimated_revenue']}
- **Views:** {video['total_views']:,}
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
EOF

chmod +x /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts/convert_json_to_md.py
```

---

## Configuration Options

### Download Videos: YES

**When to use:**
- Need to analyze video content with gemini-cli
- Creating new scripts based on reference videos
- Deep-dive analysis required

**Command:**
```bash
python run_scraper.py --product-id <id> --download-videos
```

**Output:** JSON + MD + 5 video files (~50-200 MB)

### Download Videos: NO

**When to use:**
- Only need product metadata and sales data
- Quick data gathering for reporting
- Limited storage/bandwidth

**Command:**
```bash
python run_scraper.py --product-id <id>
```

**Output:** JSON + MD only (~10 KB)

---

## Error Handling

The scraper handles common issues automatically:

### Authentication Failures
- Automatic retry with exponential backoff
- Check credentials in `scripts/config/.env`
- Run with `--headed` flag to see browser

### Empty 7-Day Data
- Automatic fallback to 30-day data
- Logged in output

### Product Not Found
- Retry 2x, then log error
- Check product ID on tabcut.com

### Video Download Failures
- Logged but doesn't block scraping
- Continues with remaining videos

---

## Quality Checklist

Before proceeding to Step 2 (Ad Analysis):

- [ ] `tabcut_data.json` created successfully
- [ ] `tabcut_data.md` created for human review
- [ ] **Review `tabcut_data.md`** - verify product data is correct
- [ ] If videos downloaded: Check `ref_video/` folder has MP4 files
- [ ] Top 5 videos metadata looks reasonable
- [ ] Sales data and metrics are populated

---

## Troubleshooting

### Issue: Scraper fails to login

**Solution:**
```bash
# Run in headed mode to see browser
cd scripts/
source venv/bin/activate
python run_scraper.py --product-id <id> --headed
```

Check for:
- CAPTCHA (requires manual solving)
- Incorrect credentials in `config/.env`
- 2FA enabled on account

### Issue: No videos downloaded

**Possible causes:**
1. Forgot `--download-videos` flag
2. Videos not available on tabcut.com
3. Download timeout (increase in `config/.env`)

**Solution:**
```bash
# Retry with longer timeout
python run_scraper.py --product-id <id> --download-videos
```

### Issue: Empty/incomplete data

**Solution:**
1. Verify product ID exists on tabcut.com
2. Check if logged in (run with `--headed`)
3. Try 30-day data period if 7-day is empty

---

## Next Step: Ad Analysis (Step 2)

After successful scraping:

1. **Review** `tabcut_data.md` for accuracy
2. **Proceed to** `.skills/tiktok_ad_analysis.md`
3. Run gemini-cli video analysis (if videos downloaded)
4. Create `video_analysis.md` and `image_analysis.md`

**Workflow:**
```
Step 1 (This skill) → tabcut_data.json + tabcut_data.md + videos
                    ↓
Step 2 (gemini-cli) → video_analysis.md + image_analysis.md
                    ↓
Step 3 (Claude Code) → 3 TikTok scripts + Campaign_Summary.md
```

---

## Version History

**v1.0.0** (2025-12-29)
- Initial release for n8n orchestration
- Wrapper around existing Python scraper
- Always creates human-readable MD file
- Optional video downloads
- Batch processing support
- Error handling documented
