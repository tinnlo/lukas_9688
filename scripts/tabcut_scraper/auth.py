"""Authentication handler for tabcut.com."""

import os
from typing import Optional
from playwright.async_api import Page, Browser, BrowserContext
from loguru import logger
from .utils import retry_async


class AuthHandler:
    """Manages authentication for tabcut.com."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize authentication handler.

        Args:
            username: Tabcut username (from .env if not provided)
            password: Tabcut password (from .env if not provided)
        """
        self.username = username or os.getenv("TABCUT_USERNAME")
        self.password = password or os.getenv("TABCUT_PASSWORD")

        if not self.username or not self.password:
            raise ValueError(
                "TABCUT_USERNAME and TABCUT_PASSWORD must be set in .env file or provided as arguments"
            )

    @retry_async(max_attempts=3, delay=2.0)
    async def login(self, page: Page) -> bool:
        """
        Perform login on tabcut.com.

        Args:
            page: Playwright page object

        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("Navigating to tabcut.com login page...")
            await page.goto("https://www.tabcut.com/zh-CN/", wait_until="domcontentloaded")

            # Wait a bit for page to load
            await page.wait_for_timeout(2000)

            # Click on "密码登录" (Password Login) tab to switch to password login mode
            logger.info("Switching to password login mode...")
            password_login_tab_selectors = [
                'text="密码登录"',
                ':text("密码登录")',
                'button:has-text("密码登录")',
                'div:has-text("密码登录")',
            ]

            tab_clicked = False
            for selector in password_login_tab_selectors:
                try:
                    tab = await page.query_selector(selector)
                    if tab:
                        await tab.click()
                        tab_clicked = True
                        logger.info("Clicked 密码登录 tab")
                        await page.wait_for_timeout(1000)
                        break
                except Exception as e:
                    logger.debug(f"Tab selector {selector} failed: {e}")
                    continue

            if not tab_clicked:
                logger.warning("Could not find 密码登录 tab, may already be on password login")

            logger.info("Filling in credentials...")

            # Find phone number field (手机号)
            phone_selectors = [
                'input[placeholder*="手机号"]',
                'input[placeholder*="手机"]',
                'input[type="tel"]',
                'input[type="text"]',
            ]

            username_filled = False
            for selector in phone_selectors:
                try:
                    username_input = await page.query_selector(selector)
                    if username_input:
                        await username_input.fill(self.username)
                        username_filled = True
                        logger.debug(f"Filled phone number using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            if not username_filled:
                raise Exception("Could not find phone number input field (手机号)")

            # Find password field (密码)
            password_selectors = [
                'input[placeholder*="密码"]',
                'input[type="password"]',
                'input[placeholder*="请输入密码"]',
            ]

            password_filled = False
            for selector in password_selectors:
                try:
                    password_input = await page.query_selector(selector)
                    if password_input:
                        await password_input.fill(self.password)
                        password_filled = True
                        logger.debug(f"Filled password using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            if not password_filled:
                raise Exception("Could not find password input field (密码)")

            # Click 登录 (Login) button
            login_button_selectors = [
                'button:has-text("登录")',
                'text="登录"',
                'button[type="submit"]',
                '.login-button',
                'button:has-text("Login")',
            ]

            button_clicked = False
            for selector in login_button_selectors:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        await button.click()
                        button_clicked = True
                        logger.debug(f"Clicked 登录 button using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            if not button_clicked:
                raise Exception("Could not find 登录 (login) button")

            # Wait for redirect or login completion
            logger.info("Waiting for login to complete...")
            await page.wait_for_timeout(3000)  # Wait for redirect

            # Check if login was successful by looking for user profile or dashboard elements
            is_logged_in = await self.is_authenticated(page)

            if is_logged_in:
                logger.success("Login successful!")
                return True
            else:
                # Check for error messages
                error_selectors = [
                    '.error-message',
                    '.login-error',
                    '[class*="error"]',
                    'text=/错误|失败|Invalid/',
                ]

                error_msg = "Unknown error"
                for selector in error_selectors:
                    try:
                        error_elem = await page.query_selector(selector)
                        if error_elem:
                            error_msg = await error_elem.inner_text()
                            break
                    except:
                        continue

                logger.error(f"Login failed: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            raise

    async def is_authenticated(self, page: Page) -> bool:
        """
        Check if currently authenticated on tabcut.com.

        Args:
            page: Playwright page object

        Returns:
            True if authenticated, False otherwise
        """
        try:
            # Check for common authenticated elements
            auth_indicators = [
                'button:has-text("退出")',
                'button:has-text("登出")',
                'button:has-text("Logout")',
                '[class*="user-profile"]',
                '[class*="avatar"]',
                'text=/我的|个人中心/',
            ]

            for selector in auth_indicators:
                try:
                    element = await page.query_selector(selector, timeout=2000)
                    if element:
                        logger.debug(f"Found authentication indicator: {selector}")
                        return True
                except:
                    continue

            # Check current URL (should not be on login page)
            current_url = page.url
            if '/login' not in current_url.lower():
                logger.debug(f"Not on login page, assuming authenticated: {current_url}")
                return True

            return False

        except Exception as e:
            logger.debug(f"Auth check error: {e}")
            return False

    async def ensure_authenticated(self, page: Page) -> bool:
        """
        Ensure the page is authenticated, login if needed.

        Args:
            page: Playwright page object

        Returns:
            True if authenticated, False if authentication failed
        """
        if await self.is_authenticated(page):
            logger.info("Already authenticated")
            return True

        logger.info("Not authenticated, logging in...")
        return await self.login(page)

    async def handle_login_modal(self, page: Page) -> bool:
        """
        Handle the login modal that appears when trying to access restricted pages.

        Args:
            page: Playwright page object

        Returns:
            True if login successful, False otherwise
        """
        try:
            # Wait for modal to appear
            await page.wait_for_timeout(2000)

            # Click on "密码登录" (Password Login) tab
            logger.info("Looking for '密码登录' tab in modal...")
            password_tab_selectors = [
                'text="密码登录"',
                ':text("密码登录")',
                'button:has-text("密码登录")',
                'div:has-text("密码登录")',
            ]

            tab_clicked = False
            for selector in password_tab_selectors:
                try:
                    tab = await page.query_selector(selector)
                    if tab:
                        logger.info(f"Found '密码登录' tab")
                        await tab.click()
                        tab_clicked = True
                        await page.wait_for_timeout(1000)
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")

            if not tab_clicked:
                logger.warning("Could not find '密码登录' tab")
                return False

            logger.info("Filling in credentials in modal...")

            # Fill phone number
            phone_input = await page.query_selector('input[placeholder*="手机"]')
            if phone_input:
                await phone_input.fill(self.username)
                logger.debug("Filled phone number")
            else:
                logger.error("Could not find phone number input")
                return False

            # Fill password
            pwd_input = await page.query_selector('input[type="password"]')
            if pwd_input:
                await pwd_input.fill(self.password)
                logger.debug("Filled password")
            else:
                logger.error("Could not find password input")
                return False

            # Click login button
            login_btn = await page.query_selector('button:has-text("登录")')
            if login_btn:
                await login_btn.click()
                logger.info("Clicked login button")
                await page.wait_for_timeout(5000)  # Wait for login to complete
                return True
            else:
                logger.error("Could not find login button")
                return False

        except Exception as e:
            logger.error(f"Error handling login modal: {e}")
            return False

    async def save_session(self, context: BrowserContext, session_file: str = "config/session.json") -> None:
        """
        Save browser session cookies for reuse.

        Args:
            context: Playwright browser context
            session_file: Path to save session data
        """
        try:
            import json
            from pathlib import Path

            session_path = Path(session_file)
            session_path.parent.mkdir(parents=True, exist_ok=True)

            # Save cookies
            cookies = await context.cookies()
            storage_state = await context.storage_state()

            with open(session_path, 'w') as f:
                json.dump(storage_state, f)

            logger.info(f"Session saved to {session_file}")

        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    async def load_session(self, browser: Browser, session_file: str = "config/session.json") -> Optional[BrowserContext]:
        """
        Load saved browser session.

        Args:
            browser: Playwright browser instance
            session_file: Path to session data file

        Returns:
            BrowserContext with loaded session or None if failed
        """
        try:
            import json
            from pathlib import Path

            session_path = Path(session_file)
            if not session_path.exists():
                logger.debug(f"No saved session found at {session_file}")
                return None

            with open(session_path, 'r') as f:
                storage_state = json.load(f)

            context = await browser.new_context(storage_state=storage_state)
            logger.info(f"Session loaded from {session_file}")
            return context

        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return None
