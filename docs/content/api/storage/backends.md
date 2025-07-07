# Storage Backends

*Module: [`agentx.storage.backends`](https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py)*

Storage backend implementations.

## LocalFileStorage <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L19" class="source-link" title="View source code">source</a>

Local filesystem storage backend with security constraints.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L22" class="source-link" title="View source code">source</a>

```python
def __init__(self, base_path: Union[str, Path])
```
### exists <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L39" class="source-link" title="View source code">source</a>

```python
async def exists(self, path: str) -> bool
```

Check if a path exists.

### get_info <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L47" class="source-link" title="View source code">source</a>

```python
async def get_info(self, path: str) -> Optional[FileInfo]
```

Get information about a file/directory.

### list_directory <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L67" class="source-link" title="View source code">source</a>

```python
async def list_directory(self, path: str = '.') -> List[FileInfo]
```

List contents of a directory.

### read_text <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L100" class="source-link" title="View source code">source</a>

```python
async def read_text(self, path: str, encoding: str = 'utf-8') -> str
```

Read text content from a file.

### write_text <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L118" class="source-link" title="View source code">source</a>

```python
async def write_text(self, path: str, content: str, encoding: str = 'utf-8') -> StorageResult
```

Write text content to a file.

### read_bytes <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L144" class="source-link" title="View source code">source</a>

```python
async def read_bytes(self, path: str) -> bytes
```

Read binary content from a file.

### write_bytes <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L154" class="source-link" title="View source code">source</a>

```python
async def write_bytes(self, path: str, content: bytes) -> StorageResult
```

Write binary content to a file.

### append_text <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L180" class="source-link" title="View source code">source</a>

```python
async def append_text(self, path: str, content: str, encoding: str = 'utf-8') -> StorageResult
```

Append text content to a file.

### delete <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L206" class="source-link" title="View source code">source</a>

```python
async def delete(self, path: str) -> StorageResult
```

Delete a file.

### create_directory <a href="https://github.com/dustland/agentx/blob/main/src/agentx/storage/backends.py#L237" class="source-link" title="View source code">source</a>

```python
async def create_directory(self, path: str) -> StorageResult
```

Create a directory.
