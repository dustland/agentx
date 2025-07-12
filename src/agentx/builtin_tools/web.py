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

    def __init__(self, workspace_storage=None):
        super().__init__("web")
        self.workspace = workspace_storage

    @tool(
        description="Extract clean content from URLs using Crawl4AI and save to files. Handles JavaScript, bypasses bot detection, generates clean markdown.",
        return_description="ToolResult with file paths and content summaries"
    )
    async def extract_content(self, urls: Union[str, List[str]], prompt: str = "Extract main content") -> ToolResult:
        """
        Extract content from URLs using Crawl4AI (open source, handles JS, reliable).

        Args:
            urls: Single URL or list of URLs to extract from
            prompt: Optional focus prompt (currently unused)

        Returns:
            ToolResult with extracted content summaries and file paths
        """
        try:
            from crawl4ai import AsyncWebCrawler
        except ImportError:
            return ToolResult(
                success=False,
                error="Crawl4AI not installed. Run: pip install crawl4ai",
                metadata={"installation_required": True}
            )

        # Convert single URL to list
        url_list = [urls] if isinstance(urls, str) else urls

        logger.info(f"Extracting content from {len(url_list)} URLs using Crawl4AI...")
        start_time = time.time()

        # Configure Crawl4AI for optimal extraction with better browser management
        config = {
            "headless": True,
            "verbose": False,
            "delay_before_return": 1.0,  # Reduce delay
            "always_by_pass_cache": False,
            "browser_type": "chromium",
            "keep_alive": False,  # Don't keep alive to prevent context issues
            "max_concurrent_sessions": 1,  # Limit concurrent sessions
        }

        async def extract_single_url(crawler, url: str) -> WebContent:
            """Extract content from a single URL with improved error handling."""
            try:
                # Add retry logic for browser context issues
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        result = await crawler.arun(
                            url=url,
                            word_count_threshold=10,
                            only_text=False,
                            process_iframes=True,
                            remove_overlay_elements=True,
                            simulate_user=True,
                            override_navigator=True,
                            markdown_generator=True,
                            page_timeout=15000,  # Reduce timeout
                            wait_for_images=False,  # Skip image loading for speed
                            delay_before_return=0.5,  # Shorter delay
                        )
                        break  # Success, exit retry loop
                    except Exception as e:
                        if "browser has been closed" in str(e).lower() and attempt < max_retries - 1:
                            logger.warning(f"Browser context closed, retrying {url} (attempt {attempt + 2}/{max_retries})")
                            await asyncio.sleep(1)  # Brief delay before retry
                            continue
                        else:
                            raise  # Re-raise if not a browser context issue or final attempt

                if not result.success:
                    raise Exception(f"Crawl failed: {result.error_message}")

                # Extract title from multiple sources
                title = url  # fallback
                if result.metadata:
                    title = (
                        result.metadata.get('title') or
                        result.metadata.get('og:title') or
                        result.metadata.get('twitter:title') or
                        url
                    )

                # Get best content
                content = result.markdown or result.cleaned_html or ""
                if not content.strip():
                    raise Exception("No content extracted")

                # Clean content
                content = re.sub(r'\n\s*\n\s*\n', '\n\n', content).strip()

                return WebContent(
                    url=url,
                    title=title.strip(),
                    content=content,
                    markdown=content,
                    metadata={
                        "extraction_method": "crawl4ai",
                        "content_length": len(content),
                        "word_count": len(content.split()),
                        "extraction_time": time.time() - start_time
                    },
                    success=True
                )

            except Exception as e:
                logger.error(f"Failed to extract {url}: {e}")
                return WebContent(
                    url=url,
                    title="Extraction Failed",
                    content="",
                    markdown="",
                    metadata={"extraction_method": "crawl4ai", "content_length": 0},
                    success=False,
                    error=str(e)
                )

        # Extract all URLs in parallel with better error handling
        extracted_contents = []
        try:
            async with AsyncWebCrawler(**config) as crawler:
                # Initialize crawler properly
                await asyncio.sleep(0.1)  # Small delay for proper initialization

                tasks = [extract_single_url(crawler, url) for url in url_list]
                extracted_contents = await asyncio.gather(*tasks, return_exceptions=True)

                # Handle any exceptions from gather
                for i, result in enumerate(extracted_contents):
                    if isinstance(result, Exception):
                        logger.error(f"Failed to extract {url_list[i]}: {result}")
                        extracted_contents[i] = WebContent(
                            url=url_list[i],
                            title="Extraction Failed",
                            content="",
                            markdown="",
                            metadata={"extraction_method": "crawl4ai", "content_length": 0},
                            success=False,
                            error=str(result)
                        )
        except Exception as e:
            logger.error(f"Critical error in web extraction: {e}")
            # Create failed results for all URLs
            extracted_contents = [
                WebContent(
                    url=url,
                    title="Extraction Failed",
                    content="",
                    markdown="",
                    metadata={"extraction_method": "crawl4ai", "content_length": 0},
                    success=False,
                    error=f"Crawler initialization failed: {e}"
                ) for url in url_list
            ]

        extraction_time = time.time() - start_time
        logger.info(f"Content extraction completed in {extraction_time:.2f}s")

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

        if isinstance(urls, str):
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
                "extraction_method": "crawl4ai",
                "message": f"Extracted content from {successful_extractions}/{len(url_list)} URLs"
            }
        )

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
