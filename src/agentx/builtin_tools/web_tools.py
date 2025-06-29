"""
Web Tools - Opinionated web automation and content extraction.

Built-in integrations:
- Firecrawl: Superior web content extraction (replaces Jina)
- browser-use: AI-first browser automation (better than Playwright for agents)
"""

from ..utils.logger import get_logger
from ..tool.models import Tool, tool, ToolResult
from ..core.exceptions import ConfigurationError
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

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
    
    def __init__(self, firecrawl_api_key: Optional[str] = None):
        super().__init__("web")
        self.firecrawl_api_key = firecrawl_api_key
        self._firecrawl_client = None
        self._browser = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize Firecrawl and browser-use clients."""
        # Initialize Firecrawl
        try:
            from firecrawl import FirecrawlApp
            
            if not self.firecrawl_api_key:
                import os
                self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
            
            if self.firecrawl_api_key:
                self._firecrawl_client = FirecrawlApp(api_key=self.firecrawl_api_key)
                logger.info("Firecrawl client initialized")
            else:
                raise ConfigurationError(
                    "Firecrawl API key not found. The web_search and extract_content tools "
                    "require a Firecrawl API key. Please get a key from https://firecrawl.dev "
                    "and set it as the FIRECRAWL_API_KEY environment variable."
                )
                
        except ImportError:
            logger.warning("Firecrawl not installed. Install with: pip install firecrawl-py")
        except Exception as e:
            logger.error(f"Failed to initialize Firecrawl: {e}")
        
        # Initialize browser-use
        try:
            from browser_use import Browser
            
            self._browser = Browser()
            logger.info("browser-use initialized")
            
        except ImportError:
            logger.warning("browser-use not installed. Install with: pip install browser-use")
        except Exception as e:
            logger.error(f"Failed to initialize browser-use: {e}")
    
    # @tool(
    #     description="Extract clean content from any URL using Firecrawl",
    #     return_description="ToolResult containing extracted web content with title, content, and markdown"
    # )
    # async def extract_content(self, url: str, include_tags: Optional[List[str]] = None, 
    #                         exclude_tags: Optional[List[str]] = None) -> ToolResult:
    #     """
    #     Extract content from a URL using Firecrawl.
    #     
    #     Args:
    #         url: The URL to extract content from (required)
    #         include_tags: HTML tags to include in extraction (optional)
    #         exclude_tags: HTML tags to exclude from extraction (optional)
    #         
    #     Returns:
    #         ToolResult with WebContent containing extracted data
    #     """
    #     if not self._firecrawl_client:
    #         return ToolResult(
    #             success=False,
    #             result=None,
    #             error="Firecrawl client not available"
    #         )
    #     
    #     try:
    #         # Use the correct Firecrawl API call format
    #         result = self._firecrawl_client.scrape_url(
    #             url, 
    #             formats=["markdown", "html"],
    #             include_tags=include_tags or ["title", "meta"],
    #             exclude_tags=exclude_tags or ["nav", "footer", "aside"],
    #             wait_for=2000  # Wait for JS to load
    #         )
    #         
    #         # Handle the ScrapeResponse object (Pydantic model with attributes)
    #         if result.success:
    #             web_content = WebContent(
    #                 url=url,
    #                 title=result.metadata.get("title", "") if result.metadata else "",
    #                 content=result.markdown or "",
    #                 markdown=result.markdown or "",
    #                 metadata=result.metadata or {},
    #                 success=True
    #             )
    #             
    #             return ToolResult(
    #                 success=True,
    #                 result=web_content,
    #                 metadata={"url": url, "extraction_method": "firecrawl"}
    #             )
    #         else:
    #             error_msg = result.error or "Unknown error occurred"
    #             return ToolResult(
    #                 success=False,
    #                 error=f"Firecrawl extraction failed: {error_msg}",
    #                 metadata={"url": url}
    #             )
    #             
    #     except Exception as e:
    #         logger.error(f"Content extraction failed for {url}: {e}")
    #         return ToolResult(
    #             success=False,
    #             result=None,
    #             error=str(e)
    #         )
    
    @tool(
        description="Extract structured data from one or more URLs based on a prompt.",
        return_description="ToolResult containing extracted content and data based on the prompt"
    )
    async def extract_content(self, urls: Union[str, List[str]], prompt: str, 
                            enable_web_search: bool = False, 
                            schema: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        Extract structured data from one or more URLs based on a prompt.
        
        This is the primary content extraction method. It uses an LLM to intelligently 
        extract information from web pages based on your specific instructions.
        
        Args:
            urls: A single URL or a list of URLs to extract content from.
            prompt: CRITICAL: A detailed, natural language prompt describing exactly what to extract. This is not optional.
            enable_web_search: Allow the tool to search the web if the URLs don't contain the answer.
            schema: An optional JSON schema to structure the output.
            
        Returns:
            ToolResult with the extracted data.
        """
        if not self._firecrawl_client:
            return ToolResult(
                success=False,
                result=None,
                error="Firecrawl client not available"
            )
        
        try:
            # Convert single URL to list
            url_list = [urls] if isinstance(urls, str) else urls
            
            # Use Extract API with LLM processing
            result = self._firecrawl_client.extract(
                urls=url_list,
                prompt=prompt,
                schema=schema,
                enable_web_search=enable_web_search
            )
            
            if result.success:
                return ToolResult(
                    success=True,
                    result=result.data,
                    metadata={
                        "urls": url_list,
                        "extraction_method": "firecrawl_extract",
                        "prompt": prompt,
                        "web_search_enabled": enable_web_search
                    }
                )
            else:
                error_msg = result.error or "Unknown error occurred"
                return ToolResult(
                    success=False,
                    error=f"Firecrawl extraction failed: {error_msg}",
                    metadata={"urls": url_list, "prompt": prompt}
                )
                
        except Exception as e:
            logger.error(f"Structured data extraction failed for {urls}: {e}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )

    @tool(
        description="Enhanced content extraction with visual data capture using Firecrawl's advanced features",
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
        if not self._firecrawl_client:
            return ToolResult(
                success=False,
                result=None,
                error="Firecrawl client not available"
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
            extract_result = self._firecrawl_client.extract(
                urls=[url],
                prompt=enhanced_prompt,
                enable_web_search=enable_web_search
            )
            
            visual_data = None
            if capture_screenshot:
                try:
                    # Also capture with screenshot for visual analysis
                    scrape_result = self._firecrawl_client.scrape_url(
                        url,
                        formats=["markdown", "screenshot@fullPage"],
                        wait_for=3000  # Wait for dynamic content to load
                    )
                    
                    if scrape_result.success and hasattr(scrape_result, 'screenshot'):
                        visual_data = {
                            "screenshot_url": scrape_result.screenshot,
                            "markdown_content": scrape_result.markdown
                        }
                except Exception as e:
                    logger.warning(f"Screenshot capture failed for {url}: {e}")
            
            if extract_result.success:
                result_data = extract_result.data
                
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
                        "extraction_method": "firecrawl_enhanced_visual",
                        "screenshot_captured": capture_screenshot and visual_data is not None,
                        "web_search_enabled": enable_web_search
                    }
                )
            else:
                error_msg = extract_result.error or "Unknown error occurred"
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
        description="Crawl multiple pages from a website using Firecrawl",
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
        if not self._firecrawl_client:
            return ToolResult(
                success=False,
                result=None,
                error="Firecrawl client not available"
            )
        
        try:
            result = self._firecrawl_client.crawl_url(
                url,
                limit=limit,
                formats=["markdown"],
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
                    error=f"Firecrawl crawl failed: {error_msg}",
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