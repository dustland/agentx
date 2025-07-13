# Git Storage

*Module: [`agentx.storage.git_storage`](https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py)*

Git-based artifact storage - Uses Git for proper versioning.

Provides Git-based versioning for artifacts, especially useful for code generation
where we need proper diffs, branching, and version history.

## GitArtifactStorage <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L31" class="source-link" title="View source code">source</a>

Git-based artifact storage with proper version control.

Uses Git for versioning artifacts, providing:
- Proper diffs and history
- Branching and merging capabilities
- Standard Git tooling integration
- Efficient storage with delta compression
- Meaningful commit messages

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L43" class="source-link" title="View source code">source</a>

```python
def __init__(self, workspace_path: Union[str, Path] = None, base_path: Union[str, Path] = None, task_id: str = None)
```
### store_artifact <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L89" class="source-link" title="View source code">source</a>

```python
async def store_artifact(self, name: str, content: Union[str, bytes], content_type: str = 'text/plain', metadata: Optional[Dict[str, Any]] = None, commit_message: Optional[str] = None) -> StorageResult
```

Store an artifact with Git versioning.

### get_artifact <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L158" class="source-link" title="View source code">source</a>

```python
async def get_artifact(self, name: str, version: Optional[str] = None) -> Optional[str]
```

Get artifact content at specific version (commit).

### list_artifacts <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L181" class="source-link" title="View source code">source</a>

```python
async def list_artifacts(self) -> List[Dict[str, Any]]
```

List all artifacts with their Git history.

### get_artifact_versions <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L218" class="source-link" title="View source code">source</a>

```python
async def get_artifact_versions(self, name: str) -> List[str]
```

Get all versions (commits) of an artifact.

### delete_artifact <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L235" class="source-link" title="View source code">source</a>

```python
async def delete_artifact(self, name: str, version: Optional[str] = None) -> StorageResult
```

Delete an artifact or specific version.

### get_artifact_diff <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L281" class="source-link" title="View source code">source</a>

```python
async def get_artifact_diff(self, name: str, version1: str, version2: str) -> Optional[str]
```

Get diff between two versions of an artifact.

### list_directory <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L428" class="source-link" title="View source code">source</a>

```python
async def list_directory(self, path: str = '') -> List[Any]
```

List directory contents (returns artifacts for compatibility).

### create_directory <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L452" class="source-link" title="View source code">source</a>

```python
async def create_directory(self, path: str) -> Any
```

Create directory (no-op for git storage).

### exists <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L457" class="source-link" title="View source code">source</a>

```python
async def exists(self, path: str) -> bool
```

Check if artifact exists.

### read_text <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L465" class="source-link" title="View source code">source</a>

```python
async def read_text(self, path: str) -> str
```

Read text content (alias for get_artifact).

### write_text <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L473" class="source-link" title="View source code">source</a>

```python
async def write_text(self, path: str, content: str) -> Any
```

Write text content (alias for store_artifact).

### write_bytes <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/git_storage.py#L481" class="source-link" title="View source code">source</a>

```python
async def write_bytes(self, path: str, content: bytes) -> Any
```

Write bytes content (alias for store_artifact).
