#!/usr/bin/env python3
"""
Quick test to check if tabcut.com requires authentication.
"""

import asyncio
from playwright.async_api import async_playwright
from loguru import logger

async def test_without_login():
    """Test accessing product page without authentication."""

    product_id = "1729630936525936882"
    url = f"https://www.tabcut.com/zh-CN/ranking/goods/detail?id={product_id}&region=DE"

    logger.info(f"Testing access to: {url}")
    logger.info("Attempting to access WITHOUT authentication...")

    async with async_playwright() as p:
        # Launch browser in headed mode so we can see what happens
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        try:
            # Navigate directly to product page
            logger.info("Navigating to product page...")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait a bit for page to load
            await asyncio.sleep(5)

            # Check current URL (might redirect to login)
            current_url = page.url
            logger.info(f"Current URL: {current_url}")

            if '/login' in current_url.lower():
                logger.error("❌ REDIRECTED TO LOGIN PAGE - Authentication is required!")
                return False

            # Try to extract product name as a test
            product_name_selectors = [
                'h1',
                '[class*="product"][class*="name"]',
                '[class*="goods"][class*="name"]',
            ]

            product_name = None
            for selector in product_name_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        product_name = await element.text_content()
                        if product_name:
                            product_name = product_name.strip()
                            break
                except:
                    continue

            if product_name:
                logger.success(f"✅ SUCCESS! Found product name: {product_name}")
                logger.success("No authentication required - we can scrape directly!")
                return True
            else:
                logger.warning("⚠️  Could not find product name")
                logger.warning("Page might require login or selectors need adjustment")

                # Take a screenshot for debugging
                await page.screenshot(path="test_no_auth_screenshot.png")
                logger.info("Screenshot saved to: test_no_auth_screenshot.png")

                # Get page content
                content = await page.content()
                logger.info(f"Page content length: {len(content)} characters")

                # Check for common login indicators
                if any(word in content.lower() for word in ['login', '登录', 'sign in', 'authentication']):
                    logger.error("❌ Page contains login indicators - authentication likely required")
                    return False
                else:
                    logger.info("No obvious login indicators found")
                    return None  # Unclear

        except Exception as e:
            logger.error(f"Error during test: {e}")
            return False

        finally:
            # Keep browser open for 10 seconds so user can see the page
            logger.info("Keeping browser open for 10 seconds for inspection...")
            await asyncio.sleep(10)
            await browser.close()

if __name__ == '__main__':
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True
    )

    result = asyncio.run(test_without_login())

    print("\n" + "="*60)
    if result is True:
        print("✅ RESULT: No authentication needed!")
        print("We can proceed without setting up credentials.")
    elif result is False:
        print("❌ RESULT: Authentication IS required!")
        print("Please set up your credentials in scripts/config/.env")
    else:
        print("⚠️  RESULT: Unclear - please check the browser window and screenshot")
    print("="*60)
