"""
Storage configuration singleton.

Allows server to configure storage settings once at startup,
which are then used by all storage instances.
"""

from typing import Optional
from .interfaces import CacheBackend


class StorageConfig:
    """Singleton configuration for storage system."""
    
    _instance = None
    _cache_backend: Optional[CacheBackend] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def set_cache_backend(self, cache_backend: Optional[CacheBackend] = None):
        """
        Set the cache backend for storage operations.
        
        Args:
            cache_backend: Cache backend to use, or None to disable caching
        """
        self._cache_backend = cache_backend
    
    @property
    def cache_backend(self) -> Optional[CacheBackend]:
        """Get configured cache backend."""
        return self._cache_backend
    
    @property
    def is_caching_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._cache_backend is not None
    
    def reset(self):
        """Reset configuration to defaults."""
        self._cache_backend = None


# Global singleton instance
storage_config = StorageConfig()