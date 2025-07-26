# Configuration Models

*Module: [`vibex.storage.config`](https://github.com/dustland/vibex/blob/main/src/vibex/storage/config.py)*

Storage configuration singleton.

Allows server to configure storage settings once at startup,
which are then used by all storage instances.

## StorageConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/config.py#L12" class="source-link" title="View source code">source</a>

Singleton configuration for storage system.

### set_cache_backend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/config.py#L23" class="source-link" title="View source code">source</a>

```python
def set_cache_backend(self, cache_backend: Optional[CacheBackend] = None)
```

Set the cache backend for storage operations.

**Args:**
    cache_backend: Cache backend to use, or None to disable caching

### cache_backend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/config.py#L33" class="source-link" title="View source code">source</a>

```python
def cache_backend(self) -> Optional[CacheBackend]
```

Get configured cache backend.

### is_caching_enabled <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/config.py#L38" class="source-link" title="View source code">source</a>

```python
def is_caching_enabled(self) -> bool
```

Check if caching is enabled.

### reset <a href="https://github.com/dustland/vibex/blob/main/src/vibex/storage/config.py#L42" class="source-link" title="View source code">source</a>

```python
def reset(self)
```

Reset configuration to defaults.
