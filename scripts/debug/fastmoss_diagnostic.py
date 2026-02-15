#!/usr/bin/env python3
"""
FastMoss DOM Structure Diagnostic Tool

Inspects the real DOM structure of FastMoss product pages to understand:
- Image element structure and CDN patterns
- Video table/list structure (table vs divs)
- Video detail page TikTok button structure

Outputs JSON report + screenshots to /tmp/fastmoss_diagnostic/
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from loguru import logger

# Product ID to diagnose
PRODUCT_ID = "1729755662202542792"
OUTPUT_DIR = Path("/tmp/fastmoss_diagnostic")


async def main():
    logger.info("Starting FastMoss diagnostic...")

    # Setup output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    diagnostic_report = {
        "product_id": PRODUCT_ID,
        "timestamp": datetime.now().isoformat(),
        "images": [],
        "video_section": {},
        "video_detail": {},
        "screenshots": [],
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Load saved session
        session_path = Path("scripts/config/.fastmoss_session.json")
        storage_state = None
        if session_path.exists():
            logger.info(f"Loading session from {session_path}")
            with open(session_path, "r") as f:
                storage_state = json.load(f)

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            locale="zh-CN",
            extra_http_headers={"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"},
            storage_state=storage_state,
        )

        page = await context.new_page()
        page.set_default_timeout(30000)

        # Navigate to product page
        product_url = f"https://www.fastmoss.com/zh/e-commerce/detail/{PRODUCT_ID}"
        logger.info(f"Navigating to {product_url}")
        await page.goto(product_url, wait_until="domcontentloaded")
        await asyncio.sleep(5)  # Let page fully load

        # Screenshot 1: Product page
        screenshot_path = OUTPUT_DIR / "product_page.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        diagnostic_report["screenshots"].append(str(screenshot_path))
        logger.success(f"Saved screenshot: {screenshot_path}")

        # === IMAGES DIAGNOSTIC ===
        logger.info("Analyzing images...")
        images_data = await page.evaluate("""() => {
            const images = [];
            const allImgs = document.querySelectorAll('img');
            
            allImgs.forEach((img, idx) => {
                const rect = img.getBoundingClientRect();
                
                // Get parent chain
                const parentChain = [];
                let current = img.parentElement;
                for (let i = 0; i < 5 && current; i++) {
                    parentChain.push({
                        tagName: current.tagName,
                        className: current.className,
                        id: current.id
                    });
                    current = current.parentElement;
                }
                
                images.push({
                    index: idx,
                    url: img.src,
                    alt: img.alt,
                    naturalWidth: img.naturalWidth,
                    naturalHeight: img.naturalHeight,
                    aspectRatio: img.naturalWidth / img.naturalHeight,
                    className: img.className,
                    rect: {
                        top: rect.top,
                        left: rect.left,
                        width: rect.width,
                        height: rect.height
                    },
                    parentChain: parentChain,
                    isCarousel: img.closest('[class*="swiper"]') !== null || 
                               img.closest('[class*="carousel"]') !== null ||
                               img.closest('[class*="slider"]') !== null
                });
            });
            
            return images;
        }""")

        diagnostic_report["images"] = images_data
        logger.success(f"Found {len(images_data)} images")

        # Analyze CDN patterns
        cdn_patterns = {}
        for img in images_data:
            url = img["url"]
            if not url.startswith("data:"):
                # Extract domain
                try:
                    domain = url.split("/")[2]
                    cdn_patterns[domain] = cdn_patterns.get(domain, 0) + 1
                except:
                    pass

        diagnostic_report["cdn_patterns"] = cdn_patterns
        logger.info(f"CDN patterns found: {cdn_patterns}")

        # === VIDEO SECTION DIAGNOSTIC ===
        logger.info("Analyzing video section...")
        video_section_data = await page.evaluate("""() => {
            const result = {
                hasTables: false,
                tableCount: 0,
                tables: [],
                videoLinks: []
            };
            
            // Check for tables
            const tables = document.querySelectorAll('table');
            result.tableCount = tables.length;
            result.hasTables = tables.length > 0;
            
            tables.forEach((table, idx) => {
                const tbody = table.querySelector('tbody');
                const thead = table.querySelector('thead');
                const rows = tbody ? tbody.querySelectorAll('tr') : [];
                
                const tableInfo = {
                    index: idx,
                    className: table.className,
                    id: table.id,
                    hasTheadTbody: thead !== null && tbody !== null,
                    rowCount: rows.length,
                    sampleRows: []
                };
                
                // Get first 2 rows
                for (let i = 0; i < Math.min(2, rows.length); i++) {
                    const row = rows[i];
                    const cells = row.querySelectorAll('td, th');
                    const cellData = [];
                    
                    cells.forEach(cell => {
                        cellData.push({
                            tagName: cell.tagName,
                            className: cell.className,
                            text: cell.textContent.trim().substring(0, 100),
                            hasLink: cell.querySelector('a') !== null,
                            linkHref: cell.querySelector('a')?.href || null
                        });
                    });
                    
                    tableInfo.sampleRows.push({
                        cellCount: cells.length,
                        cells: cellData
                    });
                }
                
                result.tables.push(tableInfo);
            });
            
            // Look for video links
            const videoLinks = document.querySelectorAll('a[href*="/video/"], a[href*="media-source"]');
            videoLinks.forEach(link => {
                result.videoLinks.push({
                    href: link.href,
                    text: link.textContent.trim().substring(0, 50),
                    className: link.className,
                    parentClassName: link.parentElement?.className
                });
            });
            
            return result;
        }""")

        diagnostic_report["video_section"] = video_section_data
        logger.success(
            f"Video section analysis: {video_section_data['tableCount']} tables, {len(video_section_data.get('videoLinks', []))} video links"
        )

        # === VIDEO DETAIL PAGE DIAGNOSTIC ===
        if (
            video_section_data.get("videoLinks")
            and len(video_section_data["videoLinks"]) > 0
        ):
            logger.info("Navigating to video detail page...")
            first_video_url = video_section_data["videoLinks"][0]["href"]

            await page.goto(first_video_url, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # Screenshot 2: Video detail page
            screenshot_path = OUTPUT_DIR / "video_detail_page.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            diagnostic_report["screenshots"].append(str(screenshot_path))
            logger.success(f"Saved screenshot: {screenshot_path}")

            # Analyze TikTok button
            video_detail_data = await page.evaluate("""() => {
                const result = {
                    tiktokButtons: [],
                    tiktokLinks: []
                };
                
                // Look for buttons/links with TikTok text
                const buttons = Array.from(document.querySelectorAll('a, button'));
                buttons.forEach(btn => {
                    const text = btn.textContent.trim();
                    if (text.includes('TikTok') || text.includes('进入TikTok')) {
                        result.tiktokButtons.push({
                            tagName: btn.tagName,
                            className: btn.className,
                            id: btn.id,
                            text: text,
                            href: btn.href || btn.getAttribute('href'),
                            onClick: btn.onclick ? 'has onclick' : null
                        });
                    }
                });
                
                // Look for any tiktok.com links
                const tiktokLinks = document.querySelectorAll('a[href*="tiktok.com"]');
                tiktokLinks.forEach(link => {
                    result.tiktokLinks.push({
                        href: link.href,
                        text: link.textContent.trim().substring(0, 50),
                        className: link.className
                    });
                });
                
                return result;
            }""")

            diagnostic_report["video_detail"] = video_detail_data
            logger.success(
                f"Video detail analysis: {len(video_detail_data['tiktokButtons'])} TikTok buttons, {len(video_detail_data['tiktokLinks'])} TikTok links"
            )

        await browser.close()

    # Save JSON report
    report_path = OUTPUT_DIR / "report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(diagnostic_report, f, indent=2, ensure_ascii=False)

    logger.success(f"Diagnostic report saved to {report_path}")

    # Print summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    print(f"\n📊 Images Found: {len(diagnostic_report['images'])}")
    print(f"\n🌐 CDN Patterns:")
    for domain, count in sorted(
        diagnostic_report.get("cdn_patterns", {}).items(), key=lambda x: -x[1]
    ):
        print(f"  - {domain}: {count} images")

    print(f"\n📹 Video Section:")
    print(f"  - Tables found: {video_section_data['tableCount']}")
    print(f"  - Video links found: {len(video_section_data.get('videoLinks', []))}")

    if diagnostic_report.get("video_detail"):
        print(f"\n🎬 Video Detail Page:")
        print(
            f"  - TikTok buttons: {len(diagnostic_report['video_detail'].get('tiktokButtons', []))}"
        )
        print(
            f"  - TikTok links: {len(diagnostic_report['video_detail'].get('tiktokLinks', []))}"
        )

    print(f"\n📸 Screenshots saved to: {OUTPUT_DIR}")
    print(f"📄 Full report: {report_path}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
