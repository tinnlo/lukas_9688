# Streamlit Cloud Deployment Guide

This guide shows you how to deploy the TikTok Shop Product Scraper as a web app that your colleagues can access from anywhere.

## Prerequisites

- GitHub account (you already have this!)
- Streamlit Cloud account (free)
- Tabcut.com credentials

## Step 1: Push Code to GitHub

First, make sure all files are committed and pushed:

```bash
# Check status
git status

# Add new files
git add streamlit_app.py requirements.txt .streamlit/ STREAMLIT_DEPLOYMENT.md .gitignore

# Commit
git commit -m "Add Streamlit web interface for non-technical users

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

## Step 2: Create Streamlit Cloud Account

1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Click **"Sign up"**
3. Choose **"Continue with GitHub"**
4. Authorize Streamlit to access your GitHub repositories

## Step 3: Deploy Your App

1. **Click "New app"** in Streamlit Cloud dashboard

2. **Configure deployment:**
   - **Repository:** `tinnlo/lukas_9688`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL:** Choose a custom URL (e.g., `tiktok-scraper-lukas` or use auto-generated)

3. **Click "Deploy"**

   The app will start building. This takes 2-5 minutes on first deployment.

## Step 4: Configure Secrets (IMPORTANT!)

After deployment starts, you need to add your Tabcut credentials:

1. In Streamlit Cloud dashboard, click on your app
2. Click **"⚙️ Settings"** (top right)
3. Go to **"Secrets"** tab
4. Paste the following (replace with your actual credentials):

```toml
TABCUT_USERNAME = "your_actual_username"
TABCUT_PASSWORD = "your_actual_password"
```

5. Click **"Save"**
6. The app will automatically restart with the new secrets

## Step 5: Install Playwright (Critical!)

Streamlit Cloud needs additional setup for Playwright:

1. In your app settings, go to **"Advanced settings"**
2. Add a `packages.txt` file to your repository:

```bash
# Create packages.txt in repository root
cat > packages.txt << 'EOF'
libnss3
libnspr4
libatk1.0-0
libatk-bridge2.0-0
libcups2
libdrm2
libxkbcommon0
libxcomposite1
libxdamage1
libxfixes3
libxrandr2
libgbm1
libasound2
EOF
```

3. Create a post-install script for Playwright:

```bash
# Create .streamlit/setup.sh
mkdir -p .streamlit
cat > .streamlit/setup.sh << 'EOF'
#!/bin/bash
playwright install chromium
playwright install-deps chromium
EOF

chmod +x .streamlit/setup.sh
```

4. Update your repository:

```bash
git add packages.txt .streamlit/setup.sh
git commit -m "Add Playwright dependencies for Streamlit Cloud

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push origin main
```

5. The app will auto-redeploy with Playwright support

## Step 6: Test Your App

1. Once deployed, click **"Open app"** to visit your web app
2. Test with a single product ID first: `1729630936525936882`
3. Verify the scraping works and data is returned

## Step 7: Share with Colleagues

Your app is now live! Share the URL with your team:

```
https://your-app-name.streamlit.app
```

**What colleagues need to do:**
1. Click the link
2. That's it! No installation, no setup

They can:
- Paste product IDs to scrape single products
- Upload CSV files for batch scraping
- Download results as JSON
- See real-time progress

## Usage Instructions for Colleagues

### Single Product Mode

1. Open the app URL
2. Go to **"🎯 Single Product"** tab
3. Enter a product ID (e.g., `1729630936525936882`)
4. Optional: Check "Download top 5 videos" in sidebar
5. Click **"Start Scraping"**
6. Wait for completion
7. Download results

### Batch Mode

1. Prepare a CSV file:
   ```csv
   product_id
   1729630936525936882
   7575477825742982403
   7520182265683381526
   ```

2. Go to **"📦 Batch Mode"** tab
3. Upload the CSV file
4. Review the product list
5. Optional: Check "Download top 5 videos"
6. Click **"Start Batch Scraping"**
7. Watch real-time progress
8. Download results when complete

## Troubleshooting

### App Won't Start
- **Check secrets:** Make sure `TABCUT_USERNAME` and `TABCUT_PASSWORD` are set correctly
- **Check logs:** Click "Manage app" → "Logs" to see error messages
- **Playwright issue:** Make sure `packages.txt` and setup script are committed

### Scraping Fails
- **Verify credentials:** Wrong username/password in secrets
- **Tabcut.com down:** Check if tabcut.com is accessible
- **Rate limiting:** Too many requests too fast

### Slow Performance
- **Video downloads:** Disable video downloads for faster scraping
- **Large batches:** Break into smaller batches (10-20 products at a time)
- **Free tier limits:** Streamlit Cloud free tier has resource limits

## Updating the App

When you make changes to the code:

```bash
git add .
git commit -m "Your update message

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push origin main
```

Streamlit Cloud will **automatically redeploy** within 1-2 minutes.

## Cost & Limits

**Streamlit Cloud Free Tier:**
- ✅ Unlimited public apps
- ✅ 1GB RAM per app
- ✅ Auto-redeploy from GitHub
- ✅ Custom URLs
- ⚠️ Apps sleep after 7 days of inactivity (wake up on visit)

**If you need more:**
- **Streamlit Cloud Team/Business** ($250-$1000/month) for:
  - More resources
  - Private apps
  - Always-on apps
  - Priority support

For your use case, **free tier should be sufficient**.

## Security Notes

- ✅ Credentials are stored securely in Streamlit secrets (encrypted)
- ✅ Secrets are never exposed in code or logs
- ⚠️ App is public by default (anyone with URL can use it)
- ⚠️ Scraped data is stored temporarily on Streamlit Cloud

**For private apps:** Upgrade to Streamlit Cloud Team plan ($250/month)

## Alternative: Run Locally with LAN Access

If you prefer to run locally and have colleagues access via LAN:

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Create local secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your credentials

# Run the app
streamlit run streamlit_app.py --server.address 0.0.0.0
```

Colleagues on same network visit: `http://YOUR_IP:8501`

## Support

For issues or questions:
- Check Streamlit Cloud logs: Settings → Logs
- Review GitHub repo: https://github.com/tinnlo/lukas_9688
- Streamlit docs: https://docs.streamlit.io

---

**Quick Reference:**

| Task | Command/Link |
|------|--------------|
| Deploy app | https://streamlit.io/cloud |
| Add secrets | App Settings → Secrets |
| View logs | App Settings → Logs |
| Update app | `git push origin main` |
| App URL | `https://your-app.streamlit.app` |
