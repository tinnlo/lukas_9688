"""Data models for link resolver."""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class LinkResolverConfig:
    """Configuration for link resolver."""

    headless: bool = True
    timeout: int = 15000  # Shorter timeout since we only need redirects
    user_agent: str = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    log_level: str = 'INFO'


@dataclass
class ResolvedProduct:
    """Resolved product information."""

    original_url: str
    product_id: str
    final_url: str
    redirect_chain: List[str]
    success: bool
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'original_url': self.original_url,
            'product_id': self.product_id,
            'final_url': self.final_url,
            'redirect_chain': self.redirect_chain,
            'success': self.success,
            'error': self.error
        }
