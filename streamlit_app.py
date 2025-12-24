#!/usr/bin/env python3
"""
TikTok Shop Product Scraper - Results Viewer
Streamlit app for viewing and analyzing scraped TikTok shop product data.
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import zipfile
import io


# Page configuration
st.set_page_config(
    page_title="TikTok Shop Scraper - Results Viewer",
    page_icon="🛍️",
    layout="wide"
)


def load_json_file(uploaded_file) -> Dict:
    """Load and parse JSON file."""
    try:
        content = uploaded_file.read()
        return json.loads(content)
    except Exception as e:
        st.error(f"Error loading JSON: {e}")
        return None


def load_multiple_json_files(uploaded_files) -> List[Dict]:
    """Load multiple JSON files."""
    results = []
    for file in uploaded_files:
        data = load_json_file(file)
        if data:
            results.append(data)
    return results


def create_summary_dataframe(data_list: List[Dict]) -> pd.DataFrame:
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
            'Scraped At': item.get('scraped_at', 'N/A')
        })

    return pd.DataFrame(summary_data)


def display_product_details(data: Dict):
    """Display detailed product information."""
    st.subheader(f"📦 {data.get('product_info', {}).get('product_name', 'Product')}")

    # Product Info
    with st.expander("🏪 Product Information", expanded=True):
        product_info = data.get('product_info', {})
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Shop Owner", product_info.get('shop_owner', 'N/A'))
        with col2:
            st.metric("Total Sales", product_info.get('total_sales', 0))
        with col3:
            st.metric("Total Revenue", product_info.get('total_sales_revenue', 'N/A'))

    # Sales Data
    with st.expander("📊 Sales Analytics"):
        sales_data = data.get('sales_data', {})
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Period", sales_data.get('date_range', 'N/A'))
        with col2:
            st.metric("Sales Count", sales_data.get('sales_count', 0))
        with col3:
            st.metric("Revenue", sales_data.get('sales_revenue', 'N/A'))
        with col4:
            st.metric("Conversion Rate", sales_data.get('conversion_rate', 'N/A'))

        st.metric("Related Videos", sales_data.get('related_videos', 0))

    # Video Analysis
    with st.expander("🎥 Video Analysis"):
        video_analysis = data.get('video_analysis', {})

        col1, col2 = st.columns(2)
        with col1:
            st.metric("带货视频数", video_analysis.get('带货视频数', 0))
            st.metric("带货视频销量", video_analysis.get('带货视频销量', 0))
        with col2:
            st.metric("带货视频达人数", video_analysis.get('带货视频达人数', 0))
            st.metric("带货视频销售额", video_analysis.get('带货视频销售额', 'N/A'))

    # Top Videos
    if data.get('top_videos'):
        with st.expander("🌟 Top Performing Videos"):
            videos_df = pd.DataFrame(data['top_videos'])

            # Select relevant columns
            display_cols = ['rank', 'title', 'creator_username', 'publish_date',
                          'estimated_sales', 'estimated_revenue', 'total_views']

            available_cols = [col for col in display_cols if col in videos_df.columns]
            st.dataframe(videos_df[available_cols], use_container_width=True)


def create_csv_template():
    """Create a CSV template for product IDs."""
    template = "product_id\n1729630936525936882\n7575477825742982403\n"
    return template


def main():
    """Main Streamlit app."""

    # Header
    st.title("🛍️ TikTok Shop Product Scraper")
    st.markdown("**Results Viewer & Workflow Manager**")

    # Sidebar
    with st.sidebar:
        st.header("📋 How It Works")

        st.markdown("""
        ### Workflow:

        1️⃣ **Download CSV Template**
        Add product IDs to scrape

        2️⃣ **Run Scraper Locally**
        Use the Python scraper on your computer

        3️⃣ **Upload Results Here**
        View and analyze data in this app

        4️⃣ **Share Results**
        Download reports for your team
        """)

        st.divider()

        # Download template
        st.subheader("📥 Get Started")
        template = create_csv_template()
        st.download_button(
            label="📄 Download CSV Template",
            data=template,
            file_name="product_ids_template.csv",
            mime="text/csv"
        )

        st.divider()

        st.markdown("""
        ### 💡 Need Help?

        - **Scraper Location:**
          `scripts/run_scraper.py`

        - **Command:**
          ```bash
          cd scripts
          python run_scraper.py \\
            --batch-file products.csv \\
            --download-videos
          ```

        - **Results Location:**
          `product_list/{product_id}/tabcut_data.json`
        """)

    # Main content
    tab1, tab2, tab3 = st.tabs(["📤 Upload Results", "📊 Batch Analysis", "ℹ️ Instructions"])

    with tab1:
        st.subheader("Upload Scraped Data")

        st.markdown("""
        Upload the `tabcut_data.json` files generated by the scraper.
        You can upload single or multiple files at once.
        """)

        uploaded_files = st.file_uploader(
            "Choose JSON files",
            type=['json'],
            accept_multiple_files=True,
            help="Select one or more tabcut_data.json files from product_list/{product_id}/"
        )

        if uploaded_files:
            st.success(f"✅ Loaded {len(uploaded_files)} file(s)")

            # Load all data
            data_list = load_multiple_json_files(uploaded_files)

            if data_list:
                # Summary view
                st.subheader("📊 Summary")
                summary_df = create_summary_dataframe(data_list)
                st.dataframe(summary_df, use_container_width=True)

                # Download summary
                csv = summary_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Summary (CSV)",
                    data=csv,
                    file_name=f"product_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

                st.divider()

                # Detailed view
                st.subheader("📦 Detailed Product Data")

                for i, data in enumerate(data_list):
                    with st.container():
                        display_product_details(data)

                        # Download individual JSON
                        json_str = json.dumps(data, indent=2, ensure_ascii=False)
                        st.download_button(
                            label=f"📥 Download JSON",
                            data=json_str,
                            file_name=f"product_{data.get('product_id', i)}.json",
                            mime="application/json",
                            key=f"download_{i}"
                        )

                        if i < len(data_list) - 1:
                            st.divider()

    with tab2:
        st.subheader("Batch Analysis Dashboard")

        uploaded_batch = st.file_uploader(
            "Upload multiple JSON files for batch analysis",
            type=['json'],
            accept_multiple_files=True,
            key="batch_upload"
        )

        if uploaded_batch:
            data_list = load_multiple_json_files(uploaded_batch)

            if data_list:
                # Metrics
                st.subheader("📈 Key Metrics")

                total_sales = sum(d.get('product_info', {}).get('total_sales', 0) for d in data_list)
                total_videos = sum(d.get('sales_data', {}).get('related_videos', 0) for d in data_list)
                avg_conversion = sum(
                    float(d.get('sales_data', {}).get('conversion_rate', '0').rstrip('%'))
                    for d in data_list
                ) / len(data_list) if data_list else 0

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Products", len(data_list))
                with col2:
                    st.metric("Total Sales", f"{total_sales:,}")
                with col3:
                    st.metric("Total Videos", total_videos)
                with col4:
                    st.metric("Avg Conversion", f"{avg_conversion:.2f}%")

                st.divider()

                # Detailed table
                st.subheader("📋 All Products")
                summary_df = create_summary_dataframe(data_list)

                # Add filters
                col1, col2 = st.columns(2)
                with col1:
                    min_sales = st.number_input("Min Total Sales", 0, value=0)
                with col2:
                    min_videos = st.number_input("Min Related Videos", 0, value=0)

                filtered_df = summary_df[
                    (summary_df['Total Sales'] >= min_sales) &
                    (summary_df['Related Videos'] >= min_videos)
                ]

                st.dataframe(filtered_df, use_container_width=True)

                # Download
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Filtered Results (CSV)",
                    data=csv,
                    file_name=f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

    with tab3:
        st.subheader("📖 Complete Workflow Guide")

        st.markdown("""
        ## For Administrators (Technical Users)

        ### Step 1: Prepare Product IDs

        1. Download the CSV template from the sidebar
        2. Add product IDs (one per row):
           ```csv
           product_id
           1729630936525936882
           7575477825742982403
           ```

        ### Step 2: Run the Scraper

        ```bash
        # Navigate to scripts directory
        cd scripts

        # Activate virtual environment
        source venv/bin/activate  # Mac/Linux
        # OR: venv\\Scripts\\activate  # Windows

        # Run scraper
        python run_scraper.py --batch-file products.csv --download-videos

        # Results will be saved to: ../product_list/{product_id}/tabcut_data.json
        ```

        ### Step 3: Upload Results

        1. Go to "Upload Results" tab
        2. Select the `tabcut_data.json` files
        3. View and analyze the data
        4. Download reports

        ---

        ## For Team Members (Non-Technical)

        ### How to View Results

        1. **Receive JSON files** from your administrator
        2. **Open this app** (bookmark the URL)
        3. **Upload files** in the "Upload Results" tab
        4. **View data** in beautiful tables and charts
        5. **Download reports** as CSV for Excel/Sheets

        ### What Data You'll See

        - ✅ Product names and shop owners
        - ✅ Sales numbers and revenue
        - ✅ Video performance metrics
        - ✅ Top performing videos
        - ✅ Conversion rates

        ---

        ## Need the Scraper?

        **For administrators only:**
        The scraper must be run locally on your computer.

        **Repository:** https://github.com/tinnlo/lukas_9688
        **Documentation:** See `scripts/README.md`

        ---

        ## Questions?

        Contact your technical administrator for:
        - Setting up the scraper
        - Running batch jobs
        - Troubleshooting issues
        """)


if __name__ == "__main__":
    main()
