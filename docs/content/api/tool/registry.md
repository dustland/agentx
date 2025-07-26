# Tool Registry

*Module: [`vibex.tool.registry`](https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py)*

Tool Registry - The single source of truth for tool definitions.

## ToolRegistry <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L11" class="source-link" title="View source code">source</a>

A thread-safe registry for managing tools and their configurations.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L21" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### register_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L30" class="source-link" title="View source code">source</a>

```python
def register_tool(self, tool: Tool)
```

Register all callable methods of a Tool instance.
Each method marked with @tool is registered as a separate tool function.

### register_function <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L40" class="source-link" title="View source code">source</a>

```python
def register_function(self, func: Callable, name: Optional[str] = None)
```

Register a standalone function as a tool.

### register_toolset <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L72" class="source-link" title="View source code">source</a>

```python
def register_toolset(self, name: str, tool_names: List[str])
```

Register a collection of tools as a named toolset.

### get_tool_function <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L83" class="source-link" title="View source code">source</a>

```python
def get_tool_function(self, name: str) -> Optional[ToolFunction]
```

Retrieve a tool function by its name.

### get_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L87" class="source-link" title="View source code">source</a>

```python
def get_tool(self, name: str)
```

Get a tool instance by name for direct access.

### get_tool_schema <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L95" class="source-link" title="View source code">source</a>

```python
def get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]
```

Get the JSON schema for a single tool.

### get_tool_schemas <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L110" class="source-link" title="View source code">source</a>

```python
def get_tool_schemas(self, tool_names: Optional[List[str]] = None) -> List[Dict[str, Any]]
```

Get a list of all tool schemas, optionally filtered.

### list_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L133" class="source-link" title="View source code">source</a>

```python
def list_tools(self) -> List[str]
```

List all registered tool names.

### get_tool_names <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L137" class="source-link" title="View source code">source</a>

```python
def get_tool_names(self) -> List[str]
```

Get all registered tool names (alias for list_tools).

### list_toolsets <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L141" class="source-link" title="View source code">source</a>

```python
def list_toolsets(self) -> List[str]
```

List all registered toolset names.

### get_builtin_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L145" class="source-link" title="View source code">source</a>

```python
def get_builtin_tools(self) -> List[str]
```

Get list of all builtin tool names.

### get_custom_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L151" class="source-link" title="View source code">source</a>

```python
def get_custom_tools(self) -> List[str]
```

Get list of all custom (non-builtin) tool names.

### clear <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L157" class="source-link" title="View source code">source</a>

```python
def clear(self)
```

Clear all registered tools and toolsets. Useful for testing.

## Functions

## get_tool_registry <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/registry.py#L164" class="source-link" title="View source code">source</a>

```python
def get_tool_registry() -> ToolRegistry
```

Get the global tool registry instance.
