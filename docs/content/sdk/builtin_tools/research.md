# Research

*Module: [`vibex.builtin_tools.research`](https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/research.py)*

Research Tool - Intelligent web research using AdaptiveCrawler and search.

Combines web search with adaptive crawling for comprehensive research tasks.
Enhanced for crawl4ai 0.7.0 with virtual scroll, link preview, and URL seeding.

## ResearchResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/research.py#L22" class="source-link" title="View source code">source</a>

Result from research operation.

## ResearchTool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/research.py#L33" class="source-link" title="View source code">source</a>

Intelligent research tool combining search and adaptive crawling.

Enhanced for crawl4ai 0.7.0 with:
- Virtual scroll support for infinite scroll pages
- Intelligent link preview with 3-layer scoring
- Async URL seeder for massive URL discovery
- Improved adaptive crawling with learning capabilities

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/research.py#L44" class="source-link" title="View source code">source</a>

```python
def __init__(self, project_storage: Optional[Any] = None) -> None
```
### research_topic <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/research.py#L53" class="source-link" title="View source code">source</a>

```python
async def research_topic(self, query: str, max_pages: int = 30, confidence_threshold: float = 0.75, search_first: bool = True, start_urls: Optional[List[str]] = None) -> ToolResult
```

Research a topic using crawl4ai 0.7.0 adaptive crawling.

**Args:**
    query: Research query or topic
    max_pages: Maximum pages to crawl (default: 30)
    confidence_threshold: Stop when this confidence is reached (default: 0.75)
    search_first: Whether to search for starting URLs first (default: True)
    start_urls: Optional list of URLs to start from (overrides search)

**Returns:**
    ToolResult with comprehensive research findings
