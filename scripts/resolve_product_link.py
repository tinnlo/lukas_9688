#!/usr/bin/env python3
"""
TikTok Product Link Resolver CLI

Resolves TikTok product links (vm.tiktok.com shortened links, direct shop links, etc.)
to extract the numeric product IDs needed for the product scraper.

Usage:
    # Single link
    python resolve_product_link.py --url "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/"

    # Multiple links from file
    python resolve_product_link.py --links-file links.txt

    # Output to CSV
    python resolve_product_link.py --links-file links.txt --output products.csv

    # Run with visible browser
    python resolve_product_link.py --url "..." --headed
"""

import argparse
import asyncio
import csv
import json
import sys
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from link_resolver.resolver import LinkResolver
from link_resolver.models import LinkResolverConfig, ResolvedProduct

console = Console()


def load_links_from_file(file_path: str) -> List[str]:
    """
    Load URLs from a text file (one per line).

    Args:
        file_path: Path to the file

    Returns:
        List of URLs
    """
    urls = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)

        logger.info(f"Loaded {len(urls)} URLs from {file_path}")
        return urls

    except Exception as e:
        logger.error(f"Failed to load links file: {e}")
        raise


def save_results_to_csv(results: List[ResolvedProduct], output_file: str) -> None:
    """
    Save resolved product IDs to CSV file (appends new IDs, avoids duplicates).

    Args:
        results: List of resolved products
        output_file: Output CSV file path
    """
    try:
        output_path = Path(output_file)
        existing_ids = set()

        # Load existing product IDs if file exists
        if output_path.exists():
            with open(output_file, 'r') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    if row and row[0].strip():
                        existing_ids.add(row[0].strip())

            logger.info(f"Found {len(existing_ids)} existing product IDs")

        # Collect new unique IDs
        new_ids = []
        duplicate_count = 0

        for result in results:
            if result.success:
                if result.product_id not in existing_ids:
                    new_ids.append(result.product_id)
                    existing_ids.add(result.product_id)
                else:
                    duplicate_count += 1
                    logger.debug(f"Skipping duplicate: {result.product_id}")

        # Append new IDs to file
        if new_ids:
            # If file doesn't exist, create with header
            if not output_path.exists():
                with open(output_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['product_id'])

            # Append new IDs
            with open(output_file, 'a', newline='') as f:
                writer = csv.writer(f)
                for product_id in new_ids:
                    writer.writerow([product_id])

            logger.info(f"Appended {len(new_ids)} new product IDs to {output_file}")
        else:
            logger.info("No new product IDs to add")

        if duplicate_count > 0:
            logger.info(f"Skipped {duplicate_count} duplicate(s)")

        # Show total count
        logger.info(f"Total product IDs in file: {len(existing_ids)}")

    except Exception as e:
        logger.error(f"Failed to save CSV: {e}")
        raise


def save_results_to_json(results: List[ResolvedProduct], output_file: str) -> None:
    """
    Save detailed results to JSON file.

    Args:
        results: List of resolved products
        output_file: Output JSON file path
    """
    try:
        data = [result.to_dict() for result in results]

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved detailed results to {output_file}")

    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")
        raise


def print_results_table(results: List[ResolvedProduct]) -> None:
    """
    Print results as a formatted table.

    Args:
        results: List of resolved products
    """
    table = Table(title="Resolved Product Links")

    table.add_column("Original URL", style="cyan", overflow="fold", max_width=40)
    table.add_column("Product ID", style="green")
    table.add_column("Status", justify="center")
    table.add_column("Error", style="red", overflow="fold", max_width=30)

    for result in results:
        status = "✅" if result.success else "❌"
        error = result.error or "-"

        table.add_row(
            result.original_url,
            result.product_id or "-",
            status,
            error
        )

    console.print(table)

    # Print summary
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful

    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  [green]✅ Successful: {successful}[/green]")
    console.print(f"  [red]❌ Failed: {failed}[/red]")


async def resolve_single_link(url: str, config: LinkResolverConfig) -> None:
    """
    Resolve a single link and print result.

    Args:
        url: TikTok product link
        config: Resolver configuration
    """
    async with LinkResolver(config) as resolver:
        result = await resolver.resolve_link(url)

    print_results_table([result])

    if result.success:
        console.print(f"\n[bold green]Product ID: {result.product_id}[/bold green]")
        sys.exit(0)
    else:
        console.print(f"\n[bold red]Failed: {result.error}[/bold red]")
        sys.exit(1)


async def resolve_multiple_links(
    urls: List[str],
    config: LinkResolverConfig,
    output_file: str = None,
    output_format: str = 'csv'
) -> None:
    """
    Resolve multiple links and optionally save results.

    Args:
        urls: List of TikTok product links
        config: Resolver configuration
        output_file: Optional output file path
        output_format: Output format ('csv' or 'json')
    """
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(
            f"[cyan]Resolving {len(urls)} links...",
            total=None
        )

        async with LinkResolver(config) as resolver:
            results = await resolver.resolve_multiple_links(urls)

        progress.update(task, completed=True)

    # Print results
    console.print()
    print_results_table(results)

    # Save results if output file specified
    if output_file:
        console.print()
        if output_format == 'csv':
            save_results_to_csv(results, output_file)
            console.print(f"[green]✅ Product IDs appended to: {output_file}[/green]")
        elif output_format == 'json':
            save_results_to_json(results, output_file)
            console.print(f"[green]✅ Detailed results saved to: {output_file}[/green]")

    # Exit with appropriate code
    failed_count = sum(1 for r in results if not r.success)
    sys.exit(0 if failed_count == 0 else 1)


def setup_logging(log_level: str) -> None:
    """Setup logging configuration."""
    logger.remove()  # Remove default handler

    # Console logging (INFO and above)
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | {message}",
        level=log_level,
        colorize=True
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='TikTok Product Link Resolver - Extract product IDs from TikTok links',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--url',
        type=str,
        help='Single TikTok product link to resolve'
    )
    input_group.add_argument(
        '--links-file',
        type=str,
        help='Text file with TikTok links (one per line)'
    )

    # Output options
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (CSV or JSON based on --format)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'json'],
        default='csv',
        help='Output format (default: csv)'
    )

    # Browser options
    parser.add_argument(
        '--headed',
        action='store_true',
        help='Run browser in headed mode (visible)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=15000,
        help='Timeout in milliseconds (default: 15000)'
    )

    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Create configuration
    config = LinkResolverConfig(
        headless=not args.headed,
        timeout=args.timeout,
        log_level=args.log_level
    )

    # Print banner
    console.print("\n[bold cyan]TikTok Product Link Resolver[/bold cyan]")
    console.print("[dim]Extracting product IDs from TikTok links...[/dim]\n")

    try:
        if args.url:
            # Single URL mode
            asyncio.run(resolve_single_link(args.url, config))

        elif args.links_file:
            # Multiple URLs mode
            urls = load_links_from_file(args.links_file)

            if not urls:
                console.print("[red]No URLs found in file[/red]")
                sys.exit(1)

            console.print(f"[cyan]Processing {len(urls)} links...[/cyan]\n")

            asyncio.run(
                resolve_multiple_links(
                    urls,
                    config,
                    output_file=args.output,
                    output_format=args.format
                )
            )

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        logger.exception("Unexpected error")
        sys.exit(1)


if __name__ == '__main__':
    main()
