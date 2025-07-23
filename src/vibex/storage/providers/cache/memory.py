"""
Memory-based cache provider implementation.

In-process LRU cache for single instance deployments.
"""

from datetime import datetime, timedelta, UTC
from typing import Any, Optional, Dict
import asyncio
from collections import OrderedDict

from ...interfaces import CacheBackend
from ....utils.logger import get_logger

logger = get_logger(__name__)


class MemoryCacheProvider(CacheBackend):
    """
    In-memory cache provider with LRU eviction.
    
    Suitable for single-process deployments and local development.
    Uses OrderedDict for efficient LRU implementation.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize memory cache provider.
        
        Args:
            max_size: Maximum number of entries to cache
        """
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._expiry: Dict[str, datetime] = {}
        self._max_size = max_size
        self._lock = asyncio.Lock()
        logger.info(f"Initialized MemoryCacheProvider with max_size={max_size}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        async with self._lock:
            if key in self._cache:
                # Check expiry
                if key in self._expiry and self._expiry[key] > datetime.now(UTC):
                    # Move to end for LRU
                    self._cache.move_to_end(key)
                    return self._cache[key]
                else:
                    # Expired or no expiry tracking
                    if key in self._expiry:
                        del self._cache[key]
                        del self._expiry[key]
                    else:
                        # No expiry = cached forever
                        self._cache.move_to_end(key)
                        return self._cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 0) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (0 = no expiry)
        """
        async with self._lock:
            # Remove oldest if at capacity
            if len(self._cache) >= self._max_size and key not in self._cache:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._expiry.pop(oldest_key, None)
            
            self._cache[key] = value
            
            # Only track expiry if TTL is set
            if ttl > 0:
                self._expiry[key] = datetime.now(UTC) + timedelta(seconds=ttl)
            elif key in self._expiry:
                # Remove expiry if TTL is 0
                del self._expiry[key]
                
            self._cache.move_to_end(key)
    
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        async with self._lock:
            self._cache.pop(key, None)
            self._expiry.pop(key, None)
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._expiry.clear()
            logger.info("Cleared all cache entries")