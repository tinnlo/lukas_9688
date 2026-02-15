#!/usr/bin/env python3
"""
Debug script to inspect video table structure on tabcut.com
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from playwright.async_api import async_playwright
from tabcut_scraper.auth import AuthHandler
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def inspect_video_table(product_id: str):
    """Inspect the video table structure to understand how to extract video IDs."""

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )

        page = await context.new_page()

        try:
            # Login
            auth_handler = AuthHandler()

            # Navigate to workbench first
            await page.goto(
                "https://www.tabcut.com/zh-CN/workbench", wait_until="domcontentloaded"
            )
            await asyncio.sleep(2)

            # Navigate to product page
            url = f"https://www.tabcut.com/zh-CN/ranking/goods/detail?id={product_id}&region=DE"
            logger.info(f"Navigating to: {url}")
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # Check for login modal
            if "loginType=signIn" in page.url:
                logger.info("Login required...")
                if await auth_handler.handle_login_modal(page):
                    logger.info("Logged in successfully")
                    await asyncio.sleep(2)

            # Click 关联视频 tab
            logger.info("Clicking 关联视频 tab...")
            await page.click('text="关联视频"')
            await asyncio.sleep(3)

            # Inspect table structure
            logger.info("\n" + "=" * 80)
            logger.info("INSPECTING TABLE STRUCTURE")
            logger.info("=" * 80)

            table_info = await page.evaluate("""() => {
                const allRows = Array.from(document.querySelectorAll('tr'));
                
                return allRows.slice(0, 7).map((row, idx) => {
                    const cells = Array.from(row.querySelectorAll('td, th'));
                    const links = Array.from(row.querySelectorAll('a'));
                    const buttons = Array.from(row.querySelectorAll('button'));
                    
                    return {
                        rowIndex: idx,
                        cellCount: cells.length,
                        cellTexts: cells.map(c => c.textContent.trim().substring(0, 50)),
                        linkCount: links.length,
                        linkHrefs: links.map(l => l.href || 'no-href').slice(0, 3),
                        buttonCount: buttons.length,
                        buttonTexts: buttons.map(b => b.textContent.trim()).slice(0, 3),
                        innerHTML: row.innerHTML.substring(0, 300)
                    };
                });
            }""")

            for row in table_info:
                print(f"\n--- Row {row['rowIndex']} ---")
                print(f"Cells: {row['cellCount']}")
                print(f"Cell texts: {row['cellTexts']}")
                print(f"Links ({row['linkCount']}): {row['linkHrefs']}")
                print(f"Buttons ({row['buttonCount']}): {row['buttonTexts']}")
                print(f"HTML sample: {row['innerHTML'][:200]}...")

            logger.info("\n" + "=" * 80)
            logger.info(
                "Browser will stay open for 60 seconds for manual inspection..."
            )
            logger.info("=" * 80)
            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
        finally:
            await browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_video_table.py <product_id>")
        sys.exit(1)

    product_id = sys.argv[1]
    asyncio.run(inspect_video_table(product_id))
