#!/usr/bin/env python3
"""
TikTok Shop Product Scraper - Full Cloud Version
Streamlit app for scraping TikTok shop product data directly in the cloud.
"""

import streamlit as st
import asyncio
import sys
import os
from pathlib import Path
from typing import List
import pandas as pd
import json
from datetime import datetime
import io
import subprocess

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))


# Install Playwright browsers on first run
@st.cache_resource
def install_playwright_browsers():
    """Install Playwright browsers if not already installed."""
    try:
        # Check if chromium is already installed
        result = subprocess.run(
            ["playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True
        )

        # If not installed, install it
        if "chromium" in result.stdout or result.returncode != 0:
            st.info("📦 Installing Playwright Chromium browser (first run only, ~2 minutes)...")

            # Install chromium
            install_result = subprocess.run(
                ["playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                timeout=300
            )

            if install_result.returncode == 0:
                st.success("✅ Playwright browser installed successfully!")
            else:
                st.error(f"❌ Failed to install Playwright: {install_result.stderr}")
                return False

        return True

    except Exception as e:
        st.error(f"❌ Error installing Playwright: {str(e)}")
        return False

from tabcut_scraper.scraper import TabcutScraper
from tabcut_scraper.models import ScraperConfig
from tabcut_scraper.utils import setup_logging


# Page configuration
st.set_page_config(
    page_title="TikTok Shop Product Scraper",
    page_icon="🛍️",
    layout="wide"
)


def init_session_state():
    """Initialize session state variables."""
    if 'scraping_results' not in st.session_state:
        st.session_state.scraping_results = None
    if 'is_scraping' not in st.session_state:
        st.session_state.is_scraping = False


async def scrape_products(
    product_ids: List[str],
    download_videos: bool,
    progress_placeholder,
    status_placeholder
) -> dict:
    """
    Scrape products with progress updates.

    Args:
        product_ids: List of product IDs to scrape
        download_videos: Whether to download videos
        progress_placeholder: Streamlit placeholder for progress bar
        status_placeholder: Streamlit placeholder for status messages

    Returns:
        Results dictionary with completed and failed products
    """
    results = {
        'completed': [],
        'failed': [],
        'data': []
    }

    # Get credentials from Streamlit secrets
    try:
        username = st.secrets["TABCUT_USERNAME"]
        password = st.secrets["TABCUT_PASSWORD"]
    except Exception as e:
        st.error(f"❌ Credentials not configured in Streamlit Secrets! Error: {e}")
        st.info("💡 Go to app Settings → Secrets and add TABCUT_USERNAME and TABCUT_PASSWORD")
        return results

    # Set environment variables for the scraper
    os.environ["TABCUT_USERNAME"] = username
    os.environ["TABCUT_PASSWORD"] = password

    # Create configuration
    config = ScraperConfig(
        headless=True,
        timeout=30000,
        max_retries=3,
        download_timeout=300000,
        output_base_dir=str(Path(__file__).parent / "product_list"),
        log_level="INFO"
    )

    # Setup logging
    setup_logging(log_dir='logs', log_level='INFO')

    total = len(product_ids)

    try:
        async with TabcutScraper(config) as scraper:
            for i, product_id in enumerate(product_ids, 1):
                # Update progress
                progress = i / total
                progress_placeholder.progress(progress, text=f"Processing product {i}/{total}: {product_id}")

                try:
                    status_placeholder.info(f"🔄 Scraping product {product_id}...")

                    await scraper.scrape_product(
                        product_id,
                        download_videos=download_videos
                    )

                    results['completed'].append(product_id)

                    # Load scraped data
                    data_file = Path(config.output_base_dir) / product_id / "tabcut_data.json"
                    if data_file.exists():
                        with open(data_file) as f:
                            results['data'].append(json.load(f))

                    status_placeholder.success(f"✅ Product {product_id} completed!")

                except Exception as e:
                    error_msg = str(e)
                    results['failed'].append({'product_id': product_id, 'error': error_msg})
                    status_placeholder.error(f"❌ Product {product_id} failed: {error_msg}")

        progress_placeholder.progress(1.0, text="✅ All products processed!")

    except Exception as e:
        status_placeholder.error(f"❌ Scraping error: {str(e)}")
        st.exception(e)

    return results


def create_summary_dataframe(data_list: List[dict]) -> pd.DataFrame:
    """Create summary DataFrame from scraped data."""
    summary_data = []

    for item in data_list:
        product_info = item.get('product_info', {})
        sales_data = item.get('sales_data', {})
        video_analysis = item.get('video_analysis', {})

        summary_data.append({
            'Product ID': item.get('product_id', 'N/A'),
            'Product Name': product_info.get('product_name', 'N/A'),
            'Shop Owner': product_info.get('shop_owner', 'N/A'),
            'Total Sales': product_info.get('total_sales', 0),
            'Total Revenue': product_info.get('total_sales_revenue', 'N/A'),
            'Period': sales_data.get('date_range', 'N/A'),
            'Period Sales': sales_data.get('sales_count', 0),
            'Period Revenue': sales_data.get('sales_revenue', 'N/A'),
            'Related Videos': sales_data.get('related_videos', 0),
            'Conversion Rate': sales_data.get('conversion_rate', 'N/A'),
            'Video Count': video_analysis.get('带货视频数', 0),
        })

    return pd.DataFrame(summary_data)


def display_results(results: dict):
    """Display scraping results."""
    st.subheader("📊 Scraping Results")

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("✅ Completed", len(results['completed']))
    with col2:
        st.metric("❌ Failed", len(results['failed']))
    with col3:
        total = len(results['completed']) + len(results['failed'])
        success_rate = (len(results['completed']) / total * 100) if total > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")

    # Show failed products
    if results['failed']:
        st.warning("⚠️ Failed Products:")
        failed_df = pd.DataFrame(results['failed'])
        st.dataframe(failed_df, use_container_width=True)

    # Show scraped data
    if results['data']:
        st.success("✅ Scraped Data:")

        # Summary table
        summary_df = create_summary_dataframe(results['data'])
        st.dataframe(summary_df, use_container_width=True)

        # Download button
        csv = summary_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Summary (CSV)",
            data=csv,
            file_name=f"scraping_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        # Download full JSON
        json_str = json.dumps(results['data'], indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Download Full Data (JSON)",
            data=json_str,
            file_name=f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def main():
    """Main Streamlit app."""
    init_session_state()

    # Header
    st.title("🛍️ TikTok Shop Product Scraper")
    st.markdown("**Cloud-Powered Product Data Extraction**")

    # Install Playwright browsers (first run only)
    if not install_playwright_browsers():
        st.error("⚠️ Failed to install Playwright browsers. Please contact administrator.")
        st.stop()

    # Check for credentials
    try:
        _ = st.secrets["TABCUT_USERNAME"]
        _ = st.secrets["TABCUT_PASSWORD"]
        credentials_ok = True
    except:
        credentials_ok = False
        st.error("⚠️ **Credentials not configured!**")
        st.info("""
        Please configure your tabcut.com credentials:
        1. Go to app Settings (⚙️)
        2. Click "Secrets"
        3. Add:
        ```toml
        TABCUT_USERNAME = "your_username"
        TABCUT_PASSWORD = "your_password"
        ```
        """)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        download_videos = st.checkbox(
            "Download top 5 videos",
            value=False,
            help="Download reference videos (takes longer, uses more resources)"
        )

        st.divider()

        st.markdown("### 📚 How to Use")
        st.markdown("""
        1. Enter product IDs (one per line)
        2. Or upload a CSV file
        3. Click "Start Scraping"
        4. Wait for results
        5. Download reports
        """)

        st.divider()

        st.markdown("### ℹ️ About")
        st.markdown("""
        Scrapes TikTok shop data:
        - Product information
        - Sales analytics
        - Video performance
        - Top videos (optional download)
        """)

    if not credentials_ok:
        st.stop()

    # Main content
    tab1, tab2 = st.tabs(["🎯 Single Product", "📦 Batch Mode"])

    with tab1:
        st.subheader("Scrape Single Product")

        product_id = st.text_input(
            "Product ID",
            placeholder="e.g., 1729630936525936882",
            help="Enter the TikTok shop product ID",
            disabled=st.session_state.is_scraping
        )

        if st.button("Start Scraping", key="single", type="primary", disabled=st.session_state.is_scraping):
            if not product_id:
                st.error("Please enter a product ID")
            else:
                st.session_state.is_scraping = True

                progress_placeholder = st.empty()
                status_placeholder = st.empty()

                with st.spinner("Initializing scraper..."):
                    results = asyncio.run(scrape_products(
                        [product_id],
                        download_videos,
                        progress_placeholder,
                        status_placeholder
                    ))

                st.session_state.scraping_results = results
                st.session_state.is_scraping = False

                if results['completed'] or results['failed']:
                    display_results(results)

    with tab2:
        st.subheader("Batch Scrape Multiple Products")

        # Text area for product IDs
        product_ids_text = st.text_area(
            "Product IDs (one per line)",
            height=150,
            placeholder="1729630936525936882\n7575477825742982403\n7520182265683381526",
            disabled=st.session_state.is_scraping
        )

        # OR CSV upload
        st.markdown("**OR upload CSV:**")
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="CSV with product_id column",
            disabled=st.session_state.is_scraping
        )

        # Parse product IDs
        product_ids = []

        if product_ids_text:
            product_ids = [pid.strip() for pid in product_ids_text.split('\n') if pid.strip()]

        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            if 'product_id' in df.columns:
                product_ids = df['product_id'].astype(str).tolist()
                st.success(f"✅ Loaded {len(product_ids)} products from CSV")
            else:
                st.error("❌ CSV must have a 'product_id' column")

        if product_ids:
            st.info(f"📋 {len(product_ids)} products ready to scrape")

            # Show preview
            with st.expander("Preview product IDs"):
                st.write(product_ids)

        if st.button("Start Batch Scraping", key="batch", type="primary", disabled=st.session_state.is_scraping or not product_ids):
            st.session_state.is_scraping = True

            progress_placeholder = st.empty()
            status_placeholder = st.empty()

            with st.spinner("Initializing scraper..."):
                results = asyncio.run(scrape_products(
                    product_ids,
                    download_videos,
                    progress_placeholder,
                    status_placeholder
                ))

            st.session_state.scraping_results = results
            st.session_state.is_scraping = False

            if results['completed'] or results['failed']:
                display_results(results)

    # Show previous results if available
    if st.session_state.scraping_results and not st.session_state.is_scraping:
        st.divider()
        display_results(st.session_state.scraping_results)


if __name__ == "__main__":
    main()
