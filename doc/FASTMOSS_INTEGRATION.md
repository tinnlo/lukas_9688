# FastMoss Integration - Quick Reference

## Overview

The TikTok Product Scraper now supports **two data sources**:
- **tabcut.com** (default, original)
- **fastmoss.com** (NEW)

Both sources provide similar TikTok Shop product data, with different authentication methods and page structures.

## Quick Start

### Scrape from FastMoss

```bash
# Single product
python run_scraper.py --product-id 1729657963479144469 --source fastmoss

# Batch with videos
python run_scraper.py --batch-file products.csv --source fastmoss --download-videos
```

### Scrape from Tabcut (default)

```bash
# Single product (--source tabcut is optional, it's the default)
python run_scraper.py --product-id 1729630936525936882

# Or explicitly specify tabcut
python run_scraper.py --product-id 1729630936525936882 --source tabcut
```

## Authentication

### FastMoss Login
- **Method**: Phone number + password
- **Credentials**: In `.env` (repository root)
  - `FASTMOSS_USERNAME=11476899`
  - `FASTMOSS_PASSWORD=abc123456`
- **Login Flow**: Auto-clicks "密码登录" (Password Login) then fills credentials

### Tabcut Login  
- **Method**: Phone number + password
- **Credentials**: In `.env` (repository root)
  - `TABCUT_USERNAME=13360945260`
  - `TABCUT_PASSWORD=qq123123`

## Output Files

Both scrapers create the same folder structure:

```
product_list/{product_id}/
├── fastmoss_data.json    # From FastMoss scraper
├── tabcut_data.json      # From Tabcut scraper
├── product_images/       # Product images
└── ref_video/            # Downloaded videos (if --download-videos)
```

## Command Reference

| Command | Description |
|---------|-------------|
| `--source tabcut` | Scrape from tabcut.com (default) |
| `--source fastmoss` | Scrape from fastmoss.com |
| `--product-id ID` | Single product ID |
| `--batch-file FILE` | CSV file with product IDs |
| `--download-videos` | Download top 5 videos |
| `--resume` | Resume interrupted batch |

## Notes

- FastMoss may have different data availability (some data behind premium accounts)
- Both scrapers use the same data models for consistency
- Output JSON format is identical for both sources
- You can scrape the same product from both sources to compare data

