# Builtin Tools

_Module: [`vibex.builtin_tools`](https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools.py)_

This directory contains the implementations of the builtin tools.

This **init**.py file is special. It contains the function that
registers all the builtin tools with the core ToolRegistry.

## register_builtin_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools.py#L16" class="source-link" title="View source code">source</a>

```python
def register_builtin_tools(registry, taskspace_path = None, memory_system = None)
```

Register all builtin tools with the registry.
