# Tool Manager

*Module: [`agentx.tool.manager`](https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py)*

Tool Manager - Unified tool registry and execution for task isolation.

Combines ToolRegistry and ToolExecutor into a single manager class
that provides both tool registration and execution capabilities.
This simplifies the Agent interface and ensures task-level tool isolation.

## ToolManager <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L18" class="source-link" title="View source code">source</a>

Unified tool manager that combines registry and execution.

This class provides task-level tool isolation by maintaining
its own registry and executor. Each task gets its own ToolManager
instance to prevent tool conflicts between tasks.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L27" class="source-link" title="View source code">source</a>

```python
def __init__(self, task_id: str = 'default')
```

Initialize tool manager with task isolation.

**Args:**
    task_id: Unique identifier for this task (for logging/debugging)

### register_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L41" class="source-link" title="View source code">source</a>

```python
def register_tool(self, tool: Tool) -> None
```

Register a tool with this task's registry.

### list_tools <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L46" class="source-link" title="View source code">source</a>

```python
def list_tools(self) -> List[str]
```

Get list of all registered tool names.

### get_tool_schemas <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L50" class="source-link" title="View source code">source</a>

```python
def get_tool_schemas(self, tool_names: List[str] = None) -> List[Dict[str, Any]]
```

Get JSON schemas for tools.

### get_tool_function <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L54" class="source-link" title="View source code">source</a>

```python
def get_tool_function(self, name: str)
```

Get a tool function by name.

### get_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L58" class="source-link" title="View source code">source</a>

```python
def get_tool(self, name: str)
```

Get a tool instance by name for direct access.

### get_builtin_tools <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L62" class="source-link" title="View source code">source</a>

```python
def get_builtin_tools(self) -> List[str]
```

Get list of all builtin tool names.

### get_custom_tools <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L66" class="source-link" title="View source code">source</a>

```python
def get_custom_tools(self) -> List[str]
```

Get list of all custom (non-builtin) tool names.

### execute_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L71" class="source-link" title="View source code">source</a>

```python
async def execute_tool(self, tool_name: str, agent_name: str = 'default') -> ToolResult
```

Execute a single tool.

### execute_tools <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L75" class="source-link" title="View source code">source</a>

```python
async def execute_tools(self, tool_calls: List[Any], agent_name: str = 'default') -> List[Dict[str, Any]]
```

Execute multiple tool calls.

### get_execution_stats <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L79" class="source-link" title="View source code">source</a>

```python
def get_execution_stats(self) -> Dict[str, Any]
```

Get execution statistics.

### get_tool_count <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L84" class="source-link" title="View source code">source</a>

```python
def get_tool_count(self) -> int
```

Get the number of registered tools.

### clear_tools <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L88" class="source-link" title="View source code">source</a>

```python
def clear_tools(self) -> None
```

Clear all registered tools (useful for testing).

### __str__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L94" class="source-link" title="View source code">source</a>

```python
def __str__(self) -> str
```
### __repr__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/manager.py#L97" class="source-link" title="View source code">source</a>

```python
def __repr__(self) -> str
```