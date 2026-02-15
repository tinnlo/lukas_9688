#!/usr/bin/env python3
"""
Test script to analyze TikTok product link resolution.
This will help us understand how to extract product IDs from vm.tiktok.com links.
"""

import asyncio
from playwright.async_api import async_playwright


async def test_link_with_mobile_ua(url: str):
    """Test accessing TikTok link with mobile user agent."""

    print(f"\n{'='*60}")
    print(f"Testing URL: {url}")
    print(f"{'='*60}\n")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)

        # Create context with mobile user agent
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            viewport={'width': 390, 'height': 844},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            locale='en-US'
        )

        page = await context.new_page()

        # Track redirects
        redirects = []

        def handle_request(request):
            if request.is_navigation_request():
                redirects.append(request.url)
                print(f"[Navigation] {request.url}")

        page.on('request', handle_request)

        try:
            # Navigate to the URL
            response = await page.goto(url, wait_until='networkidle', timeout=30000)

            print(f"\n{'='*60}")
            print("RESULTS")
            print(f"{'='*60}\n")
            print(f"Final URL: {page.url}")
            print(f"Status: {response.status if response else 'N/A'}")
            print(f"\nRedirect chain:")
            for i, redirect_url in enumerate(redirects, 1):
                print(f"  {i}. {redirect_url}")

            # Try to extract product ID from URL
            final_url = page.url
            if 'product_id=' in final_url:
                import re
                match = re.search(r'product_id=(\d+)', final_url)
                if match:
                    product_id = match.group(1)
                    print(f"\n✅ Product ID found in URL: {product_id}")
            elif '/product/' in final_url:
                import re
                match = re.search(r'/product/(\d+)', final_url)
                if match:
                    product_id = match.group(1)
                    print(f"\n✅ Product ID found in URL path: {product_id}")
            else:
                print("\n❌ Product ID not found in URL")

            # Try to find product ID in page content
            print("\n" + "="*60)
            print("Searching for product ID in page content...")
            print("="*60)

            # Check for common patterns
            content = await page.content()
            import re

            # Pattern 1: Look for product_id in meta tags or data attributes
            patterns = [
                r'"product_id":"?(\d{19})"?',
                r'product_id=(\d{19})',
                r'/product/(\d{19})',
                r'productId":"?(\d{19})"?',
                r'item_id":"?(\d{19})"?',
            ]

            found_ids = set()
            for pattern in patterns:
                matches = re.findall(pattern, content)
                found_ids.update(matches)

            if found_ids:
                print(f"\n✅ Potential product IDs found in content:")
                for pid in found_ids:
                    print(f"   - {pid}")
            else:
                print("\n❌ No product IDs found in content")

            # Wait for user inspection
            print("\n" + "="*60)
            print("Browser will stay open for 10 seconds for inspection...")
            print("="*60)
            await asyncio.sleep(10)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


async def main():
    """Main entry point."""
    # Test the sample link
    test_url = "https://vm.tiktok.com/ZG9JyURsD9J92-xzLFK/"

    await test_link_with_mobile_ua(test_url)


if __name__ == '__main__':
    asyncio.run(main())
