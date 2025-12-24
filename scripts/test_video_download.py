"""Test downloading the top 5 videos."""

import asyncio
from pathlib import Path
from dotenv import load_dotenv
from tabcut_scraper.scraper import TabcutScraper
from tabcut_scraper.models import ScraperConfig
from loguru import logger

# Load environment
load_dotenv('config/.env')

# Configure logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    colorize=True
)

async def test_video_download():
    """Test downloading videos for a product."""

    config = ScraperConfig(
        headless=False,
        timeout=30000,
        output_base_dir="../product_list"
    )

    product_id = "1729535914744781823"

    async with TabcutScraper(config) as scraper:
        try:
            logger.info(f"Testing video download for product ID: {product_id}")

            # Scrape product with video downloads enabled
            product_data = await scraper.scrape_product(
                product_id=product_id,
                download_videos=True  # Enable video downloads
            )

            logger.success("=" * 60)
            logger.success("VIDEO DOWNLOAD TEST COMPLETED!")
            logger.success("=" * 60)
            logger.info(f"Product: {product_data.product_info.product_name}")
            logger.info(f"Top Videos: {len(product_data.top_videos)}")

            # Check which videos were downloaded
            for video in product_data.top_videos:
                if video.local_path:
                    logger.success(f"✓ Video {video.rank}: Downloaded to {video.local_path}")
                else:
                    logger.warning(f"✗ Video {video.rank}: Failed to download")

            logger.success("=" * 60)

        except Exception as e:
            logger.error(f"Test failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_video_download())
