#!/usr/bin/env python3
"""
Test script to verify tabcut.com date range behavior.

This tests whether "近7天" is accessible or requires premium access.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.async_api import async_playwright
from tabcut_scraper.auth import AuthHandler
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_date_range_access(product_id: str):
    """
    Test whether we can access 7-day vs 30-day date ranges.

    Args:
        product_id: TikTok product ID to test with
    """
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,  # Show browser for debugging
            args=["--disable-blink-features=AutomationControlled"],
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        )

        page = await context.new_page()

        try:
            # Navigate to product page
            url = f"https://www.tabcut.com/shop/product/{product_id}"
            logger.info(f"Navigating to: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for page to load
            await asyncio.sleep(3)

            # Check if we need to login
            auth_manager = AuthHandler()
            is_logged_in = await auth_manager.check_login_status(page)

            if not is_logged_in:
                logger.warning("⚠️  Not logged in! Attempting login...")
                success = await auth_manager.login(page)
                if not success:
                    logger.error("❌ Login failed")
                    return
                logger.info("✅ Login successful")

                # Navigate back to product page
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)
            else:
                logger.info("✅ Already logged in")

            # Try to click "商品分析" tab
            logger.info("Clicking 商品分析 tab...")
            tab_selectors = [
                'text="商品分析"',
                'button:has-text("商品分析")',
                'div:has-text("商品分析")',
            ]

            tab_clicked = False
            for selector in tab_selectors:
                try:
                    await page.wait_for_selector(
                        selector, timeout=2000, state="attached"
                    )
                    button = await page.query_selector(selector)
                    if button:
                        await button.click()
                        await asyncio.sleep(2)
                        tab_clicked = True
                        logger.info("✅ Clicked 商品分析 tab")
                        break
                except:
                    continue

            if not tab_clicked:
                logger.warning("⚠️  Could not find 商品分析 tab")

            # Test "近7天" button
            logger.info("\n" + "=" * 60)
            logger.info("TEST 1: Trying to click '近7天' (7-day range)")
            logger.info("=" * 60)

            seven_day_found = False
            seven_day_clickable = False

            range_selectors = [
                'text="近7天"',
                'button:has-text("近7天")',
                'span:has-text("近7天")',
            ]

            for selector in range_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        seven_day_found = True
                        logger.info(
                            f"✅ Found '近7天' button with selector: {selector}"
                        )

                        # Check if it's disabled or has premium lock
                        is_disabled = await element.get_attribute("disabled")
                        classes = await element.get_attribute("class") or ""

                        logger.info(f"   Disabled: {is_disabled}")
                        logger.info(f"   Classes: {classes}")

                        # Try to click
                        try:
                            await element.click()
                            await asyncio.sleep(2)
                            seven_day_clickable = True
                            logger.info("✅ Successfully clicked '近7天'")

                            # Take screenshot
                            await page.screenshot(path="test_7day_clicked.png")
                            logger.info("📸 Screenshot saved: test_7day_clicked.png")
                        except Exception as click_error:
                            logger.error(f"❌ Could not click '近7天': {click_error}")

                        break
                except:
                    continue

            if not seven_day_found:
                logger.warning("❌ '近7天' button NOT FOUND")

            # Test "近30天" button
            logger.info("\n" + "=" * 60)
            logger.info("TEST 2: Trying to click '近30天' (30-day range)")
            logger.info("=" * 60)

            await asyncio.sleep(1)

            thirty_day_found = False
            thirty_day_clickable = False

            range_selectors_30 = [
                'text="近30天"',
                'button:has-text("近30天")',
                'span:has-text("近30天")',
            ]

            for selector in range_selectors_30:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        thirty_day_found = True
                        logger.info(
                            f"✅ Found '近30天' button with selector: {selector}"
                        )

                        is_disabled = await element.get_attribute("disabled")
                        classes = await element.get_attribute("class") or ""

                        logger.info(f"   Disabled: {is_disabled}")
                        logger.info(f"   Classes: {classes}")

                        # Try to click
                        try:
                            await element.click()
                            await asyncio.sleep(2)
                            thirty_day_clickable = True
                            logger.info("✅ Successfully clicked '近30天'")

                            # Take screenshot
                            await page.screenshot(path="test_30day_clicked.png")
                            logger.info("📸 Screenshot saved: test_30day_clicked.png")
                        except Exception as click_error:
                            logger.error(f"❌ Could not click '近30天': {click_error}")

                        break
                except:
                    continue

            if not thirty_day_found:
                logger.warning("❌ '近30天' button NOT FOUND")

            # Final report
            logger.info("\n" + "=" * 60)
            logger.info("TEST SUMMARY")
            logger.info("=" * 60)
            logger.info(f"近7天 found: {seven_day_found}")
            logger.info(f"近7天 clickable: {seven_day_clickable}")
            logger.info(f"近30天 found: {thirty_day_found}")
            logger.info(f"近30天 clickable: {thirty_day_clickable}")

            if seven_day_clickable:
                logger.info("✅ RESULT: '近7天' is ACCESSIBLE (not premium locked)")
            elif seven_day_found and not seven_day_clickable:
                logger.info(
                    "⚠️  RESULT: '近7天' is FOUND but NOT CLICKABLE (likely premium)"
                )
                logger.info("💡 RECOMMENDATION: Use '近30天' as default")
            else:
                logger.info("❌ RESULT: '近7天' not found on page")

            # Wait before closing (for manual inspection)
            logger.info(
                "\nBrowser will stay open for 30 seconds for manual inspection..."
            )
            await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"Test failed: {e}", exc_info=True)
        finally:
            await browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_date_range.py <product_id>")
        print("Example: python test_date_range.py 1729592938206960369")
        sys.exit(1)

    product_id = sys.argv[1]
    asyncio.run(test_date_range_access(product_id))
