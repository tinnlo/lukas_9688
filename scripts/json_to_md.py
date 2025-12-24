#!/usr/bin/env python3
"""
Convert tabcut_data.json files to markdown format for easier reading.
"""

import json
import os
from pathlib import Path
from datetime import datetime


def format_number(value):
    """Format a number value for display."""
    if value is None or value == "" or value == "-":
        return "N/A"
    return str(value)


def parse_title(title):
    """Extract clean title from AD title."""
    if not title or title == "AD无标题":
        return "No Title"

    # Remove AD prefix
    if title.startswith("AD"):
        title = title[2:].strip()

    # Extract discovery/update time info for reference but keep main title clean
    if "发现时间：" in title:
        # Split and keep the main title part
        parts = title.split("发现时间：")
        main_title = parts[0].strip()
        # Clean up hashtags at the end for the main title
        if "#" in main_title:
            # Keep hashtags as they're useful context
            pass
        return main_title

    return title.strip()


def extract_hashtags(title):
    """Extract hashtags from title."""
    if not title:
        return []

    # Find all hashtags
    import re
    hashtags = re.findall(r'#(\w+)', title)
    return hashtags


def convert_to_markdown(json_path, output_path=None):
    """Convert a tabcut_data.json file to markdown."""

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    product_id = data.get('product_id', 'Unknown')
    scraped_at = data.get('scraped_at', 'Unknown')

    # Parse scraped_at for readable date
    try:
        scraped_date = datetime.fromisoformat(scraped_at).strftime('%Y-%m-%d %H:%M')
    except:
        scraped_date = scraped_at

    product_info = data.get('product_info', {})
    sales_data = data.get('sales_data', {})
    video_analysis = data.get('video_analysis', {})
    top_videos = data.get('top_videos', [])

    # Build markdown content
    md_lines = []

    # Header
    product_name = product_info.get('product_name', 'Unknown Product')
    md_lines.append(f"# {product_name}\n")
    md_lines.append(f"**Product ID:** `{product_id}`  \n")
    md_lines.append(f"**Scraped:** {scraped_date}  \n")
    md_lines.append(f"**Shop:** {product_info.get('shop_owner', 'Unknown')}  \n")
    md_lines.append(f"**Rating:** {format_number(product_info.get('product_rating'))}  \n")
    md_lines.append(f"**Category:** {format_number(product_info.get('category'))}  \n")

    md_lines.append("\n---\n")

    # Sales Data
    md_lines.append("## Sales Data | 销售数据\n")
    md_lines.append(f"| Metric | Metric (中文) | Value |")
    md_lines.append(f"|:-------|:-------------|------|")
    md_lines.append(f"| Total Sales | 总销量 | {format_number(product_info.get('total_sales'))} |")
    md_lines.append(f"| Total Revenue | 总收入 | {format_number(product_info.get('total_sales_revenue'))} |")
    md_lines.append(f"| 7-Day Sales | 7天销量 | {format_number(sales_data.get('sales_count'))} |")
    md_lines.append(f"| 7-Day Revenue | 7天收入 | {format_number(sales_data.get('sales_revenue'))} |")
    md_lines.append(f"| Conversion Rate | 转化率 | {format_number(sales_data.get('conversion_rate'))} |")
    md_lines.append(f"| Click-Through Rate | 点击率 | {format_number(sales_data.get('click_through_rate'))} |")

    md_lines.append("\n---\n")

    # Video Analysis
    md_lines.append("## Video Analysis | 视频分析\n")
    md_lines.append(f"| Metric | Metric (中文) | Value |")
    md_lines.append(f"|:-------|:-------------|------|")
    md_lines.append(f"| Affiliate Videos | 带货视频数 | {format_number(video_analysis.get('带货视频数'))} |")
    md_lines.append(f"| Affiliate Creators | 带货视频达人数 | {format_number(video_analysis.get('带货视频达人数'))} |")
    md_lines.append(f"| Video Sales | 带货视频销量 | {format_number(video_analysis.get('带货视频销量'))} |")
    md_lines.append(f"| Video Revenue | 带货视频销售额 | {format_number(video_analysis.get('带货视频销售额'))} |")
    md_lines.append(f"| Ad Revenue | 广告成交金额 | {format_number(video_analysis.get('广告成交金额'))} |")
    md_lines.append(f"| Ad Revenue Ratio | 广告成交占比 | {format_number(video_analysis.get('广告成交占比'))} |")

    # Top Videos
    if top_videos:
        md_lines.append("\n---\n")
        md_lines.append("## Top Videos | 热门视频\n")

        for video in top_videos:
            rank = video.get('rank', '?')
            title = parse_title(video.get('title', ''))
            hashtags = extract_hashtags(video.get('title', ''))
            creator = video.get('creator_username', 'unknown')
            followers = video.get('creator_followers', 'N/A')
            publish_date = video.get('publish_date', 'Unknown')
            sales = format_number(video.get('estimated_sales'))
            revenue = format_number(video.get('estimated_revenue'))
            views = video.get('total_views', 'N/A')
            local_path = video.get('local_path', '')
            video_url = video.get('video_url', '')

            md_lines.append(f"### Video {rank}: {title}\n")

            if hashtags:
                md_lines.append(f"**Tags:** {' '.join(['#' + t for t in hashtags])}  \n")

            md_lines.append(f"| Field | Field (中文) | Value |")
            md_lines.append(f"|:-----|:-----------|------|")
            md_lines.append(f"| Creator | 创作者 | @{creator} |")
            md_lines.append(f"| Followers | 粉丝数 | {followers} |")
            md_lines.append(f"| Publish Date | 发布时间 | {publish_date} |")
            md_lines.append(f"| Estimated Sales | 预估销量 | {sales} |")
            md_lines.append(f"| Estimated Revenue | 预估收入 | {revenue} |")
            md_lines.append(f"| Total Views | 总观看量 | {views} |")

            if local_path:
                md_lines.append(f"| Local File | 本地文件 | `{local_path}` |")

            md_lines.append(f"\n[View on TikTok]({video_url})\n")
            md_lines.append("\n")

    # Write to file
    if output_path is None:
        output_path = json_path.parent / f"{json_path.stem}.md"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))

    return output_path


def main():
    """Convert all tabcut_data.json files in product_list directory."""

    # Find all tabcut_data.json files
    base_dir = Path("/Users/lxt/Movies/TikTok/WZ/lukas_9688/product_list")
    json_files = list(base_dir.glob("*/tabcut_data.json"))

    print(f"Found {len(json_files)} tabcut_data.json files\n")

    for json_path in sorted(json_files):
        try:
            output_path = convert_to_markdown(json_path)
            print(f"✓ Converted: {json_path.parent.name}/tabcut_data.json -> {output_path.name}")
        except Exception as e:
            print(f"✗ Failed: {json_path.parent.name}/tabcut_data.json - {e}")

    print(f"\nDone! Converted {len(json_files)} files.")


if __name__ == "__main__":
    main()
