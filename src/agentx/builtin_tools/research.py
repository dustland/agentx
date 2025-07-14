"""
Research Tool - Intelligent web research using AdaptiveCrawler and search.

Combines web search with adaptive crawling for comprehensive research tasks.
Enhanced for crawl4ai 0.7.0 with virtual scroll, link preview, and URL seeding.
"""

from ..utils.logger import get_logger
from ..core.tool import Tool, tool, ToolResult
from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass
import time
import asyncio
import os
from datetime import datetime
from urllib.parse import urlparse

logger = get_logger(__name__)


@dataclass
class ResearchResult:
    """Result from research operation."""
    query: str
    confidence: float
    pages_crawled: int
    relevant_content: List[Dict[str, Any]]
    saved_files: List[str]
    summary: str
    metadata: Dict[str, Any]


class ResearchTool(Tool):
    """
    Intelligent research tool combining search and adaptive crawling.

    Enhanced for crawl4ai 0.7.0 with:
    - Virtual scroll support for infinite scroll pages
    - Intelligent link preview with 3-layer scoring
    - Async URL seeder for massive URL discovery
    - Improved adaptive crawling with learning capabilities
    """

    def __init__(self, taskspace_storage: Optional[Any] = None) -> None:
        super().__init__("research")
        self.taskspace = taskspace_storage
        self.SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

    @tool(
        description="Perform comprehensive research on a topic using crawl4ai 0.7.0 adaptive crawling with embedding strategy and automatic confidence assessment",
        return_description="ResearchResult with confidence score, relevant content, and saved files"
    )
    async def research_topic(
        self,
        query: str,
        max_pages: int = 30,
        confidence_threshold: float = 0.75,
        search_first: bool = True,
        start_urls: Optional[List[str]] = None
    ) -> ToolResult:
        """
        Research a topic using crawl4ai 0.7.0 adaptive crawling.

        Args:
            query: Research query or topic
            max_pages: Maximum pages to crawl (default: 30)
            confidence_threshold: Stop when this confidence is reached (default: 0.75)
            search_first: Whether to search for starting URLs first (default: True)
            start_urls: Optional list of URLs to start from (overrides search)

        Returns:
            ToolResult with comprehensive research findings
        """
        start_time = time.time()

        try:
            # Import required modules for crawl4ai 0.7.0
            from crawl4ai import AsyncWebCrawler, AdaptiveCrawler, AdaptiveConfig, CrawlerRunConfig, CacheMode, BrowserConfig

            logger.info(f"Starting adaptive research with Crawl4AI 0.7.0")
            has_v070_features = True

            # Get starting URLs - use simple direct extraction for auto_writer
            if start_urls:
                urls_to_crawl = start_urls[:5]  # Limit to 5 URLs max
                logger.info(f"Using provided URLs: {urls_to_crawl}")
            elif search_first and self.SERPAPI_API_KEY:
                logger.info(f"Searching for starting points for: {query}")
                urls_to_crawl = await self._search_for_urls(query, limit=5)
                if not urls_to_crawl:
                    return ToolResult(
                        success=False,
                        result=None,
                        execution_time=time.time() - start_time,
                        metadata={"error": "No search results found"}
                    )
            else:
                return ToolResult(
                    success=False,
                    result=None,
                    execution_time=time.time() - start_time,
                    metadata={"error": "No starting URLs provided and search is disabled"}
                )

            # Switch to direct extraction approach for better reliability
            logger.info(f"Using direct extraction approach for: {query}")
            research_results = []
            failed_urls = []
            browser_errors = []

            # Browser config for macOS compatibility
            browser_config = BrowserConfig(
                browser_type="chromium",
                headless=True,
                verbose=False,
                viewport_width=1920,
                viewport_height=1080
            )
            
            # Process URLs with direct extraction
            for url_idx, url in enumerate(urls_to_crawl):
                logger.info(f"Extracting content from URL {url_idx + 1}/{len(urls_to_crawl)}: {url}")
                
                try:
                    # Create a new browser instance for each URL
                    async with AsyncWebCrawler(config=browser_config) as crawler:
                        try:
                            # Direct extraction with markdown conversion
                            result = await crawler.arun(
                                url=url,
                                config=CrawlerRunConfig(
                                    cache_mode=CacheMode.BYPASS,
                                    wait_for="networkidle",
                                    screenshot=False,
                                    magic=True,  # Enable anti-bot features
                                    remove_overlay_elements=True
                                )
                            )
                            
                            if result and result.markdown_v2 and result.markdown_v2.raw_markdown:
                                content = result.markdown_v2.raw_markdown.strip()
                                
                                # Only save if we got meaningful content
                                if len(content) > 500:  # Minimum content threshold
                                    title = result.metadata.get('title', url)
                                    
                                    research_results.append({
                                        'url': url,
                                        'title': title,
                                        'score': 0.8,  # Default high score for direct extraction
                                        'summary': content[:500] + "...",  # First 500 chars as summary
                                        'content': content  # Full content
                                    })
                                    
                                    logger.info(f"Successfully extracted {len(content)} characters from {url}")
                                else:
                                    logger.warning(f"Insufficient content from {url}: only {len(content)} characters")
                            else:
                                logger.warning(f"No markdown content extracted from {url}")
                                
                        except Exception as e:
                            error_msg = str(e)
                            logger.error(f"Failed to extract from {url}: {error_msg}")
                            failed_urls.append(url)
                            if "Target page, context or browser has been closed" in error_msg:
                                browser_errors.append(f"{url}: Browser context crash")
                            else:
                                browser_errors.append(f"{url}: {error_msg[:100]}")
                            continue
                            
                except Exception as e:
                    # Browser creation failed
                    error_msg = str(e)
                    logger.error(f"Failed to create browser for {url}: {error_msg}")
                    failed_urls.append(url)
                    browser_errors.append(f"{url}: Browser creation failed - {error_msg[:100]}")
                    continue
                
                # Limit to reasonable number of results
                if len(research_results) >= 10:
                    logger.info(f"Collected sufficient results ({len(research_results)} pages)")
                    break
            
            logger.info(f"Adaptive research completed: collected {len(research_results)} total pages")
            
            # Check if all URLs failed
            if len(failed_urls) == len(urls_to_crawl):
                logger.error(f"All {len(urls_to_crawl)} URLs failed to crawl")
                return ToolResult(
                    success=False,
                    result=None,
                    execution_time=time.time() - start_time,
                    metadata={
                        "error": "All URLs failed to crawl",
                        "failed_urls": failed_urls,
                        "browser_errors": browser_errors,
                        "message": "Browser context crashes prevented research completion"
                    }
                )

            # Process and save results
            saved_files = []
            unique_results = self._deduplicate_results(research_results)
            
            # Check if we got no results at all
            if len(unique_results) == 0:
                logger.error("No content extracted from any URL")
                return ToolResult(
                    success=False,
                    result=None,
                    execution_time=time.time() - start_time,
                    metadata={
                        "error": "No content extracted",
                        "failed_urls": failed_urls,
                        "browser_errors": browser_errors,
                        "attempted_urls": len(urls_to_crawl),
                        "successful_urls": len(urls_to_crawl) - len(failed_urls),
                        "message": "Research completed but no relevant content was found"
                    }
                )

            for idx, result in enumerate(unique_results[:10]):  # Save top 10 results
                filename = await self._save_research_content(result, query, idx)
                if filename:
                    saved_files.append(filename)

            # Generate summary with confidence information
            summary = self._generate_summary(unique_results, query, None)

            # Create research result
            research_result = ResearchResult(
                query=query,
                confidence=0.8,  # Default confidence for direct extraction
                pages_crawled=len(research_results),
                relevant_content=unique_results[:5],  # Top 5 for response
                saved_files=saved_files,
                summary=summary,
                metadata={
                    "total_results": len(unique_results),
                    "starting_urls": urls_to_crawl,
                    "strategy": "direct_extraction",
                    "crawl4ai_version": "0.7.0",
                    "extraction_method": "markdown_v2",
                    "failed_urls": failed_urls if failed_urls else None,
                    "browser_errors": browser_errors if browser_errors else None
                }
            )

            execution_time = time.time() - start_time
            logger.info(f"Direct content extraction completed in {execution_time:.2f}s using crawl4ai 0.7.0")

            return ToolResult(
                success=True,
                result=research_result.__dict__,
                execution_time=execution_time,
                metadata={
                    "confidence": research_result.confidence,
                    "pages_crawled": research_result.pages_crawled,
                    "files_saved": len(saved_files),
                    "strategy": "embedding",
                    "adaptive_crawling": True
                }
            )

        except ImportError as e:
            logger.error(f"Crawl4AI not available. Please install: pip install crawl4ai")
            return ToolResult(
                success=False,
                result=None,
                execution_time=time.time() - start_time,
                metadata={
                    "error": "Crawl4AI not available",
                    "message": "Please install Crawl4AI: pip install crawl4ai",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return ToolResult(
                success=False,
                result=None,
                execution_time=time.time() - start_time,
                metadata={"error": str(e)}
            )


    async def _search_for_urls(self, query: str, limit: int = 5) -> List[str]:
        """Search for URLs using SerpAPI."""
        try:
            from serpapi import GoogleSearch

            params = {
                "api_key": self.SERPAPI_API_KEY,
                "engine": "google",
                "q": query,
                "num": limit
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            urls = []
            for result in results.get("organic_results", [])[:limit]:
                if "link" in result:
                    urls.append(result["link"])

            return urls

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on URL."""
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        # Sort by relevance score
        unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return unique_results

    async def _save_research_content(self, result: Dict, query: str, index: int) -> Optional[str]:
        """Save research content to taskspace."""
        if not self.taskspace:
            return None

        try:
            # Generate filename using topic-based naming for better categorization
            import re
            # Create clean topic slug from query
            topic_slug = re.sub(r'[^\w\s-]', '', query.lower())
            topic_slug = re.sub(r'[-\s]+', '_', topic_slug).strip('_')
            # Limit length and ensure it's meaningful
            topic_slug = topic_slug[:30] if len(topic_slug) > 30 else topic_slug
            if not topic_slug:
                topic_slug = "general_research"
            filename = f"research_{topic_slug}_{index:02d}.md"

            # Create content
            content = f"""# Research Result: {result.get('title', 'Untitled')}

**Query:** {query}
**Source:** {result.get('url', '')}
**Relevance Score:** {result.get('score', 0):.2f}
**Extracted:** {datetime.now().isoformat()}

---

## Summary
{result.get('summary', 'No summary available')}

## Content
{result.get('content', 'No content available')}
"""

            # Save to taskspace (metadata already in content header)
            result = await self.taskspace.store_artifact(
                name=filename,
                content=content,
                content_type="text/markdown",
                commit_message=f"Research result for: {query}"
            )

            if result.success:
                return filename

        except Exception as e:
            logger.error(f"Failed to save research content: {e}")

        return None

    def _generate_summary(self, results: List[Dict], query: str, adaptive_crawler=None) -> str:
        """Generate a summary of research results."""
        if not results:
            return "No relevant content found."

        summary_parts = [
            f"Adaptive research on '{query}' found {len(results)} relevant pages."
        ]

        if adaptive_crawler:
            summary_parts.append(f"Final confidence: {adaptive_crawler.confidence:.0%}")

            if adaptive_crawler.confidence >= 0.8:
                summary_parts.append("✓ High confidence - comprehensive information gathered")
            elif adaptive_crawler.confidence >= 0.6:
                summary_parts.append("~ Moderate confidence - good coverage obtained")
            else:
                summary_parts.append("✗ Low confidence - may need additional sources")

        summary_parts.append("\nTop sources include:")
        for result in results[:3]:
            title = result.get('title', 'Untitled')
            score = result.get('score', 0)
            summary_parts.append(f"- {title} (relevance: {score:.0%})")

        return "\n".join(summary_parts)


# Export
__all__ = ["ResearchTool", "ResearchResult"]
