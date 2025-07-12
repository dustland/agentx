# Search Old

*Module: [`agentx.builtin_tools.search_old`](https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search_old.py)*

Search Tools - Web search capabilities using SerpAPI.

Built-in integration with SerpAPI for comprehensive web search across
multiple search engines (Google, Bing, DuckDuckGo, etc.).

## SearchResult <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search_old.py#L21" class="source-link" title="View source code">source</a>

Individual search result.

## SearchTool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search_old.py#L34" class="source-link" title="View source code">source</a>

Web search tool using SerpAPI.

Provides access to multiple search engines including Google, Bing,
DuckDuckGo, Yahoo, Baidu, and Yandex through a unified interface.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search_old.py#L42" class="source-link" title="View source code">source</a>

```python
def __init__(self, api_key: Optional[str] = None)
```
### web_search <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search_old.py#L62" class="source-link" title="View source code">source</a>

```python
async def web_search(self, queries: Union[str, List[str]], engine: str = 'google', max_results: int = 10, country: str = 'us', language: str = 'en') -> ToolResult
```

Search the web using various search engines. Supports multiple queries in parallel.

**Args:**
    queries: Single search query or list of queries to execute in parallel (required)
    engine: Search engine to use - google, bing, duckduckgo, yahoo, baidu, yandex (default: google)
    max_results: Maximum number of results per query, max 20 (default: 10)
    country: Country code for localized results (default: us)
    language: Language code for results (default: en)

**Returns:**
    ToolResult containing search results and metadata

### search_and_extract <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search_old.py#L216" class="source-link" title="View source code">source</a>

```python
async def search_and_extract(self, queries: Union[str, List[str]], max_results_per_query: int = 5, max_extract_per_query: int = 3, engine: str = 'google', country: str = 'us') -> ToolResult
```

Search the web and extract full content from top results.

This combines web search with content extraction to provide comprehensive
information directly, saving the need for separate search + extract operations.

**Args:**
    queries: Single search query or list of queries to process in parallel
    max_results_per_query: Maximum search results per query (default: 5)
    max_extract_per_query: Maximum URLs to extract content from per query (default: 3)
    engine: Search engine to use (default: google)
    country: Country code for localized results (default: us)

**Returns:**
    ToolResult with search results and extracted content

### news_search <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search_old.py#L402" class="source-link" title="View source code">source</a>

```python
async def news_search(self, queries: Union[str, List[str]], engine: str = 'google', max_results: int = 10, country: str = 'us') -> ToolResult
```

Search for news articles. Supports multiple queries in parallel.

**Args:**
    queries: Single news query or list of queries to execute in parallel (required)
    engine: Search engine to use - google or bing (default: google)
    max_results: Maximum number of news results per query (default: 10)
    country: Country code for localized news (default: us)

**Returns:**
    ToolResult containing news search results

### image_search <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search_old.py#L527" class="source-link" title="View source code">source</a>

```python
async def image_search(self, queries: Union[str, List[str]], engine: str = 'google', max_results: int = 10, safe_search: str = 'moderate') -> ToolResult
```

Search for images. Supports multiple queries in parallel.

**Args:**
    queries: Single image query or list of queries to execute in parallel (required)
    engine: Search engine to use - google or bing (default: google)
    max_results: Maximum number of image results per query (default: 10)
    safe_search: Safe search setting - off, moderate, strict (default: moderate)

**Returns:**
    ToolResult containing image search results
