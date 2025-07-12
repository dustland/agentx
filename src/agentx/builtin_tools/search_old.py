"""
Search Tools - Web search capabilities using SerpAPI.

Built-in integration with SerpAPI for comprehensive web search across
multiple search engines (Google, Bing, DuckDuckGo, etc.).
"""

import asyncio
import time
from ..utils.logger import get_logger
from ..core.tool import Tool, tool, ToolResult
from ..search.serpapi_backend import SerpAPIBackend
from ..search.interfaces import SearchEngine
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """Individual search result."""
    title: str
    url: str
    snippet: str
    position: int
    relevance_score: float
    language: str = "en"
    date: Optional[str] = None
    displayed_link: Optional[str] = None
    summary: Optional[str] = None


class SearchTool(Tool):
    """
    Web search tool using SerpAPI.

    Provides access to multiple search engines including Google, Bing,
    DuckDuckGo, Yahoo, Baidu, and Yandex through a unified interface.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__("search")
        self.api_key = api_key
        self._backend = None
        self._init_backend()

    def _init_backend(self):
        """Initialize SerpAPI backend."""
        try:
            self._backend = SerpAPIBackend(self.api_key)
            logger.info("SerpAPI search backend initialized")
        except ValueError as e:
            logger.error(f"Failed to initialize SerpAPI backend: {e}")
        except Exception as e:
            logger.error(f"Unexpected error initializing search backend: {e}")

    @tool(
        description="Search the web using Google, Bing, DuckDuckGo or other search engines. Supports multiple queries in parallel for better performance.",
        return_description="ToolResult containing search results with titles, URLs, and snippets"
    )
    async def web_search(self, queries: Union[str, List[str]], engine: str = "google",
                        max_results: int = 10, country: str = "us",
                        language: str = "en") -> ToolResult:
        """
        Search the web using various search engines. Supports multiple queries in parallel.

        Args:
            queries: Single search query or list of queries to execute in parallel (required)
            engine: Search engine to use - google, bing, duckduckgo, yahoo, baidu, yandex (default: google)
            max_results: Maximum number of results per query, max 20 (default: 10)
            country: Country code for localized results (default: us)
            language: Language code for results (default: en)

        Returns:
            ToolResult containing search results and metadata
        """
        if not self._backend:
            return ToolResult(
                success=False,
                result=None,
                error="Search backend not available. Check SERPAPI_KEY environment variable."
            )

        try:
            # Convert single query to list for uniform processing
            query_list = [queries] if isinstance(queries, str) else queries

            logger.info(f"Starting parallel search for {len(query_list)} queries...")
            start_time = time.time()

            async def search_single_query(query: str):
                """Execute a single search query."""
                try:
                    response = await self._backend.search(
                        query=query,
                        engine=engine,
                        max_results=min(max_results, 20),  # Cap at 20
                        country=country,
                        language=language
                    )

                    if response.success:
                        # Convert to our SearchResult format
                        search_results = [
                            SearchResult(
                                title=result.title,
                                url=result.url,
                                snippet=result.snippet,
                                position=result.position,
                                relevance_score=result.relevance_score,
                                language=result.language,
                                date=result.date,
                                displayed_link=result.displayed_link,
                                summary=result.summary
                            )
                            for result in response.results
                        ]

                        return {
                            "query": query,
                            "success": True,
                            "results": search_results,
                            "total_results": response.total_results,
                            "response_time": response.response_time,
                            "timestamp": response.timestamp
                        }
                    else:
                        return {
                            "query": query,
                            "success": False,
                            "error": response.error or "Search failed",
                            "response_time": response.response_time
                        }

                except Exception as e:
                    logger.error(f"Search failed for query '{query}': {e}")
                    return {
                        "query": query,
                        "success": False,
                        "error": str(e)
                    }

            # Execute all queries in parallel
            search_tasks = [search_single_query(query) for query in query_list]
            results = await asyncio.gather(*search_tasks, return_exceptions=True)

            total_time = time.time() - start_time
            logger.info(f"Parallel search completed in {total_time:.2f}s for {len(query_list)} queries")

            # Process results
            successful_results = []
            failed_queries = []
            all_search_results = []
            total_search_results = 0

            for result in results:
                if isinstance(result, Exception):
                    failed_queries.append({"error": str(result)})
                    continue

                if result["success"]:
                    successful_results.append(result)
                    all_search_results.extend(result["results"])
                    total_search_results += result["total_results"]
                else:
                    failed_queries.append(result)

            # Determine overall success
            overall_success = len(successful_results) > 0

            # Return results
            if isinstance(queries, str):
                # Single query case - return the results directly
                if successful_results:
                    result_data = successful_results[0]["results"]
                else:
                    result_data = None
            else:
                # Multiple queries case - return grouped results
                result_data = {
                    "queries": successful_results,
                    "all_results": all_search_results,
                    "failed_queries": failed_queries
                }

            return ToolResult(
                success=overall_success,
                result=result_data,
                execution_time=total_time,
                metadata={
                    "total_queries": len(query_list),
                    "successful_queries": len(successful_results),
                    "failed_queries": len(failed_queries),
                    "engine": engine,
                    "total_search_results": total_search_results,
                    "country": country,
                    "language": language,
                    "parallel_processing": len(query_list) > 1,
                    "search_time_seconds": total_time
                }
            )

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )

    @tool(
        description="Search the web and automatically extract full content from top results with robust open-source methods. Combines search and content extraction for comprehensive information gathering using Crawl4AI (open source, handles JS), BeautifulSoup, Firecrawl, Jina Reader, or simple extraction as needed.",
        return_description="ToolResult containing search results with extracted full content from URLs"
    )
    async def search_and_extract(self, queries: Union[str, List[str]],
                               max_results_per_query: int = 5,
                               max_extract_per_query: int = 3,
                               engine: str = "google",
                               country: str = "us") -> ToolResult:
        """
        Search the web and extract full content from top results.

        This combines web search with content extraction to provide comprehensive
        information directly, saving the need for separate search + extract operations.

        Args:
            queries: Single search query or list of queries to process in parallel
            max_results_per_query: Maximum search results per query (default: 5)
            max_extract_per_query: Maximum URLs to extract content from per query (default: 3)
            engine: Search engine to use (default: google)
            country: Country code for localized results (default: us)

        Returns:
            ToolResult with search results and extracted content
        """
        if not self._backend:
            return ToolResult(
                success=False,
                result=None,
                error="Search backend not available. Check SERPAPI_KEY environment variable."
            )

        try:
            # Import here to avoid circular imports
            from .web import WebTool

            # Initialize web tool for content extraction
            web_tool = WebTool(workspace_storage=getattr(self, 'workspace', None))

            # Convert single query to list
            query_list = [queries] if isinstance(queries, str) else queries

            logger.info(f"Starting search and extract for {len(query_list)} queries...")
            start_time = time.time()

            async def search_and_extract_query(query: str):
                """Search and extract content for a single query."""
                try:
                    # First, perform the search
                    search_response = await self._backend.search(
                        query=query,
                        engine=engine,
                        max_results=min(max_results_per_query, 20),
                        country=country,
                        language="en"
                    )

                    if not search_response.success:
                        return {
                            "query": query,
                            "success": False,
                            "error": search_response.error or "Search failed"
                        }

                    # Get top URLs for content extraction
                    top_urls = [
                        result.url for result in search_response.results[:max_extract_per_query]
                        if result.url and result.url.startswith(('http://', 'https://'))
                    ]

                    extracted_content = []
                    if top_urls:
                        # Extract content from top URLs in parallel
                        extract_result = await web_tool.extract_content(top_urls)

                        if extract_result.success:
                            if isinstance(extract_result.result, list):
                                extracted_content = extract_result.result
                            else:
                                extracted_content = [extract_result.result]
                        else:
                            # Log extraction issues but continue with search results
                            logger.warning(f"Content extraction failed for {len(top_urls)} URLs: {extract_result.error}")
                            extracted_content = []

                    # Combine search results with extracted content
                    enhanced_results = []
                    for i, search_result in enumerate(search_response.results):
                        result_data = {
                            "title": search_result.title,
                            "url": search_result.url,
                            "snippet": search_result.snippet,
                            "position": search_result.position,
                            "relevance_score": search_result.relevance_score,
                            "extracted_content": None
                        }

                        # Add extracted content if available
                        if i < len(extracted_content) and extracted_content[i]:
                            content_data = extracted_content[i]
                            if isinstance(content_data, dict):
                                result_data["extracted_content"] = {
                                    "content_preview": content_data.get("content_preview", ""),
                                    "content_length": content_data.get("content_length", 0),
                                    "saved_file": content_data.get("saved_file"),
                                    "extraction_successful": content_data.get("extraction_successful", False)
                                }

                        enhanced_results.append(result_data)

                    return {
                        "query": query,
                        "success": True,
                        "results": enhanced_results,
                        "total_results": search_response.total_results,
                        "extracted_count": len([r for r in enhanced_results if r["extracted_content"]]),
                        "response_time": search_response.response_time
                    }

                except Exception as e:
                    logger.error(f"Search and extract failed for query '{query}': {e}")
                    return {
                        "query": query,
                        "success": False,
                        "error": str(e)
                    }

            # Execute all queries in parallel
            tasks = [search_and_extract_query(query) for query in query_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            total_time = time.time() - start_time
            logger.info(f"Search and extract completed in {total_time:.2f}s for {len(query_list)} queries")

            # Process results
            successful_results = []
            failed_queries = []
            total_extracted = 0

            for result in results:
                if isinstance(result, Exception):
                    failed_queries.append({"error": str(result)})
                    continue

                if result["success"]:
                    successful_results.append(result)
                    total_extracted += result.get("extracted_count", 0)
                else:
                    failed_queries.append(result)

            # Determine return format
            if isinstance(queries, str):
                # Single query - return results directly
                result_data = successful_results[0]["results"] if successful_results else None
            else:
                # Multiple queries - return grouped results
                result_data = {
                    "queries": successful_results,
                    "failed_queries": failed_queries
                }

            return ToolResult(
                success=len(successful_results) > 0,
                result=result_data,
                execution_time=total_time,
                metadata={
                    "total_queries": len(query_list),
                    "successful_queries": len(successful_results),
                    "failed_queries": len(failed_queries),
                    "total_extracted_content": total_extracted,
                    "engine": engine,
                    "country": country,
                    "parallel_processing": len(query_list) > 1,
                    "extraction_time_seconds": total_time,
                    "message": f"Found and extracted content from {total_extracted} URLs across {len(successful_results)} queries"
                }
            )

        except Exception as e:
            logger.error(f"Search and extract failed: {e}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )

    @tool(
        description="Search for news articles using Google News or Bing News. Supports multiple queries in parallel.",
        return_description="ToolResult containing news search results with articles and publication dates"
    )
    async def news_search(self, queries: Union[str, List[str]], engine: str = "google",
                         max_results: int = 10, country: str = "us") -> ToolResult:
        """
        Search for news articles. Supports multiple queries in parallel.

        Args:
            queries: Single news query or list of queries to execute in parallel (required)
            engine: Search engine to use - google or bing (default: google)
            max_results: Maximum number of news results per query (default: 10)
            country: Country code for localized news (default: us)

        Returns:
            ToolResult containing news search results
        """
        if not self._backend:
            return ToolResult(
                success=False,
                result=None,
                error="Search backend not available"
            )

        try:
            # Convert single query to list
            query_list = [queries] if isinstance(queries, str) else queries

            logger.info(f"Starting parallel news search for {len(query_list)} queries...")
            start_time = time.time()

            async def search_news_query(query: str):
                """Execute a single news search query."""
                try:
                    response = await self._backend.search(
                        query=query,
                        engine=engine,
                        max_results=min(max_results, 20),
                        country=country,
                        tbm="nws"  # Google News search
                    )

                    if response.success:
                        return {
                            "query": query,
                            "success": True,
                            "results": response.results,
                            "total_results": response.total_results,
                            "response_time": response.response_time,
                            "timestamp": response.timestamp
                        }
                    else:
                        return {
                            "query": query,
                            "success": False,
                            "error": response.error or "News search failed"
                        }

                except Exception as e:
                    logger.error(f"News search failed for query '{query}': {e}")
                    return {
                        "query": query,
                        "success": False,
                        "error": str(e)
                    }

            # Execute all queries in parallel
            tasks = [search_news_query(query) for query in query_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            total_time = time.time() - start_time
            logger.info(f"Parallel news search completed in {total_time:.2f}s")

            # Process results
            successful_results = []
            failed_queries = []
            all_news_results = []

            for result in results:
                if isinstance(result, Exception):
                    failed_queries.append({"error": str(result)})
                    continue

                if result["success"]:
                    successful_results.append(result)
                    all_news_results.extend(result["results"])
                else:
                    failed_queries.append(result)

            # Return results
            if isinstance(queries, str):
                # Single query case
                result_data = successful_results[0]["results"] if successful_results else None
            else:
                # Multiple queries case
                result_data = {
                    "queries": successful_results,
                    "all_results": all_news_results,
                    "failed_queries": failed_queries
                }

            return ToolResult(
                success=len(successful_results) > 0,
                result=result_data,
                execution_time=total_time,
                metadata={
                    "total_queries": len(query_list),
                    "successful_queries": len(successful_results),
                    "failed_queries": len(failed_queries),
                    "engine": engine,
                    "search_type": "news",
                    "country": country,
                    "parallel_processing": len(query_list) > 1
                }
            )

        except Exception as e:
            logger.error(f"News search failed: {e}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )

    @tool(
        description="Search for images using Google Images or Bing Images. Supports multiple queries in parallel.",
        return_description="ToolResult containing image search results with URLs and metadata"
    )
    async def image_search(self, queries: Union[str, List[str]], engine: str = "google",
                          max_results: int = 10, safe_search: str = "moderate") -> ToolResult:
        """
        Search for images. Supports multiple queries in parallel.

        Args:
            queries: Single image query or list of queries to execute in parallel (required)
            engine: Search engine to use - google or bing (default: google)
            max_results: Maximum number of image results per query (default: 10)
            safe_search: Safe search setting - off, moderate, strict (default: moderate)

        Returns:
            ToolResult containing image search results
        """
        if not self._backend:
            return ToolResult(
                success=False,
                result=None,
                error="Search backend not available"
            )

        try:
            # Convert single query to list
            query_list = [queries] if isinstance(queries, str) else queries

            logger.info(f"Starting parallel image search for {len(query_list)} queries...")
            start_time = time.time()

            async def search_images_query(query: str):
                """Execute a single image search query."""
                try:
                    response = await self._backend.search(
                        query=query,
                        engine=engine,
                        max_results=min(max_results, 20),
                        tbm="isch",  # Google Images search
                        safe=safe_search
                    )

                    if response.success:
                        return {
                            "query": query,
                            "success": True,
                            "results": response.results,
                            "total_results": response.total_results,
                            "response_time": response.response_time,
                            "timestamp": response.timestamp
                        }
                    else:
                        return {
                            "query": query,
                            "success": False,
                            "error": response.error or "Image search failed"
                        }

                except Exception as e:
                    logger.error(f"Image search failed for query '{query}': {e}")
                    return {
                        "query": query,
                        "success": False,
                        "error": str(e)
                    }

            # Execute all queries in parallel
            tasks = [search_images_query(query) for query in query_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            total_time = time.time() - start_time
            logger.info(f"Parallel image search completed in {total_time:.2f}s")

            # Process results
            successful_results = []
            failed_queries = []
            all_image_results = []

            for result in results:
                if isinstance(result, Exception):
                    failed_queries.append({"error": str(result)})
                    continue

                if result["success"]:
                    successful_results.append(result)
                    all_image_results.extend(result["results"])
                else:
                    failed_queries.append(result)

            # Return results
            if isinstance(queries, str):
                # Single query case
                result_data = successful_results[0]["results"] if successful_results else None
            else:
                # Multiple queries case
                result_data = {
                    "queries": successful_results,
                    "all_results": all_image_results,
                    "failed_queries": failed_queries
                }

            return ToolResult(
                success=len(successful_results) > 0,
                result=result_data,
                execution_time=total_time,
                metadata={
                    "total_queries": len(query_list),
                    "successful_queries": len(successful_results),
                    "failed_queries": len(failed_queries),
                    "engine": engine,
                    "search_type": "images",
                    "safe_search": safe_search,
                    "parallel_processing": len(query_list) > 1
                }
            )

        except Exception as e:
            logger.error(f"Image search failed: {e}")
            return ToolResult(
                success=False,
                result=None,
                error=str(e)
            )


# Export main classes and functions
__all__ = [
    "SearchTool",
    "SearchResult",
]
