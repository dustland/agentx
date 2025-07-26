# Tool Models

*Module: [`vibex.storage.models`](https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py)*

Storage subsystem models - Self-contained data models for storage management.

This module contains all data models related to storage management, following the
architectural rule that subsystems should be self-contained and not import from core.

## StorageBackendType <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L29" class="source-link" title="View source code">source</a>

Types of storage backends.

## ArtifactType <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L39" class="source-link" title="View source code">source</a>

Types of artifacts that can be stored.

## StorageOperation <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L53" class="source-link" title="View source code">source</a>

Types of storage operations.

## FileStatus <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L65" class="source-link" title="View source code">source</a>

File status in storage.

## Artifact <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L78" class="source-link" title="View source code">source</a>

Represents a stored artifact.

### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L106" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary for serialization.

## ArtifactContent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L129" class="source-link" title="View source code">source</a>

Content of an artifact.

### get_text_content <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L136" class="source-link" title="View source code">source</a>

```python
def get_text_content(self) -> str
```

Get content as text.

### get_binary_content <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L142" class="source-link" title="View source code">source</a>

```python
def get_binary_content(self) -> bytes
```

Get content as bytes.

## StorageBackend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L155" class="source-link" title="View source code">source</a>

Abstract interface for storage backend implementations.

### store <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L159" class="source-link" title="View source code">source</a>

```python
async def store(self, path: str, content: Union[str, bytes], artifact_type: ArtifactType = ArtifactType.TEXT, metadata: Dict[str, Any] = None) -> Artifact
```

Store content at the specified path.

### retrieve <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L166" class="source-link" title="View source code">source</a>

```python
async def retrieve(self, path: str) -> Optional[ArtifactContent]
```

Retrieve content from the specified path.

### delete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L171" class="source-link" title="View source code">source</a>

```python
async def delete(self, path: str) -> bool
```

Delete content at the specified path.

### list_artifacts <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L176" class="source-link" title="View source code">source</a>

```python
async def list_artifacts(self, prefix: str = '', artifact_type: Optional[ArtifactType] = None, limit: int = 100) -> List[Artifact]
```

List artifacts with optional filtering.

### get_artifact <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L183" class="source-link" title="View source code">source</a>

```python
async def get_artifact(self, artifact_id: str) -> Optional[Artifact]
```

Get artifact metadata by ID.

### update_metadata <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L188" class="source-link" title="View source code">source</a>

```python
async def update_metadata(self, artifact_id: str, metadata: Dict[str, Any]) -> bool
```

Update artifact metadata.

### copy <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L193" class="source-link" title="View source code">source</a>

```python
async def copy(self, source_path: str, dest_path: str) -> bool
```

Copy artifact from source to destination.

### move <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L198" class="source-link" title="View source code">source</a>

```python
async def move(self, source_path: str, dest_path: str) -> bool
```

Move artifact from source to destination.

### exists <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L203" class="source-link" title="View source code">source</a>

```python
async def exists(self, path: str) -> bool
```

Check if artifact exists at path.

### get_stats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L208" class="source-link" title="View source code">source</a>

```python
async def get_stats(self) -> 'StorageStats'
```

Get storage backend statistics.

### health <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L213" class="source-link" title="View source code">source</a>

```python
async def health(self) -> Dict[str, Any]
```

Get storage backend health information.

## ProjectConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L222" class="source-link" title="View source code">source</a>

Configuration for a project workspace.

## ProjectState <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L249" class="source-link" title="View source code">source</a>

Current state of a project workspace.

## FileInfo <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L276" class="source-link" title="View source code">source</a>

Information about a file in storage.

## DirectoryListing <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L302" class="source-link" title="View source code">source</a>

Listing of directory contents.

### get_all_items <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L311" class="source-link" title="View source code">source</a>

```python
def get_all_items(self) -> List[FileInfo]
```

Get all files and directories combined.

## CommitInfo <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L320" class="source-link" title="View source code">source</a>

Information about a commit.

## BranchInfo <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L339" class="source-link" title="View source code">source</a>

Information about a branch.

## FileChange <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L357" class="source-link" title="View source code">source</a>

Represents a change to a file.

## StorageOperation <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L378" class="source-link" title="View source code">source</a>

Represents a storage operation.

## StorageOperationResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L403" class="source-link" title="View source code">source</a>

Result of a storage operation.

## StorageStats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L418" class="source-link" title="View source code">source</a>

Storage backend statistics.

## StorageHealth <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L445" class="source-link" title="View source code">source</a>

Storage backend health status.

## StorageConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L475" class="source-link" title="View source code">source</a>

Configuration for storage system.

## SearchQuery <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L511" class="source-link" title="View source code">source</a>

Query for searching artifacts.

## SearchResult <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L535" class="source-link" title="View source code">source</a>

Result from artifact search.

## Functions

## generate_short_id <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L19" class="source-link" title="View source code">source</a>

```python
def generate_short_id(length: int = 8) -> str
```

Generate a short, URL-friendly, cryptographically secure random ID.

## create_artifact <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L552" class="source-link" title="View source code">source</a>

```python
def create_artifact(name: str, path: str, artifact_type: ArtifactType, content_size: int = 0, created_by: str = None, project_id: str = None, agent_name: str = None, metadata: Dict[str, Any] = None) -> Artifact
```

Create a new artifact with the specified parameters.

## get_mime_type <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L569" class="source-link" title="View source code">source</a>

```python
def get_mime_type(file_path: str) -> str
```

Get MIME type for a file based on its extension.

## calculate_checksum <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L576" class="source-link" title="View source code">source</a>

```python
def calculate_checksum(content: Union[str, bytes]) -> str
```

Calculate SHA-256 checksum of content.

## format_file_size <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/models.py#L584" class="source-link" title="View source code">source</a>

```python
def format_file_size(size_bytes: int) -> str
```

Format file size in human-readable format.
