"""
Web Tools - Advanced URL content extraction using Firecrawl.

Supports multiple extraction strategies:
- Markdown: Clean markdown extraction (default)
- HTML: Raw HTML extraction
- Links: Extract all links from the page
- Screenshot: Capture page screenshot

Features:
- Simple API with built-in error handling
- Automatic retry on failures
- Clean markdown output optimized for LLMs
- Taskspace integration for saving extracted content
"""

from ..utils.logger import get_logger
from ..core.tool import Tool, tool, ToolResult
from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass
import time
import os
import re
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path

# Firecrawl imports
try:
    from firecrawl import FirecrawlApp
except ImportError:
    FirecrawlApp = None
    logger = get_logger(__name__)
    logger.error("firecrawl-py is not installed. Please install it with: pip install firecrawl-py")

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
    Advanced web content extraction tool using Firecrawl.

    Provides intelligent content extraction with multiple strategies:
    - Clean markdown extraction optimized for LLMs
    - HTML extraction for full content
    - Link extraction for crawling
    - Screenshot capture
    """

    def __init__(self, project_storage: Optional[Any] = None) -> None:
        super().__init__("web")
        self.project_storage = project_storage
        
        # Initialize Firecrawl with API key from environment
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            logger.warning("FIRECRAWL_API_KEY not found in environment. Web extraction may fail.")
        
        if FirecrawlApp:
            try:
                self.firecrawl = FirecrawlApp(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Firecrawl: {e}")
                self.firecrawl = None
        else:
            self.firecrawl = None

    @tool(  # type: ignore[misc]
        description="Extract content from web URLs using Firecrawl. Supports markdown and HTML extraction with automatic retry on failures.",
        return_description="ToolResult with file paths and content summaries"
    )
    async def extract_urls(
        self,
        urls: Union[str, List[str]],
        formats: List[str] = ["markdown", "html"],
        only_main_content: bool = True,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        wait_for_selector: Optional[str] = None,
        timeout: int = 30000
    ) -> ToolResult:
        """Extract content from URLs using Firecrawl with advanced features."""
        # Convert single URL to list and initialize timing
        url_list = [urls] if isinstance(urls, str) else urls
        start_time = time.time()

        if not self.firecrawl:
            return ToolResult(
                success=False,
                result=None,
                error="Firecrawl is not properly initialized. Please check FIRECRAWL_API_KEY.",
                execution_time=time.time() - start_time
            )

        logger.info(f"Using Firecrawl for web extraction of {len(url_list)} URL(s)")

        extracted_contents: List[WebContent] = []

        for url in url_list:
            try:
                logger.info(f"Extracting from {url} using Firecrawl")
                
                # Prepare scrape options
                scrape_options = {
                    "formats": formats,
                    "onlyMainContent": only_main_content,
                    "timeout": timeout
                }
                
                # Add optional parameters
                if include_tags:
                    scrape_options["includeTags"] = include_tags
                if exclude_tags:
                    scrape_options["excludeTags"] = exclude_tags
                if wait_for_selector:
                    scrape_options["waitFor"] = wait_for_selector
                
                # Scrape the URL with retry logic
                max_retries = 3
                scrape_result = None
                
                for attempt in range(max_retries):
                    try:
                        # Call scrape_url - it returns a dict-like object in latest version
                        scrape_result = self.firecrawl.scrape_url(url, **scrape_options)
                        break  # Success, exit retry loop
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}. Retrying...")
                            time.sleep(2 ** attempt)  # Exponential backoff
                        else:
                            raise  # Re-raise on final attempt
                
                # Check if we got a valid response
                if scrape_result:
                    # Extract content from result
                    content = ""
                    markdown_content = ""
                    title = url
                    
                    # Handle the response based on its type
                    # In latest Firecrawl, scrape_url returns an object with attributes
                    if hasattr(scrape_result, 'markdown'):
                        # Direct attribute access for new API
                        markdown_content = scrape_result.markdown or ""
                        content = markdown_content
                    elif isinstance(scrape_result, dict) and 'markdown' in scrape_result:
                        # Dict-like response (older API or when returned as dict)
                        markdown_content = scrape_result['markdown'] or ""
                        content = markdown_content
                    
                    # Try HTML if no markdown
                    if not content:
                        if hasattr(scrape_result, 'html'):
                            content = scrape_result.html or ""
                        elif isinstance(scrape_result, dict) and 'html' in scrape_result:
                            content = scrape_result['html'] or ""
                    
                    # Extract metadata
                    metadata = {}
                    if hasattr(scrape_result, 'metadata'):
                        metadata = scrape_result.metadata or {}
                    elif isinstance(scrape_result, dict) and 'metadata' in scrape_result:
                        metadata = scrape_result['metadata'] or {}
                    
                    title = metadata.get('title', url) if metadata else url
                    
                    # Clean up content
                    if content and content.strip():
                        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content.strip())
                        
                        extracted_contents.append(WebContent(
                            url=url,
                            title=title.strip() if isinstance(title, str) else url,
                            content=content,
                            markdown=markdown_content or content,
                            metadata={
                                "extraction_method": "firecrawl",
                                "content_length": len(content),
                                "word_count": len(content.split()),
                                "formats_used": formats,
                                "only_main_content": only_main_content,
                                **(metadata if 'metadata' in scrape_result else {})
                            },
                            success=True
                        ))
                        logger.info(f"Successfully extracted {len(content)} characters from {url}")
                    else:
                        raise Exception("No content extracted from response")
                else:
                    error_msg = scrape_result.get('error', 'Unknown error') if scrape_result else 'No response'
                    raise Exception(f"Firecrawl scrape failed: {error_msg}")
                    
            except Exception as e:
                logger.error(f"Firecrawl extraction failed for {url}: {e}")
                extracted_contents.append(WebContent(
                    url=url,
                    title="Extraction Failed",
                    content="",
                    markdown="",
                    metadata={
                        "extraction_method": "firecrawl_failed",
                        "content_length": 0,
                        "error_details": str(e)
                    },
                    success=False,
                    error=str(e)
                ))

        extraction_time = time.time() - start_time
        return await self._process_extracted_contents(
            extracted_contents, url_list, extraction_time, "firecrawl"
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

            # Save to project storage if available and extraction was successful
            if self.project_storage and content_obj.success and content_obj.content:
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

                    # Save to project storage
                    result = await self.project_storage.store_artifact(
                        name=filename,
                        content=content_with_header,
                        content_type="text/markdown",
                        commit_message=f"Extracted content from {content_obj.url}"
                    )

                    if result.success:
                        saved_files.append(filename)
                        logger.info(f"Saved content to {filename}")
                except Exception as e:
                    logger.error(f"Failed to save content to project storage: {e}")

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
                "project_storage_integration": self.project_storage is not None,
                "extraction_method": method,
                "message": f"Extracted content from {successful_extractions}/{len(url_list)} URLs"
            }
        )