# Memory System

*Module: [`vibex.builtin_tools.memory`](https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/memory.py)*

Memory Tools - Clean implementation using Memory.

## MemoryTool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/memory.py#L9" class="source-link" title="View source code">source</a>

Memory management capabilities using Memory.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/memory.py#L12" class="source-link" title="View source code">source</a>

```python
def __init__(self, memory: MemoryBackend)
```
### execute <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/memory.py#L16" class="source-link" title="View source code">source</a>

```python
async def execute(self, action: str) -> dict
```

Execute memory operations.

## Functions

## create_memory_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/memory.py#L127" class="source-link" title="View source code">source</a>

```python
def create_memory_tools(memory: MemoryBackend) -> list[MemoryTool]
```

Factory function to create memory tools.
