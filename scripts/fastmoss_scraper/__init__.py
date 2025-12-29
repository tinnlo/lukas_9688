"""FastMoss scraper package for TikTok Shop product data."""

from .scraper import FastMossScraper
from .models import ProductData, ScraperConfig

__all__ = ['FastMossScraper', 'ProductData', 'ScraperConfig']
