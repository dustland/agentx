# Redis Cache

*Module: [`vibex.server.redis_cache`](https://github.com/dustland/vibex/blob/main/src/vibex/server/redis_cache.py)*

Redis cache backend implementation for server deployments.

Provides Redis-based caching for multi-worker scenarios.

## RedisCacheBackend <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/redis_cache.py#L27" class="source-link" title="View source code">source</a>

Redis cache backend for multi-worker scenarios

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/redis_cache.py#L30" class="source-link" title="View source code">source</a>

```python
def __init__(self, redis_url: str = 'redis://localhost:6379/1')
```
### get <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/redis_cache.py#L51" class="source-link" title="View source code">source</a>

```python
async def get(self, key: str) -> Optional[Any]
```

Get value from Redis

### set <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/redis_cache.py#L63" class="source-link" title="View source code">source</a>

```python
async def set(self, key: str, value: Any, ttl: int = 0) -> None
```

Set value in Redis with optional TTL (0 = no expiry)

### delete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/redis_cache.py#L76" class="source-link" title="View source code">source</a>

```python
async def delete(self, key: str) -> None
```

Delete value from Redis

### clear <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/redis_cache.py#L84" class="source-link" title="View source code">source</a>

```python
async def clear(self) -> None
```

Clear all cache entries (use with caution)
