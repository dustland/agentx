# Builtin Tools

*Module: [`agentx.builtin_tools`](https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools.py)*

This directory contains the implementations of the builtin tools.

This __init__.py file is special. It contains the function that
registers all the builtin tools with the core ToolRegistry.

## register_builtin_tools <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools.py#L16" class="source-link" title="View source code">source</a>

```python
def register_builtin_tools(registry, taskspace_path = None, memory_system = None)
```

Register all builtin tools with the registry.
