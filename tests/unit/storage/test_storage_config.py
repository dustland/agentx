"""
Unit tests for storage configuration singleton
"""

import pytest
from agentx.storage.config import StorageConfig, storage_config
from agentx.storage.cache_backends import MemoryCacheBackend, NoOpCacheBackend


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
    cache_backend = MemoryCacheBackend()
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
    cache_backend = MemoryCacheBackend()
    storage_config.set_cache_backend(cache_backend)
    
    # Reset
    storage_config.reset()
    
    # Should be back to defaults
    assert not storage_config.is_caching_enabled
    assert storage_config.cache_backend is None


@pytest.mark.asyncio
async def test_storage_factory_uses_config():
    """Test that StorageFactory uses the configured cache backend"""
    from agentx.storage.factory import StorageFactory
    from agentx.storage.cached_taskspace import CachedTaskspaceStorage
    import tempfile
    import shutil
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Reset and configure storage
        storage_config.reset()
        cache_backend = MemoryCacheBackend()
        storage_config.set_cache_backend(cache_backend)
        
        # Create taskspace storage
        taskspace = StorageFactory.create_taskspace_storage(
            base_path=temp_dir,
            task_id="test-task"
        )
        
        # Should be wrapped with caching
        assert isinstance(taskspace, CachedTaskspaceStorage)
        
        # Reset and create again
        storage_config.reset()
        
        # Create taskspace storage without caching
        taskspace2 = StorageFactory.create_taskspace_storage(
            base_path=temp_dir,
            task_id="test-task-2"
        )
        
        # Should not be wrapped
        assert not isinstance(taskspace2, CachedTaskspaceStorage)
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        storage_config.reset()