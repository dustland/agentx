"""
Search Tools - Opinionated web search using SerpAPI with parallel support.

Simple, focused implementation:
- Uses SerpAPI for reliable search results
- Supports parallel queries for efficiency
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

    def __init__(self, api_key: Optional[str] = None, taskspace_storage=None):
        super().__init__("search")
        self.api_key = api_key
        self.taskspace = taskspace_storage
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
    async def search_web(self, queries: Union[str, List[str]], max_results: int = 10) -> ToolResult:
        """
        Search the web with one or more queries in parallel.

        Args:
            queries: Single query string or list of queries
            max_results: Maximum results per query (default: 10, max: 20)

        Returns:
            ToolResult with search results
        """
        if not self._backend:
            return ToolResult(
                success=False,
                error="Search backend not available. Set SERPAPI_API_KEY environment variable.",
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
                    # Convert to simple format
                    results = []
                    for result in response.results:
                        results.append({
                            "title": result.title,
                            "url": result.url,
                            "snippet": result.snippet,
                            "position": result.position
                        })

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

        total_time = time.time() - start_time
        logger.info(f"Search completed in {total_time:.2f}s")

        # Process results
        successful_results = []
        failed_queries = []

        for result in results:
            if isinstance(result, Exception):
                failed_queries.append({
                    "error": str(result)
                })
            elif result["success"]:
                successful_results.append(result)
            else:
                failed_queries.append(result)

        # Return results based on input type
        if len(query_list) == 1:
            # Single query - return directly
            if successful_results:
                return ToolResult(
                    success=True,
                    result=successful_results[0],
                    execution_time=total_time,
                    metadata={
                        "total_results": successful_results[0]["total_results"],
                        "search_engine": "google"
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    result=failed_queries[0] if failed_queries else None,
                    execution_time=total_time,
                    error="Search failed"
                )
        else:
            # Multiple queries - return aggregate
            return ToolResult(
                success=len(successful_results) > 0,
                result={
                    "successful": successful_results,
                    "failed": failed_queries,
                    "summary": {
                        "total_queries": len(query_list),
                        "successful_queries": len(successful_results),
                        "failed_queries": len(failed_queries)
                    }
                },
                execution_time=total_time,
                metadata={
                    "parallel_execution": True,
                    "search_engine": "google"
                }
            )


# Export
__all__ = ["SearchTool", "SearchResult"]
