# Tool System

*Module: [`vibex.core.tool`](https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py)*

Tool component for function calling and code execution.

This is the single canonical source for all tool-related models and functionality.

## ToolFunction <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L28" class="source-link" title="View source code">source</a>

A single callable function within a tool.

## ToolCall <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L40" class="source-link" title="View source code">source</a>

Tool call specification with retry policy.

## ToolResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L50" class="source-link" title="View source code">source</a>

Canonical tool execution result model.

This is the single source of truth for tool execution results across the framework.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L75" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L81" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary for JSON serialization.

### to_json <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L85" class="source-link" title="View source code">source</a>

```python
def to_json(self) -> str
```

Convert to JSON string.

### success_result <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L90" class="source-link" title="View source code">source</a>

```python
def success_result(cls, result: Any) -> 'ToolResult'
```

Create a successful result.

### error_result <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L95" class="source-link" title="View source code">source</a>

```python
def error_result(cls, error: str) -> 'ToolResult'
```

Create an error result.

## ToolRegistryEntry <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L104" class="source-link" title="View source code">source</a>

Entry in the tool registry.

## ToolExecutionContext <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L121" class="source-link" title="View source code">source</a>

Context information for tool execution.

## ToolExecutionStats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L132" class="source-link" title="View source code">source</a>

Statistics for tool execution.

## Tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L271" class="source-link" title="View source code">source</a>

Base class for tools that provide multiple callable methods for LLMs.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L274" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str = '')
```
### get_callable_methods <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L277" class="source-link" title="View source code">source</a>

```python
def get_callable_methods(self) -> Dict[str, Callable]
```

Get all methods marked with @tool decorator.

### get_tool_schemas <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L287" class="source-link" title="View source code">source</a>

```python
def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]
```

Get detailed OpenAI function schemas for all callable methods using Pydantic.

## Functions

## safe_json_serialize <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L147" class="source-link" title="View source code">source</a>

```python
def safe_json_serialize(obj: Any) -> Any
```

Safely serialize complex objects to JSON-compatible format.
Handles dataclasses, Pydantic models, and other complex types.

## safe_json_dumps <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L174" class="source-link" title="View source code">source</a>

```python
def safe_json_dumps(obj: Any) -> str
```

Safely dump complex objects to JSON string.
Uses safe_json_serialize to handle complex types.

## tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/tool.py#L187" class="source-link" title="View source code">source</a>

```python
def tool(description: str = '', return_description: str = '')
```

Decorator to mark methods as available tool calls.

**Args:**
    description: Clear description of what this tool does
    return_description: Description of what the tool returns
