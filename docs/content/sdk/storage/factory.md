# Storage Factory

*Module: [`agentx.storage.factory`](https://github.com/dustland/agentx/blob/main/src/agentx/storage/factory.py)*

Storage factory - Creates storage providers using factory pattern.

Separates pure filesystem abstraction from business logic.

## StorageFactory <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/factory.py#L18" class="source-link" title="View source code">source</a>

Factory for creating storage providers.

Creates filesystem abstractions that can be swapped for different backends
(local, S3, Azure, etc.) and taskspace storage for business logic.

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

### create_taskspace_storage <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/factory.py#L48" class="source-link" title="View source code">source</a>

```python
def create_taskspace_storage(taskspace_path: Union[str, Path] = None, use_git_artifacts: bool = True, base_path: Union[str, Path] = None, task_id: str = None, user_id: str = None) -> TaskspaceStorage
```

Create a taskspace storage for business logic.

Handles business concepts like artifacts, messages, execution plans
using the filesystem abstraction underneath.

**Args:**
    taskspace_path: Path to the taskspace directory (old API)
    use_git_artifacts: Whether to use Git for artifact versioning
    base_path: Base path for multi-tenant taskspaces (new API)
    task_id: Task ID for taskspace isolation (new API)
    user_id: User ID for multi-tenant isolation (new API)

**Returns:**
    TaskspaceStorage instance
