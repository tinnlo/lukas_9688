#!/usr/bin/env python3
"""
Batch convert PNG images to JPG with compression.
Reduces file size while maintaining acceptable quality for web use.

Usage:
    python convert_png_to_jpg.py <input_directory>

Features:
- Converts PNG to JPG format
- Compresses images with configurable quality (default: 85%)
- Creates backup of original PNGs
- Removes metadata to reduce size
- Reports size reduction statistics
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image
except ImportError:
    print("Error: PIL/Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


def convert_png_to_jpg(input_dir: str, quality: int = 85, backup: bool = True):
    """
    Convert all PNG images in a directory to JPG format with compression.

    Args:
        input_dir: Directory containing PNG files
        quality: JPG quality (1-100, default 85)
        backup: Whether to backup original PNGs (default True)
    """
    input_path = Path(input_dir).resolve()

    if not input_path.exists():
        print(f"Error: Directory not found: {input_path}")
        return

    if not input_path.is_dir():
        print(f"Error: Not a directory: {input_path}")
        return

    # Find all PNG files
    png_files = list(input_path.glob("*.png")) + list(input_path.glob("*.PNG"))

    if not png_files:
        print(f"No PNG files found in {input_path}")
        return

    print(f"Found {len(png_files)} PNG file(s) in {input_path}")
    print(f"Output quality: {quality}%")
    print(f"Backup originals: {backup}")
    print("-" * 50)

    # Create backup directory if needed
    if backup:
        backup_dir = input_path / f"png_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)
        print(f"Backup directory: {backup_dir}")

    # Statistics
    total_original_size = 0
    total_converted_size = 0
    converted_count = 0
    skipped_count = 0

    for png_file in png_files:
        try:
            # Get original file size
            original_size = png_file.stat().st_size
            total_original_size += original_size

            # Open image
            with Image.open(png_file) as img:
                # Convert to RGB (JPG doesn't support alpha channel)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Create output filename
                jpg_file = png_file.with_suffix('.jpg')

                # Save as JPG with compression
                img.save(jpg_file, 'JPEG', quality=quality, optimize=True)

            # Get converted file size
            converted_size = jpg_file.stat().st_size
            total_converted_size += converted_size
            converted_count += 1

            # Calculate reduction
            reduction_pct = (1 - converted_size / original_size) * 100

            # Print result
            original_kb = original_size / 1024
            converted_kb = converted_size / 1024
            print(f"✓ {png_file.name}")
            print(f"  {original_kb:.1f} KB → {converted_kb:.1f} KB ({reduction_pct:.1f}% reduction)")

            # Backup original PNG
            if backup:
                shutil.copy2(png_file, backup_dir / png_file.name)

            # Remove original PNG
            png_file.unlink()

        except Exception as e:
            print(f"✗ Error converting {png_file.name}: {e}")
            skipped_count += 1

    # Print summary
    print("-" * 50)
    print("SUMMARY:")
    print(f"Converted: {converted_count} file(s)")
    print(f"Skipped: {skipped_count} file(s)")

    if converted_count > 0:
        total_original_mb = total_original_size / (1024 * 1024)
        total_converted_mb = total_converted_size / (1024 * 1024)
        total_reduction = (1 - total_converted_size / total_original_size) * 100

        print(f"Total size: {total_original_mb:.2f} MB → {total_converted_mb:.2f} MB")
        print(f"Total reduction: {total_reduction:.1f}%")

        if backup:
            backup_size = sum(f.stat().st_size for f in backup_dir.glob('*')) / (1024 * 1024)
            print(f"Backup size: {backup_size:.2f} MB")


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_png_to_jpg.py <directory> [quality] [no-backup]")
        print("")
        print("Arguments:")
        print("  directory  - Path to directory containing PNG files")
        print("  quality    - JPG quality 1-100 (default: 85)")
        print("  no-backup  - Skip backing up original PNGs (optional)")
        print("")
        print("Examples:")
        print("  python convert_png_to_jpg.py ./product_images")
        print("  python convert_png_to_jpg.py ./product_images 90")
        print("  python convert_png_to_jpg.py ./product_images 85 no-backup")
        sys.exit(1)

    input_dir = sys.argv[1]
    quality = 85
    backup = True

    if len(sys.argv) >= 3:
        try:
            quality = int(sys.argv[2])
            if not 1 <= quality <= 100:
                print("Error: Quality must be between 1 and 100")
                sys.exit(1)
        except ValueError:
            print("Error: Quality must be a number")
            sys.exit(1)

    if len(sys.argv) >= 4 and sys.argv[3] == "no-backup":
        backup = False

    convert_png_to_jpg(input_dir, quality, backup)


if __name__ == "__main__":
    main()
