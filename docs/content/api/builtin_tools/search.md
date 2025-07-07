# Web Search

*Module: [`agentx.builtin_tools.search`](https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py)*

Search Tools - Web search capabilities using SerpAPI.

Built-in integration with SerpAPI for comprehensive web search across
multiple search engines (Google, Bing, DuckDuckGo, etc.).

## SearchResult <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L19" class="source-link" title="View source code">source</a>

Individual search result.

## SearchTool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L32" class="source-link" title="View source code">source</a>

Web search tool using SerpAPI.

Provides access to multiple search engines including Google, Bing,
DuckDuckGo, Yahoo, Baidu, and Yandex through a unified interface.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L40" class="source-link" title="View source code">source</a>

```python
def __init__(self, api_key: Optional[str] = None)
```
### web_search <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L60" class="source-link" title="View source code">source</a>

```python
async def web_search(self, query: str, engine: str = 'google', max_results: int = 10, country: str = 'us', language: str = 'en') -> ToolResult
```

Search the web using various search engines.

**Args:**
    query: Search query to execute (required)
    engine: Search engine to use - google, bing, duckduckgo, yahoo, baidu, yandex (default: google)
    max_results: Maximum number of results to return, max 20 (default: 10)
    country: Country code for localized results (default: us)
    language: Language code for results (default: en)

**Returns:**
    ToolResult containing search results and metadata

### news_search <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L143" class="source-link" title="View source code">source</a>

```python
async def news_search(self, query: str, engine: str = 'google', max_results: int = 10, country: str = 'us') -> ToolResult
```

Search for news articles.

**Args:**
    query: News search query (required)
    engine: Search engine to use - google or bing (default: google)
    max_results: Maximum number of news results (default: 10)
    country: Country code for localized news (default: us)

**Returns:**
    ToolResult containing news search results

### image_search <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/search.py#L206" class="source-link" title="View source code">source</a>

```python
async def image_search(self, query: str, engine: str = 'google', max_results: int = 10, safe_search: str = 'moderate') -> ToolResult
```

Search for images.

**Args:**
    query: Image search query (required)
    engine: Search engine to use - google or bing (default: google)
    max_results: Maximum number of image results (default: 10)
    safe_search: Safe search setting - off, moderate, strict (default: moderate)

**Returns:**
    ToolResult containing image search results
