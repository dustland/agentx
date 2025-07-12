"""
Web Tools - Opinionated web automation and content extraction.

Built-in integrations:
- Firecrawl: Web content extraction
- requests + BeautifulSoup: Content extraction
- browser-use: AI-first browser automation (better than Playwright for agents)
"""

from ..utils.logger import get_logger
from ..core.tool import Tool, tool, ToolResult
from ..core.exceptions import ConfigurationError
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import time

logger = get_logger(__name__)


@dataclass
class WebContent:
    """Extracted web content."""
    url: str
    title: str
    content: str
    markdown: str
    metadata: Dict[str, Any]
    success: bool
    error: Optional[str] = None


@dataclass
class BrowserAction:
    """Browser automation action result."""
    action: str
    success: bool
    result: Any
    screenshot: Optional[str] = None
    error: Optional[str] = None


class WebTool(Tool):
    """
    Web content extraction and browser automation tool.

    Combines Firecrawl for content extraction and browser-use for automation.
    """

    def __init__(self, jina_api_key: Optional[str] = None, workspace_storage=None):
        super().__init__("web")
        self.jina_api_key = jina_api_key
        self.workspace = workspace_storage  # For saving extracted content to files
        self._browser = None
        self._init_clients()

    def _init_clients(self):
        """Initialize Jina Reader and browser-use clients."""
        # Initialize Jina Reader
        try:
            if not self.jina_api_key:
                import os
                self.jina_api_key = os.getenv("JINA_API_KEY")

            if self.jina_api_key:
                logger.info("Jina Reader API key configured")
            else:
                logger.warning("Jina API key not found. Set JINA_API_KEY environment variable for enhanced features")

        except Exception as e:
            logger.error(f"Failed to initialize Jina configuration: {e}")

        # Initialize browser-use
        try:
            from browser_use import Browser

            self._browser = Browser()
            logger.info("browser-use initialized")

        except ImportError:
            logger.warning("browser-use not installed. Install with: pip install browser-use")
        except Exception as e:
            logger.error(f"Failed to initialize browser-use: {e}")

    @tool(
        description="Extract clean content from URLs with robust open-source methods and automatically save to files. Uses Crawl4AI first (open source, handles JS, most reliable), then falls back to BeautifulSoup, Firecrawl, Jina Reader, or simple extraction if needed.",
        return_description="ToolResult containing file paths where content was saved, plus content summaries"
    )
    async def extract_content(self, urls: Union[str, List[str]], prompt: str = "Extract the main content from this webpage") -> ToolResult:
        """
        Extract clean content from one or more URLs with robust fallback methods and automatically save to files.

        This tool uses multiple extraction methods in priority order to ensure reliability:
        1. Crawl4AI (primary method - open source, handles JavaScript, most reliable)
        2. BeautifulSoup + requests (fast fallback)
        3. Firecrawl API (if FIRECRAWL_API_KEY available)
        4. Jina Reader API (if JINA_API_KEY available)
        5. Simple HTML parsing (last resort)

        Content is automatically saved to workspace files to prevent overwhelming the conversation context.

        Args:
            urls: A single URL or list of URLs to extract content from
            prompt: Description of what content to focus on (optional)

        Returns:
            ToolResult with file paths and content summaries (not full content)
        """
        try:
            import asyncio
            import aiohttp
            import re
            from urllib.parse import urlparse

            # Convert single URL to list
            url_list = [urls] if isinstance(urls, str) else urls

            def _generate_filename(url: str, title: str) -> str:
                """Generate a safe filename from URL and title."""
                # Parse URL to get domain
                parsed = urlparse(url)
                domain = parsed.netloc.replace('www.', '').replace('.', '_')

                # Clean title for filename
                if title and title != url:
                    # Remove common prefixes and clean up
                    clean_title = re.sub(r'^(#\s*)', '', title)  # Remove markdown headers
                    clean_title = re.sub(r'[^\w\s\-]', '', clean_title)  # Remove special chars
                    clean_title = re.sub(r'\s+', '_', clean_title.strip())[:50]  # Replace spaces, limit length
                    filename = f"extracted_{domain}_{clean_title}.md"
                else:
                    # Fallback to domain and path
                    path_part = parsed.path.replace('/', '_').strip('_')[:30] if parsed.path != '/' else 'homepage'
                    filename = f"extracted_{domain}_{path_part}.md"

                # Ensure valid filename
                filename = re.sub(r'[^\w\-_.]', '', filename)
                return filename

            async def extract_single_url(session: aiohttp.ClientSession, url: str) -> WebContent:
                """Extract content from a single URL."""
                try:
                    # Try Crawl4AI first (open source, most reliable)
                    return await self._extract_with_crawl4ai(session, url)
                except Exception as e:
                    logger.warning(f"Crawl4AI extraction failed for {url}: {e}, trying fallback methods...")
                    # Try fallback extraction methods
                    return await self._fallback_extraction(session, url, e)

            # Create aiohttp session with connection limits for parallel processing
            connector = aiohttp.TCPConnector(
                limit=20,  # Total connection limit
                limit_per_host=5,  # Per-host connection limit to avoid overwhelming servers
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
            )

            async with aiohttp.ClientSession(connector=connector) as session:
                # Process all URLs in parallel using asyncio.gather
                logger.info(f"Starting parallel extraction of {len(url_list)} URLs...")
                start_time = asyncio.get_event_loop().time()

                extracted_contents = await asyncio.gather(
                    *[extract_single_url(session, url) for url in url_list],
                    return_exceptions=False  # Let individual URL failures be handled in extract_single_url
                )

                end_time = asyncio.get_event_loop().time()
                extraction_time = end_time - start_time
                logger.info(f"Parallel extraction completed in {extraction_time:.2f}s for {len(url_list)} URLs")

            # Save extracted content to files and prepare summaries
            saved_files = []
            content_summaries = []

            for content_obj in extracted_contents:
                if content_obj.success and content_obj.content:
                    # Generate filename
                    filename = _generate_filename(content_obj.url, content_obj.title)

                    # Prepare content for file with metadata
                    from datetime import datetime
                    file_content = f"""# Extracted Content from {content_obj.url}

**Title:** {content_obj.title}
**Source URL:** {content_obj.url}
**Extraction Date:** {datetime.now().isoformat()}
**Content Length:** {len(content_obj.content)} characters
**Extraction Method:** {content_obj.metadata.get('extraction_method', 'unknown')}

---

{content_obj.content}
"""

                    # Save to workspace if available
                    if self.workspace:
                        try:
                            # Save as artifact
                            result = await self.workspace.store_artifact(
                                name=filename,
                                content=file_content,
                                content_type="text/markdown",
                                metadata={
                                    "source_url": content_obj.url,
                                    "title": content_obj.title,
                                    "extraction_method": content_obj.metadata.get('extraction_method'),
                                    "tool": "extract_content"
                                },
                                commit_message=f"Extracted content from {content_obj.url}"
                            )

                            if result.success:
                                saved_files.append(filename)
                                logger.info(f"Saved extracted content to {filename}")
                            else:
                                logger.error(f"Failed to save {filename}: {result.error}")

                        except Exception as e:
                            logger.error(f"Error saving content to {filename}: {e}")

                    # Create summary for LLM (first 500 chars + metadata)
                    content_preview = content_obj.content[:500] + "..." if len(content_obj.content) > 500 else content_obj.content

                    summary = {
                        "url": content_obj.url,
                        "title": content_obj.title,
                        "saved_file": filename if filename in saved_files else None,
                        "content_length": len(content_obj.content),
                        "content_preview": content_preview,
                        "extraction_successful": True
                    }
                    content_summaries.append(summary)

                else:
                    # Handle failed extractions
                    summary = {
                        "url": content_obj.url,
                        "title": content_obj.title or "Unknown",
                        "saved_file": None,
                        "content_length": 0,
                        "content_preview": f"Extraction failed: {content_obj.error}",
                        "extraction_successful": False,
                        "error": content_obj.error
                    }
                    content_summaries.append(summary)

            # Return summary result instead of full content
            if isinstance(urls, str):
                # Single URL case
                result_summary = content_summaries[0] if content_summaries else None
            else:
                # Multiple URLs case
                result_summary = content_summaries

            # Check if any extractions succeeded
            success = any(summary.get('extraction_successful', False) for summary in content_summaries)
            successful_count = sum(1 for summary in content_summaries if summary.get('extraction_successful', False))

            return ToolResult(
                success=success,
                result=result_summary,
                metadata={
                    "total_urls": len(url_list),
                    "successful_extractions": successful_count,
                    "saved_files": saved_files,
                    "extraction_method": "jina_reader_with_auto_save",
                    "extraction_time_seconds": extraction_time,
                    "parallel_processing": True,
                    "message": f"Content extracted and saved to {len(saved_files)} file(s). Use read_file tool to access full content."
                }
            )

        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return ToolResult(
                success=False,
                error=f"Content extraction failed: {str(e)}",
                metadata={"urls": url_list if 'url_list' in locals() else [], "parallel_processing": True}
            )

    async def _fallback_extraction(self, session, url: str, original_error: Exception) -> WebContent:
        """Fallback content extraction methods when primary method fails."""
        fallback_methods = [
            self._extract_with_requests_bs4,
            self._extract_with_firecrawl,
            self._extract_with_jina_reader,
            self._extract_with_simple_requests
        ]

        for i, method in enumerate(fallback_methods):
            try:
                method_name = method.__name__.replace('_extract_with_', '')
                logger.info(f"Trying fallback method {i+1}/{len(fallback_methods)}: {method_name} for {url}")
                return await method(session, url)
            except Exception as e:
                logger.warning(f"Fallback method {method_name} failed for {url}: {e}")
                continue

        # All methods failed
        logger.error(f"All extraction methods failed for {url}")
        return WebContent(
            url=url,
            title="Extraction Failed",
            content="",
            markdown="",
            metadata={
                "extraction_method": "all_methods_failed",
                "original_error": str(original_error),
                "content_length": 0
            },
            success=False,
            error=f"All extraction methods failed. Original error: {original_error}"
        )

    async def _extract_with_crawl4ai(self, session, url: str) -> WebContent:
        """Extract content using Crawl4AI (open source, local processing)."""
        try:
            from crawl4ai import AsyncWebCrawler

            # Configure crawler for optimal AI content extraction
            config = {
                "headless": True,
                "browser_type": "chromium",  # or "firefox", "webkit"
                "verbose": False,
                "delay_before_return": 2.0,  # Wait for dynamic content
                "semaphore_count": 5,  # Parallel processing limit
                "always_by_pass_cache": False,
                "base_directory": "/tmp/crawl4ai_cache"
            }

            async with AsyncWebCrawler(**config) as crawler:
                # Enhanced crawling with AI-optimized extraction
                result = await crawler.arun(
                    url=url,
                    # Content extraction options
                    word_count_threshold=10,  # Minimum content length
                    only_text=False,  # Keep rich content
                    process_iframes=True,  # Extract iframe content
                    remove_overlay_elements=True,  # Remove popups/modals
                    simulate_user=True,  # Simulate human behavior
                    override_navigator=True,  # Bypass bot detection
                    # Output format options
                    markdown_generator=True,  # Generate clean markdown
                    # Performance options
                    page_timeout=30000,  # 30 second timeout
                    session_id="agentx_extraction"  # Reuse session for efficiency
                )

                if not result.success:
                    raise Exception(f"Crawl4AI failed: {result.error_message}")

                # Extract title - try multiple sources
                title = ""
                if result.metadata:
                    title = (result.metadata.get('title') or
                            result.metadata.get('og:title') or
                            result.metadata.get('twitter:title') or
                            url)

                # Get the best available content
                content = result.markdown or result.cleaned_html or result.html
                if not content:
                    raise Exception("No content extracted from page")

                # Clean up content - remove excessive whitespace
                import re
                content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
                content = content.strip()

                return WebContent(
                    url=url,
                    title=title,
                    content=content,
                    markdown=result.markdown or content,
                    metadata={
                        "extraction_method": "crawl4ai",
                        "content_length": len(content),
                        "page_title": result.metadata.get('title') if result.metadata else None,
                        "page_description": result.metadata.get('description') if result.metadata else None,
                        "extraction_time": result.extraction_time if hasattr(result, 'extraction_time') else None,
                        "word_count": len(content.split()) if content else 0,
                        "success": True
                    },
                    success=True
                )

        except ImportError:
            raise Exception("Crawl4AI not installed. Install with: pip install crawl4ai")
        except Exception as e:
            raise Exception(f"Crawl4AI extraction failed: {e}")

    async def _extract_with_requests_bs4(self, session, url: str) -> WebContent:
        """Extract content using requests + BeautifulSoup."""
        try:
            from bs4 import BeautifulSoup
            import re

            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgentX/1.0)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
            }

            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(url, headers=headers, timeout=timeout) as response:
                response.raise_for_status()
                html_content = await response.text()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()

            # Extract title
            title_elem = soup.find('title')
            title = title_elem.get_text().strip() if title_elem else url

            # Extract main content - try multiple strategies
            content_selectors = [
                'main', 'article', '[role="main"]',
                '.content', '.post-content', '.entry-content',
                '.article-body', '.post-body', '.story-body'
            ]

            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            # Fallback to body if no main content found
            if not main_content:
                main_content = soup.find('body')

            if main_content:
                # Extract text and preserve some structure
                content_text = main_content.get_text(separator='\n', strip=True)

                # Clean up the text
                content_text = re.sub(r'\n\s*\n\s*\n', '\n\n', content_text)  # Remove excessive newlines
                content_text = re.sub(r'[ \t]+', ' ', content_text)  # Normalize spaces

                # Create basic markdown structure
                paragraphs = [p.strip() for p in content_text.split('\n\n') if p.strip()]
                markdown_content = '\n\n'.join(paragraphs)
            else:
                content_text = ""
                markdown_content = ""

            return WebContent(
                url=url,
                title=title,
                content=content_text,
                markdown=markdown_content,
                metadata={
                    "extraction_method": "requests_beautifulsoup",
                    "content_length": len(content_text)
                },
                success=True
            )

        except ImportError:
            raise Exception("BeautifulSoup not installed. Install with: pip install beautifulsoup4")
        except Exception as e:
            raise Exception(f"BeautifulSoup extraction failed: {e}")

    async def _extract_with_firecrawl(self, session, url: str) -> WebContent:
        """Extract content using Firecrawl API if available."""
        try:
            import os
            import aiohttp
            firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

            if not firecrawl_api_key:
                raise Exception("FIRECRAWL_API_KEY not found in environment variables")

            # Use Firecrawl API
            firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
            headers = {
                'Authorization': f'Bearer {firecrawl_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True
            }

            timeout = aiohttp.ClientTimeout(total=45)
            async with session.post(firecrawl_url, json=payload, headers=headers, timeout=timeout) as response:
                response.raise_for_status()
                result = await response.json()

            if result.get("success"):
                data = result.get("data", {})
                content = data.get("markdown", "")
                title = data.get("metadata", {}).get("title", url)

                return WebContent(
                    url=url,
                    title=title,
                    content=content,
                    markdown=content,
                    metadata={
                        "extraction_method": "firecrawl",
                        "content_length": len(content)
                    },
                    success=True
                )
            else:
                raise Exception(f"Firecrawl API failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            raise Exception(f"Firecrawl extraction failed: {e}")

    async def _extract_with_jina_reader(self, session, url: str) -> WebContent:
        """Extract content using Jina Reader API."""
        try:
            # Use Jina Reader API
            if self.jina_api_key:
                # Use authenticated API for better rate limits and features
                jina_url = f"https://r.jina.ai/{url}"
                headers = {
                    'Authorization': f'Bearer {self.jina_api_key}',
                    'User-Agent': 'Mozilla/5.0 (compatible; AgentX/1.0)',
                    'Accept': 'application/json',
                    'X-Return-Format': 'markdown'
                }
            else:
                # Use free API (with rate limits)
                jina_url = f"https://r.jina.ai/{url}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; AgentX/1.0)',
                    'Accept': 'text/plain'
                }

            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(jina_url, headers=headers, timeout=timeout) as response:
                # If authenticated request fails with 422, try unauthenticated
                if response.status == 422 and self.jina_api_key:
                    logger.warning(f"Authenticated Jina request failed with 422 for {url}, trying unauthenticated...")
                    jina_url = f"https://r.jina.ai/{url}"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (compatible; AgentX/1.0)',
                        'Accept': 'text/plain'
                    }
                    async with session.get(jina_url, headers=headers, timeout=timeout) as retry_response:
                        retry_response.raise_for_status()
                        content = await retry_response.text()
                else:
                    response.raise_for_status()
                    content = await response.text()

            # Extract title from first line if available
            lines = content.split('\n')
            title = lines[0].strip() if lines and lines[0].strip() else url

            # Remove title from content to avoid duplication
            if len(lines) > 1 and lines[0].strip():
                content = '\n'.join(lines[1:]).strip()

            return WebContent(
                url=url,
                title=title,
                content=content,
                markdown=content,
                metadata={
                    "extraction_method": "jina_reader",
                    "api_authenticated": bool(self.jina_api_key),
                    "content_length": len(content)
                },
                success=True
            )

        except Exception as e:
            raise Exception(f"Jina Reader extraction failed: {e}")

    async def _extract_with_simple_requests(self, session, url: str) -> WebContent:
        """Simple text extraction as last resort."""
        try:
            import re

            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgentX/1.0)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(url, headers=headers, timeout=timeout) as response:
                response.raise_for_status()
                html_content = await response.text()

            # Extract title from HTML
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else url

            # Simple text extraction - remove HTML tags
            text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', '', text)  # Remove all HTML tags

            # Clean up text
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.strip()

            # Take first 5000 characters to avoid overwhelming output
            if len(text) > 5000:
                text = text[:5000] + "... [Content truncated]"

            return WebContent(
                url=url,
                title=title,
                content=text,
                markdown=text,  # No markdown formatting in simple mode
                metadata={
                    "extraction_method": "simple_requests",
                    "content_length": len(text),
                    "truncated": len(text) > 5000
                },
                success=True
            )

        except Exception as e:
            raise Exception(f"Simple extraction failed: {e}")

    @tool(
        description="Enhanced content extraction with visual data capture using browser-use's advanced features",
        return_description="ToolResult containing comprehensive content including data from charts, graphs, and visual elements"
    )
    async def extract_content_with_visuals(self, url: str, prompt: str,
                                         capture_screenshot: bool = True,
                                         enable_web_search: bool = False) -> ToolResult:
        """
        Enhanced content extraction that captures both textual and visual data from web pages.
        This method is specifically designed to extract data from charts, graphs, infographics,
        and other visual elements that traditional text extraction might miss.

        Args:
            url: Single URL to extract content from (required)
            prompt: Detailed prompt describing what to extract, including visual elements (required)
            capture_screenshot: Whether to capture full-page screenshot for visual analysis, defaults to True
            enable_web_search: Whether to expand search beyond the URL, defaults to False

        Returns:
            ToolResult with comprehensive extracted content including visual data
        """
        if not self._browser:
            return ToolResult(
                success=False,
                result=None,
                error="browser-use not available"
            )

        try:
            # Enhanced prompt that specifically requests visual data extraction
            enhanced_prompt = f"""
            {prompt}

            CRITICAL: Pay special attention to extracting data from visual elements including:
            - All statistics, percentages, and numbers shown in charts and graphs
            - Data from pie charts, bar charts, line graphs, and trend visualizations
            - Information from infographics, dashboards, and data visualizations
            - Table data with specific numbers and comparisons
            - Map data showing regional/geographic statistics
            - Timeline data from visual timelines and roadmaps
            - Competitive analysis data from comparison charts
            - Financial data from financial charts and projections

            Do not summarize visual data - extract the complete detailed information including
            all specific numbers, percentages, company names, dates, and quantified metrics
            visible in any visual elements on the page.
            """

            # Use both Extract API and Scrape API for comprehensive data capture
            result = await self._browser.extract(
                urls=[url],
                prompt=enhanced_prompt,
                enable_web_search=enable_web_search
            )

            visual_data = None
            if capture_screenshot:
                try:
                    # Also capture with screenshot for visual analysis
                    scrape_result = await self._browser.scrape_url(
                        url,
                        formats=["screenshot@fullPage"],
                        wait_for=3000  # Wait for dynamic content to load
                    )

                    if scrape_result.success and hasattr(scrape_result, 'screenshot'):
                        visual_data = {
                            "screenshot_url": scrape_result.screenshot,
                            "markdown_content": scrape_result.markdown
                        }
                except Exception as e:
                    logger.warning(f"Screenshot capture failed for {url}: {e}")

            if result.success:
                result_data = result.data

                # Combine extracted data with visual data if available
                if visual_data:
                    if isinstance(result_data, dict):
                        result_data["visual_analysis"] = visual_data
                    else:
                        result_data = {
                            "extracted_content": result_data,
                            "visual_analysis": visual_data
                        }

                return ToolResult(
                    success=True,
                    result=result_data,
                    metadata={
                        "url": url,
                        "extraction_method": "browser_use_enhanced_visual",
                        "screenshot_captured": capture_screenshot and visual_data is not None,
                        "web_search_enabled": enable_web_search
                    }
                )
            else:
                error_msg = result.error or "Unknown error occurred"
                return ToolResult(
                    success=False,
                    error=f"Enhanced extraction failed: {error_msg}",
                    metadata={"url": url}
                )

        except Exception as e:
            logger.error(f"Enhanced visual extraction failed for {url}: {e}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )

    @tool(
        description="Crawl multiple pages from a website using browser-use",
        return_description="ToolResult containing list of WebContent objects from crawled pages"
    )
    async def crawl_website(self, url: str, limit: int = 10,
                          exclude_paths: Optional[List[str]] = None) -> ToolResult:
        """
        Crawl multiple pages from a website.

        Args:
            url: The base URL to start crawling from (required)
            limit: Maximum number of pages to crawl, defaults to 10
            exclude_paths: URL paths to exclude from crawling (optional)

        Returns:
            ToolResult with list of WebContent objects
        """
        if not self._browser:
            return ToolResult(
                success=False,
                result=None,
                error="browser-use not available"
            )

        try:
            result = await self._browser.crawl_website(
                url,
                limit=limit,
                exclude_paths=exclude_paths or ["/admin", "/login"]
            )

            # Handle the CrawlStatusResponse object (Pydantic model with attributes)
            if result.success:
                web_contents = [
                    WebContent(
                        url=page.metadata.get("sourceURL", "") if page.metadata else "",
                        title=page.metadata.get("title", "") if page.metadata else "",
                        content=page.markdown or "",
                        markdown=page.markdown or "",
                        metadata=page.metadata or {},
                        success=True
                    )
                    for page in (result.data or [])
                ]

                return ToolResult(
                    success=True,
                    result=web_contents,
                    metadata={"base_url": url, "pages_crawled": len(web_contents)}
                )
            else:
                error_msg = getattr(result, 'error', 'Unknown error occurred')
                return ToolResult(
                    success=False,
                    error=f"Browser-use crawl failed: {error_msg}",
                    metadata={"base_url": url}
                )

        except Exception as e:
            logger.error(f"Website crawl failed for {url}: {e}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )

    @tool(
        description="Automate browser actions using natural language with browser-use",
        return_description="ToolResult containing browser action result with success status and data"
    )
    async def automate_browser(self, instruction: str, url: Optional[str] = None) -> ToolResult:
        """
        Perform browser automation using natural language instructions.

        Args:
            instruction: Natural language instruction for browser action (required)
            url: Optional URL to navigate to first

        Returns:
            ToolResult with BrowserAction containing action result
        """
        if not self._browser:
            return ToolResult(
                success=False,
                result=None,
                error="browser-use not available"
            )

        try:
            # Start browser session
            await self._browser.start()
            page = await self._browser.new_page()

            # Navigate to URL if provided
            if url:
                await page.goto(url)

            # Perform AI action
            result = await page.ai_action(instruction)

            browser_action = BrowserAction(
                action=instruction,
                success=True,
                result=result
            )

            # Close browser
            await self._browser.close()

            return ToolResult(
                success=True,
                result=browser_action,
                metadata={"instruction": instruction, "url": url}
            )

        except Exception as e:
            logger.error(f"Browser automation failed: {e}")

            # Ensure browser is closed
            try:
                if self._browser:
                    await self._browser.close()
            except:
                pass

            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )




# Export main classes and functions
__all__ = [
    "WebTool",
    "WebContent",
    "BrowserAction",
]
