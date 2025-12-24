"""Data extraction logic for tabcut.com product pages."""

import re
import asyncio
from typing import List, Optional, Dict
from playwright.async_api import Page
from loguru import logger
from .models import ProductInfo, SalesData, VideoAnalysis, VideoData
from .utils import format_number, parse_duration


class DataExtractor:
    """Extract structured data from tabcut.com product pages."""

    def __init__(self, page: Page):
        """
        Initialize data extractor.

        Args:
            page: Playwright page object
        """
        self.page = page

    async def _safe_text_content(self, selector: str, default: str = "") -> str:
        """
        Safely extract text content from element.

        Args:
            selector: CSS selector
            default: Default value if element not found

        Returns:
            Text content or default
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                text = await element.text_content()
                return text.strip() if text else default
            return default
        except Exception as e:
            logger.debug(f"Failed to extract text from {selector}: {e}")
            return default

    async def _safe_get_attribute(self, selector: str, attribute: str, default: str = "") -> str:
        """
        Safely extract attribute from element.

        Args:
            selector: CSS selector
            attribute: Attribute name
            default: Default value if not found

        Returns:
            Attribute value or default
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                value = await element.get_attribute(attribute)
                return value.strip() if value else default
            return default
        except Exception as e:
            logger.debug(f"Failed to extract {attribute} from {selector}: {e}")
            return default

    async def extract_product_info(self) -> ProductInfo:
        """
        Extract product information from top section using JavaScript evaluation.

        Returns:
            ProductInfo object
        """
        logger.info("Extracting product information...")

        try:
            # Use JavaScript to extract data with specific selectors
            data = await self.page.evaluate('''() => {
                // Product name - specific chakra-text class
                const productNameEl = document.querySelector('p.chakra-text.css-1cdjl0i');
                const productName = productNameEl?.textContent?.trim() || '';

                // Shop name - specific css class for shop owner
                const shopEl = document.querySelector('div.css-1skcopj');
                const shopOwner = shopEl?.textContent?.trim() || '';

                // Helper to find value by label
                const findValueByLabel = (labelText) => {
                    const allElements = Array.from(document.querySelectorAll('*'));
                    const label = allElements.find(el =>
                        el.textContent.trim() === labelText &&
                        el.children.length === 0
                    );

                    if (!label) return null;

                    // Try parent's next sibling (this works for the stats section)
                    if (label.parentElement?.nextElementSibling) {
                        return label.parentElement.nextElementSibling.textContent.trim();
                    }

                    // Try next sibling
                    if (label.nextElementSibling) {
                        return label.nextElementSibling.textContent.trim();
                    }

                    return null;
                };

                // Total sales and revenue
                const totalSales = findValueByLabel('总销量');
                const totalRevenue = findValueByLabel('总销售额');

                return {
                    productName,
                    shopOwner,
                    totalSales,
                    totalRevenue
                };
            }''')

            product_name = data.get('productName', '') or "Unknown Product"
            shop_owner = data.get('shopOwner', '') or "Unknown Shop"
            total_sales_text = data.get('totalSales', '')
            total_sales = format_number(total_sales_text) if total_sales_text else None
            total_sales_revenue = data.get('totalRevenue', '') or None

            logger.info(f"Product: {product_name}, Shop: {shop_owner}")

            return ProductInfo(
                product_name=product_name,
                shop_owner=shop_owner,
                total_sales=total_sales,
                total_sales_revenue=total_sales_revenue
            )

        except Exception as e:
            logger.error(f"Failed to extract product info: {e}")
            import traceback
            traceback.print_exc()
            return ProductInfo(
                product_name="Unknown Product",
                shop_owner="Unknown Shop"
            )

    async def _click_tab(self, tab_name: str, wait_selector: Optional[str] = None) -> bool:
        """
        Click on a tab and wait for content to load.

        Args:
            tab_name: Text of the tab to click
            wait_selector: Optional selector to wait for after clicking

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Switching to {tab_name} tab...")

            # Try multiple ways to click the tab
            tab_selectors = [
                f'text="{tab_name}"',
                f'button:has-text("{tab_name}")',
                f'a:has-text("{tab_name}")',
                f'div:has-text("{tab_name}")',
            ]

            tab_clicked = False
            for selector in tab_selectors:
                try:
                    tab_element = await self.page.query_selector(selector)
                    if tab_element:
                        await tab_element.click()
                        tab_clicked = True
                        logger.debug(f"Clicked {tab_name} tab using selector: {selector}")
                        break
                except:
                    continue

            if not tab_clicked:
                logger.warning(f"Could not click {tab_name} tab")
                return False

            # Wait for content to load
            await asyncio.sleep(2)  # Initial wait

            if wait_selector:
                await self.page.wait_for_selector(wait_selector, timeout=10000)

            logger.info(f"{tab_name} tab loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to switch to {tab_name} tab: {e}")
            return False

    async def _click_date_range(self, range_text: str) -> bool:
        """
        Click on a date range button.

        Args:
            range_text: Text of the date range button (e.g., "近7天", "近30天")

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Clicking date range: {range_text}")

            range_selectors = [
                f'text="{range_text}"',
                f'button:has-text("{range_text}")',
                f'span:has-text("{range_text}")',
            ]

            for selector in range_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        await button.click()
                        await asyncio.sleep(1)  # Wait for data to update
                        logger.debug(f"Clicked {range_text} button")
                        return True
                except:
                    continue

            return False

        except Exception as e:
            logger.error(f"Failed to click date range {range_text}: {e}")
            return False

    async def extract_sales_data(self, try_30day_fallback: bool = True) -> SalesData:
        """
        Extract sales data from 商品分析 tab.

        Args:
            try_30day_fallback: If True and 7-day data is empty, try 30-day data

        Returns:
            SalesData object
        """
        logger.info("Extracting sales data...")

        try:
            # Click on 商品分析 tab
            if not await self._click_tab("商品分析"):
                logger.warning("Failed to switch to 商品分析 tab, using current page data")

            # Try 7-day data first
            await self._click_date_range("近7天")
            sales_data = await self._extract_sales_data_from_page("7day")

            # Check if data is empty and try 30-day fallback
            if try_30day_fallback and self._is_sales_data_empty(sales_data):
                logger.info("7-day data is empty, trying 30-day data...")
                await self._click_date_range("近30天")
                sales_data = await self._extract_sales_data_from_page("30day")

            return sales_data

        except Exception as e:
            logger.error(f"Failed to extract sales data: {e}")
            return SalesData(date_range="7day")

    def _is_sales_data_empty(self, sales_data: SalesData) -> bool:
        """Check if sales data is empty."""
        return (
            sales_data.sales_count is None and
            sales_data.sales_revenue is None and
            sales_data.related_videos is None
        )

    async def _extract_sales_data_from_page(self, date_range: str) -> SalesData:
        """
        Extract sales data from current page state using JavaScript.

        Args:
            date_range: Date range identifier ('7day' or '30day')

        Returns:
            SalesData object
        """
        try:
            # Use JavaScript to find data values in the 商品数据统计 section
            data = await self.page.evaluate('''() => {
                // Helper function to find value next to a label
                const findValueByLabel = (labelText) => {
                    const labels = Array.from(document.querySelectorAll('*'));
                    const label = labels.find(el =>
                        el.textContent.trim() === labelText &&
                        el.children.length === 0
                    );

                    if (!label) return null;

                    // Try parent's next sibling FIRST (this is the pattern used on this site)
                    if (label.parentElement?.nextElementSibling) {
                        const value = label.parentElement.nextElementSibling.textContent.trim();
                        // Make sure we got a value, not another label
                        if (value && !value.includes('销') && !value.includes('达人') && !value.includes('视频')) {
                            return value;
                        }
                    }

                    // Try next sibling
                    if (label.nextElementSibling) {
                        return label.nextElementSibling.textContent.trim();
                    }

                    return null;
                };

                return {
                    salesCount: findValueByLabel('销量'),
                    salesRevenue: findValueByLabel('销售额'),
                    relatedVideos: findValueByLabel('关联视频'),
                    relatedCreators: findValueByLabel('关联达人'),
                    relatedLivestreams: findValueByLabel('关联直播'),
                    conversionRate: findValueByLabel('视频出单率'),
                    creatorConversionRate: findValueByLabel('达人出单率')
                };
            }''')

            return SalesData(
                date_range=date_range,
                sales_count=format_number(data.get('salesCount')) if data.get('salesCount') else None,
                sales_revenue=data.get('salesRevenue') or None,
                related_videos=format_number(data.get('relatedVideos')) if data.get('relatedVideos') else None,
                related_creators=format_number(data.get('relatedCreators')) if data.get('relatedCreators') else None,
                conversion_rate=data.get('conversionRate') or None
            )
        except Exception as e:
            logger.error(f"Failed to extract sales data: {e}")
            return SalesData(date_range=date_range)

    async def extract_video_analysis(self) -> VideoAnalysis:
        """
        Extract video analysis metrics from 关联视频 tab using JavaScript.

        Returns:
            VideoAnalysis object
        """
        logger.info("Extracting video analysis data...")

        try:
            # Click on 关联视频 tab
            if not await self._click_tab("关联视频"):
                logger.warning("Failed to switch to 关联视频 tab")

            # Use JavaScript to extract video analysis data
            data = await self.page.evaluate('''() => {
                const findValueByLabel = (labelText) => {
                    const labels = Array.from(document.querySelectorAll('*'));
                    const label = labels.find(el =>
                        el.textContent.trim() === labelText &&
                        el.children.length === 0
                    );

                    if (!label) return null;

                    // Try parent's next sibling
                    if (label.parentElement?.nextElementSibling) {
                        const value = label.parentElement.nextElementSibling.textContent.trim();
                        // Make sure we got a value, not another label
                        if (value && !value.includes('带货') && !value.includes('广告')) {
                            return value;
                        }
                    }

                    // Try next sibling
                    if (label.nextElementSibling) {
                        return label.nextElementSibling.textContent.trim();
                    }

                    return null;
                };

                return {
                    videoCount: findValueByLabel('带货视频数'),
                    creatorCount: findValueByLabel('带货视频达人数'),
                    videoSales: findValueByLabel('带货视频销量'),
                    videoRevenue: findValueByLabel('带货视频销售额'),
                    adRevenue: findValueByLabel('广告成交金额'),
                    adRatio: findValueByLabel('广告成交占比')
                };
            }''')

            return VideoAnalysis(
                带货视频数=format_number(data.get('videoCount')) if data.get('videoCount') else None,
                带货视频达人数=format_number(data.get('creatorCount')) if data.get('creatorCount') else None,
                带货视频销量=format_number(data.get('videoSales')) if data.get('videoSales') else None,
                带货视频销售额=data.get('videoRevenue') or None,
                广告成交金额=data.get('adRevenue') or None,
                广告成交占比=data.get('adRatio') or None
            )

        except Exception as e:
            logger.error(f"Failed to extract video analysis: {e}")
            return VideoAnalysis()

    async def extract_top_videos(self, limit: int = 5) -> List[VideoData]:
        """
        Extract top N videos from the video list.

        Args:
            limit: Number of top videos to extract

        Returns:
            List of VideoData objects
        """
        logger.info(f"Extracting top {limit} videos...")

        try:
            # Ensure we're on the 关联视频 tab
            await self._click_tab("关联视频")

            # Wait for video list to load
            await asyncio.sleep(2)

            # Find video rows - try multiple patterns
            all_rows = await self.page.query_selector_all('tr')

            if not all_rows:
                logger.warning("No video rows found")
                return []

            # Skip header row (index 0) and empty row (index 1)
            # Start from index 2 for actual video data
            video_rows = all_rows[2:] if len(all_rows) > 2 else []

            if not video_rows:
                logger.warning("No video data rows found after skipping headers")
                return []

            videos = []
            for rank, row in enumerate(video_rows[:limit], start=1):
                try:
                    video = await self._extract_video_from_row(row, rank)
                    if video:
                        videos.append(video)
                except Exception as e:
                    logger.warning(f"Failed to extract video {rank}: {e}")
                    continue

            logger.info(f"Successfully extracted {len(videos)} videos")
            return videos

        except Exception as e:
            logger.error(f"Failed to extract top videos: {e}")
            return []

    async def _extract_video_from_row(self, row, rank: int) -> Optional[VideoData]:
        """
        Extract video data from a table row using cell positions.

        Args:
            row: Playwright element handle for the row
            rank: Video rank position

        Returns:
            VideoData object or None
        """
        try:
            # Use JavaScript to extract data from specific cell positions
            data = await row.evaluate('''(row) => {
                const cells = Array.from(row.querySelectorAll('td'));

                if (cells.length < 4) return null;

                // Cell 0: Video title/description
                const title = cells[0]?.textContent?.trim() || '';

                // Cell 1: Creator info - format: "Name@username粉丝数：count"
                const creatorText = cells[1]?.textContent?.trim() || '';
                let creatorUsername = 'unknown';
                let creatorFollowers = null;

                // Extract username (text after @)
                const atMatch = creatorText.match(/@([^\s粉]+)/);
                if (atMatch) {
                    creatorUsername = atMatch[1];
                }

                // Extract follower count
                const followersMatch = creatorText.match(/粉丝数：([\d.]+万?|[\d]+)/);
                if (followersMatch) {
                    creatorFollowers = followersMatch[1];
                }

                // Cell 2: Publish date
                const publishDate = cells[2]?.textContent?.trim() || null;

                // Cell 3: Estimated sales
                const estimatedSales = cells[3]?.textContent?.trim() || null;

                // Cell 4: Estimated revenue (if exists)
                const estimatedRevenue = cells[4]?.textContent?.trim() || null;

                // Cell 6: Total views (if exists)
                const totalViews = cells[6]?.textContent?.trim() || null;

                return {
                    title,
                    creatorUsername,
                    creatorFollowers,
                    publishDate,
                    estimatedSales,
                    estimatedRevenue,
                    totalViews
                };
            }''')

            if not data:
                return None

            # Extract video URL by clicking "跳转至 TikTok" button
            video_url = await self._extract_video_url_from_row(row, rank)

            return VideoData(
                rank=rank,
                title=data.get('title', f"Video {rank}"),
                creator_username=data.get('creatorUsername', 'unknown'),
                creator_followers=data.get('creatorFollowers'),
                publish_date=data.get('publishDate'),
                estimated_sales=format_number(data.get('estimatedSales')) if data.get('estimatedSales') else None,
                estimated_revenue=data.get('estimatedRevenue'),
                total_views=data.get('totalViews'),
                video_url=video_url
            )

        except Exception as e:
            logger.debug(f"Error extracting video data from row: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _extract_video_url_from_row(self, row, rank: int) -> Optional[str]:
        """
        Extract video URL by clicking the "跳转至 TikTok" button and capturing popup.

        Args:
            row: Playwright element handle for the row
            rank: Video rank position

        Returns:
            TikTok video URL or None
        """
        try:
            # Find the "跳转至 TikTok" button in the row
            tiktok_button = await row.query_selector('button:has-text("跳转至 TikTok"), a:has-text("跳转至 TikTok"), :text("跳转至 TikTok")')

            if not tiktok_button:
                logger.debug(f"No '跳转至 TikTok' button found for video {rank}")
                return None

            # Set up popup listener before clicking
            popup_promise = self.page.wait_for_event("popup", timeout=5000)

            # Click the button
            await tiktok_button.click()

            # Wait for popup
            popup = await popup_promise
            video_url = popup.url

            # Close the popup
            await popup.close()

            logger.debug(f"Extracted video URL for rank {rank}: {video_url}")
            return video_url

        except Exception as e:
            logger.debug(f"Failed to extract video URL for rank {rank}: {e}")
            return None
