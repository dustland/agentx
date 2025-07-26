# Tool Models

*Module: [`vibex.memory.models`](https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py)*

Memory subsystem models - Self-contained data models for memory management.

This module contains all data models related to memory management, following the
architectural rule that subsystems should be self-contained and not import from core.

## MemoryType <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L30" class="source-link" title="View source code">source</a>

Types of memory content.

### __str__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L41" class="source-link" title="View source code">source</a>

```python
def __str__(self)
```
## MemoryBackendType <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L45" class="source-link" title="View source code">source</a>

Types of memory backends.

## MemoryOperation <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L55" class="source-link" title="View source code">source</a>

Types of memory operations.

## MemoryItem <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L71" class="source-link" title="View source code">source</a>

Individual memory item with metadata.

### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L86" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary for serialization.

### from_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L104" class="source-link" title="View source code">source</a>

```python
def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem'
```

Create MemoryItem from dictionary.

## Memory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L138" class="source-link" title="View source code">source</a>

Base memory model for synthesis engine.

## Constraint <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L151" class="source-link" title="View source code">source</a>

Memory representing user constraints, preferences, or rules.

## HotIssue <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L159" class="source-link" title="View source code">source</a>

Memory representing active problems that need attention.

## DocumentChunk <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L168" class="source-link" title="View source code">source</a>

Memory representing a chunk of document content for semantic search.

## MemoryQuery <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L183" class="source-link" title="View source code">source</a>

Query parameters for memory operations.

## MemorySearchResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L200" class="source-link" title="View source code">source</a>

Result from memory search operations.

### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L209" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary for serialization.

## MemoryBackend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L225" class="source-link" title="View source code">source</a>

Abstract interface for memory backend implementations.

### add <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L229" class="source-link" title="View source code">source</a>

```python
async def add(self, content: str, memory_type: MemoryType, agent_name: str, metadata: dict = None, importance: float = 1.0) -> str
```

Add a new memory item.

### query <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L236" class="source-link" title="View source code">source</a>

```python
async def query(self, query: MemoryQuery) -> MemorySearchResult
```

Query memories with structured parameters.

### search <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L241" class="source-link" title="View source code">source</a>

```python
async def search(self, query: MemoryQuery) -> MemorySearchResult
```

Semantic search across memories.

### get <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L246" class="source-link" title="View source code">source</a>

```python
async def get(self, memory_id: str) -> Optional[MemoryItem]
```

Get a specific memory by ID.

### update <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L251" class="source-link" title="View source code">source</a>

```python
async def update(self, memory_id: str) -> bool
```

Update a memory item.

### delete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L256" class="source-link" title="View source code">source</a>

```python
async def delete(self, memory_id: str) -> bool
```

Delete a memory item.

### clear <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L261" class="source-link" title="View source code">source</a>

```python
async def clear(self, agent_name: str = None) -> int
```

Clear memories, optionally filtered by agent.

### count <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L266" class="source-link" title="View source code">source</a>

```python
async def count(self) -> int
```

Count memories with optional filters.

### stats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L271" class="source-link" title="View source code">source</a>

```python
async def stats(self) -> 'MemoryStats'
```

Get memory backend statistics.

### health <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L276" class="source-link" title="View source code">source</a>

```python
async def health(self) -> Dict[str, Any]
```

Get backend health information.

## MemoryStats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L286" class="source-link" title="View source code">source</a>

Memory backend statistics.

### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L297" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary for serialization.

## MemoryHealth <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L311" class="source-link" title="View source code">source</a>

Memory backend health status.

## MemoryConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L326" class="source-link" title="View source code">source</a>

Configuration for memory system.

## MemoryOperationResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L357" class="source-link" title="View source code">source</a>

Result of a memory operation.

## MemoryEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L367" class="source-link" title="View source code">source</a>

Event emitted by memory operations.

## SynthesisRule <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L383" class="source-link" title="View source code">source</a>

Rule for memory synthesis.

## SynthesisResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L393" class="source-link" title="View source code">source</a>

Result of memory synthesis operation.

## MemoryContext <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L409" class="source-link" title="View source code">source</a>

Context for memory retrieval and injection.

## MemoryInjection <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L421" class="source-link" title="View source code">source</a>

Memory content injected into agent context.

## Functions

## generate_short_id <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L20" class="source-link" title="View source code">source</a>

```python
def generate_short_id(length: int = 8) -> str
```

Generate a short, URL-friendly, cryptographically secure random ID.

## calculate_memory_importance <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L434" class="source-link" title="View source code">source</a>

```python
def calculate_memory_importance(content: str, agent_name: str, memory_type: MemoryType, metadata: Dict[str, Any] = None) -> float
```

Calculate importance score for a memory item.

## create_memory_item <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/models.py#L468" class="source-link" title="View source code">source</a>

```python
def create_memory_item(content: str, memory_type: MemoryType, agent_name: str, metadata: Dict[str, Any] = None, importance: float = None) -> MemoryItem
```

Create a new memory item with calculated importance.
