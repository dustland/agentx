# Tool Manager

*Module: [`vibex.tool.manager`](https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py)*

Tool Manager - Unified tool registry and execution for task isolation.

Combines ToolRegistry and ToolExecutor into a single manager class
that provides both tool registration and execution capabilities.
This simplifies the Agent interface and ensures task-level tool isolation.

## ToolManager <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L18" class="source-link" title="View source code">source</a>

Unified tool manager that combines registry and execution.

This class provides task-level tool isolation by maintaining
its own registry and executor. Each task gets its own ToolManager
instance to prevent tool conflicts between tasks.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L27" class="source-link" title="View source code">source</a>

```python
def __init__(self, project_id: str = 'default', workspace_path: Optional[str] = None)
```

Initialize tool manager with task isolation.

**Args:**
    project_id: Unique identifier for this task (for logging/debugging)
    workspace_path: Path to project-specific workspace (for file tools)

### register_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L70" class="source-link" title="View source code">source</a>

```python
def register_tool(self, tool: Tool) -> None
```

Register a tool with this task's registry.

### list_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L75" class="source-link" title="View source code">source</a>

```python
def list_tools(self) -> List[str]
```

Get list of all registered tool names.

### get_tool_schemas <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L79" class="source-link" title="View source code">source</a>

```python
def get_tool_schemas(self, tool_names: List[str] = None) -> List[Dict[str, Any]]
```

Get JSON schemas for tools.

### get_tool_function <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L83" class="source-link" title="View source code">source</a>

```python
def get_tool_function(self, name: str)
```

Get a tool function by name.

### get_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L87" class="source-link" title="View source code">source</a>

```python
def get_tool(self, name: str)
```

Get a tool instance by name for direct access.

### get_builtin_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L91" class="source-link" title="View source code">source</a>

```python
def get_builtin_tools(self) -> List[str]
```

Get list of all builtin tool names.

### get_custom_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L95" class="source-link" title="View source code">source</a>

```python
def get_custom_tools(self) -> List[str]
```

Get list of all custom (non-builtin) tool names.

### execute_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L100" class="source-link" title="View source code">source</a>

```python
async def execute_tool(self, tool_name: str, agent_name: str = 'default') -> ToolResult
```

Execute a single tool.

### execute_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L104" class="source-link" title="View source code">source</a>

```python
async def execute_tools(self, tool_calls: List[Any], agent_name: str = 'default') -> List[Dict[str, Any]]
```

Execute multiple tool calls.

### get_execution_stats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L108" class="source-link" title="View source code">source</a>

```python
def get_execution_stats(self) -> Dict[str, Any]
```

Get execution statistics.

### get_tool_count <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L113" class="source-link" title="View source code">source</a>

```python
def get_tool_count(self) -> int
```

Get the number of registered tools.

### clear_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L117" class="source-link" title="View source code">source</a>

```python
def clear_tools(self) -> None
```

Clear all registered tools (useful for testing).

### __str__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L123" class="source-link" title="View source code">source</a>

```python
def __str__(self) -> str
```
### __repr__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/manager.py#L126" class="source-link" title="View source code">source</a>

```python
def __repr__(self) -> str
```