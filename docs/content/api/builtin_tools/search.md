# Web Search

*Module: [`agentx.builtin_tools.search`](https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py)*

Search Tools - Opinionated web search using SerpAPI with parallel support.

Simple, focused implementation:
- Uses SerpAPI for reliable search results
- Supports parallel queries for efficiency
- Integrates with Crawl4AI for content extraction
- No complex configuration options

## SearchResult <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L24" class="source-link" title="View source code">source</a>

Clean search result.

## SearchTool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L32" class="source-link" title="View source code">source</a>

Opinionated search tool using SerpAPI.

Simple and reliable - uses best practices as defaults.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L39" class="source-link" title="View source code">source</a>

```python
def __init__(self, api_key: Optional[str] = None, workspace_storage = None)
```
### web_search <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L60" class="source-link" title="View source code">source</a>

```python
async def web_search(self, queries: Union[str, List[str]], max_results: int = 10) -> ToolResult
```

Search the web using Google. Supports single or multiple queries in parallel.

**Args:**
    queries: Single query string or list of queries for parallel search
    max_results: Maximum results per query (default: 10, max: 20)

**Returns:**
    ToolResult with search results

### search_and_extract <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L180" class="source-link" title="View source code">source</a>

```python
async def search_and_extract(self, queries: Union[str, List[str]], max_results: int = 5, max_extract: int = 3) -> ToolResult
```

Search the web and extract content from top results in one operation.

**Args:**
    queries: Single query or list of queries
    max_results: Maximum search results per query (default: 5)
    max_extract: Maximum URLs to extract content from per query (default: 3)

**Returns:**
    ToolResult with search results and extracted content
