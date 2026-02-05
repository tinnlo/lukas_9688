# Streamlit Cloud Deployment Guide (Simplified Version)

This guide shows you how to deploy the **TikTok Shop Product Scraper Results Viewer** as a web app.

## What This App Does

**This is a RESULTS VIEWER, not a scraper runner.**

- ✅ Colleagues upload scraped JSON files
- ✅ View beautiful data visualizations
- ✅ Download reports and summaries
- ✅ Batch analysis dashboard
- ❌ Does NOT run the scraper (you do that locally)

## Why This Approach?

The scraper requires **browser automation (Playwright)** which doesn't work well on Streamlit Cloud free tier. Instead:

1. **You (admin)** run the scraper locally
2. **Colleagues** upload results to this app for viewing
3. **Everyone** benefits from easy data analysis

## Deployment Steps

### Step 1: Code is Ready ✅

All code is already pushed to GitHub!

### Step 2: Deploy to Streamlit Cloud

1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign in with GitHub
3. Click **"Deploy a public app from GitHub"**
4. Configure:
   - **Repository:** `tinnlo/lukas_9688`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL:** Choose a name (e.g., `tiktok-scraper-viewer`)
5. Click **"Deploy!"**

The app will deploy in **~1 minute** (much faster than before!)

### Step 3: Test the App

1. Once deployed, click **"Open app"**
2. You should see the Results Viewer interface
3. Try uploading a sample JSON file

### Step 4: Share with Colleagues

Share the URL: `https://your-app-name.streamlit.app`

## How Colleagues Use the App

### For Non-Technical Users:

1. **Receive JSON files** from you (via email, Slack, shared folder)
2. **Open the app** in their browser
3. **Upload JSON files** in the "Upload Results" tab
4. **View data** in tables and charts
5. **Download reports** as CSV for Excel

### What They'll See:

- Product information
- Sales analytics
- Video performance metrics
- Top performing videos
- Batch analysis dashboard

## How You (Admin) Use the Workflow

### Step 1: Run Scraper Locally

```bash
cd scripts
python3 run_scraper.py --batch-file products.csv --download-videos
```

Results saved to: `product_list/{product_id}/tabcut_data.json`

### Step 2: Share Results

**Option A: Direct File Sharing**
- Email JSON files to colleagues
- Or use Slack/Teams/Dropbox

**Option B: Colleagues Access Directly**
- If they have access to the shared folder
- They can grab JSON files themselves

### Step 3: Colleagues View in App

They upload the JSON files to the Streamlit app.

## Features

### Upload Results Tab
- Upload single or multiple JSON files
- View detailed product information
- Download summary CSV

### Batch Analysis Tab
- Upload many files at once
- See aggregate metrics
- Filter by sales/videos
- Download filtered results

### Instructions Tab
- Complete workflow guide
- Commands for running scraper
- Help for non-technical users

## No Secrets Required!

Unlike the previous version, this app **doesn't need secrets** because:
- It doesn't scrape anything
- It only displays data
- No authentication needed

## Troubleshooting

### App Won't Start
- Check Streamlit Cloud logs
- Usually deploys in 1-2 minutes
- If stuck >5 minutes, cancel and redeploy

### Can't Upload Files
- File must be valid JSON
- Use files from `product_list/{product_id}/tabcut_data.json`

### Data Looks Wrong
- Verify JSON file structure matches scraper output
- Check for corrupted files

## Updating the App

When you update the code:

```bash
git add streamlit_app.py
git commit -m "Update results viewer

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push origin main
```

Streamlit auto-redeploys in ~1 minute.

## Cost

**100% FREE on Streamlit Cloud:**
- Public apps unlimited
- No resource issues (very lightweight)
- Always available

## Alternative: Local Sharing

If you prefer not to use cloud:

```bash
# Run locally
streamlit run streamlit_app.py

# Access on LAN
streamlit run streamlit_app.py --server.address 0.0.0.0

# Colleagues visit: http://YOUR_IP:8501
```

---

**Quick Reference:**

| Task | Solution |
|------|----------|
| Deploy app | Streamlit Cloud → Deploy from GitHub |
| Update app | `git push origin main` |
| Share results | Email JSON files or shared folder |
| View data | Colleagues upload to app |
| Download reports | Click download buttons in app |

## Summary

This simplified approach:
- ✅ Deploys fast (1 minute)
- ✅ No resource issues
- ✅ 100% free
- ✅ Easy for non-technical users
- ✅ You control scraping locally
- ✅ Colleagues get beautiful UI

Perfect for your use case!
