# Tool System

*Module: [`agentx.core.tool`](https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py)*

Tool component for function calling and code execution.

## ToolCall <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L19" class="source-link" title="View source code">source</a>

Tool call specification with retry policy.

## ToolResult <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L30" class="source-link" title="View source code">source</a>

Result of tool execution.

## Tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L125" class="source-link" title="View source code">source</a>

Base class for tools that provide multiple callable methods for LLMs.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L128" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str = '')
```
### get_callable_methods <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L131" class="source-link" title="View source code">source</a>

```python
def get_callable_methods(self) -> Dict[str, Callable]
```

Get all methods marked with @tool decorator.

### get_tool_schemas <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L141" class="source-link" title="View source code">source</a>

```python
def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]
```

Get detailed OpenAI function schemas for all callable methods using Pydantic.

## ToolRegistry <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L187" class="source-link" title="View source code">source</a>

Global tool registry that manages all available tools and creates schemas.

This is a singleton that holds all registered tools and provides
schema generation for any subset of tool names.

### clear <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L205" class="source-link" title="View source code">source</a>

```python
def clear(self)
```

Clears all registered tools. Primarily for testing.

### register_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L209" class="source-link" title="View source code">source</a>

```python
def register_tool(self, tool: Tool)
```

Register a tool and all its callable methods.

### get_tool_schemas <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L223" class="source-link" title="View source code">source</a>

```python
def get_tool_schemas(self, tool_names: List[str]) -> List[Dict[str, Any]]
```

Get detailed OpenAI function schemas for specified tools.

### get_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L236" class="source-link" title="View source code">source</a>

```python
def get_tool(self, name: str) -> Optional[tuple[Tool, Callable, Optional[BaseModel]]]
```

Get a tool, method, and pydantic model by name (for executor use).

### list_tools <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L240" class="source-link" title="View source code">source</a>

```python
def list_tools(self) -> List[str]
```

List all registered tool names.

### execute_tool_sync <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L244" class="source-link" title="View source code">source</a>

```python
def execute_tool_sync(self, name: str) -> ToolResult
```

Synchronous wrapper for executing a tool. For use in non-async contexts.

### execute_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L257" class="source-link" title="View source code">source</a>

```python
async def execute_tool(self, name: str) -> ToolResult
```

Execute a tool by name with automatic parameter validation.

## Functions

## tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L43" class="source-link" title="View source code">source</a>

```python
def tool(description: str = '', return_description: str = '')
```

Decorator to mark methods as available tool calls.

**Args:**
    description: Clear description of what this tool does
    return_description: Description of what the tool returns

## get_tool_registry <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L290" class="source-link" title="View source code">source</a>

```python
def get_tool_registry() -> ToolRegistry
```

Get the global tool registry instance.

## register_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L295" class="source-link" title="View source code">source</a>

```python
def register_tool(tool: Tool)
```

Register a tool with the global registry.

## get_tool_schemas <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L300" class="source-link" title="View source code">source</a>

```python
def get_tool_schemas(tool_names: List[str]) -> List[Dict[str, Any]]
```

Get tool schemas from the global registry.

## get_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L305" class="source-link" title="View source code">source</a>

```python
def get_tool(name: str) -> Optional[tuple[Tool, Callable, Optional[BaseModel]]]
```

Get a tool from the global registry.

## list_tools <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L310" class="source-link" title="View source code">source</a>

```python
def list_tools() -> List[str]
```

List all registered tool names.

## execute_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L315" class="source-link" title="View source code">source</a>

```python
async def execute_tool(name: str) -> ToolResult
```

Execute a tool from the global registry.

## print_available_tools <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L320" class="source-link" title="View source code">source</a>

```python
def print_available_tools()
```

Prints a formatted table of all available tools.

## validate_agent_tools <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L338" class="source-link" title="View source code">source</a>

```python
def validate_agent_tools(tool_names: List[str]) -> tuple[List[str], List[str]]
```

Validate a list of tool names against the registry.

**Returns:**
    A tuple of (valid_tools, invalid_tools)

## suggest_tools_for_agent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/tool.py#L354" class="source-link" title="View source code">source</a>

```python
def suggest_tools_for_agent(agent_name: str, agent_description: str = '') -> List[str]
```

Suggest a list of relevant tools for a new agent.
(This is a placeholder for a more intelligent suggestion mechanism)
