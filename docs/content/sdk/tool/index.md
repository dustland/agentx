# Tool System

*Module: [`vibex.tool`](https://github.com/dustland/vibex/blob/main/src/vibex/tool.py)*

Tool execution framework for VibeX.

This module provides:
- Tool registration and discovery
- Secure tool execution with performance monitoring
- Tool result formatting and error handling
- Unified tool management for task isolation

## register_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool.py#L20" class="source-link" title="View source code">source</a>

```python
def register_tool(tool: Tool)
```
## register_function <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool.py#L23" class="source-link" title="View source code">source</a>

```python
def register_function(func, name = None)
```
## list_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool.py#L26" class="source-link" title="View source code">source</a>

```python
def list_tools()
```
## get_tool_schemas <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool.py#L29" class="source-link" title="View source code">source</a>

```python
def get_tool_schemas(tool_names = None)
```
## validate_agent_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool.py#L32" class="source-link" title="View source code">source</a>

```python
def validate_agent_tools(tool_names: list[str]) -> tuple[list[str], list[str]]
```

Validate a list of tool names against the registry.

**Returns:**
    A tuple of (valid_tools, invalid_tools)

## suggest_tools_for_agent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool.py#L46" class="source-link" title="View source code">source</a>

```python
def suggest_tools_for_agent(agent_name: str, agent_description: str = '') -> list[str]
```

Suggest a list of relevant tools for a new agent.
(This is a placeholder for a more intelligent suggestion mechanism)
