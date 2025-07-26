# Search Manager

*Module: [`vibex.search.search_manager`](https://github.com/dustland/vibex/blob/main/src/vibex/search/search_manager.py)*

Search manager that coordinates different search backends.

## SearchManager <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/search_manager.py#L10" class="source-link" title="View source code">source</a>

Manages multiple search backends and provides unified search interface.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/search_manager.py#L15" class="source-link" title="View source code">source</a>

```python
def __init__(self, default_backend: str = 'serpapi')
```

Initialize search manager.

**Args:**
    default_backend: Default backend to use for searches
    **backend_configs: Configuration for different backends

### add_backend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/search_manager.py#L40" class="source-link" title="View source code">source</a>

```python
def add_backend(self, name: str, backend: SearchBackend) -> None
```

Add a new search backend.

### get_backend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/search_manager.py#L44" class="source-link" title="View source code">source</a>

```python
def get_backend(self, name: Optional[str] = None) -> SearchBackend
```

Get a search backend by name.

### list_backends <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/search_manager.py#L57" class="source-link" title="View source code">source</a>

```python
def list_backends(self) -> Dict[str, bool]
```

List all backends and their availability status.

### search <a href="https://github.com/dustland/vibex/blob/main/src/vibex/search/search_manager.py#L64" class="source-link" title="View source code">source</a>

```python
async def search(self, query: str, backend: Optional[str] = None) -> SearchResponse
```

Execute a search using the specified or default backend.

**Args:**
    query: Search query
    backend: Backend to use (defaults to default_backend)
    **kwargs: Additional search parameters

**Returns:**
    SearchResponse with results
