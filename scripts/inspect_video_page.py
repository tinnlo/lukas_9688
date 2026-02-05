#!/usr/bin/env python3
"""
Inspect the actual video table HTML to find where video IDs are located.
"""

import asyncio
from playwright.async_api import async_playwright
import json


async def inspect_video_table():
    """Inspect the real video table structure."""

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Keep browser open to see what we're doing
            args=["--disable-blink-features=AutomationControlled"],
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )

        page = await context.new_page()

        try:
            # Navigate directly to the product page with video tab
            url = "https://www.tabcut.com/zh-CN/ranking/goods/detail?id=1729476728478930974&region=DE&currentTab=video"
            print(f"Navigating to: {url}")
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(5)  # Wait for content to load

            # Close any popup ads (Topview, etc.)
            print("Checking for popup ads...")
            try:
                # Try to find and close modal/popup
                await page.evaluate("""() => {
                    // Close any modal overlays
                    const closeButtons = document.querySelectorAll('button[aria-label="Close"], .modal-close, .close-button, [class*="close"]');
                    closeButtons.forEach(btn => {
                        if (btn.offsetParent !== null) {  // Only visible buttons
                            btn.click();
                        }
                    });
                    
                    // Remove modal backdrops
                    const modals = document.querySelectorAll('.modal, [class*="modal"], [class*="popup"], [class*="dialog"]');
                    modals.forEach(modal => {
                        if (modal.offsetParent !== null) {
                            modal.style.display = 'none';
                        }
                    });
                }""")
                await asyncio.sleep(1)
                print("✓ Closed any popup ads")
            except Exception as e:
                print(f"No popups to close or error: {e}")

            # Check if we need to login
            current_url = page.url
            print(f"Current URL: {current_url}")

            if "loginType=signIn" in current_url:
                print("\n⚠️  Login required. Please login manually in the browser.")
                print("After logging in, the script will continue automatically.")

                # Wait for user to login manually
                await page.wait_for_url("**/ranking/goods/detail**", timeout=120000)
                print("✓ Login detected, continuing...")

                # Navigate again after login
                await page.goto(url, wait_until="domcontentloaded")
                await asyncio.sleep(3)

            print("\n" + "=" * 80)
            print("INSPECTING VIDEO TABLE STRUCTURE")
            print("=" * 80)

            # Extract detailed information about the table rows
            table_data = await page.evaluate("""() => {
                const allRows = Array.from(document.querySelectorAll('tr'));
                
                return allRows.slice(0, 7).map((row, idx) => {
                    const cells = Array.from(row.querySelectorAll('td, th'));
                    const links = Array.from(row.querySelectorAll('a'));
                    const buttons = Array.from(row.querySelectorAll('button'));
                    
                    // Try to find video ID in various places
                    let videoIdCandidates = [];
                    
                    // IMPORTANT: Look for "跳转至 TikTok" button specifically
                    const tiktokButtons = Array.from(row.querySelectorAll('button, a, span')).filter(el => 
                        el.textContent.includes('跳转') || el.textContent.includes('TikTok')
                    );
                    
                    tiktokButtons.forEach(btn => {
                        videoIdCandidates.push({
                            type: 'tiktok-button',
                            tagName: btn.tagName,
                            text: btn.textContent.trim(),
                            onclick: btn.getAttribute('onclick') || '',
                            href: btn.href || '',
                            className: btn.className,
                            outerHTML: btn.outerHTML.substring(0, 200)
                        });
                    });
                    
                    // Check links
                    links.forEach(link => {
                        const href = link.href || '';
                        const onclick = link.getAttribute('onclick') || '';
                        if (href.includes('video') || onclick.includes('video')) {
                            videoIdCandidates.push({
                                type: 'link',
                                href: href,
                                onclick: onclick,
                                text: link.textContent.trim().substring(0, 50)
                            });
                        }
                    });
                    
                    // Check buttons
                    buttons.forEach(btn => {
                        const onclick = btn.getAttribute('onclick') || '';
                        if (onclick) {
                            videoIdCandidates.push({
                                type: 'button',
                                onclick: onclick,
                                text: btn.textContent.trim()
                            });
                        }
                    });
                    
                    // Get row's data attributes
                    const dataAttrs = {};
                    Array.from(row.attributes).forEach(attr => {
                        if (attr.name.startsWith('data-')) {
                            dataAttrs[attr.name] = attr.value;
                        }
                    });
                    
                    return {
                        rowIndex: idx,
                        cellCount: cells.length,
                        cellTexts: cells.map(c => c.textContent.trim().substring(0, 60)),
                        linkCount: links.length,
                        buttonCount: buttons.length,
                        videoIdCandidates: videoIdCandidates,
                        dataAttributes: dataAttrs,
                        outerHTML: row.outerHTML.substring(0, 500)
                    };
                });
            }""")

            # Print the results nicely
            for row_info in table_data:
                print(f"\n{'=' * 80}")
                print(f"ROW {row_info['rowIndex']}")
                print(f"{'=' * 80}")
                print(f"Cells: {row_info['cellCount']}")
                print(f"Cell texts:")
                for i, text in enumerate(row_info["cellTexts"]):
                    print(f"  [{i}] {text}")

                print(
                    f"\nLinks: {row_info['linkCount']}, Buttons: {row_info['buttonCount']}"
                )

                if row_info["videoIdCandidates"]:
                    print(f"\nVideo ID Candidates:")
                    for candidate in row_info["videoIdCandidates"]:
                        print(f"  Type: {candidate['type']}")
                        print(f"  Text: {candidate.get('text', 'N/A')}")
                        if candidate.get("tagName"):
                            print(f"  Tag: {candidate['tagName']}")
                        if candidate.get("className"):
                            print(f"  Class: {candidate['className']}")
                        if candidate.get("href"):
                            print(f"  Href: {candidate['href']}")
                        if candidate.get("onclick"):
                            print(f"  OnClick: {candidate['onclick'][:150]}")
                        if candidate.get("outerHTML"):
                            print(f"  HTML: {candidate['outerHTML']}")
                        print()

                if row_info["dataAttributes"]:
                    print(f"\nData Attributes: {row_info['dataAttributes']}")

                print(f"\nHTML Preview:\n{row_info['outerHTML'][:300]}...")

            print("\n" + "=" * 80)
            print("Keeping browser open for 60 seconds for manual inspection...")
            print("=" * 80)
            await asyncio.sleep(60)

        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_video_table())
