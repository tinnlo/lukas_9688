#!/usr/bin/env python3
"""
Test the updated scraper with a real product ID.
"""

import asyncio
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

from tabcut_scraper.scraper import TabcutScraper
from tabcut_scraper.models import ScraperConfig

async def test_scraper():
    """Test scraping a product."""

    # Load environment
    load_dotenv('config/.env')

    # Configure logging
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True
    )

    # Configure scraper
    config = ScraperConfig(
        headless=False,  # Run in headed mode to watch
        timeout=30000,
        output_base_dir="../product_list"
    )

    product_id = "1729535914744781823"

    async with TabcutScraper(config) as scraper:
        try:
            logger.info(f"Testing scraper with product ID: {product_id}")

            product_data = await scraper.scrape_product(
                product_id=product_id,
                download_videos=False  # Don't download videos for this test
            )

            logger.success("=" * 60)
            logger.success("SCRAPING COMPLETED SUCCESSFULLY!")
            logger.success("=" * 60)
            logger.info(f"Product: {product_data.product_info.product_name}")
            logger.info(f"Shop: {product_data.product_info.shop_owner}")
            logger.info(f"Total Sales: {product_data.product_info.total_sales}")
            logger.info(f"Sales Data: {product_data.sales_data.sales_count} sales, {product_data.sales_data.sales_revenue} revenue")
            logger.info(f"Top Videos: {len(product_data.top_videos)}")
            logger.success("=" * 60)

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_scraper())
