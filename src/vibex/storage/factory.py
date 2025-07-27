"""
Storage factory - Creates storage providers using factory pattern.

Separates pure filesystem abstraction from business logic.
"""

from typing import Union, Optional, Dict, Type, Callable
from pathlib import Path

from .interfaces import FileStorage, CacheBackend
from .backends import LocalFileStorage
from .project import ProjectStorage
from .providers.cache import MemoryCacheProvider, NoOpCacheProvider
from .providers.storage import FileStorageProvider
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ProjectStorageFactory:
    """
    Factory for creating project storage with two layers of providers:
    
    1. Storage Providers: Handle actual data persistence (file, S3, Azure, etc.)
    2. Cache Providers: Handle performance optimization (memory, Redis, etc.)
    """
    
    # Registry for storage providers (file storage backends)
    _storage_providers: Dict[str, Callable[[Path], FileStorage]] = {
        "file": lambda path: LocalFileStorage(path)
    }
    
    # Registry for cache providers
    _cache_providers: Dict[str, CacheBackend] = {}
    
    # Initialize default providers
    _initialized = False
    
    @classmethod
    def _ensure_initialized(cls):
        """Ensure default providers are registered."""
        if not cls._initialized:
            # Register default cache providers
            cls._cache_providers["memory"] = MemoryCacheProvider()
            cls._cache_providers["noop"] = NoOpCacheProvider()
            cls._cache_providers["none"] = NoOpCacheProvider()  # Alias for noop
            
            # Try to register Redis cache provider (server module optional)
            try:
                from ..server.redis_cache import RedisCacheBackend
                cls._cache_providers["redis"] = RedisCacheBackend()
                logger.info("Registered Redis cache provider from server module")
            except ImportError:
                logger.debug("Redis cache provider not available (server module not found)")
            
            cls._initialized = True

    @classmethod
    def register_storage_provider(cls, name: str, provider_factory: Callable[[Path], FileStorage]):
        """
        Register a storage provider factory.
        
        Args:
            name: Name to register the provider under (e.g., "s3", "azure")
            provider_factory: Factory function that creates a FileStorage instance given a path
        """
        cls._storage_providers[name] = provider_factory
        logger.info(f"Registered storage provider: {name}")
    
    @classmethod
    def get_storage_provider(cls, name: str = "file") -> Callable[[Path], FileStorage]:
        """
        Get a registered storage provider factory by name.
        
        Args:
            name: Name of the storage provider (default: "file")
            
        Returns:
            Storage provider factory function
        """
        if name not in cls._storage_providers:
            raise ValueError(f"Unknown storage provider: {name}. Available: {list(cls._storage_providers.keys())}")
        return cls._storage_providers[name]
    
    @classmethod
    def register_cache_provider(cls, name: str, provider: CacheBackend):
        """
        Register a cache provider for use in project storage.
        
        Args:
            name: Name to register the provider under
            provider: CacheBackend instance
        """
        cls._cache_providers[name] = provider
        logger.info(f"Registered cache provider: {name}")
    
    @classmethod
    def get_cache_provider(cls, name: Optional[str]) -> Optional[CacheBackend]:
        """
        Get a registered cache provider by name.
        
        Args:
            name: Name of the cache provider, or None
            
        Returns:
            CacheBackend instance or None
        """
        cls._ensure_initialized()
        
        if name is None:
            return None
        return cls._cache_providers.get(name)

    @classmethod
    def create_file_storage(cls, base_path: Union[str, Path], provider: str = "file") -> FileStorage:
        """
        Create a filesystem abstraction.

        Args:
            base_path: Base path for the filesystem
            provider: Name of the storage provider to use (default: "file")

        Returns:
            FileStorage implementation
        """
        base_path = Path(base_path)
        base_path.mkdir(parents=True, exist_ok=True)

        # Get the provider factory and create the storage
        provider_factory = cls.get_storage_provider(provider)
        storage = provider_factory(base_path)
        
        logger.info(f"Created {provider} storage provider: {base_path}")
        return storage

    @classmethod
    def create_project_storage(
        cls,
        project_root: Union[str, Path],
        project_id: str,
        use_git_artifacts: bool = True,
        storage_provider: str = "file",
        cache_provider: Optional[str] = None
    ) -> ProjectStorage:
        """
        Create a project storage for business logic.

        Handles business concepts like artifacts, messages, execution plans
        using configurable storage and cache providers.

        Args:
            project_root: Root directory for all projects (e.g., .vibex/projects)
            project_id: Project ID for storage isolation
            use_git_artifacts: Whether to use Git for artifact versioning
            storage_provider: Name of storage provider to use (default: "file")
            cache_provider: Name of cache provider to use (default: None for no caching)

        Returns:
            ProjectStorage instance with specified storage and cache providers
        """
        # Get cache backend if specified
        cache_backend = cls.get_cache_provider(cache_provider)
        
        # Create project directory path: project_root + project_id
        project_dir = Path(project_root) / project_id
        
        # Create the filesystem abstraction for the project directory
        file_storage = cls.create_file_storage(project_dir, provider=storage_provider)
        
        # Create the final project storage with correct parameters
        project_storage = ProjectStorage(
            project_path=project_dir,
            project_id=project_id,
            file_storage=file_storage,
            use_git_artifacts=use_git_artifacts,
            cache_backend=cache_backend
        )
        
        logger.debug(f"Created project storage: {project_storage.project_path} (Storage: {storage_provider}, Cache: {cache_provider or 'disabled'}, Git: {use_git_artifacts})")
        
        return project_storage




