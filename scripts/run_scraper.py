#!/usr/bin/env python3
"""
TikTok Shop Product Scraper CLI - Multi-Source Support

Usage:
    # Single product from tabcut.com (default)
    python run_scraper.py --product-id 1729630936525936882

    # Single product from fastmoss.com
    python run_scraper.py --product-id 1729630936525936882 --source fastmoss

    # Batch from CSV
    python run_scraper.py --batch-file products.csv

    # Batch from fastmoss with video downloads
    python run_scraper.py --batch-file products.csv --source fastmoss --download-videos

    # Analyze downloaded videos
    python run_scraper.py --batch-file products.csv --analyze-videos

    # Resume interrupted batch
    python run_scraper.py --batch-file products.csv --resume
"""

import argparse
import asyncio
import csv
import json
import os
import sys
from pathlib import Path
from typing import List, Set
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from loguru import logger

# Add scrapers to path
sys.path.insert(0, str(Path(__file__).parent))

from tabcut_scraper.scraper import TabcutScraper
from tabcut_scraper.models import ScraperConfig
from tabcut_scraper.utils import setup_logging
from fastmoss_scraper.scraper import FastMossScraper

# Import video analyzer
import analyze_video


console = Console()


class ProgressTracker:
    """Track batch scraping progress with resume capability."""

    def __init__(self, batch_file: str):
        """
        Initialize progress tracker.

        Args:
            batch_file: Path to the batch CSV file
        """
        self.batch_file = batch_file
        self.progress_file = f"{batch_file}.progress.json"
        self.progress = self._load_progress()

    def _load_progress(self) -> dict:
        """Load existing progress or create new."""
        if Path(self.progress_file).exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load progress file: {e}")

        return {
            'completed': [],
            'failed': [],
            'pending': []
        }

    def save_progress(self) -> None:
        """Save current progress to file."""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")

    def mark_completed(self, product_id: str) -> None:
        """Mark product as completed."""
        if product_id in self.progress['pending']:
            self.progress['pending'].remove(product_id)
        if product_id not in self.progress['completed']:
            self.progress['completed'].append(product_id)
        self.save_progress()

    def mark_failed(self, product_id: str, error: str) -> None:
        """Mark product as failed."""
        if product_id in self.progress['pending']:
            self.progress['pending'].remove(product_id)
        self.progress['failed'].append({'product_id': product_id, 'error': error})
        self.save_progress()

    def get_remaining(self, all_ids: List[str]) -> List[str]:
        """
        Get IDs not yet completed.

        Args:
            all_ids: All product IDs from batch file

        Returns:
            List of product IDs to process
        """
        completed_ids = set(self.progress['completed'])
        return [pid for pid in all_ids if pid not in completed_ids]

    def is_completed(self, product_id: str) -> bool:
        """Check if product is already completed."""
        return product_id in self.progress['completed']


def load_product_ids_from_csv(csv_file: str) -> List[str]:
    """
    Load product IDs from CSV file.

    Args:
        csv_file: Path to CSV file

    Returns:
        List of product IDs
    """
    product_ids = []

    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                # Skip header row
                if i == 0 and row[0].lower() == 'product_id':
                    continue

                if row and row[0].strip():
                    product_ids.append(row[0].strip())

        logger.info(f"Loaded {len(product_ids)} product IDs from {csv_file}")
        return product_ids

    except Exception as e:
        logger.error(f"Failed to load CSV file: {e}")
        raise


async def scrape_single_product(
    product_id: str,
    config: ScraperConfig,
    download_videos: bool = False,
    source: str = 'tabcut'
) -> bool:
    """
    Scrape a single product.

    Args:
        product_id: Product ID to scrape
        config: Scraper configuration
        download_videos: Whether to download videos
        source: Data source ('tabcut' or 'fastmoss')

    Returns:
        True if successful, False otherwise
    """
    try:
        # Select appropriate scraper
        ScraperClass = FastMossScraper if source == 'fastmoss' else TabcutScraper

        async with ScraperClass(config) as scraper:
            await scraper.scrape_product(
                product_id,
                download_videos=download_videos
            )
        return True

    except Exception as e:
        logger.error(f"Failed to scrape product {product_id}: {e}")
        return False


async def scrape_batch(
    product_ids: List[str],
    config: ScraperConfig,
    download_videos: bool = False,
    resume: bool = False,
    source: str = 'tabcut'
) -> dict:
    """
    Scrape multiple products with progress tracking.

    Args:
        product_ids: List of product IDs
        config: Scraper configuration
        download_videos: Whether to download videos
        resume: Whether to resume from previous run
        source: Data source ('tabcut' or 'fastmoss')

    Returns:
        Results dictionary
    """
    # Initialize progress tracker
    tracker = ProgressTracker(args.batch_file) if resume else None

    # Filter out completed IDs if resuming
    if resume and tracker:
        product_ids = tracker.get_remaining(product_ids)
        console.print(f"[yellow]Resuming: {len(product_ids)} products remaining[/yellow]")

    if not product_ids:
        console.print("[green]All products already completed![/green]")
        return {'completed': [], 'failed': []}

    results = {
        'completed': [],
        'failed': []
    }

    # Select appropriate scraper
    ScraperClass = FastMossScraper if source == 'fastmoss' else TabcutScraper

    # Progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task(
            f"[cyan]Scraping products from {source}...",
            total=len(product_ids)
        )

        async with ScraperClass(config) as scraper:
            for i, product_id in enumerate(product_ids, 1):
                progress.update(
                    task,
                    description=f"[cyan]Product {i}/{len(product_ids)}: {product_id}"
                )

                try:
                    await scraper.scrape_product(
                        product_id,
                        download_videos=download_videos
                    )
                    results['completed'].append(product_id)

                    if tracker:
                        tracker.mark_completed(product_id)

                    console.print(f"[green]✓ Product {product_id} completed[/green]")

                except Exception as e:
                    error_msg = str(e)
                    results['failed'].append({'product_id': product_id, 'error': error_msg})

                    if tracker:
                        tracker.mark_failed(product_id, error_msg)

                    console.print(f"[red]✗ Product {product_id} failed: {error_msg}[/red]")

                progress.advance(task)

    return results


def analyze_product_videos(product_ids: List[str], output_base_dir: str) -> dict:
    """
    Analyze all downloaded videos for products.

    Args:
        product_ids: List of product IDs
        output_base_dir: Base output directory

    Returns:
        Analysis results summary
    """
    results = {
        'analyzed': [],
        'failed': []
    }

    output_dir = Path(output_base_dir)

    for product_id in product_ids:
        product_dir = output_dir / product_id / 'ref_video'

        if not product_dir.exists():
            console.print(f"[yellow]No videos found for {product_id}[/yellow]")
            continue

        # Find all MP4 files
        videos = list(product_dir.glob('*.mp4'))

        if not videos:
            console.print(f"[yellow]No MP4 videos found for {product_id}[/yellow]")
            continue

        console.print(f"[cyan]Analyzing {len(videos)} videos for {product_id}...[/cyan]")

        # Create analysis output directory
        analysis_dir = product_dir / 'analysis'
        analysis_dir.mkdir(exist_ok=True)

        for video in videos:
            try:
                console.print(f"  - {video.name}...", end="")
                analyze_video.analyze_video(str(video), str(analysis_dir))
                console.print(" [green]✓[/green]")
                results['analyzed'].append(f"{product_id}/{video.name}")

            except Exception as e:
                console.print(f" [red]✗[/red] {e}")
                results['failed'].append({'product': product_id, 'video': video.name, 'error': str(e)})

    return results


def create_config(args) -> ScraperConfig:
    """
    Create scraper configuration from arguments and environment.

    Args:
        args: Parsed command line arguments

    Returns:
        ScraperConfig object
    """
    return ScraperConfig(
        headless=not args.headed,
        timeout=int(os.getenv('DEFAULT_TIMEOUT', 30000)),
        max_retries=int(os.getenv('MAX_RETRIES', 3)),
        download_timeout=int(os.getenv('DOWNLOAD_TIMEOUT', 300000)),
        output_base_dir=args.output_dir or os.getenv('OUTPUT_BASE_DIR', '../product_list'),
        log_level=args.log_level or os.getenv('LOG_LEVEL', 'INFO')
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='TikTok Shop Product Scraper - Multi-Source Support (tabcut.com & fastmoss.com)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--product-id',
        type=str,
        help='Single product ID to scrape'
    )
    input_group.add_argument(
        '--batch-file',
        type=str,
        help='CSV file with product IDs'
    )

    # Source selection
    parser.add_argument(
        '--source',
        type=str,
        choices=['tabcut', 'fastmoss'],
        default='tabcut',
        help='Data source to scrape from (default: tabcut)'
    )

    # Scraping options
    parser.add_argument(
        '--download-videos',
        action='store_true',
        help='Download top 5 videos for each product'
    )
    parser.add_argument(
        '--analyze-videos',
        action='store_true',
        help='Analyze downloaded videos (requires videos to be downloaded first)'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume interrupted batch (requires --batch-file)'
    )

    # Output options
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory (default: ../product_list)'
    )

    # Browser options
    parser.add_argument(
        '--headed',
        action='store_true',
        help='Run browser in headed mode (visible)'
    )

    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )

    global args
    args = parser.parse_args()

    # Load environment variables
    env_path = Path(__file__).parent / 'config' / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        console.print("[yellow]Warning: .env file not found. Make sure credentials are set.[/yellow]")

    # Setup logging
    log_level = args.log_level or os.getenv('LOG_LEVEL', 'INFO')
    setup_logging(log_dir='logs', log_level=log_level)

    # Create configuration
    config = create_config(args)

    # Print banner
    console.print("\n[bold cyan]TikTok Shop Product Scraper[/bold cyan]")
    console.print(f"[dim]Data source: {args.source.upper()}[/dim]\n")

    # Run scraper
    try:
        if args.product_id:
            # Single product mode
            console.print(f"[cyan]Scraping product ID: {args.product_id} from {args.source}[/cyan]")
            success = asyncio.run(
                scrape_single_product(
                    args.product_id,
                    config,
                    download_videos=args.download_videos,
                    source=args.source
                )
            )

            if success:
                console.print("\n[bold green]✓ Scraping completed successfully![/bold green]")
                sys.exit(0)
            else:
                console.print("\n[bold red]✗ Scraping failed![/bold red]")
                sys.exit(1)

        elif args.batch_file:
            # Batch mode
            product_ids = load_product_ids_from_csv(args.batch_file)

            console.print(f"[cyan]Batch mode: {len(product_ids)} products from {args.source}[/cyan]")
            if args.download_videos:
                console.print("[cyan]Video downloads: ENABLED[/cyan]")
            if args.analyze_videos:
                console.print("[cyan]Video analysis: ENABLED[/cyan]")
            if args.resume:
                console.print("[yellow]Resume mode: ENABLED[/yellow]")

            console.print()

            results = asyncio.run(
                scrape_batch(
                    product_ids,
                    config,
                    download_videos=args.download_videos,
                    resume=args.resume,
                    source=args.source
                )
            )

            # Print summary
            console.print("\n[bold]Batch Scraping Summary:[/bold]")
            console.print(f"[green]✓ Completed: {len(results['completed'])}[/green]")
            console.print(f"[red]✗ Failed: {len(results['failed'])}[/red]")

            if results['failed']:
                console.print("\n[bold red]Failed Products:[/bold red]")
                for failure in results['failed']:
                    console.print(f"  - {failure['product_id']}: {failure['error']}")

            # Video analysis step
            if args.analyze_videos and results['completed']:
                console.print("\n[bold cyan]Analyzing Videos...[/bold cyan]")
                analysis_results = analyze_product_videos(
                    results['completed'],
                    config.output_base_dir
                )

                console.print("\n[bold]Video Analysis Summary:[/bold]")
                console.print(f"[green]✓ Analyzed: {len(analysis_results['analyzed'])}[/green]")
                if analysis_results['failed']:
                    console.print(f"[red]✗ Failed: {len(analysis_results['failed'])}[/red]")

            # Exit with appropriate code
            sys.exit(0 if not results['failed'] else 1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Scraping interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        logger.exception("Unexpected error")
        sys.exit(1)


if __name__ == '__main__':
    main()
