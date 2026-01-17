"""
Metadata extraction for TikTok URLs (Phase 1).

Extracts video ID, fetches metadata using yt-dlp, and downloads video files.
"""

import re
import subprocess
import json
from pathlib import Path
from typing import Optional, Tuple
from loguru import logger

from .models import VideoMetadata


def extract_video_id(url: str) -> str:
    """
    Extract video ID from TikTok URL.

    Supports formats:
    - https://www.tiktok.com/@username/video/1234567890
    - https://vm.tiktok.com/ABCDEFG (short URL)
    - https://vt.tiktok.com/ABCDEFG (another short URL)

    Args:
        url: TikTok video URL

    Returns:
        Video ID as string

    Raises:
        ValueError: If video ID cannot be extracted
    """
    # Pattern 1: Standard URL with video ID
    match = re.search(r'/video/(\d+)', url)
    if match:
        video_id = match.group(1)
        logger.debug(f"Extracted video ID from URL pattern: {video_id}")
        return video_id

    # Pattern 2: Short URL - use yt-dlp to get full ID
    logger.debug(f"URL appears to be a short link, using yt-dlp to resolve")
    try:
        result = subprocess.run(
            ['yt-dlp', '--print', 'id', url],
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        video_id = result.stdout.strip()
        if video_id:
            logger.info(f"Resolved short URL to video ID: {video_id}")
            return video_id
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to extract video ID with yt-dlp: {e}")
        raise ValueError(f"Could not extract video ID from URL: {url}")

    raise ValueError(f"Invalid TikTok URL format: {url}")


def fetch_metadata(url: str, max_retries: int = 3) -> VideoMetadata:
    """
    Fetch video metadata using yt-dlp.

    Args:
        url: TikTok video URL
        max_retries: Maximum number of retry attempts

    Returns:
        VideoMetadata object with extracted information

    Raises:
        RuntimeError: If metadata fetch fails after all retries
    """
    video_id = extract_video_id(url)
    logger.info(f"Fetching metadata for video ID: {video_id}")

    # Build yt-dlp command
    cmd = [
        'yt-dlp',
        '--dump-json',
        '--no-download',
        '--cookies-from-browser', 'chrome',  # Use browser cookies for rate limit bypass
        url
    ]

    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )

            # Parse JSON output
            data = json.loads(result.stdout)

            # Extract relevant fields
            metadata = VideoMetadata(
                video_id=video_id,
                url=url,
                creator=data.get('uploader', 'Unknown'),
                title=data.get('title', 'Untitled'),
                duration=float(data.get('duration', 0)),
                views=data.get('view_count'),
                likes=data.get('like_count'),
                comments=data.get('comment_count'),
                shares=data.get('repost_count'),
                upload_date=data.get('upload_date'),
                description=data.get('description'),
                music=data.get('track')
            )

            logger.success(
                f"Metadata fetched: {metadata.creator} | "
                f"{metadata.duration:.1f}s | "
                f"{metadata.views or 'N/A'} views"
            )

            return metadata

        except subprocess.TimeoutExpired:
            logger.warning(f"Metadata fetch timeout (attempt {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                raise RuntimeError(f"Metadata fetch timed out after {max_retries} attempts")

        except subprocess.CalledProcessError as e:
            logger.warning(
                f"yt-dlp error (attempt {attempt + 1}/{max_retries}): {e.stderr}"
            )
            if attempt == max_retries - 1:
                raise RuntimeError(f"Failed to fetch metadata: {e.stderr}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse yt-dlp JSON output: {e}")
            raise RuntimeError(f"Invalid JSON response from yt-dlp")

    raise RuntimeError("Metadata fetch failed after all retries")


def download_video(
    url: str,
    output_dir: Path,
    filename: Optional[str] = None,
    max_retries: int = 3
) -> Tuple[Path, float]:
    """
    Download TikTok video using yt-dlp.

    Args:
        url: TikTok video URL
        output_dir: Directory to save video
        filename: Optional custom filename (without extension)
        max_retries: Maximum number of retry attempts

    Returns:
        Tuple of (video_path, duration_seconds)

    Raises:
        RuntimeError: If download fails after all retries
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    video_id = extract_video_id(url)

    # Set output template
    if filename:
        output_template = str(output_dir / f"{filename}.%(ext)s")
    else:
        output_template = str(output_dir / "video.%(ext)s")

    logger.info(f"Downloading video ID: {video_id} to {output_dir}")

    # Build yt-dlp command
    cmd = [
        'yt-dlp',
        '--format', 'best',
        '--output', output_template,
        '--cookies-from-browser', 'chrome',
        '--no-playlist',
        url
    ]

    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
                check=True
            )

            # Find the downloaded file
            video_files = list(output_dir.glob("video.*"))
            if not video_files:
                # Try with custom filename if specified
                if filename:
                    video_files = list(output_dir.glob(f"{filename}.*"))

            if not video_files:
                raise RuntimeError("Downloaded video file not found")

            video_path = video_files[0]

            # Get duration using ffprobe
            try:
                duration_cmd = [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    str(video_path)
                ]
                duration_result = subprocess.run(
                    duration_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=True
                )
                duration = float(duration_result.stdout.strip())
            except Exception as e:
                logger.warning(f"Could not determine video duration: {e}")
                duration = 0.0

            file_size_mb = video_path.stat().st_size / (1024 * 1024)
            logger.success(
                f"Video downloaded: {video_path.name} "
                f"({file_size_mb:.1f}MB, {duration:.1f}s)"
            )

            return video_path, duration

        except subprocess.TimeoutExpired:
            logger.warning(f"Download timeout (attempt {attempt + 1}/{max_retries})")
            if attempt == max_retries - 1:
                raise RuntimeError(f"Download timed out after {max_retries} attempts")

        except subprocess.CalledProcessError as e:
            logger.warning(
                f"yt-dlp download error (attempt {attempt + 1}/{max_retries}): {e.stderr}"
            )
            if attempt == max_retries - 1:
                raise RuntimeError(f"Failed to download video: {e.stderr}")

    raise RuntimeError("Video download failed after all retries")


def extract_metadata_and_download(
    url: str,
    output_dir: Path,
    product_name: Optional[str] = None
) -> Tuple[VideoMetadata, Path]:
    """
    Complete Phase 1: Extract metadata and download video.

    Args:
        url: TikTok video URL
        output_dir: Directory to save outputs
        product_name: Optional product name for context

    Returns:
        Tuple of (metadata, video_path)
    """
    logger.info(f"=== PHASE 1: METADATA EXTRACTION ===")
    logger.info(f"URL: {url}")
    if product_name:
        logger.info(f"Product: {product_name}")

    # Step 1: Fetch metadata
    metadata = fetch_metadata(url)

    # Step 2: Download video
    video_path, duration = download_video(url, output_dir)

    # Update duration from actual video file if more accurate
    if duration > 0 and abs(duration - metadata.duration) > 1.0:
        logger.info(f"Updating duration from metadata ({metadata.duration:.1f}s) to actual ({duration:.1f}s)")
        metadata.duration = duration

    # Step 3: Save metadata to JSON
    metadata_path = output_dir / "metadata.json"
    metadata.save_to_file(metadata_path)
    logger.success(f"Metadata saved to: {metadata_path}")

    logger.success(f"✅ PHASE 1 COMPLETE")
    return metadata, video_path
