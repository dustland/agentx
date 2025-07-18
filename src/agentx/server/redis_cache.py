"""
Redis cache backend implementation for server deployments.

Provides Redis-based caching for multi-worker scenarios.
"""

import json
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from redis.asyncio import Redis

from ..storage.interfaces import CacheBackend
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Optional Redis support
try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    redis = None
    HAS_REDIS = False


class RedisCacheBackend(CacheBackend):
    """Redis cache backend for multi-worker scenarios"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/1"):
        self.redis_url = redis_url
        self._redis: Optional['Redis'] = None
    
    async def _ensure_connected(self):
        """Ensure Redis connection is established"""
        if self._redis is None:
            if not HAS_REDIS:
                raise ImportError(
                    "Redis is not installed. Install it with: pip install redis[asyncio]"
                )
            try:
                self._redis = redis.from_url(self.redis_url, decode_responses=True)  # type: ignore
                await self._redis.ping()  # type: ignore
                logger.info(f"Connected to Redis cache at {self.redis_url}")
            except ImportError:
                raise ImportError("redis package not installed. Install with: pip install redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            await self._ensure_connected()
            value = await self._redis.get(key)  # type: ignore
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis get failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 0) -> None:
        """Set value in Redis with optional TTL (0 = no expiry)"""
        try:
            await self._ensure_connected()
            json_value = json.dumps(value, default=str)
            if ttl > 0:
                await self._redis.setex(key, ttl, json_value)  # type: ignore
            else:
                await self._redis.set(key, json_value)  # type: ignore
        except Exception as e:
            logger.warning(f"Redis set failed for key {key}: {e}")
            # Fail silently - cache is optional
    
    async def delete(self, key: str) -> None:
        """Delete value from Redis"""
        try:
            await self._ensure_connected()
            await self._redis.delete(key)  # type: ignore
        except Exception as e:
            logger.warning(f"Redis delete failed for key {key}: {e}")
    
    async def clear(self) -> None:
        """Clear all cache entries (use with caution)"""
        try:
            await self._ensure_connected()
            await self._redis.flushdb()  # type: ignore
        except Exception as e:
            logger.warning(f"Redis clear failed: {e}")