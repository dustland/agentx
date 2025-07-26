# Tool Executor

*Module: [`vibex.tool.executor`](https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py)*

Tool executor for secure and performant tool execution.

The executor is responsible for:
- Secure tool execution with validation
- Performance monitoring and resource limits
- Error handling and result formatting
- Security policies and audit logging

## SecurityPolicy <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L142" class="source-link" title="View source code">source</a>

Security policies for tool execution.

## ToolExecutor <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L160" class="source-link" title="View source code">source</a>

Secure tool executor with performance monitoring and security policies.

This class handles the actual execution of tools with:
- Security validation and permissions
- Resource limits and monitoring
- Error handling and logging
- Audit trails

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L171" class="source-link" title="View source code">source</a>

```python
def __init__(self, registry: Optional[ToolRegistry] = None)
```

Initialize tool executor.

**Args:**
    registry: Tool registry to use (defaults to global registry)

### execute_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L185" class="source-link" title="View source code">source</a>

```python
async def execute_tool(self, tool_name: str, agent_name: str = 'default') -> ToolResult
```

Execute a single tool with security validation.

**Args:**
    tool_name: Name of the tool to execute
    agent_name: Name of the agent requesting execution (for permissions)
    **kwargs: Tool arguments

**Returns:**
    ToolResult with execution outcome

### execute_tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L276" class="source-link" title="View source code">source</a>

```python
async def execute_tools(self, tool_calls: List[Any], agent_name: str = 'default') -> List[Dict[str, Any]]
```

Execute multiple tool calls and return formatted results for LLM.

**Args:**
    tool_calls: List of tool call objects from LLM response
    agent_name: Name of the agent requesting execution

**Returns:**
    List of tool result messages formatted for LLM conversation

### get_execution_stats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L482" class="source-link" title="View source code">source</a>

```python
def get_execution_stats(self) -> Dict[str, Any]
```

Get execution statistics.

### clear_history <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L495" class="source-link" title="View source code">source</a>

```python
def clear_history(self)
```

Clear execution history.

## Functions

## safe_json_serialize <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L25" class="source-link" title="View source code">source</a>

```python
def safe_json_serialize(obj)
```

Safely serialize objects to JSON, handling dataclasses, Pydantic models, and other complex types.

## safe_json_dumps <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L44" class="source-link" title="View source code">source</a>

```python
def safe_json_dumps(obj)
```

Safely serialize objects to JSON with fallback handling.

## truncate_for_logging <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L55" class="source-link" title="View source code">source</a>

```python
def truncate_for_logging(content: str, max_length: int = 500) -> str
```

Truncate content for logging purposes while preserving readability.

**Args:**
    content: Content to truncate
    max_length: Maximum length before truncation

**Returns:**
    Truncated content with ellipsis if needed

## safe_json_dumps_for_logging <a href="https://github.com/dustland/vibex/blob/main/src/vibex/tool/executor.py#L73" class="source-link" title="View source code">source</a>

```python
def safe_json_dumps_for_logging(obj, max_content_length: int = 500)
```

Safely serialize objects to JSON with content truncation for logging.

**Args:**
    obj: Object to serialize
    max_content_length: Maximum length for content fields before truncation
    **kwargs: Additional JSON serialization arguments

**Returns:**
    JSON string with truncated content for logging
