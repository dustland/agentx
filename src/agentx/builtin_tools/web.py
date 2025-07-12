"""
Web Tools - Opinionated content extraction using the best available methods.

Uses Crawl4AI as the primary and only method for reliability and consistency.
No complex fallback chains - if Crawl4AI fails, the extraction fails clearly.
"""

from ..utils.logger import get_logger
from ..core.tool import Tool, tool, ToolResult
from typing import List, Optional, Union
from dataclasses import dataclass
import time
import asyncio
import re
from urllib.parse import urlparse
from datetime import datetime

logger = get_logger(__name__)


@dataclass
class WebContent:
    """Extracted web content."""
    url: str
    title: str
    content: str
    markdown: str
    metadata: dict
    success: bool
    error: Optional[str] = None


class WebTool(Tool):
    """
    Opinionated web content extraction tool using Crawl4AI.

    Simple, reliable, and consistent - no complex fallback chains.
    """

    def __init__(self, workspace_storage=None, use_crawl4ai=True):
        super().__init__("web")
        self.workspace = workspace_storage
        self.use_crawl4ai = use_crawl4ai  # Re-enabled - need to fix crashes properly

    @tool(
        description="Extract clean content from URLs and save to files. Uses direct Playwright implementation to avoid browser crashes.",
        return_description="ToolResult with file paths and content summaries"
    )
    async def extract_content(self, urls: Union[str, List[str]], prompt: str = "Extract main content") -> ToolResult:
        """
        Extract content from URLs using Crawl4AI for advanced extraction.

        Args:
            urls: Single URL or list of URLs to extract from
            prompt: Optional focus prompt (currently unused)

        Returns:
            ToolResult with extracted content summaries and file paths

        Note: Uses improved Crawl4AI configuration based on stable Playwright patterns.
        Falls back to simple HTTP extraction if Crawl4AI fails.
        """
        # Convert single URL to list and initialize timing
        url_list = [urls] if isinstance(urls, str) else urls
        start_time = time.time()

        # Choose extraction method based on configuration
        if self.use_crawl4ai:
            try:
                from crawl4ai import AsyncWebCrawler
                logger.info("Using Crawl4AI for advanced extraction")
                return await self._extract_with_crawl4ai_fixed(url_list, start_time)
            except ImportError:
                logger.warning("Crawl4AI not installed, falling back to simple extraction")
                self.use_crawl4ai = False

        logger.info(f"Extracting content from {len(url_list)} URLs using simple HTTP extraction...")

        # Extract URLs sequentially
        extracted_contents = []

        for url in url_list:
            try:
                logger.info(f"Processing URL: {url}")
                # Use simple extraction directly to avoid browser crashes
                result = await self._simple_fallback_extraction(url)
                extracted_contents.append(result)

            except Exception as e:
                logger.error(f"Simple extraction failed for {url}: {e}")
                extracted_contents.append(WebContent(
                    url=url,
                    title="Extraction Failed",
                    content="",
                    markdown="",
                    metadata={"extraction_method": "simple_failed", "content_length": 0},
                    success=False,
                    error=str(e)
                ))

        extraction_time = time.time() - start_time
        logger.info(f"Content extraction completed in {extraction_time:.2f}s")

        return await self._process_extracted_contents(extracted_contents, url_list, extraction_time, "simple_http")

    async def _process_extracted_contents(self, extracted_contents: List[WebContent], url_list: List[str],
                                        extraction_time: float, method: str) -> ToolResult:
        """Process extracted contents into final result format."""
        # Save to workspace and create summaries
        saved_files = []
        content_summaries = []

        for content_obj in extracted_contents:
            if content_obj.success and content_obj.content:
                # Generate filename
                filename = self._generate_filename(content_obj.url, content_obj.title)

                # Create file content with metadata
                file_content = f"""# {content_obj.title}

**Source:** {content_obj.url}
**Extracted:** {datetime.now().isoformat()}
**Length:** {len(content_obj.content)} characters

---

{content_obj.content}
"""

                # Save to workspace
                if self.workspace:
                    try:
                        result = await self.workspace.store_artifact(
                            name=filename,
                            content=file_content,
                            content_type="text/markdown",
                            metadata={
                                "source_url": content_obj.url,
                                "title": content_obj.title,
                                "tool": "extract_content"
                            },
                            commit_message=f"Extracted content from {content_obj.url}"
                        )

                        if result.success:
                            saved_files.append(filename)
                            logger.info(f"Saved content to {filename}")
                    except Exception as e:
                        logger.error(f"Failed to save {filename}: {e}")

                # Create summary
                preview = content_obj.content[:300] + "..." if len(content_obj.content) > 300 else content_obj.content
                content_summaries.append({
                    "url": content_obj.url,
                    "title": content_obj.title,
                    "saved_file": filename if filename in saved_files else None,
                    "content_length": len(content_obj.content),
                    "content_preview": preview,
                    "extraction_successful": True
                })
            else:
                # Failed extraction
                content_summaries.append({
                    "url": content_obj.url,
                    "title": "Extraction Failed",
                    "saved_file": None,
                    "content_length": 0,
                    "content_preview": f"Failed: {content_obj.error}",
                    "extraction_successful": False,
                    "error": content_obj.error
                })

        # Return results
        successful_extractions = sum(1 for s in content_summaries if s["extraction_successful"])

        if len(url_list) == 1:
            result_data = content_summaries[0] if content_summaries else None
        else:
            result_data = content_summaries

        return ToolResult(
            success=successful_extractions > 0,
            result=result_data,
            execution_time=extraction_time,
            metadata={
                "total_urls": len(url_list),
                "successful_extractions": successful_extractions,
                "saved_files": saved_files,
                "extraction_method": method,
                "message": f"Extracted content from {successful_extractions}/{len(url_list)} URLs"
            }
        )

    async def _extract_with_crawl4ai_fixed(self, url_list: List[str], start_time: float) -> ToolResult:
        """Fixed Crawl4AI implementation - create new crawler for each URL to avoid lifecycle bug."""
        try:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

            # Try Crawl4AI with workaround for the browser lifecycle bug
            # Based on https://github.com/unclecode/crawl4ai/pull/1211
            logger.info("Attempting Crawl4AI with per-URL crawler instances")

            extracted_contents = []

            # Process each URL with its own crawler instance to avoid context issues
            for url in url_list:
                try:
                    logger.info(f"Processing URL with Crawl4AI: {url}")

                    # Create a fresh browser config for each URL
                    browser_config = BrowserConfig(
                        browser_type="chromium",
                        headless=True,
                        # Use system Chrome instead of bundled Chromium
                        chrome_channel="chrome",  # This uses system Chrome
                        # Use context mode to avoid lifecycle issues
                        browser_mode="context",
                        # Don't use persistent context
                        use_persistent_context=False,
                        # Minimal args for stability
                        extra_args=['--no-sandbox', '--disable-dev-shm-usage']
                    )

                    # Create a new crawler for this URL only
                    async with AsyncWebCrawler(config=browser_config) as crawler:
                        # Run configuration with minimal options
                        run_config = CrawlerRunConfig(
                            word_count_threshold=10,
                            page_timeout=30000,
                            exclude_external_links=True,
                            exclude_social_media_links=True,
                            wait_until="domcontentloaded"
                        )

                        result = await crawler.arun(url=url, config=run_config)

                        if result.success and result.markdown:
                            title = result.metadata.get('title', url) if result.metadata else url
                            content = result.markdown.strip()

                            if content:
                                content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
                                extracted_contents.append(WebContent(
                                    url=url,
                                    title=title.strip() if isinstance(title, str) else url,
                                    content=content,
                                    markdown=content,
                                    metadata={
                                        "extraction_method": "crawl4ai_workaround",
                                        "content_length": len(content),
                                        "word_count": len(content.split()),
                                    },
                                    success=True
                                ))
                            else:
                                raise Exception("No content extracted")
                        else:
                            raise Exception(f"Crawl failed: {result.error_message if result else 'Unknown error'}")

                except Exception as e:
                    logger.warning(f"Crawl4AI failed for {url}: {e}")
                    # Try simple fallback
                    try:
                        fallback_result = await self._simple_fallback_extraction(url)
                        extracted_contents.append(fallback_result)
                    except Exception as fallback_error:
                        logger.error(f"Both Crawl4AI and fallback failed for {url}: {fallback_error}")
                        extracted_contents.append(WebContent(
                            url=url,
                            title="Extraction Failed",
                            content="",
                            markdown="",
                            metadata={"extraction_method": "failed", "content_length": 0},
                            success=False,
                            error=str(e)
                        ))

            extraction_time = time.time() - start_time
            return await self._process_extracted_contents(extracted_contents, url_list, extraction_time, "crawl4ai_workaround")

        except ImportError:
            logger.warning("Crawl4AI not installed, using direct Playwright")
        except Exception as e:
            logger.error(f"Crawl4AI with workaround failed: {e}, falling back to Playwright")

        # Fallback to direct Playwright implementation
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed, falling back to simple extraction")
            # Fall back to simple extraction for all URLs
            extracted_contents = []
            for url in url_list:
                try:
                    result = await self._simple_fallback_extraction(url)
                    extracted_contents.append(result)
                except Exception as e:
                    logger.error(f"Simple extraction failed for {url}: {e}")
                    extracted_contents.append(WebContent(
                        url=url,
                        title="Extraction Failed",
                        content="",
                        markdown="",
                        metadata={"extraction_method": "failed", "content_length": 0},
                        success=False,
                        error=str(e)
                    ))
            extraction_time = time.time() - start_time
            return await self._process_extracted_contents(extracted_contents, url_list, extraction_time, "simple_http")

        extracted_contents = []

        # Use Playwright directly with proper context management
        async with async_playwright() as p:
            # Try system Chrome first, then webkit, then firefox
            browser = None
            browser_type = "chrome"

            try:
                # First try system Chrome (most stable on macOS)
                browser = await p.chromium.launch(
                    channel="chrome",  # Use system Chrome instead of Chromium
                    headless=True
                )
                browser_type = "chrome"
                logger.info("Using system Chrome browser")
            except Exception as e:
                logger.warning(f"System Chrome not found: {e}, trying webkit")
                try:
                    # WebKit is usually stable on macOS
                    browser = await p.webkit.launch(headless=True)
                    browser_type = "webkit"
                    logger.info("Using WebKit browser")
                except Exception as e2:
                    logger.warning(f"WebKit failed: {e2}, trying Firefox")
                    try:
                        browser = await p.firefox.launch(headless=True)
                        browser_type = "firefox"
                        logger.info("Using Firefox browser")
                    except Exception as e3:
                        logger.error(f"All browsers failed: Chrome: {e}, WebKit: {e2}, Firefox: {e3}")
                        # Fall back to simple extraction
                        for url in url_list:
                            try:
                                result = await self._simple_fallback_extraction(url)
                                extracted_contents.append(result)
                            except Exception as e4:
                                extracted_contents.append(WebContent(
                                    url=url,
                                    title="Extraction Failed",
                                    content="",
                                    markdown="",
                                    metadata={"extraction_method": "failed", "content_length": 0},
                                    success=False,
                                    error=str(e4)
                                ))
                        extraction_time = time.time() - start_time
                        return await self._process_extracted_contents(extracted_contents, url_list, extraction_time, "simple_http")

            # Process URLs with direct Playwright control
            for url in url_list:
                context = None
                page = None

                try:
                    logger.info(f"Processing URL with Playwright {browser_type}: {url}")

                    # Create a new context for each URL (isolation)
                    context = await browser.new_context(
                        viewport={'width': 1280, 'height': 720},
                        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    )

                    page = await context.new_page()

                    # Navigate with timeout
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)

                    # Wait a bit for dynamic content
                    await page.wait_for_timeout(2000)

                    # Extract content
                    content = await page.content()
                    title = await page.title()

                    # Convert to markdown-like format
                    text_content = await page.evaluate("""() => {
                        // Remove script and style elements
                        const scripts = document.querySelectorAll('script, style');
                        scripts.forEach(el => el.remove());

                        // Get text content
                        return document.body.innerText || document.body.textContent || '';
                    }""")

                    if text_content:
                        # Clean up text
                        text_content = re.sub(r'\n\s*\n\s*\n', '\n\n', text_content.strip())

                        extracted_contents.append(WebContent(
                            url=url,
                            title=title or url,
                            content=text_content,
                            markdown=text_content,
                            metadata={
                                "extraction_method": f"playwright_{browser_type}",
                                "content_length": len(text_content),
                                "word_count": len(text_content.split()),
                            },
                            success=True
                        ))
                    else:
                        raise Exception("No content extracted")

                except Exception as e:
                    logger.warning(f"Playwright extraction failed for {url}: {e}")
                    # Try simple fallback
                    try:
                        fallback_result = await self._simple_fallback_extraction(url)
                        extracted_contents.append(fallback_result)
                    except Exception as fallback_error:
                        logger.error(f"Both Playwright and fallback failed for {url}: {fallback_error}")
                        extracted_contents.append(WebContent(
                            url=url,
                            title="Extraction Failed",
                            content="",
                            markdown="",
                            metadata={"extraction_method": "failed", "content_length": 0},
                            success=False,
                            error=str(e)
                        ))
                finally:
                    # Clean up page and context
                    if page:
                        try:
                            await page.close()
                        except:
                            pass
                    if context:
                        try:
                            await context.close()
                        except:
                            pass

            # Close browser
            if browser:
                try:
                    await browser.close()
                except:
                    pass

        # Process results
        extraction_time = time.time() - start_time
        return await self._process_extracted_contents(extracted_contents, url_list, extraction_time, f"playwright_{browser_type}")

    async def _simple_fallback_extraction(self, url: str) -> WebContent:
        """Simple fallback extraction when Crawl4AI fails."""
        import aiohttp
        import re

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgentX/1.0)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    response.raise_for_status()
                    html_content = await response.text()

            # Extract title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else url

            # Simple text extraction - remove HTML tags
            text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', '', text)  # Remove all HTML tags

            # Clean up text
            text = re.sub(r'\s+', ' ', text).strip()

            # Limit content size
            if len(text) > 3000:
                text = text[:3000] + "... [Content truncated for fallback extraction]"

            return WebContent(
                url=url,
                title=title,
                content=text,
                markdown=text,
                metadata={
                    "extraction_method": "simple_fallback",
                    "content_length": len(text),
                    "truncated": len(text) > 3000
                },
                success=True
            )

        except Exception as e:
            raise Exception(f"Simple fallback extraction failed: {e}")

    def _generate_filename(self, url: str, title: str) -> str:
        """Generate a clean filename from URL and title."""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '').replace('.', '_')

        if title and title != url and title != "Extraction Failed":
            # Clean title
            clean_title = re.sub(r'[^\w\s\-]', '', title)
            clean_title = re.sub(r'\s+', '_', clean_title.strip())[:40]
            filename = f"extracted_{domain}_{clean_title}.md"
        else:
            # Use domain and path
            path_part = parsed.path.replace('/', '_').strip('_')[:20] if parsed.path != '/' else 'homepage'
            filename = f"extracted_{domain}_{path_part}.md"

        # Ensure valid filename
        return re.sub(r'[^\w\-_.]', '', filename)


# Export
__all__ = ["WebTool", "WebContent"]
