"""Authentication handler for FastMoss.com."""

import os
import asyncio
from pathlib import Path
from playwright.async_api import Page, BrowserContext
from loguru import logger


class AuthHandler:
    """Handle FastMoss.com authentication."""

    def __init__(self):
        """Initialize auth handler."""
        self.phone = os.getenv('FASTMOSS_USERNAME')
        self.password = os.getenv('FASTMOSS_PASSWORD')
        self.session_file = Path(__file__).parent.parent / 'config' / '.fastmoss_session.json'
        self.is_authenticated = False

    async def ensure_authenticated(self, page: Page) -> bool:
        """
        Ensure user is authenticated on FastMoss.

        Args:
            page: Playwright page object

        Returns:
            True if authenticated, False otherwise
        """
        if self.is_authenticated:
            return True

        # Check if already logged in by looking for user-specific elements
        try:
            # Try to find logout button or user menu which would indicate logged-in state
            user_menu = await page.query_selector('[class*="user"], [class*="User"], [class*="avatar"]')
            if user_menu:
                logger.info("Already authenticated (found user menu)")
                self.is_authenticated = True
                return True
        except Exception:
            pass

        # Not logged in, perform login
        logger.info("Not authenticated, starting login process...")
        return await self.login(page)

    async def login(self, page: Page) -> bool:
        """
        Perform login to FastMoss via popup modal.

        Args:
            page: Playwright page object

        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("Opening FastMoss login popup...")

            # Go to homepage first
            await page.goto("https://www.fastmoss.com/zh", wait_until="domcontentloaded")
            await asyncio.sleep(2)

            # Find and click login button using getByText
            logger.info("Looking for '注册/登录' button...")
            login_trigger = page.get_by_text('注册/登录')

            if await login_trigger.count() > 0:
                logger.info("Found login button, clicking to open popup...")
                await login_trigger.first.click()
                await asyncio.sleep(3)
                logger.success("Login modal opened")
            else:
                logger.error("Could not find login button")
                await page.screenshot(path='fastmoss_no_login_button.png')
                return False

            # Click on "手机号登录/注册" tab to switch from WeChat to phone login
            logger.info("Switching to phone number login tab...")
            phone_tab = page.get_by_text('手机号登录/注册')

            if await phone_tab.count() > 0:
                logger.info("Clicking '手机号登录/注册' tab...")
                await phone_tab.first.click()
                await asyncio.sleep(2)
            else:
                logger.warning("Could not find phone number tab, might already be on it")

            # Click on "密码登录" (Password Login) to switch to password mode
            logger.info("Looking for '密码登录' link in modal...")
            password_login_link = page.get_by_text('密码登录')

            if await password_login_link.count() > 0:
                logger.info("Clicking '密码登录' to switch to password mode...")
                await password_login_link.first.click()
                await asyncio.sleep(1)
            else:
                logger.warning("Could not find '密码登录' link, assuming already in password mode")

            # Find phone number input (手机号码) - use more specific selectors for modal
            logger.info("Looking for login form inputs in modal...")

            # Try multiple selector strategies for phone input
            phone_input = await page.query_selector('input[placeholder*="手机号"]')
            if not phone_input:
                phone_input = await page.query_selector('input[placeholder*="手机"]')
            if not phone_input:
                # Try finding first text input in modal
                phone_input = await page.query_selector('.ant-modal input[type="text"], [class*="modal"] input[type="text"], [class*="Modal"] input[type="text"]')

            # Find password input
            pwd_input = await page.query_selector('input[type="password"]')

            if not phone_input or not pwd_input:
                logger.error(f"Could not find login inputs (phone: {phone_input is not None}, password: {pwd_input is not None})")
                # Take screenshot for debugging
                await page.screenshot(path='fastmoss_login_error.png')
                logger.error("Screenshot saved to fastmoss_login_error.png for debugging")
                return False

            logger.info(f"Logging in with phone: {self.phone}")

            # Fill phone number
            await phone_input.fill(self.phone)
            await asyncio.sleep(0.5)

            # Fill password
            await pwd_input.fill(self.password)
            await asyncio.sleep(0.5)

            # Find and click login button (注册/登录)
            login_button = page.get_by_role('button').filter(has_text='注册/登录')

            if await login_button.count() == 0:
                # Try alternative selector
                login_button = page.get_by_text('注册/登录').filter(has=page.locator('button'))

            if await login_button.count() > 0:
                logger.info("Clicking login button...")
                await login_button.first.click()
                await asyncio.sleep(5)

                # Check if login successful - modal should close
                # Look for user menu or avatar
                user_menu = await page.query_selector('[class*="user"], [class*="User"], [class*="avatar"]')
                if user_menu:
                    logger.success("✅ LOGIN SUCCESSFUL! User menu found")
                    self.is_authenticated = True
                    return True

                # Check if modal is still open (login failed)
                modal = await page.query_selector('.ant-modal')
                if not modal or not await modal.is_visible():
                    logger.success("✅ LOGIN SUCCESSFUL! Modal closed")
                    self.is_authenticated = True
                    return True

                logger.error("Login might have failed - modal still open or no user menu found")
                await page.screenshot(path='fastmoss_login_failed.png')
                return False
            else:
                logger.error("Could not find login submit button")
                return False

        except Exception as e:
            logger.error(f"Login failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def handle_login_modal(self, page: Page) -> bool:
        """
        Handle login modal if it appears during scraping.

        Args:
            page: Playwright page object

        Returns:
            True if handled successfully, False otherwise
        """
        try:
            # Check if login modal is visible
            modal = await page.query_selector('[class*="modal"], [class*="Modal"]')
            if not modal:
                return False

            logger.info("Login modal detected, attempting to login...")
            return await self.login(page)

        except Exception as e:
            logger.error(f"Failed to handle login modal: {e}")
            return False

    async def save_session(self, context: BrowserContext) -> None:
        """
        Save browser session for reuse.

        Args:
            context: Browser context to save
        """
        try:
            # Save session cookies and storage state
            await context.storage_state(path=str(self.session_file))
            logger.info(f"Session saved to {self.session_file}")
        except Exception as e:
            logger.warning(f"Failed to save session: {e}")

    async def load_session(self, context: BrowserContext) -> bool:
        """
        Load saved browser session.

        Args:
            context: Browser context to load into

        Returns:
            True if session loaded, False otherwise
        """
        if not self.session_file.exists():
            logger.info("No saved session found")
            return False

        try:
            logger.info(f"Loading session from {self.session_file}")
            # Session loading happens during context creation, not after
            # So this method is mainly for checking if session exists
            return True
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
            return False
