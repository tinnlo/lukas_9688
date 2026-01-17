# TikTok Product Folder Structure Patterns

The repository supports TWO folder patterns for organizing products:

## Pattern 1: Dated Batches (Daily Workflow)
```
product_list/YYYYMMDD/{product_id}/
├── tabcut_data.json
├── product_images/
│   ├── image_analysis.md
│   └── product_image_*.webp
├── ref_video/
│   ├── video_*_analysis.md
│   └── video_synthesis.md
└── scripts/
    ├── Script1.md
    ├── Script2.md
    ├── Script3.md
    └── Campaign_Summary.md
```

**Example:** `product_list/20260116/1729621910970800644/`

## Pattern 2: Category-Based (Special Campaigns/Vendors)
```
product_list/{category}/{product_id}/
├── tabcut_data.json
├── product_images/
│   ├── image_analysis.md
│   └── product_image_*.webp
├── ref_video/
│   ├── video_*_analysis.md
│   └── video_synthesis.md
└── scripts/
    ├── Script1.md
    ├── Script2.md
    ├── Script3.md
    └── Campaign_Summary.md
```

**Categories in use:**
- `samples` - Sample/test products
- `htc` - HTC vendor products  
- `sonnesee` - Sonnesee vendor products
- `tools` - MAWIRON tools products

**Example:** `product_list/htc/1729479916562717270/`

## Key Rules

1. **Scripts location**: Always `{base}/{product_id}/scripts/` (NEVER `scripts/YYYYMMDD/`)
2. **Campaign_Summary.md**: Always inside `scripts/` folder (not at product root)
3. **Internal structure**: Identical for both patterns (product_images, ref_video, scripts)
4. **All skills must support both patterns** using `--base` parameter

## Usage in Scripts

```bash
# Dated batch
python script.py {product_id} --date 20260116

# Category-based  
python script.py {product_id} --base product_list/samples
python script.py {product_id} --base product_list/htc
```
