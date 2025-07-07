# File Operations

*Module: [`agentx.builtin_tools.file`](https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py)*

File operations for AgentX.

## FileTool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L17" class="source-link" title="View source code">source</a>

File tool that works with workspace artifacts and provides simple file operations.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L20" class="source-link" title="View source code">source</a>

```python
def __init__(self, workspace_storage: WorkspaceStorage)
```
### write_file <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L34" class="source-link" title="View source code">source</a>

```python
async def write_file(self, filename: Annotated[str, "Name of the file (e.g., 'report.html', 'requirements.md')"], content: Annotated[str, 'Content to write to the file']) -> ToolResult
```

Write content to file as a workspace artifact with versioning.

### read_file <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L87" class="source-link" title="View source code">source</a>

```python
async def read_file(self, filename: Annotated[str, 'Name of the file to read'], version: Annotated[Optional[str], 'Specific version to read (optional, defaults to latest)'] = None) -> ToolResult
```

Read file contents from workspace artifacts.

### list_files <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L124" class="source-link" title="View source code">source</a>

```python
async def list_files(self) -> ToolResult
```

List all file artifacts in the workspace.

### file_exists <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L186" class="source-link" title="View source code">source</a>

```python
async def file_exists(self, filename: Annotated[str, 'Name of the file to check']) -> ToolResult
```

Check if a file artifact exists in the workspace.

### delete_file <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L244" class="source-link" title="View source code">source</a>

```python
async def delete_file(self, filename: Annotated[str, 'Name of the file to delete'], version: Annotated[Optional[str], 'Specific version to delete (optional, deletes all versions if not specified)'] = None) -> ToolResult
```

Delete a file artifact from the workspace.

### get_file_versions <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L284" class="source-link" title="View source code">source</a>

```python
async def get_file_versions(self, filename: Annotated[str, 'Name of the file to get versions for']) -> ToolResult
```

Get version history of a file artifact.

### get_workspace_summary <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L347" class="source-link" title="View source code">source</a>

```python
async def get_workspace_summary(self) -> ToolResult
```

Get a summary of the workspace contents.

### create_directory <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L385" class="source-link" title="View source code">source</a>

```python
async def create_directory(self, path: Annotated[str, "Directory path to create (e.g., 'reports', 'data/sources')"]) -> ToolResult
```

Create a directory in the workspace using the underlying file storage.

### list_directory <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L424" class="source-link" title="View source code">source</a>

```python
async def list_directory(self, path: Annotated[str, 'Directory path to list (defaults to workspace root)'] = '') -> ToolResult
```

List the contents of a directory in the workspace.

## Functions

## create_file_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/file.py#L502" class="source-link" title="View source code">source</a>

```python
def create_file_tool(workspace_path: str) -> FileTool
```

Create a file tool for workspace operations.

**Args:**
    workspace_path: Path to the workspace directory

**Returns:**
    FileTool instance that properly uses workspace abstraction
