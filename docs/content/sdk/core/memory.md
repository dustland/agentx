# Memory System

*Module: [`vibex.core.memory`](https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py)*

Memory component for context and knowledge management.

This module provides the main Memory interface that agents use, backed by
intelligent memory backends (Mem0) for semantic search and advanced operations.

## MemoryItem <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L24" class="source-link" title="View source code">source</a>

Individual memory item.

### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L34" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary.

### from_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L47" class="source-link" title="View source code">source</a>

```python
def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem'
```

Create from dictionary.

## Memory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L60" class="source-link" title="View source code">source</a>

Memory component for individual agents.

Provides a simple interface backed by intelligent memory backends
for semantic search and advanced memory operations.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L68" class="source-link" title="View source code">source</a>

```python
def __init__(self, agent: 'Agent', config = None)
```
### save_async <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L81" class="source-link" title="View source code">source</a>

```python
async def save_async(self, content: str, metadata: Optional[Dict[str, Any]] = None, importance: float = 1.0) -> str
```

Save content to memory.

### save <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L94" class="source-link" title="View source code">source</a>

```python
def save(self, content: str, metadata: Optional[Dict[str, Any]] = None, importance: float = 1.0) -> str
```

Save content to memory (sync wrapper).

### search_async <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L109" class="source-link" title="View source code">source</a>

```python
async def search_async(self, query: str, limit: int = 10) -> List[MemoryItem]
```

Search memories by content.

### search <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L135" class="source-link" title="View source code">source</a>

```python
def search(self, query: str, limit: int = 10) -> List[MemoryItem]
```

Search memories by content (sync wrapper).

### get_async <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L148" class="source-link" title="View source code">source</a>

```python
async def get_async(self, memory_id: str) -> Optional[MemoryItem]
```

Get a specific memory by ID.

### get <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L165" class="source-link" title="View source code">source</a>

```python
def get(self, memory_id: str) -> Optional[MemoryItem]
```

Get a specific memory by ID (sync wrapper).

### delete_async <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L178" class="source-link" title="View source code">source</a>

```python
async def delete_async(self, memory_id: str) -> bool
```

Delete a memory by ID.

### delete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L186" class="source-link" title="View source code">source</a>

```python
def delete(self, memory_id: str) -> bool
```

Delete a memory by ID (sync wrapper).

### clear_async <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L199" class="source-link" title="View source code">source</a>

```python
async def clear_async(self) -> bool
```

Clear all memories for this agent.

### clear <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/memory.py#L207" class="source-link" title="View source code">source</a>

```python
def clear(self) -> bool
```

Clear all memories for this agent (sync wrapper).
