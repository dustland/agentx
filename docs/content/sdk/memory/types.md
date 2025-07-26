# Memory Types

*Module: [`vibex.memory.types`](https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py)*

Memory System Types

Data models and types for the memory backend system.

## MemoryType <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L22" class="source-link" title="View source code">source</a>

Types of memory content.

### __str__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L33" class="source-link" title="View source code">source</a>

```python
def __str__(self)
```
## MemoryItem <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L38" class="source-link" title="View source code">source</a>

Individual memory item with metadata.

### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L53" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary for serialization.

### from_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L71" class="source-link" title="View source code">source</a>

```python
def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem'
```

Create MemoryItem from dictionary.

## Memory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L102" class="source-link" title="View source code">source</a>

Base memory model for synthesis engine.

## Constraint <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L115" class="source-link" title="View source code">source</a>

Memory representing user constraints, preferences, or rules.

## HotIssue <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L121" class="source-link" title="View source code">source</a>

Memory representing active problems that need attention.

## DocumentChunk <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L128" class="source-link" title="View source code">source</a>

Memory representing a chunk of document content for semantic search.

## MemoryQuery <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L137" class="source-link" title="View source code">source</a>

Query parameters for memory operations.

## MemorySearchResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L152" class="source-link" title="View source code">source</a>

Result from memory search operations.

### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L160" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary for serialization.

## MemoryStats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L172" class="source-link" title="View source code">source</a>

Memory backend statistics.

### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/types.py#L182" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary for serialization.
