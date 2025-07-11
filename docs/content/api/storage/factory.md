# Storage Factory

*Module: [`agentx.storage.factory`](https://github.com/dustland/agentx/blob/main/src/agentx/storage/factory.py)*

Storage factory - Creates storage providers using factory pattern.

Separates pure filesystem abstraction from business logic.

## StorageFactory <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/factory.py#L18" class="source-link" title="View source code">source</a>

Factory for creating storage providers.

Creates filesystem abstractions that can be swapped for different backends
(local, S3, Azure, etc.) and workspace storage for business logic.

### create_file_storage <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/factory.py#L27" class="source-link" title="View source code">source</a>

```python
def create_file_storage(base_path: Union[str, Path]) -> FileStorage
```

Create a filesystem abstraction.

This can be swapped for different backends like S3FileStorage,
AzureFileStorage, etc. without changing the business logic.

**Args:**
    base_path: Base path for the filesystem

**Returns:**
    FileStorage implementation

### create_workspace_storage <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/factory.py#L48" class="source-link" title="View source code">source</a>

```python
def create_workspace_storage(workspace_path: Union[str, Path], use_git_artifacts: bool = True) -> WorkspaceStorage
```

Create a workspace storage for business logic.

Handles business concepts like artifacts, messages, execution plans
using the filesystem abstraction underneath.

**Args:**
    workspace_path: Path to the workspace directory
    use_git_artifacts: Whether to use Git for artifact versioning

**Returns:**
    WorkspaceStorage instance
