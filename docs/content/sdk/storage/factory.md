# Storage Factory

*Module: [`vibex.storage.factory`](https://github.com/dustland/vibex/blob/main/src/vibex/storage/factory.py)*

Storage factory - Creates storage providers using factory pattern.

Separates pure filesystem abstraction from business logic.

## ProjectStorageFactory <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/factory.py#L20" class="source-link" title="View source code">source</a>

Factory for creating project storage with two layers of providers:

1. Storage Providers: Handle actual data persistence (file, S3, Azure, etc.)
2. Cache Providers: Handle performance optimization (memory, Redis, etc.)

### register_storage_provider <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/factory.py#L59" class="source-link" title="View source code">source</a>

```python
def register_storage_provider(cls, name: str, provider_factory: Callable[[Path], FileStorage])
```

Register a storage provider factory.

**Args:**
    name: Name to register the provider under (e.g., "s3", "azure")
    provider_factory: Factory function that creates a FileStorage instance given a path

### get_storage_provider <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/factory.py#L71" class="source-link" title="View source code">source</a>

```python
def get_storage_provider(cls, name: str = 'file') -> Callable[[Path], FileStorage]
```

Get a registered storage provider factory by name.

**Args:**
    name: Name of the storage provider (default: "file")

**Returns:**
    Storage provider factory function

### register_cache_provider <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/factory.py#L86" class="source-link" title="View source code">source</a>

```python
def register_cache_provider(cls, name: str, provider: CacheBackend)
```

Register a cache provider for use in project storage.

**Args:**
    name: Name to register the provider under
    provider: CacheBackend instance

### get_cache_provider <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/factory.py#L98" class="source-link" title="View source code">source</a>

```python
def get_cache_provider(cls, name: Optional[str]) -> Optional[CacheBackend]
```

Get a registered cache provider by name.

**Args:**
    name: Name of the cache provider, or None

**Returns:**
    CacheBackend instance or None

### create_file_storage <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/factory.py#L115" class="source-link" title="View source code">source</a>

```python
def create_file_storage(cls, base_path: Union[str, Path], provider: str = 'file') -> FileStorage
```

Create a filesystem abstraction.

**Args:**
    base_path: Base path for the filesystem
    provider: Name of the storage provider to use (default: "file")

**Returns:**
    FileStorage implementation

### create_project_storage <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/factory.py#L137" class="source-link" title="View source code">source</a>

```python
def create_project_storage(cls, base_path: Union[str, Path], project_id: str, use_git_artifacts: bool = True, storage_provider: str = 'file', cache_provider: Optional[str] = None) -> ProjectStorage
```

Create a project storage for business logic.

Handles business concepts like artifacts, messages, execution plans
using configurable storage and cache providers.

**Args:**
    base_path: Base path for project storage
    project_id: Project ID for storage isolation
    use_git_artifacts: Whether to use Git for artifact versioning
    storage_provider: Name of storage provider to use (default: "file")
    cache_provider: Name of cache provider to use (default: None for no caching)

**Returns:**
    ProjectStorage instance with specified storage and cache providers
