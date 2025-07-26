# Context Tool

*Module: [`vibex.builtin_tools.context`](https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/context.py)*

Context Management Tools - LLM-friendly context tracking and management.

Provides flexible context management with loose JSON parsing and natural language
queries. Designed to work seamlessly with LLM agents without strict formatting.

## ContextTool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/context.py#L19" class="source-link" title="View source code">source</a>

Generic context management tool for tracking project state, variables, and metadata.

Features:
- Loose JSON parsing (handles malformed JSON gracefully)
- Natural language queries for context retrieval
- Flexible key-value storage with nested objects
- Automatic timestamping and versioning
- File-based persistence with backup

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/context.py#L31" class="source-link" title="View source code">source</a>

```python
def __init__(self, context_file: str = 'context.json', project_path: str = './.vibex/projects')
```
### update_context <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/context.py#L149" class="source-link" title="View source code">source</a>

```python
async def update_context(self, updates: str, merge_strategy: str = 'merge') -> ToolResult
```

Update context variables with loose JSON parsing.

**Args:**
    updates: JSON string or key-value pairs to update (flexible format)
    merge_strategy: How to handle updates - "merge", "replace", or "append"

**Returns:**
    ToolResult with success status and updated context summary

### get_context <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/context.py#L232" class="source-link" title="View source code">source</a>

```python
async def get_context(self, query: str = '', keys: Optional[str] = None, format_output: str = 'json') -> ToolResult
```

Retrieve context data with flexible querying.

**Args:**
    query: Natural language query or empty for all context
    keys: Comma-separated list of specific keys to retrieve
    format_output: Output format - "json", "text", or "summary"

**Returns:**
    ToolResult with requested context data

### clear_context <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/context.py#L315" class="source-link" title="View source code">source</a>

```python
async def clear_context(self, backup: bool = True, keep_metadata: bool = True) -> ToolResult
```

Clear context data with optional backup.

**Args:**
    backup: Whether to create a backup before clearing
    keep_metadata: Whether to preserve metadata

**Returns:**
    ToolResult with operation status
