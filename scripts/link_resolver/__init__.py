"""
TikTok Product Link Resolver

This module resolves TikTok product links (vm.tiktok.com, direct shop links, etc.)
to extract the numeric product ID needed for the product scraper.
"""

from .resolver import LinkResolver
from .models import ResolvedProduct, LinkResolverConfig

__all__ = ['LinkResolver', 'ResolvedProduct', 'LinkResolverConfig']
__version__ = '1.0.0'
