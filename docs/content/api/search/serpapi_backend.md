# SerpAPI Backend

*Module: [`vibex.search.serpapi_backend`](https://github.com/dustland/vibex/blob/main/src/vibex/search/serpapi_backend.py)*

SerpAPI backend implementation for web search.

## SerpAPIBackend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/serpapi_backend.py#L14" class="source-link" title="View source code">source</a>

Search backend using SerpAPI service.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/serpapi_backend.py#L17" class="source-link" title="View source code">source</a>

```python
def __init__(self, api_key: Optional[str] = None)
```

Initialize SerpAPI backend.

**Args:**
    api_key: SerpAPI key. If not provided, uses SERPAPI_API_KEY environment variable.

### name <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/serpapi_backend.py#L41" class="source-link" title="View source code">source</a>

```python
def name(self) -> str
```
### is_available <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/serpapi_backend.py#L44" class="source-link" title="View source code">source</a>

```python
def is_available(self) -> bool
```

Check if SerpAPI backend is available.

### search <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/serpapi_backend.py#L48" class="source-link" title="View source code">source</a>

```python
async def search(self, query: str, engine: str = 'google', max_results: int = 10, country: str = 'us', language: str = 'en') -> SearchResponse
```

Execute search using SerpAPI.

**Args:**
    query: Search query
    engine: Search engine to use
    max_results: Maximum number of results (capped at 20)
    country: Country code for localization
    language: Language code for results
    **kwargs: Additional search parameters

**Returns:**
    SearchResponse with results and metadata
