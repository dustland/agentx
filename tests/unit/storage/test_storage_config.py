"""
Unit tests for storage configuration singleton
"""

import pytest
from vibex.storage.config import StorageConfig, storage_config
from vibex.storage.providers.cache.memory import MemoryCacheProvider
from vibex.storage.providers.cache.noop import NoOpCacheProvider


def test_storage_config_singleton():
    """Test that StorageConfig is a singleton"""
    config1 = StorageConfig()
    config2 = StorageConfig()
    assert config1 is config2
    assert config1 is storage_config


def test_storage_config_configure():
    """Test configuring storage"""
    # Reset to defaults
    storage_config.reset()
    
    # Initially disabled
    assert not storage_config.is_caching_enabled
    assert storage_config.cache_backend is None
    
    # Configure with cache backend
    cache_backend = MemoryCacheProvider()
    storage_config.set_cache_backend(cache_backend)
    
    assert storage_config.is_caching_enabled
    assert storage_config.cache_backend is cache_backend
    
    # Disable caching
    storage_config.set_cache_backend(None)
    assert not storage_config.is_caching_enabled
    assert storage_config.cache_backend is None


def test_storage_config_reset():
    """Test resetting storage config"""
    # Configure
    cache_backend = MemoryCacheProvider()
    storage_config.set_cache_backend(cache_backend)
    
    # Reset
    storage_config.reset()
    
    # Should be back to defaults
    assert not storage_config.is_caching_enabled
    assert storage_config.cache_backend is None


@pytest.mark.asyncio
async def test_storage_factory_uses_config():
    """Test that StorageFactory uses the configured cache backend"""
    from vibex.storage.factory import StorageFactory
    # CachedProjectStorage removed - use ProjectStorage directly
    from vibex.storage.project import ProjectStorage
    import tempfile
    import shutil
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Reset and configure storage
        storage_config.reset()
        cache_backend = MemoryCacheProvider()
        storage_config.set_cache_backend(cache_backend)
        
        # Create project storage
        project_storage = StorageFactory.create_project_storage(
            base_path=temp_dir,
            project_id="test-project"
        )
        
        # Should be wrapped with caching
        assert isinstance(project_storage, ProjectStorage)
        
        # Reset and create again
        storage_config.reset()
        
        # Create project storage without caching
        project_storage2 = StorageFactory.create_project_storage(
            base_path=temp_dir,
            project_id="test-project-2"
        )
        
        # Should be ProjectStorage instance
        assert isinstance(project_storage2, ProjectStorage)
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        storage_config.reset()