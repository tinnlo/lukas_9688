"""Main scraper orchestrator for FastMoss.com."""

import asyncio
import random
from datetime import datetime
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger

from .auth import AuthHandler
from .extractors import DataExtractor
from .models import ProductData, ScraperConfig
from .downloader import VideoDownloader
from .utils import ensure_product_folder, retry_async


class FastMossScraper:
    """Main scraper class for FastMoss.com product data."""

    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize scraper.

        Args:
            config: Scraper configuration (uses defaults if not provided)
        """
        self.config = config or ScraperConfig()
        self.auth_handler = AuthHandler()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start browser and create context."""
        logger.info("Starting browser...")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless
        )

        # Create context with Chinese locale
        logger.info("Creating browser context with Chinese locale...")
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            locale='zh-CN',
            extra_http_headers={
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
        )

        self.page = await self.context.new_page()
        self.page.set_default_timeout(self.config.timeout)

        logger.info("Browser started successfully")

    async def close(self) -> None:
        """Close browser and cleanup."""
        logger.info("Closing browser...")

        if self.page:
            await self.page.close()
        if self.context:
            # Save session before closing
            await self.auth_handler.save_session(self.context)
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

        logger.info("Browser closed")

    async def _random_delay(self) -> None:
        """Add random delay to avoid detection."""
        delay = random.uniform(
            self.config.random_delay_min,
            self.config.random_delay_max
        )
        logger.debug(f"Random delay: {delay:.2f}s")
        await asyncio.sleep(delay)

    async def _ensure_authenticated(self) -> bool:
        """Ensure user is authenticated."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        return await self.auth_handler.ensure_authenticated(self.page)

    @retry_async(max_attempts=3, delay=5.0)
    async def scrape_product(
        self,
        product_id: str,
        output_dir: Optional[str] = None,
        download_videos: bool = False
    ) -> ProductData:
        """
        Scrape data for a single product.

        Args:
            product_id: TikTok shop product ID
            output_dir: Output directory (uses config default if not provided)
            download_videos: Whether to download videos

        Returns:
            ProductData object with all scraped data
        """
        logger.info(f"Starting scrape for product ID: {product_id}")

        try:
            # Ensure authenticated
            if not await self._ensure_authenticated():
                raise Exception("Authentication failed")

            # Navigate to product page
            product_url = f"https://www.fastmoss.com/zh/e-commerce/detail/{product_id}"
            logger.info(f"Navigating to: {product_url}")

            await self.page.goto(product_url, wait_until="domcontentloaded")
            await self._random_delay()

            # Wait for page to fully load
            await asyncio.sleep(3)

            # Check if we got redirected to login
            current_url = self.page.url
            if 'login' in current_url.lower():
                logger.info("Redirected to login, handling authentication...")
                if await self.auth_handler.login(self.page):
                    logger.success("Successfully logged in")
                    # Navigate back to product page
                    await self.page.goto(product_url, wait_until="domcontentloaded")
                    await asyncio.sleep(3)
                else:
                    raise Exception("Failed to login")

            logger.info(f"Current URL: {current_url}")

            # Create extractor
            extractor = DataExtractor(self.page)

            # Extract product info
            product_info = await extractor.extract_product_info()
            await self._random_delay()

            # Extract sales data (with 30-day fallback)
            sales_data = await extractor.extract_sales_data(try_30day_fallback=True)
            await self._random_delay()

            # Extract video analysis
            video_analysis = await extractor.extract_video_analysis()
            await self._random_delay()

            # Extract top 5 videos
            top_videos = await extractor.extract_top_videos(limit=5)

            # Create product data
            product_data = ProductData(
                product_id=product_id,
                scraped_at=datetime.now().isoformat(),
                product_info=product_info,
                sales_data=sales_data,
                video_analysis=video_analysis,
                top_videos=top_videos
            )

            # Save to file
            output_base = output_dir or self.config.output_base_dir
            product_folder = ensure_product_folder(product_id, output_base)
            json_path = product_folder / "fastmoss_data.json"

            product_data.save_to_file(str(json_path))
            logger.success(f"Product data saved to: {json_path}")

            # Download product images
            logger.info("Downloading product images...")
            downloader = VideoDownloader(self.page, timeout=self.config.download_timeout)
            image_paths = await downloader.download_product_images(product_folder)
            logger.success(f"Downloaded {len(image_paths)} product images")

            # Download videos if requested
            if download_videos and top_videos:
                logger.info(f"Downloading top {len(top_videos)} videos...")
                video_output_dir = product_folder / "ref_video"

                # Clean old videos to prevent duplicates
                if video_output_dir.exists():
                    import shutil
                    shutil.rmtree(video_output_dir)
                    logger.info("Cleaned old video files")

                await downloader.download_videos_batch(top_videos, video_output_dir)

                # Update JSON with video paths
                product_data.save_to_file(str(json_path))
                logger.success("Videos downloaded and data updated")

            return product_data

        except Exception as e:
            logger.error(f"Failed to scrape product {product_id}: {e}")
            raise

    async def scrape_batch(
        self,
        product_ids: list[str],
        output_dir: Optional[str] = None,
        download_videos: bool = False,
        resume: bool = False
    ) -> dict:
        """
        Scrape multiple products.

        Args:
            product_ids: List of product IDs to scrape
            output_dir: Output directory
            download_videos: Whether to download videos
            resume: Whether to resume from previous run

        Returns:
            Dictionary with results summary
        """
        logger.info(f"Starting batch scrape for {len(product_ids)} products")

        results = {
            'completed': [],
            'failed': []
        }

        for i, product_id in enumerate(product_ids, 1):
            logger.info(f"Processing product {i}/{len(product_ids)}: {product_id}")

            try:
                product_data = await self.scrape_product(
                    product_id,
                    output_dir=output_dir,
                    download_videos=download_videos
                )
                results['completed'].append(product_id)
                logger.success(f"✓ Product {product_id} completed")

            except Exception as e:
                logger.error(f"✗ Product {product_id} failed: {e}")
                results['failed'].append({'product_id': product_id, 'error': str(e)})

            # Random delay between products
            if i < len(product_ids):
                await self._random_delay()

        logger.info(
            f"Batch complete: {len(results['completed'])} succeeded, "
            f"{len(results['failed'])} failed"
        )

        return results
