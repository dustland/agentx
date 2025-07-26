# Storage Interfaces

*Module: [`vibex.search.interfaces`](https://github.com/dustland/vibex/blob/main/src/vibex/search/interfaces.py)*

Search interfaces and base classes.

## SearchEngine <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/interfaces.py#L12" class="source-link" title="View source code">source</a>

Supported search engines

## SearchResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/interfaces.py#L23" class="source-link" title="View source code">source</a>

Represents a single search result.

## SearchResponse <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/interfaces.py#L37" class="source-link" title="View source code">source</a>

Represents a complete search response.

## SearchBackend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/interfaces.py#L49" class="source-link" title="View source code">source</a>

Abstract base class for search backends.

### search <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/interfaces.py#L53" class="source-link" title="View source code">source</a>

```python
async def search(self, query: str, engine: str = 'google', max_results: int = 10, country: str = 'us', language: str = 'en') -> SearchResponse
```

Execute a search query.

### is_available <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/interfaces.py#L60" class="source-link" title="View source code">source</a>

```python
def is_available(self) -> bool
```

Check if the backend is available and properly configured.

### name <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/interfaces.py#L66" class="source-link" title="View source code">source</a>

```python
def name(self) -> str
```

Backend name.
