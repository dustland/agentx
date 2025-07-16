"""
Redis cache backend implementation for server deployments.

Provides Redis-based caching for multi-worker scenarios.
"""

import json
from typing import Any, Optional

from ..storage.interfaces import CacheBackend
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RedisCacheBackend(CacheBackend):
    """Redis cache backend for multi-worker scenarios"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/1"):
        self.redis_url = redis_url
        self._redis = None
    
    async def _ensure_connected(self):
        """Ensure Redis connection is established"""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self.redis_url, decode_responses=True)
                await self._redis.ping()
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
            value = await self._redis.get(key)
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
                await self._redis.setex(key, ttl, json_value)
            else:
                await self._redis.set(key, json_value)
        except Exception as e:
            logger.warning(f"Redis set failed for key {key}: {e}")
            # Fail silently - cache is optional
    
    async def delete(self, key: str) -> None:
        """Delete value from Redis"""
        try:
            await self._ensure_connected()
            await self._redis.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete failed for key {key}: {e}")
    
    async def clear(self) -> None:
        """Clear all cache entries (use with caution)"""
        try:
            await self._ensure_connected()
            await self._redis.flushdb()
        except Exception as e:
            logger.warning(f"Redis clear failed: {e}")