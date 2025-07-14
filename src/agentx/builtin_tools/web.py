"""
Web Tools - Advanced URL content extraction using crawl4ai 0.7.0.

Supports multiple extraction strategies:
- Markdown: Clean markdown extraction (default)
- Structured: Schema-based structured data extraction
- CSS: Targeted extraction using CSS selectors

Features:
- Virtual scroll for infinite scroll pages
- Custom JavaScript execution
- Flexible extraction strategies
- Taskspace integration for saving extracted content
"""

from ..utils.logger import get_logger
from ..core.tool import Tool, tool, ToolResult
from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass
import time
import asyncio
import re
from urllib.parse import urlparse

# Crawl4AI imports
from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    BrowserConfig,
    CacheMode,
    VirtualScrollConfig,
    DefaultMarkdownGenerator,
    JsonCssExtractionStrategy,
    LLMExtractionStrategy
)
try:
    from crawl4ai.models import CrawlResultContainer, CrawlResult
except ImportError:
    # Fallback for older versions
    CrawlResultContainer = None
    CrawlResult = None
from datetime import datetime
import os
from pathlib import Path

logger = get_logger(__name__)

@dataclass
class WebContent:
    """Content extracted from a web page."""
    url: str
    title: str
    content: str
    markdown: str
    metadata: Dict[str, Any]
    success: bool = True
    error: Optional[str] = None

class WebTool(Tool):
    """
    Advanced web content extraction tool using crawl4ai 0.7.0.

    Provides intelligent content extraction with multiple strategies:
    - CSS selector-based targeted extraction
    - Virtual scroll for dynamic content
    - Custom JavaScript execution
    """

    def __init__(self, taskspace_storage: Optional[Any] = None) -> None:
        super().__init__("web")
        self.taskspace = taskspace_storage

    @tool(  # type: ignore[misc]
        description="Extract content from web URLs using advanced crawling. Supports markdown, structured extraction via CSS selectors, and virtual scroll for infinite scroll pages.",
        return_description="ToolResult with file paths and content summaries"
    )
    async def extract_urls(
        self,
        urls: Union[str, List[str]],
        extraction_type: str = "markdown",
        schema: Optional[Dict[str, Any]] = None,
        css_selector: Optional[str] = None,
        regex_patterns: Optional[List[str]] = None,
        enable_virtual_scroll: bool = False,
        enable_pdf: bool = False,
        js_code: Optional[str] = None,
        wait_for: Optional[str] = None
    ) -> ToolResult:
        """Extract content from URLs using Crawl4AI with advanced features."""
        # Convert single URL to list and initialize timing
        url_list = [urls] if isinstance(urls, str) else urls
        start_time = time.time()

        logger.info("Using Crawl4AI for web extraction")

        return await self._extract_with_crawl4ai_v070(
            url_list, start_time, extraction_type, schema, css_selector, regex_patterns,
            enable_virtual_scroll, enable_pdf, js_code, wait_for, True
        )

    async def _process_extracted_contents(self, extracted_contents: List[WebContent], url_list: List[str],
                                        extraction_time: float, method: str) -> ToolResult:
        """Process extracted contents into final result format."""
        content_summaries = []
        saved_files = []

        for i, content_obj in enumerate(extracted_contents):
            summary = {
                "url": content_obj.url,
                "title": content_obj.title,
                "content_length": len(content_obj.content) if content_obj.content else 0,
                "extraction_successful": content_obj.success,
                "error": content_obj.error,
                "metadata": content_obj.metadata
            }
            content_summaries.append(summary)

            # Save to taskspace if available and extraction was successful
            if self.taskspace and content_obj.success and content_obj.content:
                try:
                    # Create safe filename from URL
                    parsed_url = urlparse(content_obj.url)
                    hostname = parsed_url.netloc.replace('www.', '')
                    safe_hostname = re.sub(r'[^a-zA-Z0-9\-]', '_', hostname)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"web_extract_{safe_hostname}_{timestamp}_{i}.md"

                    # Enhanced metadata
                    file_metadata = {
                        "url": content_obj.url,
                        "title": content_obj.title,
                        "extraction_method": method,
                        "extraction_time": datetime.now().isoformat(),
                        "content_length": len(content_obj.content),
                        **content_obj.metadata
                    }

                    # Create content with metadata header
                    content_with_header = f"""# {content_obj.title}

**URL:** {content_obj.url}
**Extracted:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Method:** {method}

---

{content_obj.content}
"""

                    # Save to taskspace (no separate metadata file needed - it's in the content)
                    result = await self.taskspace.store_artifact(
                        name=filename,
                        content=content_with_header,
                        content_type="text/markdown",
                        commit_message=f"Extracted content from {content_obj.url}"
                    )

                    if result.success:
                        saved_files.append(filename)
                        logger.info(f"Saved content to {filename}")
                except Exception as e:
                    logger.error(f"Failed to save content to taskspace: {e}")

        # Return results
        successful_extractions = sum(1 for s in content_summaries if s["extraction_successful"])

        if len(url_list) == 1:
            result_data: Union[Dict[str, Any], List[Dict[str, Any]], None] = content_summaries[0] if content_summaries else None
        else:
            result_data = content_summaries

        return ToolResult(  # type: ignore[no-untyped-call]
            success=successful_extractions > 0,
            result=result_data,
            execution_time=extraction_time,
            metadata={
                "total_urls": len(url_list),
                "successful_extractions": successful_extractions,
                "failed_extractions": len(url_list) - successful_extractions,
                "saved_files": saved_files,
                "taskspace_integration": self.taskspace is not None,
                "extraction_method": method,
                "message": f"Extracted content from {successful_extractions}/{len(url_list)} URLs"
            }
        )

    async def _extract_with_crawl4ai_v070(
        self,
        url_list: List[str],
        start_time: float,
        extraction_type: str,
        schema: Optional[Dict[str, Any]],
        css_selector: Optional[str],
        regex_patterns: Optional[List[str]],
        enable_virtual_scroll: bool,
        enable_pdf: bool,
        js_code: Optional[str],
        wait_for: Optional[str],
        has_v070_features: bool
    ) -> ToolResult:
        """Extract content using crawl4ai 0.7.0 with proper extraction strategies."""
        # Check for PDF support
        has_pdf_support = False
        try:
            from crawl4ai.processors.pdf import PDFCrawlerStrategy
            has_pdf_support = True
        except ImportError:
            pass

        logger.info(f"Processing {len(url_list)} URL(s) with crawl4ai 0.7.0 - extraction type: {extraction_type}")

        # Configure extraction strategy based on type
        extraction_strategy = None
        if extraction_type == "structured" and schema:
            extraction_strategy = JsonCssExtractionStrategy(schema)
            logger.info("Using JsonCssExtractionStrategy for structured extraction")
        elif extraction_type == "css" and css_selector:
            # Create simple schema for CSS selector
            simple_schema = {
                "name": "CSS Extraction",
                "baseSelector": css_selector,
                "fields": [
                    {"name": "content", "selector": css_selector, "type": "text"}
                ]
            }
            extraction_strategy = JsonCssExtractionStrategy(simple_schema)
            logger.info(f"Using CSS selector extraction: {css_selector}")
        elif extraction_type == "regex" and regex_patterns:
            # Note: RegexExtractionStrategy may not be available in all versions
            logger.warning("Regex extraction not implemented, falling back to markdown")
            extraction_type = "markdown"

        # Browser configuration with minimal flags for macOS compatibility
        browser_config = BrowserConfig(
            browser_type="chromium",
            headless=True,
            viewport_width=1920,
            viewport_height=1080,
            verbose=False
        )

        extracted_contents: List[WebContent] = []

        # Create a single browser instance and reuse it
        async with AsyncWebCrawler(config=browser_config) as crawler:
            # Process each URL with the same browser instance
            for url in url_list:
                try:
                    logger.info(f"Extracting from {url} using {extraction_type} strategy")

                    # Build run configuration - only use supported parameters
                    run_config = CrawlerRunConfig(
                        cache_mode=CacheMode.BYPASS,
                        screenshot=False,
                        verbose=False
                    )

                    if extraction_strategy:
                        run_config.extraction_strategy = extraction_strategy

                    # Add PDF extraction if enabled
                    if enable_pdf and has_pdf_support:
                        try:
                            from crawl4ai.processors.pdf import PDFCrawlerStrategy
                            run_config.pdf_crawler_strategy = PDFCrawlerStrategy()
                            logger.info("PDF extraction enabled")
                        except ImportError:
                            logger.warning("PDF extraction not available in this version")

                    # Add JavaScript and wait conditions if specified
                    if js_code:
                        run_config.js_code = js_code
                    if wait_for:
                        run_config.wait_for = wait_for

                    # Add virtual scroll if enabled and available
                    if enable_virtual_scroll and has_v070_features:
                        try:
                            scroll_config = VirtualScrollConfig(
                                container_selector="body",
                                scroll_count=5,
                                scroll_by="container_height",
                                wait_after_scroll=0.5
                            )
                            run_config.virtual_scroll_config = scroll_config
                            logger.info("Virtual scroll enabled with intelligent content detection")
                        except Exception as e:
                            logger.warning(f"Virtual scroll configuration failed: {e}")

                    # Execute crawling with retry logic for browser issues
                    crawl_result = None
                    max_retries = 2
                    for attempt in range(max_retries + 1):
                        try:
                            crawl_result = await crawler.arun(url=url, config=run_config)
                            break  # Success, exit retry loop
                        except Exception as e:
                            if attempt < max_retries and any(phrase in str(e) for phrase in [
                                "Target page, context or browser has been closed",
                                "BrowserContext",
                                "Page.goto"
                            ]):
                                logger.warning(f"Browser issue on attempt {attempt + 1}, retrying: {e}")
                                await asyncio.sleep(1.0)  # Brief pause before retry
                                continue
                            else:
                                raise  # Re-raise if not retryable or max retries exceeded

                    # Check if crawling succeeded
                    if crawl_result is None:
                        raise Exception("Crawling failed after all retry attempts")
                        
                    # Type assertion to help static analyzers understand the interface
                    # CrawlResultContainer delegates all attributes to CrawlResult
                    success: bool = getattr(crawl_result, 'success', False)
                    if success:
                        # Extract content based on strategy using correct API
                        content = ""
                        title = url

                        # Safe attribute access using getattr to avoid type issues
                        extracted_content = getattr(crawl_result, 'extracted_content', None)
                        markdown_content = getattr(crawl_result, 'markdown', None)
                        cleaned_html = getattr(crawl_result, 'cleaned_html', None)
                        metadata = getattr(crawl_result, 'metadata', None)

                        if extraction_strategy and extracted_content:
                            # Structured extraction - extracted_content is JSON string
                            content = extracted_content
                            title = f"Structured data from {url}"
                        elif markdown_content:
                            # Markdown extraction - markdown has the content
                            content = str(markdown_content)
                            if metadata:
                                title = metadata.get('title', url)
                            else:
                                title = url
                        elif cleaned_html:
                            # Fallback to cleaned HTML
                            content = cleaned_html
                            title = f"Content from {url}"
                        else:
                            logger.warning(f"No extractable content found for {url}")
                            continue

                        if content and content.strip():
                            # Clean up content
                            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content.strip())

                            extracted_contents.append(WebContent(
                                url=url,
                                title=title.strip() if isinstance(title, str) else url,
                                content=content,
                                markdown=content,
                                metadata={
                                    "extraction_method": f"crawl4ai_v070_{extraction_type}",
                                    "extraction_type": extraction_type,
                                    "content_length": len(content),
                                    "word_count": len(content.split()),
                                    "has_structured_data": extraction_strategy is not None,
                                    "virtual_scroll_enabled": enable_virtual_scroll,
                                    **(metadata or {})
                                },
                                success=True
                            ))
                            logger.info(f"Successfully extracted {len(content)} characters from {url}")
                        else:
                            raise Exception("No content extracted after processing")
                    else:
                        error_msg = getattr(crawl_result, 'error_message', None) or 'Unknown error'
                        raise Exception(f"Crawl failed: {error_msg}")

                except Exception as e:
                    logger.error(f"Crawl4AI extraction failed for {url}: {e}")
                    extracted_contents.append(WebContent(
                        url=url,
                        title="Extraction Failed",
                        content="",
                        markdown="",
                        metadata={
                            "extraction_method": "crawl4ai_failed",
                            "extraction_type": extraction_type,
                            "content_length": 0,
                            "error_details": str(e)
                        },
                        success=False,
                        error=str(e)
                    ))

        extraction_time = time.time() - start_time
        return await self._process_extracted_contents(
            extracted_contents, url_list, extraction_time,
            f"crawl4ai_v070_{extraction_type}"
        )
