"""
Web Tools - Opinionated web automation and content extraction.

Built-in integrations:
- Firecrawl: Superior web content extraction (with fallback)
- requests + BeautifulSoup: Reliable fallback for content extraction
- browser-use: AI-first browser automation (better than Playwright for agents)
"""

from ..utils.logger import get_logger
from ..tool.models import Tool, tool, ToolResult
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
    
    def __init__(self, jina_api_key: Optional[str] = None):
        super().__init__("web")
        self.jina_api_key = jina_api_key
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
        description="Extract clean content from URLs using Jina Reader",
        return_description="ToolResult containing extracted web content with title and markdown"
    )
    async def extract_content(self, urls: Union[str, List[str]], prompt: str = "Extract the main content from this webpage") -> ToolResult:
        """
        Extract clean content from one or more URLs using Jina Reader.
        
        Jina Reader is specifically designed for AI content extraction and handles
        anti-bot protection, JavaScript rendering, and modern web challenges.
        
        Args:
            urls: A single URL or list of URLs to extract content from
            prompt: Description of what content to focus on (optional)
            
        Returns:
            ToolResult with extracted content
        """
        try:
            import requests
            
            # Convert single URL to list
            url_list = [urls] if isinstance(urls, str) else urls
            
            extracted_contents = []
            
            for url in url_list:
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
                        
                        # Add prompt for focused extraction
                        if prompt and prompt != "Extract the main content from this webpage":
                            headers['X-Target-Selector'] = prompt
                            
                    else:
                        # Use free API (with rate limits)
                        jina_url = f"https://r.jina.ai/{url}"
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (compatible; AgentX/1.0)',
                            'Accept': 'text/plain'
                        }
                    
                    response = requests.get(jina_url, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    content = response.text
                    
                    # Extract title from first line if available
                    lines = content.split('\n')
                    title = lines[0].strip() if lines and lines[0].strip() else url
                    
                    # Remove title from content to avoid duplication
                    if len(lines) > 1 and lines[0].strip():
                        content = '\n'.join(lines[1:]).strip()
                    
                    web_content = WebContent(
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
                    
                    extracted_contents.append(web_content)
                    
                except Exception as e:
                    logger.error(f"Jina Reader extraction failed for {url}: {e}")
                    
                    # Add failed extraction to results
                    failed_content = WebContent(
                        url=url,
                        title="",
                        content="",
                        markdown="",
                        metadata={"extraction_method": "jina_reader"},
                        success=False,
                        error=str(e)
                    )
                    extracted_contents.append(failed_content)
            
            # Return single content or list based on input
            if isinstance(urls, str):
                result_data = extracted_contents[0] if extracted_contents else None
            else:
                result_data = extracted_contents
            
            # Check if any extractions succeeded
            success = any(content.success for content in extracted_contents)
            
            return ToolResult(
                success=success,
                result=result_data,
                metadata={
                    "total_urls": len(url_list),
                    "successful_extractions": sum(1 for c in extracted_contents if c.success),
                    "extraction_method": "jina_reader"
                }
            )
            
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return ToolResult(
                success=False,
                error=f"Content extraction failed: {str(e)}",
                metadata={"urls": url_list if 'url_list' in locals() else []}
            )

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

    def _extract_with_jina(self, url: str) -> ToolResult:
        """
        Fallback content extraction using Jina Reader.
        More reliable than Firecrawl for many websites.
        """
        try:
            import requests
            
            # Jina Reader API - free and reliable
            jina_url = f"https://r.jina.ai/{url}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; AgentX/1.0; +https://github.com/agentx)',
                'Accept': 'text/plain'
            }
            
            response = requests.get(jina_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            content = response.text
            
            # Extract title from first line if available
            lines = content.split('\n')
            title = lines[0] if lines else url
            
            web_content = WebContent(
                url=url,
                title=title,
                content=content,
                markdown=content,
                metadata={"extraction_method": "jina_reader"},
                success=True
            )
            
            return ToolResult(
                success=True,
                result=web_content,
                metadata={"url": url, "extraction_method": "jina_reader"}
            )
            
        except Exception as e:
            logger.error(f"Jina Reader extraction failed for {url}: {e}")
            return ToolResult(
                success=False,
                error=f"Jina Reader extraction failed: {str(e)}",
                metadata={"url": url}
            )


# Export main classes and functions
__all__ = [
    "WebTool",
    "WebContent",
    "BrowserAction",
] 