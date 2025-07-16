"""
Integration tests for storage caching layer
"""

import asyncio
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock

import pytest

from agentx.storage.providers.cache import MemoryCacheProvider, NoOpCacheProvider
from agentx.storage import TaskspaceFactory
from agentx.storage import storage_config


@pytest.fixture
async def temp_taskspace():
    """Create a temporary taskspace with test data"""
    temp_dir = tempfile.mkdtemp()
    task_id = "test-task-123"
    
    # Create taskspace structure
    taskspace_path = Path(temp_dir) / task_id
    taskspace_path.mkdir(parents=True)
    
    # Create test plan
    plan_data = {
        "goal": "Test task",
        "tasks": [
            {"id": "task1", "name": "Task 1", "status": "completed"},
            {"id": "task2", "name": "Task 2", "status": "in_progress"},
            {"id": "task3", "name": "Task 3", "status": "pending"}
        ]
    }
    
    import json
    with open(taskspace_path / "plan.json", "w") as f:
        json.dump(plan_data, f)
    
    # For simple storage, create artifacts with version suffix
    artifacts_dir = taskspace_path / "artifacts"
    artifacts_dir.mkdir()
    
    # Simple storage format: name_version.data
    (artifacts_dir / "test.txt_v1.data").write_text("test content")
    (artifacts_dir / "test.txt_v1.metadata").write_text('{"name": "test.txt", "version": "v1", "created_at": "2024-01-01T00:00:00"}')
    (artifacts_dir / "result.json_v1.data").write_text('{"result": "success"}')
    (artifacts_dir / "result.json_v1.metadata").write_text('{"name": "result.json", "version": "v1", "created_at": "2024-01-01T00:00:00"}')
    
    yield temp_dir, task_id
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_cache_performance(temp_taskspace):
    """Test that caching improves performance"""
    temp_dir, task_id = temp_taskspace
    
    # Create storage with and without cache
    base_storage = TaskspaceFactory.create_taskspace(
        base_path=Path(temp_dir),
        task_id=task_id,
        cache_provider=None
    )
    
    cached_storage = TaskspaceFactory.create_taskspace(
        base_path=Path(temp_dir),
        task_id=f"{task_id}_cached",
        cache_provider="memory"
    )
    
    # Test get_plan performance
    # Without cache - multiple reads
    start = time.time()
    for _ in range(10):
        await base_storage.get_plan()
    no_cache_time = time.time() - start
    
    # With cache - first read is slow, rest are fast
    start = time.time()
    for _ in range(10):
        await cached_storage.get_plan()
    cache_time = time.time() - start
    
    # Cache should be significantly faster
    assert cache_time < no_cache_time
    # Allow some variance but expect at least 2x speedup
    assert no_cache_time / cache_time > 2.0


@pytest.mark.asyncio
async def test_cache_invalidation(temp_taskspace):
    """Test that cache is properly invalidated on writes"""
    temp_dir, task_id = temp_taskspace
    
    cached_storage = TaskspaceFactory.create_taskspace(
        base_path=Path(temp_dir),
        task_id=task_id,
        cache_provider="memory"
    )
    
    # Read plan (should be cached)
    result1 = await cached_storage.get_plan()
    assert result1 is not None
    original_goal = result1["goal"]
    
    # Modify plan
    new_plan = result1.copy()
    new_plan["goal"] = "Modified test task"
    await cached_storage.store_plan(new_plan)
    
    # Read again (should get updated version)
    result2 = await cached_storage.get_plan()
    assert result2 is not None
    assert result2["goal"] == "Modified test task"
    assert result2["goal"] != original_goal


# Removed task status extraction test as it's not part of core TaskspaceStorage


@pytest.mark.asyncio
async def test_artifact_caching(temp_taskspace):
    """Test artifact list caching"""
    temp_dir, task_id = temp_taskspace
    
    cached_storage = TaskspaceFactory.create_taskspace(
        base_path=Path(temp_dir),
        task_id=task_id,
        cache_provider="memory"
    )
    
    # Store some artifacts first
    await cached_storage.store_artifact("test1.txt", "content1")
    await cached_storage.store_artifact("test2.txt", "content2")
    
    # List artifacts (should be cached)
    result1 = await cached_storage.list_artifacts()
    assert result1 is not None
    assert len(result1) == 2
    
    # Add new artifact (should invalidate cache)
    await cached_storage.store_artifact("new.txt", "new content")
    
    # List again (cache should be invalidated, showing new artifact)
    result2 = await cached_storage.list_artifacts()
    assert result2 is not None
    assert len(result2) == 3


@pytest.mark.asyncio
async def test_no_op_cache_provider():
    """Test that NoOpCacheProvider doesn't break functionality"""
    provider = NoOpCacheProvider()
    
    # All operations should work but do nothing
    assert await provider.get("key") is None
    await provider.set("key", "value")
    assert await provider.get("key") is None
    await provider.delete("key")
    await provider.clear()


@pytest.mark.asyncio
async def test_cache_ttl_expiration():
    """Test that cache entries expire after TTL"""
    provider = MemoryCacheProvider()
    
    # Set with short TTL
    await provider.set("test_key", "test_value", ttl=1)
    
    # Should be available immediately
    assert await provider.get("test_key") == "test_value"
    
    # Wait for expiration
    await asyncio.sleep(1.1)
    
    # Should be expired
    assert await provider.get("test_key") is None


@pytest.mark.asyncio
async def test_memory_cache_lru():
    """Test LRU eviction in memory cache"""
    provider = MemoryCacheProvider(max_size=3)
    
    # Fill cache
    await provider.set("key1", "value1")
    await provider.set("key2", "value2")
    await provider.set("key3", "value3")
    
    # Access key1 to make it recently used
    assert await provider.get("key1") == "value1"
    
    # Add new key (should evict key2 as least recently used)
    await provider.set("key4", "value4")
    
    # Check what's in cache
    assert await provider.get("key1") == "value1"  # Recently accessed
    assert await provider.get("key2") is None      # Evicted
    assert await provider.get("key3") == "value3"  # Still there
    assert await provider.get("key4") == "value4"  # Newly added