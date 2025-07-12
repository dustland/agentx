"""
Search Tools - Opinionated web search using SerpAPI with parallel support.

Simple, focused implementation:
- Uses SerpAPI for reliable search results
- Supports parallel queries for efficiency
- Integrates with Crawl4AI for content extraction
- No complex configuration options
"""

import asyncio
import time
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

from ..utils.logger import get_logger
from ..core.tool import Tool, tool, ToolResult
from ..search.serpapi_backend import SerpAPIBackend

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """Clean search result."""
    title: str
    url: str
    snippet: str
    position: int


class SearchTool(Tool):
    """
    Opinionated search tool using SerpAPI.

    Simple and reliable - uses best practices as defaults.
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
            logger.error(f"Failed to initialize SerpAPI: {e}")
        except Exception as e:
            logger.error(f"Unexpected error initializing search: {e}")

    @tool(
        description="Search the web using Google. Supports parallel queries for efficiency.",
        return_description="ToolResult with search results"
    )
    async def web_search(self, queries: Union[str, List[str]], max_results: int = 10) -> ToolResult:
        """
        Search the web using Google. Supports single or multiple queries in parallel.

        Args:
            queries: Single query string or list of queries for parallel search
            max_results: Maximum results per query (default: 10, max: 20)

        Returns:
            ToolResult with search results
        """
        if not self._backend:
            return ToolResult(
                success=False,
                error="Search backend not available. Set SERPAPI_KEY environment variable.",
                metadata={"backend_missing": True}
            )

        # Convert single query to list for uniform processing
        query_list = [queries] if isinstance(queries, str) else queries
        max_results = min(max_results, 20)  # Cap at 20

        logger.info(f"Searching for {len(query_list)} queries...")
        start_time = time.time()

        async def search_single_query(query: str):
            """Execute a single search query."""
            try:
                response = await self._backend.search(
                    query=query,
                    engine="google",
                    max_results=max_results,
                    country="us",
                    language="en"
                )

                if response.success:
                    # Convert to clean SearchResult format
                    results = [
                        SearchResult(
                            title=result.title,
                            url=result.url,
                            snippet=result.snippet,
                            position=result.position
                        )
                        for result in response.results
                    ]

                    return {
                        "query": query,
                        "success": True,
                        "results": results,
                        "total_results": response.total_results
                    }
                else:
                    return {
                        "query": query,
                        "success": False,
                        "error": response.error or "Search failed"
                    }
            except Exception as e:
                logger.error(f"Search failed for '{query}': {e}")
                return {
                    "query": query,
                    "success": False,
                    "error": str(e)
                }

        # Execute all queries in parallel
        tasks = [search_single_query(query) for query in query_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        search_time = time.time() - start_time
        logger.info(f"Search completed in {search_time:.2f}s")

        # Process results
        successful_results = []
        failed_queries = []
        all_results = []

        for result in results:
            if isinstance(result, Exception):
                failed_queries.append({"error": str(result)})
                continue

            if result["success"]:
                successful_results.append(result)
                all_results.extend(result["results"])
            else:
                failed_queries.append(result)

        # Return format based on input
        if isinstance(queries, str):
            # Single query - return results directly
            result_data = successful_results[0]["results"] if successful_results else []
        else:
            # Multiple queries - return structured format
            result_data = {
                "queries": successful_results,
                "all_results": all_results,
                "failed_queries": failed_queries
            }

        return ToolResult(
            success=len(successful_results) > 0,
            result=result_data,
            execution_time=search_time,
            metadata={
                "total_queries": len(query_list),
                "successful_queries": len(successful_results),
                "failed_queries": len(failed_queries),
                "total_results": len(all_results),
                "search_engine": "google"
            }
        )

    @tool(
        description="Search and extract content in one operation. Combines web search with content extraction using Crawl4AI.",
        return_description="ToolResult with search results and extracted content"
    )
    async def search_and_extract(self, queries: Union[str, List[str]],
                                max_results: int = 5, max_extract: int = 3) -> ToolResult:
        """
        Search the web and extract content from top results in one operation.

        Args:
            queries: Single query or list of queries
            max_results: Maximum search results per query (default: 5)
            max_extract: Maximum URLs to extract content from per query (default: 3)

        Returns:
            ToolResult with search results and extracted content
        """
        if not self._backend:
            return ToolResult(
                success=False,
                error="Search backend not available. Set SERPAPI_KEY environment variable.",
                metadata={"backend_missing": True}
            )

        # Import web tool here to avoid circular imports
        from .web import WebTool
        web_tool = WebTool(workspace_storage=getattr(self, 'workspace', None))

        query_list = [queries] if isinstance(queries, str) else queries
        max_results = min(max_results, 20)
        max_extract = min(max_extract, max_results)

        logger.info(f"Search and extract for {len(query_list)} queries...")
        start_time = time.time()

        async def search_and_extract_query(query: str):
            """Search and extract for a single query."""
            try:
                # First search
                search_response = await self._backend.search(
                    query=query,
                    engine="google",
                    max_results=max_results,
                    country="us",
                    language="en"
                )

                if not search_response.success:
                    return {
                        "query": query,
                        "success": False,
                        "error": search_response.error or "Search failed"
                    }

                # Get top URLs for extraction
                top_urls = [
                    result.url for result in search_response.results[:max_extract]
                    if result.url and result.url.startswith(('http://', 'https://'))
                ]

                # Extract content if we have URLs
                extracted_content = []
                if top_urls:
                    extract_result = await web_tool.extract_content(top_urls)
                    if extract_result.success:
                        if isinstance(extract_result.result, list):
                            extracted_content = extract_result.result
                        else:
                            extracted_content = [extract_result.result]

                # Combine results
                enhanced_results = []
                for i, search_result in enumerate(search_response.results):
                    result_data = {
                        "title": search_result.title,
                        "url": search_result.url,
                        "snippet": search_result.snippet,
                        "position": search_result.position,
                        "extracted_content": None
                    }

                    # Add extracted content if available
                    if i < len(extracted_content) and extracted_content[i]:
                        content = extracted_content[i]
                        if isinstance(content, dict) and content.get("extraction_successful"):
                            result_data["extracted_content"] = {
                                "content_preview": content.get("content_preview", ""),
                                "content_length": content.get("content_length", 0),
                                "saved_file": content.get("saved_file"),
                                "successful": True
                            }

                    enhanced_results.append(result_data)

                return {
                    "query": query,
                    "success": True,
                    "results": enhanced_results,
                    "total_results": search_response.total_results,
                    "extracted_count": len([r for r in enhanced_results if r["extracted_content"]])
                }

            except Exception as e:
                logger.error(f"Search and extract failed for '{query}': {e}")
                return {
                    "query": query,
                    "success": False,
                    "error": str(e)
                }

        # Execute all queries in parallel
        tasks = [search_and_extract_query(query) for query in query_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time
        logger.info(f"Search and extract completed in {total_time:.2f}s")

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

        # Return format
        if isinstance(queries, str):
            result_data = successful_results[0]["results"] if successful_results else []
        else:
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
                "search_engine": "google",
                "message": f"Searched and extracted from {total_extracted} URLs across {len(successful_results)} queries"
            }
        )


# Export
__all__ = ["SearchTool", "SearchResult"]
