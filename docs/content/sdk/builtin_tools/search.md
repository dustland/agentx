# Web Search

*Module: [`vibex.builtin_tools.search`](https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/search.py)*

Search Tools - Opinionated web search using SerpAPI with parallel support.

Simple, focused implementation:
- Uses SerpAPI for reliable search results
- Supports parallel queries for efficiency
- No complex configuration options

## SearchResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/search.py#L23" class="source-link" title="View source code">source</a>

Clean search result.

## SearchTool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/search.py#L31" class="source-link" title="View source code">source</a>

Opinionated search tool using SerpAPI.

Simple and reliable - uses best practices as defaults.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/search.py#L38" class="source-link" title="View source code">source</a>

```python
def __init__(self, api_key: Optional[str] = None, project_storage = None)
```
### search_web <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/search.py#L59" class="source-link" title="View source code">source</a>

```python
async def search_web(self, queries: Union[str, List[str]], max_results: int = 10) -> ToolResult
```

Search the web with one or more queries in parallel.

**Args:**
    queries: Single query string or list of queries
    max_results: Maximum results per query (default: 10, max: 20)

**Returns:**
    ToolResult with search results
