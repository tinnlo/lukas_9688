# Quick Start Guide - TikTok Shop Product Scraper Results Viewer

## For Non-Technical Users (Your Colleagues)

This app lets you view TikTok shop product data **without any coding**.

## Access the Web App

Visit: **[Your App URL - bookmark this!]**

## How to Use

### Step 1: Get Data Files

Ask your administrator for the scraped data files (`.json` files).

They will send you files like:
- `1729630936525936882/tabcut_data.json`
- `7575477825742982403/tabcut_data.json`

### Step 2: Upload to App

1. Open the app in your browser
2. Go to **"📤 Upload Results"** tab
3. Click **"Browse files"**
4. Select one or more JSON files
5. Click **"Open"**

### Step 3: View the Data

You'll see:
- **Product information** (name, shop owner, total sales)
- **Sales analytics** (revenue, conversion rates)
- **Video performance** (top videos, views, engagement)
- **Detailed breakdowns** for each product

### Step 4: Download Reports

Click **"📥 Download Summary (CSV)"** to get:
- Excel-friendly CSV file
- All products in one table
- Easy to analyze in Excel/Google Sheets

## Features

### 📤 Upload Results
- Upload single or multiple product data files
- View detailed information for each product
- Download individual or summary reports

### 📊 Batch Analysis
- Upload many files at once
- See aggregate metrics across all products
- Filter by sales numbers or video count
- Download filtered results

### ℹ️ Instructions
- Complete workflow guide
- Help and support information

## What Data You'll See

Each product shows:
- ✅ Product name and shop owner
- ✅ Total sales and revenue
- ✅ Sales period (7-day or 30-day data)
- ✅ Related videos count
- ✅ Conversion rates
- ✅ Top 5 performing videos with metrics
- ✅ Video analysis (creators, views, estimated sales)

## Tips

- **Multiple files**: You can upload many files at once for batch analysis
- **CSV export**: Perfect for creating reports in Excel
- **Bookmark the app**: Save the URL for easy access
- **Share the link**: Send the app URL to team members

## Need Data?

Contact your administrator to:
- Request new product data
- Get scraped files
- Report any issues

---

## For Administrators (Technical Users)

### Your Workflow

1. **Run the scraper locally:**
   ```bash
   cd scripts
   source venv/bin/activate
   python run_scraper.py --batch-file products.csv --download-videos
   ```

2. **Share results:**
   - Find JSON files in `product_list/{product_id}/tabcut_data.json`
   - Send to colleagues via email/Slack/shared folder

3. **Colleagues use the app:**
   - They upload JSON files
   - View and analyze data
   - Download reports

### Scraper Location

- **Repository:** https://github.com/tinnlo/lukas_9688
- **Scraper:** `scripts/run_scraper.py`
- **Documentation:** `scripts/README.md`

### Key Commands

```bash
# Single product
python run_scraper.py --product-id 1729630936525936882

# Batch with videos
python run_scraper.py --batch-file products.csv --download-videos

# Resume interrupted batch
python run_scraper.py --batch-file products.csv --resume
```

---

**Questions?**

Ask your administrator or check the **"ℹ️ Instructions"** tab in the app.
