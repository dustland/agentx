# Builtin Tools

*Module: [`vibex.builtin_tools`](https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools.py)*

This directory contains the implementations of the builtin tools.

This __init__.py file is special. It contains the function that
registers all the builtin tools with the core ToolRegistry.

## register_builtin_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools.py#L19" class="source-link" title="View source code">source</a>

```python
def register_builtin_tools(registry: ToolRegistry, project_storage: Optional[Any] = None, memory_system: Optional[Any] = None)
```

Register all built-in tools with the tool registry.

**Args:**
    registry: The tool registry to register tools with
    project_storage: Optional ProjectStorage instance to use for tools
    memory_system: Optional memory system for memory tools
