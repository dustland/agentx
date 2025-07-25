"""
VibeX Storage - Clean persistence abstractions for the framework.

Provides storage backends and interfaces that can be used directly by the framework
and wrapped as tools for LLM agents.
"""

from .interfaces import StorageBackend, FileStorage, ArtifactStorage, StorageResult, StorageProvider, CacheBackend
from .backends import LocalFileStorage
from .factory import ProjectStorageFactory
from .project import ProjectStorage
from .git_storage import GitArtifactStorage
from .config import storage_config
from .providers.cache import MemoryCacheProvider, NoOpCacheProvider
from .providers.storage import FileStorageProvider

__all__ = [
    "StorageBackend",
    "FileStorage",
    "ArtifactStorage",
    "StorageResult",
    "StorageProvider",
    "CacheBackend",
    "LocalFileStorage",
    "ProjectStorageFactory",
    "ProjectStorage",
    "GitArtifactStorage",
    "storage_config",
    "MemoryCacheProvider",
    "NoOpCacheProvider",
    "FileStorageProvider"
]
