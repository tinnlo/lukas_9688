"""Data models for tabcut scraper."""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional
import json


@dataclass
class ProductInfo:
    """Product information from top section."""
    product_name: str
    shop_owner: str
    total_sales: Optional[int] = None
    total_sales_revenue: Optional[str] = None
    product_rating: Optional[float] = None
    category: Optional[str] = None


@dataclass
class SalesData:
    """Sales data from 商品分析 tab."""
    date_range: str  # '7day' or '30day'
    sales_count: Optional[int] = None  # 销量
    sales_revenue: Optional[str] = None  # 销售额
    related_videos: Optional[int] = None  # 关联视频
    related_creators: Optional[int] = None  # 关联达人
    conversion_rate: Optional[str] = None  # 转化率
    click_through_rate: Optional[str] = None  # 点击率


@dataclass
class VideoAnalysis:
    """Video analysis metrics from 关联视频 tab."""
    带货视频数: Optional[int] = None  # Number of sales videos
    带货视频达人数: Optional[int] = None  # Number of creators
    带货视频销量: Optional[int] = None  # Video sales count
    带货视频销售额: Optional[str] = None  # Video sales revenue
    广告成交金额: Optional[str] = None  # Ad transaction amount
    广告成交占比: Optional[str] = None  # Ad transaction ratio


@dataclass
class VideoData:
    """Individual video data."""
    rank: int
    title: str
    creator_username: str
    creator_followers: Optional[int] = None
    publish_date: Optional[str] = None
    estimated_sales: Optional[int] = None  # 预估销量
    estimated_revenue: Optional[str] = None  # 预估销售额
    total_views: Optional[int] = None  # 总播放量
    video_url: Optional[str] = None
    video_id: Optional[str] = None
    local_path: Optional[str] = None


@dataclass
class ProductData:
    """Complete product data structure."""
    product_id: str
    scraped_at: str
    product_info: ProductInfo
    sales_data: SalesData
    video_analysis: VideoAnalysis
    top_videos: List[VideoData] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, ensure_ascii: bool = False, indent: int = 2) -> str:
        """
        Convert to JSON string.

        Args:
            ensure_ascii: If True, escape non-ASCII characters
            indent: JSON indentation level

        Returns:
            JSON string
        """
        return json.dumps(
            self.to_dict(),
            ensure_ascii=ensure_ascii,
            indent=indent
        )

    @classmethod
    def from_dict(cls, data: dict) -> 'ProductData':
        """Create ProductData from dictionary."""
        product_info = ProductInfo(**data.get('product_info', {}))
        sales_data = SalesData(**data.get('sales_data', {}))
        video_analysis = VideoAnalysis(**data.get('video_analysis', {}))
        top_videos = [
            VideoData(**video) for video in data.get('top_videos', [])
        ]

        return cls(
            product_id=data['product_id'],
            scraped_at=data['scraped_at'],
            product_info=product_info,
            sales_data=sales_data,
            video_analysis=video_analysis,
            top_videos=top_videos
        )

    def save_to_file(self, file_path: str) -> None:
        """
        Save product data to JSON file.

        Args:
            file_path: Path to save JSON file
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, file_path: str) -> 'ProductData':
        """
        Load product data from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            ProductData instance
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class ScraperConfig:
    """Configuration for scraper."""
    headless: bool = True
    timeout: int = 30000
    max_retries: int = 3
    download_timeout: int = 300000
    output_base_dir: str = "../product_list"
    log_level: str = "INFO"
    random_delay_min: float = 2.0
    random_delay_max: float = 5.0
