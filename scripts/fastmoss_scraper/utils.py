"""Utility functions for the FastMoss scraper - independent implementation."""

import os
import re
from pathlib import Path
from typing import Optional
from loguru import logger
import asyncio
from functools import wraps


def setup_logging(log_dir: str = "logs", log_level: str = "INFO") -> None:
    """
    Configure logging to file and console.

    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Remove default logger
    logger.remove()

    # Add console logger with color
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # Add file logger for all logs
    logger.add(
        log_path / "fastmoss_scraper_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    )

    # Add separate error log
    logger.add(
        log_path / "fastmoss_errors_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    )


def retry_async(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator for async functions with exponential backoff retry.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise

                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator


def ensure_product_folder(product_id: str, base_dir: str = "../product_list") -> Path:
    """
    Create product folder structure if not exists.

    Args:
        product_id: TikTok shop product ID
        base_dir: Base directory for product folders

    Returns:
        Path to the product folder
    """
    base_path = Path(base_dir)
    product_path = base_path / product_id
    product_path.mkdir(parents=True, exist_ok=True)

    # Create ref_video subdirectory
    video_path = product_path / "ref_video"
    video_path.mkdir(exist_ok=True)

    logger.debug(f"Ensured product folder exists: {product_path}")
    return product_path


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize filename for safe file system usage.

    Args:
        filename: Original filename
        max_length: Maximum filename length

    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')

    # Truncate if too long
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext

    return filename


def format_number(value: str) -> Optional[int]:
    """
    Parse number format (including Euro/Chinese formats) to integer.

    Args:
        value: Number string (e.g., "€1175.6", "1.23万", "5187")

    Returns:
        Parsed integer or None
    """
    if not value:
        return None

    try:
        # Remove currency symbols and spaces
        value = re.sub(r'[€$¥\s]', '', value)

        # Handle Chinese units (万 = 10,000, 亿 = 100,000,000)
        if '万' in value:
            value = value.replace('万', '')
            multiplier = 10000
        elif '亿' in value:
            value = value.replace('亿', '')
            multiplier = 100000000
        else:
            multiplier = 1

        # Parse number
        number = float(value.replace(',', ''))
        return int(number * multiplier)
    except (ValueError, AttributeError):
        logger.warning(f"Failed to parse number: {value}")
        return None


def parse_duration(duration_str: str) -> Optional[int]:
    """
    Parse video duration string to seconds.

    Args:
        duration_str: Duration string (e.g., "00:00:31", "01:23")

    Returns:
        Duration in seconds or None
    """
    if not duration_str:
        return None

    try:
        parts = duration_str.split(':')
        if len(parts) == 3:  # HH:MM:SS
            h, m, s = map(int, parts)
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:  # MM:SS
            m, s = map(int, parts)
            return m * 60 + s
        else:
            return int(parts[0])
    except (ValueError, AttributeError):
        logger.warning(f"Failed to parse duration: {duration_str}")
        return None
