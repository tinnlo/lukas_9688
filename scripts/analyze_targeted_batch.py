#!/usr/bin/env python3
"""
Targeted TikTok Video Analysis - Batch Processing

Processes multiple TikTok URLs from a CSV file.

CSV Format:
url,product_name,campaign_id
https://www.tiktok.com/@user1/video/111,Product A,winter_2026
https://www.tiktok.com/@user2/video/222,Product B,

Usage:
    python analyze_targeted_batch.py \
        --csv targeted_videos.csv \
        --output-dir "targeted_analysis/20260114"
"""

import argparse
import csv
import sys
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger


def analyze_single_video(url: str, product_name: str, output_dir: str) -> dict:
    """
    Run analyze_targeted_video.py for a single video.

    Returns:
        dict with status, video_id, error (if any)
    """
    try:
        # Extract video ID for logging
        from targeted_analysis.metadata_extractor import extract_video_id
        video_id = extract_video_id(url)

        logger.info(f"Starting analysis: {video_id} ({product_name})")

        # Call analyze_targeted_video.py as subprocess
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).parent / "analyze_targeted_video.py"),
                "--url", url,
                "--product-name", product_name,
                "--output-dir", output_dir
            ],
            capture_output=True,
            text=True,
            timeout=1200  # 20 minutes per video
        )

        if result.returncode == 0:
            logger.success(f"✅ Completed: {video_id}")
            return {"status": "success", "video_id": video_id, "url": url}
        else:
            logger.error(f"❌ Failed: {video_id}")
            logger.error(result.stderr[-500:])  # Last 500 chars of error
            return {"status": "failed", "video_id": video_id, "url": url, "error": result.stderr[-200:]}

    except Exception as e:
        logger.error(f"❌ Exception: {url} - {e}")
        return {"status": "error", "url": url, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Batch analyze targeted TikTok videos"
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="CSV file with columns: url, product_name, campaign_id"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Base output directory (e.g., targeted_analysis/20260114)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=3,
        help="Maximum concurrent videos (default: 3)"
    )

    args = parser.parse_args()

    # Setup logging
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    # Read CSV
    csv_path = Path(args.csv)
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return 1

    tasks = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('url') or not row.get('product_name'):
                logger.warning(f"Skipping invalid row: {row}")
                continue
            tasks.append({
                'url': row['url'].strip(),
                'product_name': row['product_name'].strip(),
                'campaign_id': row.get('campaign_id', '').strip()
            })

    logger.info("=" * 70)
    logger.info("TARGETED VIDEO ANALYSIS - BATCH PROCESSING")
    logger.info("=" * 70)
    logger.info(f"CSV: {csv_path}")
    logger.info(f"Output: {args.output_dir}")
    logger.info(f"Videos: {len(tasks)}")
    logger.info(f"Max workers: {args.max_workers}")
    logger.info("=" * 70)

    # Process videos in parallel
    results = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(
                analyze_single_video,
                task['url'],
                task['product_name'],
                args.output_dir
            ): task
            for task in tasks
        }

        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Task failed: {task['url']} - {e}")
                results.append({"status": "error", "url": task['url'], "error": str(e)})

    # Summary
    logger.info("=" * 70)
    logger.info("BATCH PROCESSING COMPLETE")
    logger.info("=" * 70)

    success_count = sum(1 for r in results if r['status'] == 'success')
    failed_count = len(results) - success_count

    logger.info(f"Total: {len(results)}")
    logger.info(f"Success: {success_count}")
    logger.info(f"Failed: {failed_count}")

    if failed_count > 0:
        logger.warning("\nFailed videos:")
        for r in results:
            if r['status'] != 'success':
                logger.warning(f"  - {r.get('video_id', r['url'])}: {r.get('error', 'Unknown error')[:100]}")

    logger.info("=" * 70)

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
