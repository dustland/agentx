"""
No-operation cache provider implementation.

Used to disable caching entirely.
"""

from typing import Any, Optional

from ...interfaces import CacheBackend
from ....utils.logger import get_logger

logger = get_logger(__name__)


class NoOpCacheProvider(CacheBackend):
    """
    No-operation cache provider that disables caching.
    
    All operations are no-ops, effectively disabling the cache layer.
    Useful for debugging or when caching is not desired.
    """
    
    def __init__(self):
        """Initialize no-op cache provider."""
        logger.info("Initialized NoOpCacheProvider (caching disabled)")
    
    async def get(self, key: str) -> Optional[Any]:
        """Always returns None (cache miss)."""
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 0) -> None:
        """Does nothing."""
        pass
    
    async def delete(self, key: str) -> None:
        """Does nothing."""
        pass
    
    async def clear(self) -> None:
        """Does nothing."""
        pass