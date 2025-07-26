# Project

*Module: [`vibex.storage.project`](https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py)*

Project storage - Business logic layer for project storage management.

Handles all project-related storage including workspace (artifacts), logs, 
chat history, execution plans, etc. Uses the filesystem abstraction layer underneath.

## ProjectStorage <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L20" class="source-link" title="View source code">source</a>

Project storage that handles all project-related data.

Manages execution plans, messages, artifacts (in workspace/), logs,
chat history, and other project
content using a filesystem abstraction underneath.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L29" class="source-link" title="View source code">source</a>

```python
def __init__(self, base_path: Union[str, Path], project_id: str, file_storage: FileStorage = None, use_git_artifacts: bool = True, cache_backend: Optional[CacheBackend] = None)
```
### get_project_path <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L91" class="source-link" title="View source code">source</a>

```python
def get_project_path(self) -> Path
```

Get the project path.

### store_artifact <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L96" class="source-link" title="View source code">source</a>

```python
async def store_artifact(self, name: str, content: Union[str, bytes], content_type: str = 'text/plain', metadata: Optional[Dict[str, Any]] = None, commit_message: Optional[str] = None) -> StorageResult
```

Store an artifact with versioning.

### get_artifact <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L125" class="source-link" title="View source code">source</a>

```python
async def get_artifact(self, name: str, version: Optional[str] = None) -> Optional[str]
```

Get artifact content with caching.

### list_artifacts <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L148" class="source-link" title="View source code">source</a>

```python
async def list_artifacts(self) -> List[Dict[str, Any]]
```

List all artifacts with caching.

### get_artifact_versions <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L171" class="source-link" title="View source code">source</a>

```python
async def get_artifact_versions(self, name: str) -> List[str]
```

Get all versions of an artifact.

### delete_artifact <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L178" class="source-link" title="View source code">source</a>

```python
async def delete_artifact(self, name: str, version: Optional[str] = None) -> StorageResult
```

Delete an artifact or specific version.

### get_artifact_diff <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L204" class="source-link" title="View source code">source</a>

```python
async def get_artifact_diff(self, name: str, version1: str, version2: str) -> Optional[str]
```

Get diff between two versions of an artifact (Git only).

### store_message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L376" class="source-link" title="View source code">source</a>

```python
async def store_message(self, message: Dict[str, Any], conversation_id: str = 'default') -> StorageResult
```

Store a conversation message.

### get_conversation_history <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L408" class="source-link" title="View source code">source</a>

```python
async def get_conversation_history(self, conversation_id: str = 'default') -> List[Dict[str, Any]]
```

Get conversation history with caching.

### save_file <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L453" class="source-link" title="View source code">source</a>

```python
async def save_file(self, path: str, content: Union[str, Dict[str, Any]]) -> StorageResult
```

Save a file with JSON content.

### read_file <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L465" class="source-link" title="View source code">source</a>

```python
async def read_file(self, path: str) -> Optional[str]
```

Read a file from storage.

### store_plan <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L475" class="source-link" title="View source code">source</a>

```python
async def store_plan(self, plan: Dict[str, Any]) -> StorageResult
```

Store the project plan as plan.json with write-through caching.

### get_plan <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L495" class="source-link" title="View source code">source</a>

```python
async def get_plan(self) -> Optional[Dict[str, Any]]
```

Get the project plan from plan.json with caching.

### list_directory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L525" class="source-link" title="View source code">source</a>

```python
async def list_directory(self, path: str = '') -> Dict[str, Any]
```

List contents of a directory in the project.

### get_project_summary <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/project.py#L558" class="source-link" title="View source code">source</a>

```python
async def get_project_summary(self) -> Dict[str, Any]
```

Get a summary of project contents with caching.
