# Storage Interfaces

_Module: [`vibex.storage.interfaces`](https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py)_

Storage interfaces - Clean abstractions for different types of storage operations.

## StorageResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L13" class="source-link" title="View source code">source</a>

Result of a storage operation.

## FileInfo <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L30" class="source-link" title="View source code">source</a>

Information about a stored file.

## StorageBackend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L44" class="source-link" title="View source code">source</a>

Base interface for all storage backends.

### exists <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L48" class="source-link" title="View source code">source</a>

```python
async def exists(self, path: str) -> bool
```

Check if a path exists.

### get_info <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L53" class="source-link" title="View source code">source</a>

```python
async def get_info(self, path: str) -> Optional[FileInfo]
```

Get information about a file/directory.

### list_directory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L58" class="source-link" title="View source code">source</a>

```python
async def list_directory(self, path: str = '.') -> List[FileInfo]
```

List contents of a directory.

## FileStorage <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L63" class="source-link" title="View source code">source</a>

Interface for file storage operations.

### read_text <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L67" class="source-link" title="View source code">source</a>

```python
async def read_text(self, path: str, encoding: str = 'utf-8') -> str
```

Read text content from a file.

### write_text <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L72" class="source-link" title="View source code">source</a>

```python
async def write_text(self, path: str, content: str, encoding: str = 'utf-8') -> StorageResult
```

Write text content to a file.

### read_bytes <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L77" class="source-link" title="View source code">source</a>

```python
async def read_bytes(self, path: str) -> bytes
```

Read binary content from a file.

### write_bytes <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L82" class="source-link" title="View source code">source</a>

```python
async def write_bytes(self, path: str, content: bytes) -> StorageResult
```

Write binary content to a file.

### append_text <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L87" class="source-link" title="View source code">source</a>

```python
async def append_text(self, path: str, content: str, encoding: str = 'utf-8') -> StorageResult
```

Append text content to a file.

### delete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L92" class="source-link" title="View source code">source</a>

```python
async def delete(self, path: str) -> StorageResult
```

Delete a file.

### create_directory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L97" class="source-link" title="View source code">source</a>

```python
async def create_directory(self, path: str) -> StorageResult
```

Create a directory.

## ArtifactStorage <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L102" class="source-link" title="View source code">source</a>

Interface for artifact storage with versioning and metadata.

### store_artifact <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L106" class="source-link" title="View source code">source</a>

```python
async def store_artifact(self, name: str, content: Union[str, bytes], content_type: str = 'text/plain', metadata: Optional[Dict[str, Any]] = None) -> StorageResult
```

Store an artifact with versioning.

### get_artifact <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L117" class="source-link" title="View source code">source</a>

```python
async def get_artifact(self, name: str, version: Optional[str] = None) -> Optional[str]
```

Get artifact content by name and optional version.

### list_artifacts <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L122" class="source-link" title="View source code">source</a>

```python
async def list_artifacts(self) -> List[Dict[str, Any]]
```

List all artifacts with their metadata.

### get_artifact_versions <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L127" class="source-link" title="View source code">source</a>

```python
async def get_artifact_versions(self, name: str) -> List[str]
```

Get all versions of an artifact.

### delete_artifact <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/interfaces.py#L132" class="source-link" title="View source code">source</a>

```python
async def delete_artifact(self, name: str, version: Optional[str] = None) -> StorageResult
```

Delete an artifact or specific version.
