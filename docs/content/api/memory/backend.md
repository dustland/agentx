# Memory Backend

*Module: [`vibex.memory.backend`](https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py)*

Memory Backend Interface

Abstract base class defining the contract for memory backend implementations.

## MemoryBackend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L12" class="source-link" title="View source code">source</a>

Abstract interface for memory storage backends.

Provides a clean interface for storing and retrieving memories,
with support for specialized memory types (constraints, hot issues, document chunks).

### add <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L21" class="source-link" title="View source code">source</a>

```python
async def add(self, content: str, memory_type: MemoryType, agent_name: str, metadata: Dict[str, Any] = None, importance: float = 1.0) -> str
```

Add a memory to the backend.

**Args:**
    content: Memory content
    memory_type: Type of memory (text, constraint, hot_issue, etc.)
    agent_name: Name of the agent creating the memory
    metadata: Additional metadata
    importance: Importance score (0.0 to 3.0)

**Returns:**
    Memory ID

### search <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L45" class="source-link" title="View source code">source</a>

```python
async def search(self, query: MemoryQuery) -> MemorySearchResult
```

Search memories using semantic similarity and filters.

**Args:**
    query: Search query with filters and parameters

**Returns:**
    Search results with relevant memories

### query <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L58" class="source-link" title="View source code">source</a>

```python
async def query(self, query: MemoryQuery) -> MemorySearchResult
```

Alias for search method for backward compatibility.

### get <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L63" class="source-link" title="View source code">source</a>

```python
async def get(self, memory_id: str) -> Optional[MemoryItem]
```

Get a specific memory by ID.

**Args:**
    memory_id: Memory identifier

**Returns:**
    Memory item if found, None otherwise

### update <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L76" class="source-link" title="View source code">source</a>

```python
async def update(self, memory_id: str) -> bool
```

Update memory metadata or content.

**Args:**
    memory_id: Memory identifier
    **kwargs: Fields to update

**Returns:**
    True if updated successfully, False otherwise

### delete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L90" class="source-link" title="View source code">source</a>

```python
async def delete(self, memory_id: str) -> bool
```

Delete a memory.

**Args:**
    memory_id: Memory identifier

**Returns:**
    True if deleted successfully, False otherwise

### clear <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L103" class="source-link" title="View source code">source</a>

```python
async def clear(self, agent_name: str = None) -> int
```

Clear memories, optionally filtered by agent.

**Args:**
    agent_name: Agent name filter (None to clear all)

**Returns:**
    Number of memories cleared

### count <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L116" class="source-link" title="View source code">source</a>

```python
async def count(self) -> int
```

Count memories with optional filters.

**Args:**
    **filters: Filter criteria

**Returns:**
    Number of matching memories

### stats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L129" class="source-link" title="View source code">source</a>

```python
async def stats(self) -> MemoryStats
```

Get memory backend statistics.

**Returns:**
    Statistics about the memory backend

### health <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L139" class="source-link" title="View source code">source</a>

```python
async def health(self) -> Dict[str, Any]
```

Get backend health status.

**Returns:**
    Health status information

### get_active_constraints <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L149" class="source-link" title="View source code">source</a>

```python
async def get_active_constraints(self) -> List[MemoryItem]
```

Get all active constraint memories.

### get_active_hot_issues <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L160" class="source-link" title="View source code">source</a>

```python
async def get_active_hot_issues(self) -> List[MemoryItem]
```

Get all active hot issue memories.

### get_active_rules <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L171" class="source-link" title="View source code">source</a>

```python
async def get_active_rules(self) -> List[MemoryItem]
```

Get all active constraints and hot issues.

### search_documents <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L177" class="source-link" title="View source code">source</a>

```python
async def search_documents(self, query: str, top_k: int = 5) -> List[MemoryItem]
```

Search document chunks for semantic similarity.

### save_memories <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/backend.py#L187" class="source-link" title="View source code">source</a>

```python
async def save_memories(self, memories: List[Dict[str, Any]]) -> List[str]
```

Save multiple memories in batch.

**Args:**
    memories: List of memory dictionaries

**Returns:**
    List of memory IDs
