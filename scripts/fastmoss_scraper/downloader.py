"""Video and image downloader for FastMoss - independent implementation."""

import asyncio
import httpx
import subprocess
from pathlib import Path
from typing import List, Optional
from playwright.async_api import Page
from loguru import logger

from .models import VideoData
from .utils import retry_async, sanitize_filename


class VideoDownloader:
    """Download TikTok videos and product images from FastMoss data."""

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
        Download product images from FastMoss product gallery/carousel.

        Args:
            output_dir: Directory to save images

        Returns:
            List of saved image paths
        """
        logger.info("Downloading product images from FastMoss gallery...")

        # Create images directory
        images_dir = output_dir / "product_images"
        images_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Extract product images from carousel/gallery
            image_urls = await self.page.evaluate("""() => {
                const images = [];

                // Strategy 1: Look for carousel/swiper images
                const carouselImages = document.querySelectorAll('.swiper-slide img, [class*="swiper"] img, [class*="carousel"] img, [class*="slider"] img');
                carouselImages.forEach(img => {
                    if (img.src && img.naturalWidth > 150 && !img.src.includes('avatar')) {
                        images.push(img.src);
                    }
                });

                // Strategy 2: Look for large images in the upper portion (product gallery)
                if (images.length === 0) {
                    const allImages = Array.from(document.querySelectorAll('img'))
                        .filter(img => {
                            const rect = img.getBoundingClientRect();
                            const aspectRatio = img.naturalWidth / img.naturalHeight;
                            
                            // Reject banners (very wide/short) and vertical ads (very tall/narrow)
                            const isReasonableAspect = aspectRatio >= 0.4 && aspectRatio <= 3.0;
                            
                            return img.src &&
                                   img.naturalWidth > 300 &&
                                   img.naturalHeight > 300 &&
                                   isReasonableAspect &&  // NEW: Reject banners & weird ratios
                                   rect.top < 1000 &&  // In upper portion
                                   !img.src.includes('avatar') &&
                                   !img.src.includes('logo') &&
                                   !img.src.includes('icon') &&
                                   !img.src.includes('banner');  // NEW: Explicit banner rejection
                        })
                        .map(img => img.src);
                    images.push(...allImages);
                }

                // Remove duplicates
                return [...new Set(images)];
            }""")

            if not image_urls:
                logger.warning("No product images found in gallery")
                return []

            logger.info(f"Found {len(image_urls)} product images in gallery")

            saved_paths = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                for idx, img_url in enumerate(image_urls, start=1):
                    try:
                        # Determine file extension
                        ext = (
                            "webp"
                            if ".webp" in img_url
                            else ("png" if ".png" in img_url else "jpg")
                        )
                        filename = f"product_image_{idx}.{ext}"
                        output_path = images_dir / filename

                        # Skip if exists
                        if output_path.exists():
                            logger.debug(f"Image already exists: {filename}")
                            saved_paths.append(f"product_images/{filename}")
                            continue

                        # Download image
                        logger.debug(
                            f"Downloading image {idx}/{len(image_urls)}: {filename}"
                        )
                        response = await client.get(img_url)
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

        except Exception as e:
            logger.error(f"Failed to download product images: {e}")
            return []

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

        # Strategy 2: Direct HTTP download
        if not success:
            success = await self._download_via_http(video.video_url, output_path)

        # Strategy 3: Extract video source from page
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
        Download video using yt-dlp.

        Args:
            video_url: URL to the TikTok video
            output_path: Path to save the video

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug("Trying yt-dlp strategy...")

            cmd = [
                "yt-dlp",
                "-f",
                "best",
                "--no-playlist",
                "-o",
                str(output_path),
                "--quiet",
                "--no-warnings",
                video_url,
            ]

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
                follow_redirects=True, timeout=self.timeout / 1000
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
