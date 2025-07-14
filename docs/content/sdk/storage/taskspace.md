# Taskspace Management

*Module: [`agentx.storage.taskspace`](https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py)*

Taskspace storage - Business logic layer for taskspace management.

Handles business concepts like execution plans, messages, artifacts, etc.
Uses the filesystem abstraction layer underneath.

## TaskspaceStorage <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L20" class="source-link" title="View source code">source</a>

Taskspace storage that handles business concepts.

Manages execution plans, messages, artifacts, and other taskspace
content using a filesystem abstraction underneath.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L28" class="source-link" title="View source code">source</a>

```python
def __init__(self, taskspace_path: Union[str, Path] = None, file_storage: FileStorage = None, use_git_artifacts: bool = True, base_path: Union[str, Path] = None, task_id: str = None, user_id: str = None)
```
### get_taskspace_path <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L98" class="source-link" title="View source code">source</a>

```python
def get_taskspace_path(self) -> Path
```

Get the taskspace path.

### store_artifact <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L103" class="source-link" title="View source code">source</a>

```python
async def store_artifact(self, name: str, content: Union[str, bytes], content_type: str = 'text/plain', metadata: Optional[Dict[str, Any]] = None, commit_message: Optional[str] = None) -> StorageResult
```

Store an artifact with versioning.

### get_artifact <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L121" class="source-link" title="View source code">source</a>

```python
async def get_artifact(self, name: str, version: Optional[str] = None) -> Optional[str]
```

Get artifact content.

### list_artifacts <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L128" class="source-link" title="View source code">source</a>

```python
async def list_artifacts(self) -> List[Dict[str, Any]]
```

List all artifacts.

### get_artifact_versions <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L135" class="source-link" title="View source code">source</a>

```python
async def get_artifact_versions(self, name: str) -> List[str]
```

Get all versions of an artifact.

### delete_artifact <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L142" class="source-link" title="View source code">source</a>

```python
async def delete_artifact(self, name: str, version: Optional[str] = None) -> StorageResult
```

Delete an artifact or specific version.

### get_artifact_diff <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L149" class="source-link" title="View source code">source</a>

```python
async def get_artifact_diff(self, name: str, version1: str, version2: str) -> Optional[str]
```

Get diff between two versions of an artifact (Git only).

### store_message <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L321" class="source-link" title="View source code">source</a>

```python
async def store_message(self, message: Dict[str, Any], conversation_id: str = 'default') -> StorageResult
```

Store a conversation message.

### get_conversation_history <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L348" class="source-link" title="View source code">source</a>

```python
async def get_conversation_history(self, conversation_id: str = 'default') -> List[Dict[str, Any]]
```

Get conversation history.

### store_plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L377" class="source-link" title="View source code">source</a>

```python
async def store_plan(self, plan: Dict[str, Any]) -> StorageResult
```

Store the taskspace plan as plan.json.

### get_plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L390" class="source-link" title="View source code">source</a>

```python
async def get_plan(self) -> Optional[Dict[str, Any]]
```

Get the taskspace plan from plan.json.

### list_directory <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L404" class="source-link" title="View source code">source</a>

```python
async def list_directory(self, path: str = '') -> Dict[str, Any]
```

List contents of a directory in the taskspace.

### get_taskspace_summary <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/taskspace.py#L437" class="source-link" title="View source code">source</a>

```python
async def get_taskspace_summary(self) -> Dict[str, Any]
```

Get a summary of taskspace contents.
