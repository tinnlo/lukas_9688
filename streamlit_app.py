#!/usr/bin/env python3
"""
TikTok Shop Product Scraper - Web Interface
Streamlit app for non-technical users to scrape TikTok shop product data.
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

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

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
    username = st.secrets.get("TABCUT_USERNAME", os.getenv("TABCUT_USERNAME"))
    password = st.secrets.get("TABCUT_PASSWORD", os.getenv("TABCUT_PASSWORD"))

    if not username or not password:
        st.error("❌ Credentials not configured! Please contact administrator.")
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

    return results


def display_results(results: dict):
    """Display scraping results in a nice format."""
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

    # Show failed products if any
    if results['failed']:
        st.warning("⚠️ Failed Products:")
        failed_df = pd.DataFrame(results['failed'])
        st.dataframe(failed_df, use_container_width=True)

    # Show scraped data
    if results['data']:
        st.success("✅ Scraped Data:")

        # Create summary table
        summary_data = []
        for item in results['data']:
            product_info = item.get('product_info', {})
            sales_data = item.get('sales_data', {})

            summary_data.append({
                'Product ID': item.get('product_id'),
                'Product Name': product_info.get('product_name', 'N/A'),
                'Shop Owner': product_info.get('shop_owner', 'N/A'),
                'Total Sales': product_info.get('total_sales', 0),
                'Sales Revenue': product_info.get('total_sales_revenue', 'N/A'),
                'Period': sales_data.get('date_range', 'N/A'),
                'Related Videos': sales_data.get('related_videos', 0)
            })

        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)

        # Download button for full data
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
    st.markdown("Extract product data from tabcut.com - No coding required!")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        download_videos = st.checkbox(
            "Download top 5 videos",
            help="Download reference videos for each product (takes longer)"
        )

        st.divider()

        st.markdown("### 📚 How to Use")
        st.markdown("""
        1. **Single Product**: Enter one product ID
        2. **Batch Mode**: Upload a CSV file with product IDs
        3. Click "Start Scraping"
        4. Download results when complete
        """)

        st.divider()

        st.markdown("### ℹ️ About")
        st.markdown("""
        This tool scrapes TikTok shop product data including:
        - Product information
        - Sales analytics
        - Video performance
        - Top performing videos
        """)

    # Main content
    tab1, tab2 = st.tabs(["🎯 Single Product", "📦 Batch Mode"])

    with tab1:
        st.subheader("Scrape Single Product")

        product_id = st.text_input(
            "Product ID",
            placeholder="e.g., 1729630936525936882",
            help="Enter the TikTok shop product ID"
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

        st.markdown("""
        Upload a CSV file with product IDs. The CSV should have a header row with `product_id`:

        ```
        product_id
        1729630936525936882
        7575477825742982403
        7520182265683381526
        ```
        """)

        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="CSV file with product_id column"
        )

        if uploaded_file is not None:
            # Preview the file
            df = pd.read_csv(uploaded_file)

            if 'product_id' not in df.columns:
                st.error("❌ CSV must have a 'product_id' column")
            else:
                st.success(f"✅ Found {len(df)} products")
                st.dataframe(df.head(10), use_container_width=True)

                if len(df) > 10:
                    st.info(f"Showing first 10 of {len(df)} products")

                if st.button("Start Batch Scraping", key="batch", type="primary", disabled=st.session_state.is_scraping):
                    product_ids = df['product_id'].astype(str).tolist()

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
