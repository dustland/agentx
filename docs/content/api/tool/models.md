# Tool Models

*Module: [`agentx.tool.models`](https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py)*

Tool subsystem models - Self-contained data models for tool execution.

This module contains all data models related to tool execution, following the
architectural rule that subsystems should be self-contained and not import from core.

## ToolFunction <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L36" class="source-link" title="View source code">source</a>

A single callable function within a tool.

## Tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L48" class="source-link" title="View source code">source</a>

Base class for tools that provide multiple callable methods for LLMs.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L51" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str = '')
```
### get_callable_methods <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L54" class="source-link" title="View source code">source</a>

```python
def get_callable_methods(self) -> Dict[str, Callable]
```

Get all methods marked with @tool decorator.

### get_tool_schemas <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L64" class="source-link" title="View source code">source</a>

```python
def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]
```

Get detailed OpenAI function schemas for all callable methods using Pydantic.

## ToolCall <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L109" class="source-link" title="View source code">source</a>

Tool call specification with retry policy.

## ToolResult <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L119" class="source-link" title="View source code">source</a>

Canonical tool execution result model.

This is the single source of truth for tool execution results across the framework.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L144" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### to_dict <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L150" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary for JSON serialization.

### to_json <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L154" class="source-link" title="View source code">source</a>

```python
def to_json(self) -> str
```

Convert to JSON string.

### success_result <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L159" class="source-link" title="View source code">source</a>

```python
def success_result(cls, result: Any) -> 'ToolResult'
```

Create a successful result.

### error_result <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L164" class="source-link" title="View source code">source</a>

```python
def error_result(cls, error: str) -> 'ToolResult'
```

Create an error result.

## ToolRegistryEntry <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L173" class="source-link" title="View source code">source</a>

Entry in the tool registry.

## ToolExecutionContext <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L190" class="source-link" title="View source code">source</a>

Context information for tool execution.

## ToolExecutionStats <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L201" class="source-link" title="View source code">source</a>

Statistics for tool execution.

## Functions

## generate_short_id <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L26" class="source-link" title="View source code">source</a>

```python
def generate_short_id(length: int = 8) -> str
```

Generate a short, URL-friendly, cryptographically secure random ID.

## safe_json_serialize <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L216" class="source-link" title="View source code">source</a>

```python
def safe_json_serialize(obj: Any) -> Any
```

Safely serialize complex objects to JSON-compatible format.
Handles dataclasses, Pydantic models, and other complex types.

## safe_json_dumps <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L243" class="source-link" title="View source code">source</a>

```python
def safe_json_dumps(obj: Any) -> str
```

Safely dump complex objects to JSON string.
Uses safe_json_serialize to handle complex types.

## tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/tool/models.py#L255" class="source-link" title="View source code">source</a>

```python
def tool(description: str = '', return_description: str = '')
```

Decorator to mark a method as a callable tool for an LLM.
