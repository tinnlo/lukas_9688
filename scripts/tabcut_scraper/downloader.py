"""Video and image downloader for TikTok/Douyin videos and product images."""

import asyncio
import httpx
import subprocess
from pathlib import Path
from typing import List, Optional, Dict
from playwright.async_api import Page
from loguru import logger

from .models import VideoData
from .utils import retry_async, sanitize_filename


class VideoDownloader:
    """Download TikTok/Douyin videos and product images with multiple fallback strategies."""

    def __init__(self, page: Page, timeout: int = 300000):
        """
        Initialize video downloader.

        Args:
            page: Playwright page object
            timeout: Download timeout in milliseconds
        """
        self.page = page
        self.timeout = timeout

    @retry_async(max_attempts=3, delay=2.0)
    async def download_product_images(self, output_dir: Path) -> List[str]:
        """
        Download all product images from the current page by navigating the carousel.

        Args:
            output_dir: Directory to save images

        Returns:
            List of saved image paths
        """
        logger.info("Downloading product images...")

        # Create images directory
        images_dir = output_dir / "product_images"
        images_dir.mkdir(parents=True, exist_ok=True)

        # Collect all unique images by navigating the carousel
        all_image_urls = {}

        async def collect_current_images():
            """Collect images currently in the DOM."""
            imgs = await self.page.evaluate("""() => {
                const images = Array.from(document.querySelectorAll('img'));
                const productImages = images
                    .filter(img =>
                        img.src &&
                        img.src.includes('cdn.tabcut.com/dataservice/media/item/') &&
                        !img.src.includes('avatar')
                    )
                    .map(img => {
                        const baseUrl = img.src.split('?')[0];
                        return {
                            url: img.src,
                            baseUrl: baseUrl,
                            filename: baseUrl.split('/').pop()
                        };
                    });

                const uniqueImages = new Map();
                for (const img of productImages) {
                    if (!uniqueImages.has(img.filename)) {
                        uniqueImages.set(img.filename, img.url);
                    }
                }
                return Array.from(uniqueImages.entries()).map(([filename, url]) => ({filename, url}));
            }""")

            new_count = 0
            for img in imgs:
                if img["filename"] not in all_image_urls:
                    all_image_urls[img["filename"]] = img["url"]
                    new_count += 1
            return new_count

        # Collect initial images
        logger.info("Collecting initial images...")
        await collect_current_images()
        logger.info(f"Initial: {len(all_image_urls)} images")

        # Navigate carousel to collect all images
        try:
            # Scroll the carousel into view first
            await self.page.evaluate("""() => {
                const productImages = Array.from(document.querySelectorAll('img')).filter(img =>
                    img.src && img.src.includes('cdn.tabcut.com/dataservice/media/item/')
                );
                if (productImages.length > 0) {
                    productImages[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }""")
            await asyncio.sleep(1)  # Wait for scroll to complete

            # Find the right arrow position
            arrow_pos = await self.page.evaluate("""() => {
                const productImages = Array.from(document.querySelectorAll('img')).filter(img =>
                    img.src && img.src.includes('cdn.tabcut.com/dataservice/media/item/')
                );
                if (productImages.length === 0) return null;

                let container = productImages[0].parentElement;
                while (container && container.tagName !== 'BODY') {
                    const imgs = container.querySelectorAll('img[src*="cdn.tabcut.com/dataservice/media/item/"]');
                    if (imgs.length > 1) break;
                    container = container.parentElement;
                }
                const containerRect = container.getBoundingClientRect();

                const allSvgs = Array.from(document.querySelectorAll('svg'));
                const rightArrowSvg = allSvgs.find(svg => {
                    const rect = svg.getBoundingClientRect();
                    const path = svg.querySelector('path');
                    const pathData = path ? path.getAttribute('d') : null;
                    const onRightSide = rect.x > containerRect.x + containerRect.width - 50;
                    const inVerticalRange = rect.y >= containerRect.y && rect.y <= containerRect.bottom;
                    const hasRightArrowPath = pathData && pathData.includes('l6-6');
                    return onRightSide && inVerticalRange && hasRightArrowPath && rect.width > 0;
                });

                if (!rightArrowSvg) return null;

                const rect = rightArrowSvg.getBoundingClientRect();
                return {
                    x: rect.x + rect.width / 2,
                    y: rect.y + rect.height / 2
                };
            }""")

            if arrow_pos:
                logger.info(
                    f"Found carousel arrow at ({arrow_pos['x']}, {arrow_pos['y']})"
                )

                # Click the arrow multiple times to collect all images
                for click_num in range(5):  # Max 5 clicks
                    await self.page.mouse.click(arrow_pos["x"], arrow_pos["y"])
                    await asyncio.sleep(2)  # Wait for lazy loading

                    new_added = await collect_current_images()
                    logger.info(
                        f"Click {click_num + 1}: +{new_added} new images (total: {len(all_image_urls)})"
                    )
                    if new_added == 0:
                        break  # No new images, we've seen them all

                logger.info(
                    f"After carousel navigation: {len(all_image_urls)} total images"
                )
            else:
                logger.info("No carousel arrow found, using initial images only")

        except Exception as e:
            logger.warning(f"Could not navigate carousel: {e}")

        image_urls = list(all_image_urls.values())

        if not image_urls:
            logger.warning("No product images found")
            return []

        logger.info(f"Found {len(image_urls)} unique product images")

        saved_paths = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for idx, img_url in enumerate(image_urls, start=1):
                try:
                    # Convert thumbnail URL to full-resolution URL
                    # Remove resize parameter from Aliyun OSS URL
                    full_res_url = self._convert_to_full_resolution_url(img_url)

                    # Determine file extension
                    ext = "webp" if ".webp" in full_res_url else "jpg"
                    filename = f"product_image_{idx}.{ext}"
                    output_path = images_dir / filename

                    # Skip if exists
                    if output_path.exists():
                        logger.debug(f"Image already exists: {filename}")
                        saved_paths.append(f"product_images/{filename}")
                        continue

                    # Download image at full resolution
                    logger.debug(
                        f"Downloading image {idx}/{len(image_urls)}: {filename}"
                    )
                    response = await client.get(full_res_url)
                    response.raise_for_status()

                    # Save image
                    output_path.write_bytes(response.content)
                    saved_paths.append(f"product_images/{filename}")
                    logger.debug(f"✓ Saved: {filename}")

                except Exception as e:
                    logger.warning(f"Failed to download image {idx}: {e}")
                    continue

        logger.success(
            f"✓ Downloaded {len(saved_paths)}/{len(image_urls)} product images"
        )
        return saved_paths

    def _convert_to_full_resolution_url(self, url: str) -> str:
        """
        Convert thumbnail URL to full-resolution URL by removing resize parameters.

        Args:
            url: Original image URL (may include resize parameters)

        Returns:
            Full-resolution image URL
        """
        # If URL has Aliyun OSS parameters
        if "?x-oss-process=" in url:
            base_url = url.split("?")[0]
            # Return base URL with only format parameter (no resize)
            return f"{base_url}?x-oss-process=image/format,webp"

        # If no parameters, return as-is
        return url

    @retry_async(max_attempts=3, delay=3.0)
    async def download_video(self, video: VideoData, output_dir: Path) -> bool:
        """
        Download a single video with retry logic.

        Args:
            video: VideoData object with video information
            output_dir: Directory to save the video

        Returns:
            True if download successful, False otherwise
        """
        if not video.video_url:
            logger.warning(f"No video URL for video {video.rank}: {video.title}")
            return False

        # Generate filename
        safe_creator = sanitize_filename(video.creator_username)
        filename = f"video_{video.rank}_{safe_creator}.mp4"
        output_path = output_dir / filename

        # Skip if already exists
        if output_path.exists():
            logger.info(f"Video already exists: {filename}")
            video.local_path = f"ref_video/{filename}"
            return True

        logger.info(f"Downloading video {video.rank}: {video.title}")

        # Try multiple download strategies
        success = False

        # Strategy 1: yt-dlp (most reliable for TikTok)
        if not success:
            success = await self._download_via_ytdlp(video.video_url, output_path)

        # Strategy 2: Playwright network intercept
        if not success:
            success = await self._download_via_playwright_intercept(
                video.video_url, output_path
            )

        # Strategy 3: Direct HTTP download
        if not success:
            success = await self._download_via_http(video.video_url, output_path)

        # Strategy 4: Extract video source from page
        if not success:
            success = await self._download_from_embedded_video(
                video.video_url, output_path
            )

        if success:
            video.local_path = f"ref_video/{filename}"
            logger.success(f"✓ Downloaded: {filename}")
        else:
            logger.error(f"✗ Failed to download: {filename}")

        return success

    async def _download_via_ytdlp(self, video_url: str, output_path: Path) -> bool:
        """
        Download video using yt-dlp (most reliable for TikTok).

        Args:
            video_url: URL to the TikTok video
            output_path: Path to save the video

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug("Trying yt-dlp strategy...")

            # yt-dlp command with options
            # Use python3 -m yt_dlp since yt-dlp is not in PATH
            cmd = [
                "python3",
                "-m",
                "yt_dlp",
                "-f",
                "best",  # Download best quality
                "--no-playlist",  # Don't download playlists
                "-o",
                str(output_path),  # Output path
                "--quiet",  # Less verbose
                "--no-warnings",  # Suppress warnings
                video_url,
            ]

            # Run yt-dlp in subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0 and output_path.exists():
                logger.debug(f"Saved video via yt-dlp: {output_path.name}")
                return True
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.debug(f"yt-dlp failed: {error_msg}")
                return False

        except Exception as e:
            logger.debug(f"yt-dlp strategy failed: {e}")
            return False

    async def _download_via_playwright_intercept(
        self, video_url: str, output_path: Path
    ) -> bool:
        """
        Download video by intercepting network requests.

        Args:
            video_url: URL to the video page
            output_path: Path to save the video

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug("Trying Playwright network intercept strategy...")

            video_data = []
            video_captured = asyncio.Event()

            async def handle_response(response):
                """Handle network responses to capture video."""
                try:
                    content_type = response.headers.get("content-type", "")

                    # Look for video content
                    if any(
                        t in content_type.lower()
                        for t in [
                            "video/mp4",
                            "video/quicktime",
                            "application/octet-stream",
                        ]
                    ):
                        # Check if it's a significant video file (not a thumbnail)
                        content_length = response.headers.get("content-length")
                        if content_length and int(content_length) > 100000:  # > 100KB
                            logger.debug(f"Capturing video response: {response.url}")
                            body = await response.body()
                            video_data.append(body)
                            video_captured.set()
                except Exception as e:
                    logger.debug(f"Error in response handler: {e}")

            # Set up response handler
            self.page.on("response", handle_response)

            try:
                # Navigate to video page
                await self.page.goto(
                    video_url, wait_until="networkidle", timeout=self.timeout
                )

                # Wait a bit for video to load
                await asyncio.sleep(3)

                # Wait for video capture (with timeout)
                try:
                    await asyncio.wait_for(video_captured.wait(), timeout=10)
                except asyncio.TimeoutError:
                    logger.debug("No video captured via intercept")
                    return False

                # Save the captured video
                if video_data:
                    with open(output_path, "wb") as f:
                        f.write(video_data[0])
                    logger.debug(f"Saved video via intercept: {output_path.name}")
                    return True

                return False

            finally:
                # Remove response handler
                self.page.remove_listener("response", handle_response)

        except Exception as e:
            logger.debug(f"Playwright intercept failed: {e}")
            return False

    async def _download_via_http(self, video_url: str, output_path: Path) -> bool:
        """
        Download video via direct HTTP request.

        Args:
            video_url: URL to download from
            output_path: Path to save the video

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug("Trying direct HTTP download strategy...")

            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=self.timeout / 1000,  # Convert to seconds
            ) as client:
                response = await client.get(video_url)

                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")

                    if "video" in content_type.lower():
                        with open(output_path, "wb") as f:
                            f.write(response.content)
                        logger.debug(f"Saved video via HTTP: {output_path.name}")
                        return True

                logger.debug(f"HTTP download failed: status {response.status_code}")
                return False

        except Exception as e:
            logger.debug(f"HTTP download failed: {e}")
            return False

    async def _download_from_embedded_video(
        self, video_url: str, output_path: Path
    ) -> bool:
        """
        Download video by extracting source from embedded video element.

        Args:
            video_url: URL to the video page
            output_path: Path to save the video

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug("Trying embedded video extraction strategy...")

            # Navigate to page
            await self.page.goto(
                video_url, wait_until="domcontentloaded", timeout=self.timeout
            )
            await asyncio.sleep(3)

            # Find video element
            video_element = await self.page.query_selector("video")

            if not video_element:
                logger.debug("No video element found")
                return False

            # Get video source
            video_src = await video_element.get_attribute("src")

            if not video_src:
                # Try to find source element
                source_element = await video_element.query_selector("source")
                if source_element:
                    video_src = await source_element.get_attribute("src")

            if not video_src:
                logger.debug("No video source found")
                return False

            logger.debug(f"Found video source: {video_src[:100]}...")

            # Download from the extracted source
            return await self._download_via_http(video_src, output_path)

        except Exception as e:
            logger.debug(f"Embedded video extraction failed: {e}")
            return False

    async def download_videos_batch(
        self, videos: List[VideoData], output_dir: Path, max_concurrent: int = 3
    ) -> List[VideoData]:
        """
        Download multiple videos in batch.

        Args:
            videos: List of VideoData objects
            output_dir: Directory to save videos
            max_concurrent: Maximum concurrent downloads

        Returns:
            List of VideoData objects with updated local_path
        """
        logger.info(f"Downloading {len(videos)} videos to {output_dir}")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Download videos with limited concurrency
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_with_semaphore(video: VideoData) -> VideoData:
            async with semaphore:
                await self.download_video(video, output_dir)
                return video

        # Download all videos
        results = await asyncio.gather(
            *[download_with_semaphore(video) for video in videos],
            return_exceptions=True,
        )

        # Count successes
        successful = sum(
            1 for r in results if not isinstance(r, Exception) and r.local_path
        )
        logger.info(f"Downloaded {successful}/{len(videos)} videos successfully")

        return videos
