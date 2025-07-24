# File Operations

_Module: [`vibex.builtin_tools.file`](https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py)_

File operations for VibeX.

## FileTool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L17" class="source-link" title="View source code">source</a>

File tool that works with taskspace artifacts and provides simple file operations.

### **init** <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L20" class="source-link" title="View source code">source</a>

```python
def __init__(self, taskspace_storage: TaskspaceStorage)
```

### write_file <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L34" class="source-link" title="View source code">source</a>

```python
async def write_file(self, filename: Annotated[str, "Name of the file (e.g., 'report.html', 'requirements.md')"], content: Annotated[str, 'Content to write to the file']) -> ToolResult
```

Write content to file as a taskspace artifact with versioning.

### append_file <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L87" class="source-link" title="View source code">source</a>

```python
async def append_file(self, filename: Annotated[str, 'Name of the file to append to'], content: Annotated[str, 'Content to append to the file'], separator: Annotated[str, 'Separator between existing and new content (default: newline)'] = '\n') -> ToolResult
```

Append content to an existing file. Creates the file if it doesn't exist.

WARNING: This tool should NOT be used for structured files like:

- HTML files (will add content after closing tags)
- XML files (will break document structure)
- JSON files (will create invalid JSON)

For structured files, read the entire content, modify it, and use write_file instead.

### read_file <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L155" class="source-link" title="View source code">source</a>

```python
async def read_file(self, filename: Annotated[str, 'Name of the file to read'], version: Annotated[Optional[str], 'Specific version to read (optional, defaults to latest)'] = None) -> ToolResult
```

Read file contents from taskspace artifacts.

### list_files <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L192" class="source-link" title="View source code">source</a>

```python
async def list_files(self) -> ToolResult
```

List all file artifacts in the taskspace.

### file_exists <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L254" class="source-link" title="View source code">source</a>

```python
async def file_exists(self, filename: Annotated[str, 'Name of the file to check']) -> ToolResult
```

Check if a file artifact exists in the taskspace.

### delete_file <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L312" class="source-link" title="View source code">source</a>

```python
async def delete_file(self, filename: Annotated[str, 'Name of the file to delete'], version: Annotated[Optional[str], 'Specific version to delete (optional, deletes all versions if not specified)'] = None) -> ToolResult
```

Delete a file artifact from the taskspace.

### get_file_versions <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L352" class="source-link" title="View source code">source</a>

```python
async def get_file_versions(self, filename: Annotated[str, 'Name of the file to get versions for']) -> ToolResult
```

Get version history of a file artifact.

### get_taskspace_summary <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L415" class="source-link" title="View source code">source</a>

```python
async def get_taskspace_summary(self) -> ToolResult
```

Get a summary of the taskspace contents.

### create_directory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L453" class="source-link" title="View source code">source</a>

```python
async def create_directory(self, path: Annotated[str, "Directory path to create (e.g., 'reports', 'data/sources')"]) -> ToolResult
```

Create a directory in the taskspace using the underlying file storage.

### list_directory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L492" class="source-link" title="View source code">source</a>

```python
async def list_directory(self, path: Annotated[str, 'Directory path to list (defaults to taskspace root)'] = '') -> ToolResult
```

List the contents of a directory in the taskspace.

## Functions

## create_file_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/file.py#L570" class="source-link" title="View source code">source</a>

```python
def create_file_tool(taskspace_path: str) -> FileTool
```

Create a file tool for taskspace operations.

**Args:**
taskspace_path: Path to the taskspace directory

**Returns:**
FileTool instance that properly uses taskspace abstraction
