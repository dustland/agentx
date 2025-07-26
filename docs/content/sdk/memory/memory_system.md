# Memory System

*Module: [`vibex.memory.memory_system`](https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py)*

Memory System - Coordinated Memory Management

This module provides the main Memory System interface that coordinates:
- Memory backend for storage
- Synthesis engine for event-driven analysis
- Context retrieval for agent prompt enhancement

## MemorySystem <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L27" class="source-link" title="View source code">source</a>

Coordinated Memory System that integrates storage, synthesis, and retrieval.

This is the main interface for the memory system that provides:
- Event-driven memory synthesis
- Context-aware memory retrieval
- Specialized memory management (constraints, hot issues, document chunks)

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L37" class="source-link" title="View source code">source</a>

```python
def __init__(self, backend: MemoryBackend, synthesis_engine: MemorySynthesisEngine = None)
```
### initialize <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L44" class="source-link" title="View source code">source</a>

```python
async def initialize(self) -> None
```

Initialize the memory system.

### on_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L61" class="source-link" title="View source code">source</a>

```python
async def on_event(self, event: Event) -> None
```

Handle events for memory synthesis.

This is the main event handler that gets called by the event bus.

### get_relevant_context <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L73" class="source-link" title="View source code">source</a>

```python
async def get_relevant_context(self, last_user_message: str, agent_name: str = None) -> str
```

Get memory-derived context for agent prompt injection.

This implements the context retrieval pipeline from the architecture.

### add_memory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L90" class="source-link" title="View source code">source</a>

```python
async def add_memory(self, content: str, memory_type: MemoryType, agent_name: str, metadata: Dict[str, Any] = None, importance: float = 1.0) -> str
```

Add a memory to the system.

### search_memories <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L110" class="source-link" title="View source code">source</a>

```python
async def search_memories(self, query: MemoryQuery) -> MemorySearchResult
```

Search memories in the system.

### get_memory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L117" class="source-link" title="View source code">source</a>

```python
async def get_memory(self, memory_id: str) -> Optional[MemoryItem]
```

Get a specific memory by ID.

### update_memory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L124" class="source-link" title="View source code">source</a>

```python
async def update_memory(self, memory_id: str) -> bool
```

Update memory fields.

### delete_memory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L131" class="source-link" title="View source code">source</a>

```python
async def delete_memory(self, memory_id: str) -> bool
```

Delete a memory.

### get_active_constraints <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L139" class="source-link" title="View source code">source</a>

```python
async def get_active_constraints(self) -> List[MemoryItem]
```

Get all active constraint memories.

### get_active_hot_issues <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L146" class="source-link" title="View source code">source</a>

```python
async def get_active_hot_issues(self) -> List[MemoryItem]
```

Get all active hot issue memories.

### search_documents <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L153" class="source-link" title="View source code">source</a>

```python
async def search_documents(self, query: str, top_k: int = 5) -> List[MemoryItem]
```

Search document chunks for semantic similarity.

### get_system_status <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L160" class="source-link" title="View source code">source</a>

```python
async def get_system_status(self) -> Dict[str, Any]
```

Get comprehensive system status.

## Functions

## create_memory_system <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/memory_system.py#L192" class="source-link" title="View source code">source</a>

```python
def create_memory_system(backend: MemoryBackend, brain: Optional['Brain'] = None) -> MemorySystem
```

Create a memory system with synthesis engine.
