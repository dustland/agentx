# Mem0 Backend

*Module: [`vibex.memory.mem0_backend`](https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py)*

Mem0 Backend Implementation

Intelligent memory backend using Mem0 for semantic search, vector storage,
and advanced memory operations.

## Mem0Backend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L19" class="source-link" title="View source code">source</a>

Mem0-powered memory backend with semantic search and intelligent storage.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L22" class="source-link" title="View source code">source</a>

```python
def __init__(self, config)
```

Initialize Mem0 backend.

**Args:**
    config: Memory configuration

### add <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L72" class="source-link" title="View source code">source</a>

```python
async def add(self, content: str, memory_type: MemoryType, agent_name: str, metadata: Optional[Dict[str, Any]] = None, importance: float = 1.0) -> str
```

Add content to Mem0 memory.

### query <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L112" class="source-link" title="View source code">source</a>

```python
async def query(self, query: MemoryQuery) -> MemorySearchResult
```

Query Mem0 for content retrieval with semantic search.

### search <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L161" class="source-link" title="View source code">source</a>

```python
async def search(self, query: MemoryQuery) -> MemorySearchResult
```

Search Mem0 for item discovery and filtering.

### get <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L167" class="source-link" title="View source code">source</a>

```python
async def get(self, memory_id: str) -> Optional[MemoryItem]
```

Get a specific memory by ID.

### update <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L195" class="source-link" title="View source code">source</a>

```python
async def update(self, memory_id: str) -> bool
```

Update memory metadata or content.

### delete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L231" class="source-link" title="View source code">source</a>

```python
async def delete(self, memory_id: str) -> bool
```

Delete memory from Mem0.

### clear <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L243" class="source-link" title="View source code">source</a>

```python
async def clear(self, agent_name: Optional[str] = None) -> int
```

Clear memories from Mem0.

### count <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L261" class="source-link" title="View source code">source</a>

```python
async def count(self, memory_type: Optional[MemoryType] = None, agent_name: Optional[str] = None, metadata_filter: Optional[Dict[str, Any]] = None) -> int
```

Count memories in Mem0.

### stats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L292" class="source-link" title="View source code">source</a>

```python
async def stats(self) -> MemoryStats
```

Get memory statistics from Mem0.

### health <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/mem0_backend.py#L365" class="source-link" title="View source code">source</a>

```python
async def health(self) -> Dict[str, Any]
```

Check Mem0 backend health.
