# TikTok Shop Product Scraper

A Python-based web scraper for extracting TikTok shop product data from tabcut.com, including product information, sales analytics, and video performance data.

## Features

- **Product Information**: Extract product name, shop owner, and sales metrics
- **Sales Analytics**: 7-day sales data with automatic 30-day fallback
- **Video Analysis**: Top performing videos with detailed metrics
- **Video Downloads**: Download top 5 reference videos to `ref_video/` folder
- **Batch Processing**: Scrape multiple products from CSV file
- **Resume Capability**: Resume interrupted batch jobs
- **Error Handling**: Automatic retries with exponential backoff
- **Progress Tracking**: Real-time progress bars and detailed logging

## Installation

### Prerequisites

- Python 3.8 or higher
- Valid tabcut.com account credentials

### Setup

1. **Navigate to the scripts directory:**
   ```bash
   cd /Users/lxt/Movies/TikTok/WZ/lukas_9688/scripts
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure credentials:**
   ```bash
   cp config/.env.example config/.env
   ```

   Edit `config/.env` and add your tabcut.com credentials:
   ```bash
   TABCUT_USERNAME=your_username_here
   TABCUT_PASSWORD=your_password_here
   ```

## Usage

### Single Product

Scrape a single product by ID:

```bash
python run_scraper.py --product-id 1729630936525936882
```

With video downloads:

```bash
python run_scraper.py --product-id 1729630936525936882 --download-videos
```

### Batch Processing

Create a CSV file with product IDs (`products.csv`):

```csv
product_id
1729630936525936882
7575477825742982403
7520182265683381526
```

Scrape all products:

```bash
python run_scraper.py --batch-file products.csv
```

With video downloads:

```bash
python run_scraper.py --batch-file products.csv --download-videos
```

### Resume Interrupted Batch

If a batch job is interrupted, resume from where it left off:

```bash
python run_scraper.py --batch-file products.csv --resume
```

### Additional Options

```bash
# Run in headed mode (visible browser)
python run_scraper.py --product-id 1729630936525936882 --headed

# Custom output directory
python run_scraper.py --product-id 1729630936525936882 --output-dir /path/to/output

# Debug logging
python run_scraper.py --product-id 1729630936525936882 --log-level DEBUG
```

## Output Structure

Scraped data is saved to `product_list/{product_id}/`:

```
product_list/
└── 1729630936525936882/
    ├── tabcut_data.json        # All scraped metadata
    └── ref_video/               # Downloaded reference videos
        ├── video_1_htc_earphone.mp4
        ├── video_2_leoreich.mp4
        ├── video_3_king_gondal.mp4
        ├── video_4_htc_earphone.mp4
        └── video_5_htc_earphone.mp4
```

### Data Schema

The `tabcut_data.json` file contains:

```json
{
  "product_id": "1729630936525936882",
  "scraped_at": "2025-12-23T19:30:00Z",
  "product_info": {
    "product_name": "HTC NE20 Translator Bluetooth...",
    "shop_owner": "HTC.DE",
    "total_sales": 5187,
    "total_sales_revenue": "€ 7.02万"
  },
  "sales_data": {
    "date_range": "7day",
    "sales_count": 417,
    "sales_revenue": "$ 6369.08",
    "related_videos": 73,
    "conversion_rate": "10.96%"
  },
  "video_analysis": {
    "带货视频数": 73,
    "带货视频达人数": 26,
    "带货视频销量": 17,
    "带货视频销售额": "$ 259.65",
    "广告成交金额": "$ 61.09"
  },
  "top_videos": [
    {
      "rank": 1,
      "title": "HTC translation earphones...",
      "creator_username": "htc.earphone",
      "publish_date": "2025-12-17",
      "estimated_sales": 4,
      "estimated_revenue": "€ 52.48",
      "total_views": 10800,
      "local_path": "ref_video/video_1_htc_earphone.mp4"
    }
  ]
}
```

## Configuration

Configuration can be set via `config/.env`:

```bash
# Authentication
TABCUT_USERNAME=your_cellphone_username
TABCUT_PASSWORD=your_password

# Browser Settings
HEADLESS=true
DEFAULT_TIMEOUT=30000
DOWNLOAD_TIMEOUT=300000

# Scraper Settings
MAX_RETRIES=3
OUTPUT_BASE_DIR=../product_list

# Logging
LOG_LEVEL=INFO
```

## Error Handling

The scraper implements robust error handling:

- **Authentication failures**: Automatic retry with exponential backoff
- **Empty 7-day data**: Automatic fallback to 30-day data
- **Product ID failures**: Retry 2x, then log error
- **Video download failures**: Log and continue (doesn't block scraping)
- **Rate limiting**: Automatic detection and backoff

## Logging

Logs are saved to `logs/`:

- `scraper_{date}.log`: All logs (DEBUG level)
- `errors_{date}.log`: Error logs only
- Console: INFO level with color coding

## Troubleshooting

### Authentication Issues

If login fails:

1. Verify credentials in `config/.env`
2. Run in headed mode to see the browser:
   ```bash
   python run_scraper.py --product-id 1729630936525936882 --headed
   ```
3. Check for CAPTCHA or 2FA requirements

### Playwright Issues

If browser fails to launch:

```bash
playwright install chromium
```

### Empty Data

If scraped data is empty:

1. Check if you're logged in (run with `--headed`)
2. Verify the product ID exists on tabcut.com
3. Try a different product ID

## Development

### Project Structure

```
scripts/
├── tabcut_scraper/          # Main package
│   ├── __init__.py
│   ├── auth.py              # Authentication
│   ├── extractors.py        # Data extraction
│   ├── downloader.py        # Video downloads
│   ├── models.py            # Data models
│   ├── scraper.py           # Main orchestrator
│   └── utils.py             # Utilities
├── config/
│   ├── .env.example
│   └── .env                 # Your credentials
├── logs/                    # Log files
├── run_scraper.py           # CLI entry point
├── requirements.txt
└── README.md
```

### Running Tests

```bash
# Test single product (no downloads)
python run_scraper.py --product-id 1729630936525936882 --log-level DEBUG

# Test with videos (small batch)
echo "1729630936525936882" > test.csv
python run_scraper.py --batch-file test.csv --download-videos
```

## Additional Documentation

### Vertex AI API Usage

For information on using Google Vertex AI API for image and text generation with Gemini models, see:

**[VERTEX_AI_USAGE.md](VERTEX_AI_USAGE.md)**

This guide covers:
- Authentication setup with gcloud
- API endpoint structure and available models
- Image and text generation examples
- Response handling and base64 image extraction
- Error handling and best practices

The Vertex AI integration enables AI-powered content generation for TikTok video scripts and visual assets.

## License

Internal tool for TikTok content creation workflow.

## Support

For issues or questions, refer to the implementation plan at:
`/Users/lxt/.claude/plans/buzzing-herding-gem.md`
