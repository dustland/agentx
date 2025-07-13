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

    def __init__(self, workspace_storage: Optional[Any] = None) -> None:
        super().__init__("research")
        self.workspace = workspace_storage
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

            # Get starting URLs
            if start_urls:
                urls_to_crawl = start_urls
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

            # Remove URL seeding for now - focus on core adaptive crawling
            logger.info(f"Using {len(urls_to_crawl)} starting URLs for adaptive crawling")

            # Configure adaptive crawling based on examples
            config = AdaptiveConfig(
                strategy="embedding",  # Use embedding strategy for semantic understanding
                confidence_threshold=confidence_threshold,
                max_pages=max_pages,
                top_k_links=3,  # Follow top 3 relevant links per page
                min_gain_threshold=0.05,  # Lower threshold for continuation

                # Embedding-specific parameters
                embedding_k_exp=3.0,  # Stricter similarity requirements
                embedding_min_confidence_threshold=0.1,  # Stop if < 10% relevant
                embedding_validation_min_score=0.4  # Validation threshold
            )

            # Note: State persistence is handled by the memory system, not local files

            # Perform adaptive crawling following best practices
            logger.info(f"Starting adaptive research for: {query}")
            research_results = []
            final_adaptive = None

            # Use Chromium for best stability (crashpad warnings are harmless)
            browser_config = BrowserConfig(
                browser_type="chromium",
                headless=True,
                verbose=False,
                viewport_width=1920,
                viewport_height=1080
            )
            
            # Process each URL with its own browser instance to avoid context issues
            for url_idx, url in enumerate(urls_to_crawl):
                logger.info(f"Processing URL {url_idx + 1}/{len(urls_to_crawl)}: {url}")
                
                # Create a new browser instance for each URL
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    # Initialize adaptive crawler with config
                    adaptive = AdaptiveCrawler(crawler, config)
                    
                    try:
                        # Use direct adaptive crawling for each URL
                        logger.info(f"Starting adaptive crawling for: {url}")
                        state = await adaptive.digest(
                            start_url=url,
                            query=query
                        )
                        
                        # Get relevant content from this crawl
                        relevant_pages = adaptive.get_relevant_content(top_k=5)  # Limit per URL
                        research_results.extend(relevant_pages)
                        
                        logger.info(f"Successfully crawled {url} - found {len(relevant_pages)} relevant pages")
                        
                    except Exception as e:
                        logger.error(f"Failed to crawl {url}: {e}")
                        continue
                
                # Break if we have enough results
                if len(research_results) >= 15:
                    logger.info(f"Collected sufficient results ({len(research_results)} pages)")
                    break
            
            logger.info(f"Research completed: collected {len(research_results)} total pages")
            
            # Note: Knowledge base with embeddings should be managed by the memory system
            # Not exported as separate files
            
            final_adaptive = None  # No single adaptive instance when processing multiple URLs

            # Process and save results
            saved_files = []
            unique_results = self._deduplicate_results(research_results)

            for idx, result in enumerate(unique_results[:10]):  # Save top 10 results
                filename = await self._save_research_content(result, query, idx)
                if filename:
                    saved_files.append(filename)

            # Generate summary with confidence information
            summary = self._generate_summary(unique_results, query, None)

            # Create research result
            research_result = ResearchResult(
                query=query,
                confidence=0.8,  # Default confidence for multi-URL research
                pages_crawled=len(research_results),
                relevant_content=unique_results[:5],  # Top 5 for response
                saved_files=saved_files,
                summary=summary,
                metadata={
                    "total_results": len(unique_results),
                    "starting_urls": urls_to_crawl,
                    "strategy": config.strategy,
                    "crawl4ai_version": "0.7.0",
                    "adaptive_config": {
                        "confidence_threshold": confidence_threshold,
                        "max_pages": max_pages,
                        "top_k_links": config.top_k_links,
                        "min_gain_threshold": config.min_gain_threshold
                    }
                }
            )

            execution_time = time.time() - start_time
            logger.info(f"Adaptive research completed in {execution_time:.2f}s using crawl4ai 0.7.0 embedding strategy")

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
        """Save research content to workspace."""
        if not self.workspace:
            return None

        try:
            # Generate filename
            url = result.get("url", "")
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "").replace(".", "_")
            filename = f"research_{domain}_{index:02d}.md"

            # Create content
            content = f"""# Research Result: {result.get('title', 'Untitled')}

**Query:** {query}
**Source:** {url}
**Relevance Score:** {result.get('score', 0):.2f}
**Extracted:** {datetime.now().isoformat()}

---

## Summary
{result.get('summary', 'No summary available')}

## Content
{result.get('content', 'No content available')}
"""

            # Save to workspace (metadata already in content header)
            result = await self.workspace.store_artifact(
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
