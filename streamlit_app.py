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
import zipfile
from loguru import logger

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
            # Show message only during actual installation
            with st.spinner("📦 Installing Playwright Chromium browser (first run only, ~2 minutes)..."):
                # Install chromium
                install_result = subprocess.run(
                    ["playwright", "install", "chromium"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if install_result.returncode == 0:
                    st.success("✅ Playwright browser installed successfully!")
                    return True
                else:
                    st.error(f"❌ Failed to install Playwright: {install_result.stderr}")
                    return False

        # Already installed - no message needed
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
    layout="centered"
)


def init_session_state():
    """Initialize session state variables."""
    if 'scraping_results' not in st.session_state:
        st.session_state.scraping_results = None
    if 'is_scraping' not in st.session_state:
        st.session_state.is_scraping = False
    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = {}
    if 'show_carousel' not in st.session_state:
        st.session_state.show_carousel = None


def create_images_zip(product_id: str, images_dir: Path) -> bytes:
    """Create a ZIP file of all product images."""
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")) + list(images_dir.glob("*.webp"))

        for img_file in sorted(image_files):
            # Add file to zip with relative path
            zip_file.write(img_file, arcname=img_file.name)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def generate_markdown_report(data: dict) -> str:
    """Generate markdown report from scraped data."""
    product_info = data.get('product_info', {})
    sales_data = data.get('sales_data', {})
    video_analysis = data.get('video_analysis', {})
    top_videos = data.get('top_videos', [])

    md = f"""# {product_info.get('product_name', 'Product Report')}

## Product Information

- **Product ID:** {data.get('product_id', 'N/A')}
- **Shop Owner:** {product_info.get('shop_owner', 'N/A')}
- **Total Sales:** {product_info.get('total_sales', 0):,}
- **Total Revenue:** {product_info.get('total_sales_revenue', 'N/A')}
- **Scraped At:** {data.get('scraped_at', 'N/A')}

---

## Sales Analytics

- **Period:** {sales_data.get('date_range', 'N/A')}
- **Period Sales:** {sales_data.get('sales_count', 0):,}
- **Period Revenue:** {sales_data.get('sales_revenue', 'N/A')}
- **Related Videos:** {sales_data.get('related_videos', 0)}
- **Conversion Rate:** {sales_data.get('conversion_rate', 'N/A')}

---

## Video Analysis

- **带货视频数:** {video_analysis.get('带货视频数', 0)}
- **带货视频达人数:** {video_analysis.get('带货视频达人数', 0)}
- **带货视频销量:** {video_analysis.get('带货视频销量', 0)}
- **带货视频销售额:** {video_analysis.get('带货视频销售额', 'N/A')}
- **广告成交金额:** {video_analysis.get('广告成交金额', 'N/A')}

---

## Top Performing Videos

"""

    if top_videos:
        for video in top_videos[:10]:  # Top 10
            # Safe formatting for numeric values
            total_views = video.get('total_views', 0)
            total_views_str = f"{int(total_views):,}" if isinstance(total_views, (int, float)) else str(total_views)

            estimated_sales = video.get('estimated_sales', 0)
            estimated_sales_str = f"{int(estimated_sales):,}" if isinstance(estimated_sales, (int, float)) else str(estimated_sales)

            # Clean up video title - remove metadata after "发现时间" if present
            title = video.get('title', 'Video')
            if '发现时间' in title:
                title = title.split('发现时间')[0].strip()

            md += f"""### {video.get('rank', '?')}. {title}

- **Creator:** @{video.get('creator_username', 'unknown')}
- **Published:** {video.get('publish_date', 'N/A')}
- **Views:** {total_views_str}
- **Estimated Sales:** {estimated_sales_str}
- **Estimated Revenue:** {video.get('estimated_revenue', 'N/A')}

"""
    else:
        md += "*No video data available*\n"

    md += "\n---\n\n*Generated by TikTok Shop Product Scraper*\n"

    return md


async def scrape_products(
    product_ids: List[str],
    download_videos: bool,
    download_images: bool,
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

                    # Download product images if requested
                    if download_images:
                        from tabcut_scraper.downloader import VideoDownloader
                        product_dir = Path(config.output_base_dir) / product_id

                        status_placeholder.info(f"📸 Downloading product images for {product_id}...")
                        downloader = VideoDownloader(scraper.page, config.download_timeout)
                        image_paths = await downloader.download_product_images(product_dir)
                        logger.info(f"Downloaded {len(image_paths)} product images")

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

        # Display product images if available
        for data in results['data']:
            product_id = data.get('product_id')
            if product_id:
                images_dir = Path(f"product_list/{product_id}/product_images")
                if images_dir.exists():
                    image_files = sorted(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")) + list(images_dir.glob("*.webp")))
                    if image_files:
                        product_name = data.get('product_info', {}).get('product_name', product_id)[:50]

                        with st.expander(f"📸 Product Images - {product_name}... ({len(image_files)} images)"):
                            # Download all images button
                            zip_data = create_images_zip(product_id, images_dir)
                            st.download_button(
                                label=f"📦 Download All Images ({len(image_files)} files)",
                                data=zip_data,
                                file_name=f"product_{product_id}_images_{datetime.now().strftime('%Y%m%d')}.zip",
                                mime="application/zip",
                                key=f"download_images_{product_id}_{datetime.now().timestamp()}"
                            )

                            st.markdown("---")

                            # Image carousel
                            carousel_key = f"carousel_{product_id}"

                            # Initialize carousel index for this product
                            if carousel_key not in st.session_state.carousel_index:
                                st.session_state.carousel_index[carousel_key] = 0

                            current_idx = st.session_state.carousel_index[carousel_key]

                            # Navigation buttons
                            col1, col2, col3 = st.columns([1, 3, 1])

                            with col1:
                                if st.button("⬅️ Prev", key=f"prev_{product_id}", disabled=current_idx == 0):
                                    st.session_state.carousel_index[carousel_key] = max(0, current_idx - 1)
                                    st.rerun()

                            with col2:
                                st.markdown(f"<center><b>Image {current_idx + 1} of {len(image_files)}</b></center>", unsafe_allow_html=True)

                            with col3:
                                if st.button("Next ➡️", key=f"next_{product_id}", disabled=current_idx >= len(image_files) - 1):
                                    st.session_state.carousel_index[carousel_key] = min(len(image_files) - 1, current_idx + 1)
                                    st.rerun()

                            # Display current full-size image (max 700px)
                            current_image = image_files[current_idx]
                            st.image(str(current_image), width=700, caption=current_image.name)

                            st.markdown("---")

                            # Thumbnail navigation
                            st.markdown("**Click thumbnail to jump:**")
                            thumb_cols = st.columns(min(6, len(image_files)))
                            for idx, img_file in enumerate(image_files):
                                with thumb_cols[idx % 6]:
                                    if st.button(
                                        f"🖼️ {idx + 1}",
                                        key=f"thumb_{product_id}_{idx}",
                                        type="primary" if idx == current_idx else "secondary",
                                        use_container_width=True
                                    ):
                                        st.session_state.carousel_index[carousel_key] = idx
                                        st.rerun()

        # Download buttons
        col1, col2 = st.columns(2)

        with col1:
            # Generate markdown report
            if len(results['data']) == 1:
                md_content = generate_markdown_report(results['data'][0])
                st.download_button(
                    label="📄 Download Report (Markdown)",
                    data=md_content,
                    file_name=f"product_{results['data'][0].get('product_id', 'report')}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    key=f"download_md_{datetime.now().timestamp()}"
                )
            else:
                # For multiple products, create combined markdown
                md_content = f"# TikTok Shop Products Report\n\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n---\n\n"
                for data in results['data']:
                    md_content += generate_markdown_report(data) + "\n---\n\n"

                st.download_button(
                    label="📄 Download Report (Markdown)",
                    data=md_content,
                    file_name=f"products_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    key=f"download_md_{datetime.now().timestamp()}"
                )

        with col2:
            # Download full JSON
            json_str = json.dumps(results['data'], indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download Full Data (JSON)",
                data=json_str,
                file_name=f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key=f"download_json_{datetime.now().timestamp()}"
            )


def main():
    """Main Streamlit app."""
    init_session_state()

    # Custom CSS to limit max width and center entire app (sidebar + main)
    st.markdown("""
        <style>
        /* Constrain the entire app container */
        .appview-container .main {
            max-width: 1280px;
            margin: 0 auto;
        }

        /* Ensure sidebar + main content are within the constraint */
        section[data-testid="stSidebar"],
        .main .block-container {
            max-width: 100%;
        }

        /* Center the root container */
        .stApp {
            max-width: 1280px;
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)

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

        download_images = st.checkbox(
            "Download product images",
            value=True,
            help="Download product carousel images"
        )

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
                        download_images,
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
                    download_images,
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
