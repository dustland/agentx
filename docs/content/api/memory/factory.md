# Storage Factory

*Module: [`vibex.memory.factory`](https://github.com/dustland/vibex/blob/main/src/vibex/memory/factory.py)*

Memory Backend Factory

Factory functions for creating memory backend instances based on configuration.

## create_memory_backend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/factory.py#L16" class="source-link" title="View source code">source</a>

```python
def create_memory_backend(config = None) -> MemoryBackend
```

Create a memory backend instance based on configuration.

**Args:**
    config: Memory configuration. If None, uses default Mem0 config.

**Returns:**
    Memory backend instance

**Raises:**
    ValueError: If backend type is not supported
    ImportError: If required dependencies are not installed

## create_default_memory_backend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/memory/factory.py#L51" class="source-link" title="View source code">source</a>

```python
def create_default_memory_backend() -> MemoryBackend
```

Create a memory backend with default configuration.

**Returns:**
    Memory backend instance with default settings
