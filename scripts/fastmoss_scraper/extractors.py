"""Data extractors for FastMoss.com product pages - table-based parsing."""

import re
import asyncio
from typing import List, Optional, Dict
from playwright.async_api import Page
from loguru import logger

from .models import ProductInfo, SalesData, VideoAnalysis, VideoData
from .utils import format_number


class DataExtractor:
    """Extract data from FastMoss product pages using table-based parsing."""

    def __init__(self, page: Page):
        """
        Initialize extractor.

        Args:
            page: Playwright page object
        """
        self.page = page

    def _clean_number(self, text: str) -> Optional[int]:
        """
        Extract integer from text, handling commas and spaces.

        Args:
            text: Text containing number

        Returns:
            Integer value or None
        """
        if not text:
            return None

        try:
            # Remove commas, spaces, and extract digits
            cleaned = re.sub(r"[,\s]", "", text)
            match = re.search(r"\d+", cleaned)
            return int(match.group()) if match else None
        except Exception:
            return None

    def _clean_currency(self, text: str) -> Optional[str]:
        """
        Clean and preserve currency value.

        Args:
            text: Text containing currency

        Returns:
            Cleaned currency string or None
        """
        if not text:
            return None
        return text.strip()

    def _parse_engagement_rate(self, text: str) -> Optional[str]:
        """
        Parse engagement rate (e.g., "0.3%" -> "0.3%").

        Args:
            text: Text containing percentage

        Returns:
            Percentage string or None
        """
        if not text:
            return None

        match = re.search(r"(\d+\.?\d*)%", text)
        if match:
            return f"{match.group(1)}%"
        return None

    def _sanitize_value(self, value: Optional[str]) -> Optional[str]:
        """Normalize placeholder values to None."""
        if not value:
            return None
        cleaned = value.strip()
        if cleaned in {"-", "--", "—", "N/A", ".", "·"}:
            return None
        return cleaned

    def _extract_metric_text(self, text: str, labels: List[str]) -> Optional[str]:
        """Extract a raw metric value that appears near a label."""
        if not text:
            return None

        label_pattern = "|".join(re.escape(label) for label in labels)
        pattern = rf"(?:{label_pattern})\s*[:：]?\s*([€$¥]?\s*[\d.,]+(?:万|亿)?%?)"
        match = re.search(pattern, text)
        if match:
            return self._sanitize_value(match.group(1))

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for idx, line in enumerate(lines):
            if any(label in line for label in labels):
                line_clean = line
                for label in labels:
                    line_clean = line_clean.replace(label, " ")
                match = re.search(r"([€$¥]?\s*[\d.,]+(?:万)?%?)", line_clean)
                if match:
                    return self._sanitize_value(match.group(1))
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1]
                    match = re.search(r"([€$¥]?\s*[\d.,]+(?:万)?%?)", next_line)
                    if match:
                        return self._sanitize_value(match.group(1))
        return None

    async def _collect_page_text(self) -> str:
        """Collect page text from visible, hidden, and app-state sources."""
        inner_text = await self.page.evaluate("""() => {
            return document.body ? (document.body.innerText || "") : "";
        }""")
        text_content = await self.page.evaluate("""() => {
            return document.body ? (document.body.textContent || "") : "";
        }""")
        state_text = await self.page.evaluate("""() => {
            const chunks = [];
            const nextData = document.getElementById('__NEXT_DATA__');
            if (nextData && nextData.textContent) {
                chunks.push(nextData.textContent);
            }
            if (window.__NUXT__) {
                try {
                    chunks.push(JSON.stringify(window.__NUXT__));
                } catch (e) {
                    // Ignore stringify failures for large/cyclic state
                }
            }
            return chunks.join('\\n');
        }""")

        return "\n".join(
            part for part in [inner_text, text_content, state_text] if part
        )

    def _normalize_currency(self, value: Optional[str]) -> Optional[str]:
        """Normalize currency text to a compact form (e.g., €1,234.56)."""
        cleaned = self._sanitize_value(value)
        if not cleaned:
            return None
        compact = cleaned.replace(" ", "")
        match = re.search(r"€([\d.,]+)", compact)
        if match:
            return f"€{match.group(1)}"
        return compact

    def _normalize_percent(self, value: Optional[str]) -> Optional[str]:
        """Normalize percent values to include %."""
        cleaned = self._sanitize_value(value)
        if not cleaned:
            return None
        compact = cleaned.replace(" ", "")
        match = re.search(r"([\d.]+%)", compact)
        if match:
            return match.group(1)
        return compact

    async def extract_product_info(self) -> ProductInfo:
        """
        Extract product information from top section.

        Returns:
            ProductInfo object
        """
        logger.info("Extracting product info from FastMoss...")

        try:
            # Wait for page to be fully loaded
            await asyncio.sleep(2)

            # Extract product name from page title or heading
            product_name = await self.page.evaluate("""() => {
                // Try multiple selectors for product name
                const selectors = ['h1', '[class*="title"]', '[class*="Title"]'];
                for (const selector of selectors) {
                    const elem = document.querySelector(selector);
                    if (elem && elem.textContent.trim().length > 0) {
                        return elem.textContent.trim();
                    }
                }
                return "Unknown Product";
            }""")

            # Extract shop owner
            shop_owner = await self.page.evaluate("""() => {
                // Look for shop/store elements
                const selectors = ['[class*="shop"]', '[class*="Shop"]', '[class*="store"]'];
                for (const selector of selectors) {
                    const elem = document.querySelector(selector);
                    if (elem && elem.textContent.trim().length > 0) {
                        return elem.textContent.trim();
                    }
                }
                return "Unknown Shop";
            }""")

            # Extract sales and revenue from top metrics
            metrics = await self.page.evaluate("""() => {
                const result = {
                    sales: null,
                    revenue: null
                };

                // Look for metric values in the page
                const allText = document.body.innerText;

                // Try to find sales (销量) with number before it
                const salesMatch = allText.match(/(\\d+)\\s*销量/);
                if (salesMatch) {
                    result.sales = parseInt(salesMatch[1]);
                }

                // Try to find revenue (销售额) with Euro amount
                const revenueMatch = allText.match(/€([\\d,]+\\.?\\d*)/);
                if (revenueMatch) {
                    result.revenue = '€' + revenueMatch[1];
                }

                return result;
            }""")

            return ProductInfo(
                product_name=product_name,
                shop_owner=shop_owner,
                total_sales=metrics.get("sales"),
                total_sales_revenue=metrics.get("revenue"),
            )

        except Exception as e:
            logger.error(f"Failed to extract product info: {e}")
            return ProductInfo(
                product_name="Unknown Product", shop_owner="Unknown Shop"
            )

    async def extract_sales_data(self, try_30day_fallback: bool = True) -> SalesData:
        """
        Extract sales data from 数据总览 section.

        Args:
            try_30day_fallback: Try 30-day data if 7-day is empty (FastMoss uses 28-day)

        Returns:
            SalesData object
        """
        logger.info("Extracting sales data from 数据总览...")

        try:
            # FastMoss typically shows 28-day data
            date_range = "28day"

            # Extract from page using table parsing
            sales_metrics = await self.page.evaluate("""() => {
                const result = {
                    sales_count: null,
                    sales_revenue: null,
                    related_videos: null,
                    related_creators: null
                };

                // Parse from the page text
                const pageText = document.body.innerText;

                // Look for sales count (销量)
                const salesMatch = pageText.match(/(\\d+)\\s*销量/);
                if (salesMatch) {
                    result.sales_count = parseInt(salesMatch[1]);
                }

                // Look for sales revenue (销售额)
                const revenueMatch = pageText.match(/€([\\d,]+\\.?\\d*)\\s*销售额/);
                if (!revenueMatch) {
                    // Try alternative pattern
                    const altMatch = pageText.match(/销售额.*?€([\\d,]+\\.?\\d*)/);
                    if (altMatch) {
                        result.sales_revenue = '€' + altMatch[1];
                    }
                } else {
                    result.sales_revenue = '€' + revenueMatch[1];
                }

                return result;
            }""")

            page_text = await self._collect_page_text()
            sales_count = sales_metrics.get("sales_count")
            sales_revenue = sales_metrics.get("sales_revenue")

            if sales_count is None:
                sales_count = format_number(
                    self._extract_metric_text(page_text, ["销量"])
                )
            if not sales_revenue:
                sales_revenue = self._normalize_currency(
                    self._extract_metric_text(page_text, ["销售额"])
                )

            related_videos = format_number(
                self._extract_metric_text(page_text, ["关联视频", "相关视频"])
            )
            related_creators = format_number(
                self._extract_metric_text(page_text, ["关联达人", "相关达人"])
            )
            conversion_rate = self._normalize_percent(
                self._extract_metric_text(page_text, ["转化率"])
            )
            click_through_rate = self._normalize_percent(
                self._extract_metric_text(page_text, ["点击率"])
            )

            return SalesData(
                date_range=date_range,
                sales_count=sales_count,
                sales_revenue=sales_revenue,
                related_videos=related_videos,
                related_creators=related_creators,
                conversion_rate=conversion_rate,
                click_through_rate=click_through_rate,
            )

        except Exception as e:
            logger.error(f"Failed to extract sales data: {e}")
            return SalesData(date_range="28day")

    async def extract_video_analysis(self) -> VideoAnalysis:
        """
        Extract video analysis metrics from 商品关联视频 tab.

        Returns:
            VideoAnalysis object
        """
        logger.info("Extracting video analysis...")

        try:
            page_text = await self._collect_page_text()

            return VideoAnalysis(
                带货视频数=format_number(
                    self._extract_metric_text(page_text, ["带货视频数"])
                ),
                带货视频达人数=format_number(
                    self._extract_metric_text(
                        page_text, ["带货视频达人数", "带货视频达人"]
                    )
                ),
                带货视频销量=format_number(
                    self._extract_metric_text(page_text, ["带货视频销量"])
                ),
                带货视频销售额=self._normalize_currency(
                    self._extract_metric_text(page_text, ["带货视频销售额"])
                ),
                广告成交金额=self._normalize_currency(
                    self._extract_metric_text(page_text, ["广告成交金额"])
                ),
                广告成交占比=self._normalize_percent(
                    self._extract_metric_text(page_text, ["广告成交占比"])
                ),
            )

        except Exception as e:
            logger.error(f"Failed to extract video analysis: {e}")
            return VideoAnalysis()

    async def extract_top_videos(self, limit: int = 5) -> List[VideoData]:
        """
        Extract top performing videos from 商品关联视频 TABLE.

        This parses the HTML table with columns:
        - Col 1: Video/Creator (thumbnail + username)
        - Col 2: 销量(近28天) - Sales last 28 days
        - Col 3: 销售额(近28天) - Revenue last 28 days
        - Col 4: 播放量 - Views
        - Col 5: 点赞数 - Likes
        - Col 6: 评论数 - Comments
        - Col 7: 互动率 - Engagement rate
        - Col 8: 视频发布时间 - Publish date

        Then navigates to each video detail page to extract TikTok URL.

        Args:
            limit: Maximum number of videos to extract

        Returns:
            List of VideoData objects
        """
        logger.info(f"Extracting top {limit} videos from table...")

        videos = []

        try:
            # Wait for page to load
            await asyncio.sleep(2)

            # Extract video data from table rows - skip invalid rows
            video_data_list = await self.page.evaluate(
                """(limit) => {
                const videos = [];

                // Helper function to parse numbers with K/M/万/亿 suffixes
                function parseNumber(text) {
                    if (!text) return null;
                    const match = text.match(/([\\d,.]+)\\s*(K|M|万|亿)?/i);
                    if (!match) return null;
                    let num = parseFloat(match[1].replace(/,/g, ''));
                    const suffix = match[2];
                    if (suffix) {
                        if (suffix === 'K' || suffix === 'k') num *= 1000;
                        else if (suffix === 'M' || suffix === 'm') num *= 1000000;
                        else if (suffix === '万') num *= 10000;
                        else if (suffix === '亿') num *= 100000000;
                    }
                    return Math.round(num);
                }

                // Find all table rows (tbody tr)
                const tables = document.querySelectorAll('table');

                for (const table of tables) {
                    const tbody = table.querySelector('tbody');
                    if (!tbody) continue;

                    const rows = tbody.querySelectorAll('tr');

                    for (let i = 0; i < rows.length && videos.length < limit; i++) {
                        const row = rows[i];
                        const cells = row.querySelectorAll('td');

                        // Skip if not enough columns
                        if (cells.length < 7) continue;

                        try {
                            // Get FastMoss video detail page URL from first column
                            const videoLink = cells[0]?.querySelector('a[href*="/video/"], a[href*="media-source"]');
                            const fastmossVideoUrl = videoLink ? videoLink.href : null;

                            // Skip rows without video links (likely header or empty rows)
                            if (!fastmossVideoUrl) continue;

                            // Column 1: Creator username (will be replaced from TikTok URL later)
                            const creatorText = cells[0]?.textContent?.trim() || '';
                            const creatorMatch = creatorText.match(/@?(\\w+)/);
                            const creator = creatorMatch ? creatorMatch[1] : 'Unknown';

                            // Skip if creator couldn't be extracted
                            if (creator === 'Unknown' || creator.length < 2) continue;

                            // Column 2: Sales (销量) - use parseNumber to handle K/万
                            const salesText = cells[1]?.textContent?.trim() || '0';
                            const sales = parseNumber(salesText);

                            // Column 3: Revenue (销售额)
                            const revenueText = cells[2]?.textContent?.trim() || '';
                            const revenueMatch = revenueText.match(/€([\\d,.]+)/);
                            const revenue = revenueMatch ? '€' + revenueMatch[1] : null;

                            // Column 4: Views (播放量) - use parseNumber to handle K/万
                            const viewsText = cells[3]?.textContent?.trim() || '0';
                            const views = parseNumber(viewsText);

                            // Column 5: Likes (点赞数) - use parseNumber to handle K/万
                            const likesText = cells[4]?.textContent?.trim() || '0';
                            const likes = parseNumber(likesText);

                            // Column 6: Comments (评论数) - use parseNumber to handle K/万
                            const commentsText = cells[5]?.textContent?.trim() || '0';
                            const comments = parseNumber(commentsText);

                            // Column 7: Engagement rate (互动率)
                            const engagementText = cells[6]?.textContent?.trim() || '';
                            const engagementMatch = engagementText.match(/([\\d.]+)%/);
                            const engagement = engagementMatch ? engagementMatch[1] + '%' : null;

                            // Column 8: Publish date (if exists)
                            const dateText = cells[7]?.textContent?.trim() || '';
                            const dateMatch = dateText.match(/\\d{4}-\\d{2}-\\d{2}/);
                            const publishDate = dateMatch ? dateMatch[0] : null;

                            // Add to videos list with sequential rank
                            videos.push({
                                rank: videos.length + 1,  // Rank based on valid videos found
                                creator: creator,
                                sales: sales,
                                revenue: revenue,
                                views: views,
                                likes: likes,
                                comments: comments,
                                engagement: engagement,
                                publishDate: publishDate,
                                fastmossVideoUrl: fastmossVideoUrl,
                                title: `Video by ${creator}`
                            });

                        } catch (err) {
                            console.error('Error parsing row:', err);
                        }
                    }

                    // If we found videos, stop looking
                    if (videos.length > 0) break;
                }

                return videos;
            }""",
                limit,
            )

            # Now navigate to each video detail page to extract TikTok URL
            current_url = self.page.url  # Save current URL to return later

            for video_dict in video_data_list:
                try:
                    fastmoss_url = video_dict.get("fastmossVideoUrl")
                    tiktok_url = None

                    # Navigate to FastMoss video detail page to get TikTok URL
                    if fastmoss_url:
                        try:
                            logger.debug(
                                f"Navigating to video detail page: {fastmoss_url}"
                            )
                            await self.page.goto(
                                fastmoss_url,
                                wait_until="domcontentloaded",
                                timeout=15000,
                            )
                            await asyncio.sleep(2)

                            # Find the "进入TikTok官方视频主页" button and extract its href
                            tiktok_url = await self.page.evaluate("""() => {
                                // Look for the button/link with text "进入TikTok官方视频主页"
                                const button = Array.from(document.querySelectorAll('a, button'))
                                    .find(el => el.textContent.includes('进入TikTok官方视频主页') ||
                                                el.textContent.includes('TikTok'));

                                if (button) {
                                    return button.href || button.getAttribute('href');
                                }

                                // Alternative: look for any tiktok.com link on the page
                                const tiktokLink = document.querySelector('a[href*="tiktok.com"]');
                                return tiktokLink ? tiktokLink.href : null;
                            }""")

                            if tiktok_url:
                                logger.debug(f"Found TikTok URL: {tiktok_url}")
                            else:
                                logger.warning(
                                    f"No TikTok URL found on video detail page"
                                )

                        except Exception as e:
                            logger.warning(
                                f"Failed to navigate to video detail page: {e}"
                            )

                    # Extract creator username from TikTok URL (more reliable than cell text)
                    creator_username = video_dict.get("creator", "Unknown")
                    if tiktok_url:
                        import re

                        # Extract username from tiktok.com/@username/video/...
                        url_match = re.search(r"tiktok\.com/@([^/]+)", tiktok_url)
                        if url_match:
                            creator_username = url_match.group(1)
                            logger.debug(
                                f"Extracted username from URL: @{creator_username}"
                            )
                        else:
                            logger.debug(
                                f"Could not extract username from URL, using fallback: {creator_username}"
                            )

                    # Create VideoData object
                    video = VideoData(
                        rank=video_dict.get("rank", 0),
                        title=f"Video by {creator_username}",  # Use extracted username in title
                        creator_username=creator_username,
                        estimated_sales=video_dict.get("sales"),
                        estimated_revenue=video_dict.get("revenue"),
                        total_views=video_dict.get("views"),
                        likes=video_dict.get("likes"),
                        comments=video_dict.get("comments"),
                        engagement_rate=video_dict.get("engagement"),
                        publish_date=video_dict.get("publishDate"),
                        video_url=tiktok_url,
                    )
                    videos.append(video)
                    logger.debug(
                        f"Extracted video {video.rank}: @{video.creator_username}, "
                        f"Sales: {video.estimated_sales}, Revenue: {video.estimated_revenue}, "
                        f"TikTok URL: {tiktok_url[:50] if tiktok_url else 'None'}"
                    )

                except Exception as e:
                    logger.warning(f"Failed to create VideoData object: {e}")
                    continue

            # Return to product page
            logger.debug(f"Returning to product page: {current_url}")
            await self.page.goto(
                current_url, wait_until="domcontentloaded", timeout=15000
            )
            await asyncio.sleep(1)

            logger.success(
                f"Extracted {len(videos)} videos from table with TikTok URLs"
            )

        except Exception as e:
            logger.error(f"Failed to extract videos: {e}")
            import traceback

            traceback.print_exc()

        return videos
