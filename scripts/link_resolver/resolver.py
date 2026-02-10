"""TikTok Product Link Resolver implementation."""

import re
from typing import Optional, List
from playwright.async_api import async_playwright, Page, BrowserContext
from loguru import logger

from .models import LinkResolverConfig, ResolvedProduct


class LinkResolver:
    """Resolves TikTok product links to extract product IDs."""

    # Product ID patterns (19-digit TikTok IDs)
    PRODUCT_ID_PATTERNS = [
        r'/view/product/(\d{19})',      # Main pattern: /view/product/{id}
        r'/product/(\d{19})',            # Alternative: /product/{id}
        r'product_id=(\d{19})',          # Query param: ?product_id={id}
        r'"product_id":"?(\d{19})"?',   # JSON: "product_id":"123"
        r'productId":"?(\d{19})"?',     # Alternative JSON key
        r'item_id":"?(\d{19})"?',       # Another common key
    ]

    def __init__(self, config: LinkResolverConfig):
        """
        Initialize link resolver.

        Args:
            config: Configuration for the resolver
        """
        self.config = config
        self.browser = None
        self.context = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._setup_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup()

    async def _setup_browser(self) -> None:
        """Setup Playwright browser with mobile user agent."""
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless
        )

        # Mobile context to bypass desktop blocking
        self.context = await self.browser.new_context(
            user_agent=self.config.user_agent,
            viewport={'width': 390, 'height': 844},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            locale='en-US'
        )

        logger.info("Browser setup complete with mobile user agent")

    async def _cleanup(self) -> None:
        """Cleanup browser resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser cleanup complete")

    def _extract_product_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract product ID from URL using regex patterns.

        Only extracts from product URLs, not video URLs.

        Args:
            url: URL to extract from

        Returns:
            Product ID if found, None otherwise
        """
        # Skip video URLs - we need to search page content for those
        if '/video/' in url or '/@' in url:
            logger.debug(f"Skipping video URL, will search page content: {url}")
            return None

        for pattern in self.PRODUCT_ID_PATTERNS:
            match = re.search(pattern, url)
            if match:
                product_id = match.group(1)
                logger.debug(f"Found product ID {product_id} using pattern: {pattern}")
                return product_id
        return None

    def _extract_product_id_from_content(self, content: str) -> Optional[str]:
        """
        Extract product ID from page content.

        Prioritizes product-specific patterns and filters out video IDs.

        Args:
            content: HTML content to search

        Returns:
            Product ID if found, None otherwise
        """
        # Product-specific patterns (prioritize these)
        product_specific_patterns = [
            r'"product_id":"?(\d{19})"?',
            r'productId":"?(\d{19})"?',
            r'/view/product/(\d{19})',
            r'product_id=(\d{19})',
        ]

        # Try product-specific patterns first
        for pattern in product_specific_patterns:
            matches = re.findall(pattern, content)
            for product_id in matches:
                # Filter: TikTok product IDs typically start with "172"
                # Video IDs often start with "7" or other prefixes
                if product_id.startswith('172'):
                    logger.debug(f"Found product ID {product_id} in content using pattern: {pattern}")
                    return product_id

        # Fallback: try all patterns but still filter by prefix
        for pattern in self.PRODUCT_ID_PATTERNS:
            matches = re.findall(pattern, content)
            for product_id in matches:
                if product_id.startswith('172'):
                    logger.debug(f"Found product ID {product_id} in content using pattern: {pattern}")
                    return product_id

        logger.warning("No product ID found in content (only video IDs or no IDs)")
        return None

    async def resolve_link(self, url: str) -> ResolvedProduct:
        """
        Resolve a TikTok product link to extract the product ID.

        Args:
            url: TikTok product link (vm.tiktok.com, direct shop link, etc.)

        Returns:
            ResolvedProduct with product ID and metadata
        """
        redirect_chain = []
        product_id = None
        final_url = url
        error = None

        try:
            logger.info(f"Resolving link: {url}")

            page = await self.context.new_page()

            # Track navigation requests to capture redirects
            def handle_request(request):
                if request.is_navigation_request():
                    redirect_url = request.url
                    redirect_chain.append(redirect_url)
                    logger.debug(f"Navigation: {redirect_url}")

                    # Try to extract product ID from each redirect URL
                    nonlocal product_id
                    if not product_id:
                        product_id = self._extract_product_id_from_url(redirect_url)

            page.on('request', handle_request)

            # Navigate with shorter timeout, we only need redirects
            try:
                # Use 'domcontentloaded' instead of 'networkidle' since we only need URL
                response = await page.goto(
                    url,
                    wait_until='domcontentloaded',
                    timeout=self.config.timeout
                )
                final_url = page.url

                # If we didn't get product ID from redirects, try final URL
                if not product_id:
                    product_id = self._extract_product_id_from_url(final_url)

                # Last resort: search page content
                if not product_id:
                    logger.debug("Product ID not found in URLs, searching page content...")
                    content = await page.content()
                    product_id = self._extract_product_id_from_content(content)

            except Exception as nav_error:
                # Timeout or navigation error - check if we got product ID from redirects
                logger.warning(f"Navigation error (likely timeout), but may have captured redirects: {nav_error}")
                if redirect_chain:
                    final_url = redirect_chain[-1] if redirect_chain else url
                    if not product_id:
                        product_id = self._extract_product_id_from_url(final_url)

            finally:
                await page.close()

            # Validate result
            if product_id:
                logger.info(f"✅ Successfully resolved product ID: {product_id}")
                return ResolvedProduct(
                    original_url=url,
                    product_id=product_id,
                    final_url=final_url,
                    redirect_chain=redirect_chain,
                    success=True
                )
            else:
                error = "Product ID not found in URL or page content"
                logger.error(f"❌ {error}")
                return ResolvedProduct(
                    original_url=url,
                    product_id='',
                    final_url=final_url,
                    redirect_chain=redirect_chain,
                    success=False,
                    error=error
                )

        except Exception as e:
            error = str(e)
            logger.error(f"❌ Failed to resolve link: {error}")
            return ResolvedProduct(
                original_url=url,
                product_id='',
                final_url=final_url,
                redirect_chain=redirect_chain,
                success=False,
                error=error
            )

    async def resolve_multiple_links(self, urls: List[str]) -> List[ResolvedProduct]:
        """
        Resolve multiple TikTok product links.

        Args:
            urls: List of TikTok product links

        Returns:
            List of ResolvedProduct results
        """
        results = []

        for i, url in enumerate(urls, 1):
            logger.info(f"Processing link {i}/{len(urls)}")
            result = await self.resolve_link(url)
            results.append(result)

        return results
