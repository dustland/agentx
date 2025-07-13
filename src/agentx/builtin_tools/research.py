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
            from crawl4ai import AsyncWebCrawler, AdaptiveCrawler, AdaptiveConfig, CrawlerRunConfig, CacheMode

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

            # Add state persistence for long crawls
            if max_pages > 20:
                config.save_state = True
                config.state_path = f"research_{hash(query)}.json"

            # Perform adaptive crawling following best practices
            logger.info(f"Starting adaptive research for: {query}")
            research_results = []
            final_adaptive = None

            async with AsyncWebCrawler(verbose=False) as crawler:
                # Initialize adaptive crawler with config
                adaptive = AdaptiveCrawler(crawler, config)

                # For multiple URLs, use batch processing for better performance
                if len(urls_to_crawl) > 1:
                    logger.info(f"Using batch processing for {len(urls_to_crawl)} URLs")

                    # Use arun_many for performance with limited URLs to avoid overwhelming
                    batch_urls = urls_to_crawl[:3]  # Limit to 3 URLs for batch processing

                    try:
                        # Batch crawl the initial URLs to get content quickly
                        batch_results = await crawler.arun_many(
                            urls=batch_urls,
                            config=CrawlerRunConfig(
                                cache_mode=CacheMode.BYPASS,
                                page_timeout=30000
                            )
                        )

                        # Process successful batch results first
                        successful_urls = []
                        for result in batch_results:
                            if result.success and result.markdown:
                                successful_urls.append(result.url)

                        logger.info(f"Batch crawl successful for {len(successful_urls)} URLs")

                        # Now use adaptive crawling starting from the most successful URL
                        if successful_urls:
                            best_url = successful_urls[0]  # Use first successful URL
                            logger.info(f"Starting adaptive crawling from: {best_url}")

                            state = await adaptive.digest(
                                start_url=best_url,
                                query=query
                            )
                        else:
                            # Fall back to individual crawling if batch failed
                            state = await adaptive.digest(
                                start_url=urls_to_crawl[0],
                                query=query
                            )

                    except Exception as e:
                        logger.warning(f"Batch processing failed: {e}, falling back to individual crawling")
                        # Fall back to individual crawling
                        state = await adaptive.digest(
                            start_url=urls_to_crawl[0],
                            query=query
                        )
                else:
                    # Single URL - use direct adaptive crawling
                    logger.info(f"Single URL adaptive crawling: {urls_to_crawl[0]}")
                    state = await adaptive.digest(
                        start_url=urls_to_crawl[0],
                        query=query
                    )

                # Get relevant content from the adaptive crawl
                relevant_pages = adaptive.get_relevant_content(top_k=15)
                research_results.extend(relevant_pages)

                logger.info(f"Adaptive crawl completed: {len(state.crawled_urls)} pages, confidence: {adaptive.confidence:.0%}")

                # Export knowledge base
                kb_path = f"research_kb_{hash(query)}.jsonl"
                adaptive.export_knowledge_base(kb_path)
                logger.info(f"Exported knowledge base to {kb_path}")

                final_adaptive = adaptive

            # Process and save results
            saved_files = []
            unique_results = self._deduplicate_results(research_results)

            for idx, result in enumerate(unique_results[:10]):  # Save top 10 results
                filename = await self._save_research_content(result, query, idx)
                if filename:
                    saved_files.append(filename)

            # Generate summary with confidence information
            summary = self._generate_summary(unique_results, query, final_adaptive)

            # Create research result
            research_result = ResearchResult(
                query=query,
                confidence=final_adaptive.confidence if final_adaptive else 0.0,
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

            # Save to workspace
            result = await self.workspace.store_artifact(
                name=filename,
                content=content,
                content_type="text/markdown",
                metadata={
                    "source_url": url,
                    "query": query,
                    "tool": "research_topic",
                    "relevance_score": result.get('score', 0)
                },
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
