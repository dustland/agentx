"""
Tests for ProjectStorageFactory and integrated caching.

Tests the new ProjectStorageFactory with dual provider registries
and the integrated caching functionality in ProjectStorage.
"""

import asyncio
import time
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock

import pytest

from vibex.storage.factory import ProjectStorageFactory
from vibex.storage.project import ProjectStorage
from vibex.storage.providers.cache.memory import MemoryCacheProvider
from vibex.storage.providers.cache.noop import NoOpCacheProvider
from vibex.storage.interfaces import CacheBackend


class TestProjectStorageFactory:
    """Test ProjectStorageFactory provider system."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_id = "test_project"
        self.user_id = "test_user"
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_factory_registers_default_providers(self):
        """ProjectStorageFactory should register default cache providers."""
        # Should not raise errors
        memory_cache = ProjectStorageFactory.get_cache_provider("memory")
        noop_cache = ProjectStorageFactory.get_cache_provider("noop")
        none_cache = ProjectStorageFactory.get_cache_provider("none")
        
        assert isinstance(memory_cache, MemoryCacheProvider)
        assert isinstance(noop_cache, NoOpCacheProvider) 
        assert isinstance(none_cache, NoOpCacheProvider)
    
    def test_factory_create_project_storage_new_api(self):
        """create_project_storage should use new API properly."""
        project_storage = ProjectStorageFactory.create_project_storage(
            base_path=self.temp_dir,
            project_id=self.project_id,
            user_id=self.user_id,
            cache_provider="memory"
        )
        
        assert isinstance(project_storage, ProjectStorage)
        assert project_storage.project_id == self.project_id
        assert project_storage.user_id == self.user_id
        assert project_storage.get_project_path() == self.temp_dir / self.user_id / self.project_id
        assert project_storage._cache is not None
    
    def test_factory_create_project_storage_without_user(self):
        """create_project_storage should work without user_id."""
        project_storage = ProjectStorageFactory.create_project_storage(
            base_path=self.temp_dir,
            project_id=self.project_id,
            cache_provider="noop"
        )
        
        assert isinstance(project_storage, ProjectStorage)
        assert project_storage.project_id == self.project_id
        assert project_storage.user_id is None
        assert project_storage.get_project_path() == self.temp_dir / self.project_id
        assert project_storage._cache is not None
    
    def test_factory_create_storage_old_api(self):
        """create_storage should support old API for backward compatibility."""
        project_path = self.temp_dir / "direct_path"
        project_storage = ProjectStorageFactory.create_storage(
            project_path=project_path,
            cache_provider="memory"
        )
        
        assert isinstance(project_storage, ProjectStorage)
        assert project_storage.get_project_path() == project_path
        assert project_storage._cache is not None
    
    def test_factory_no_cache_provider(self):
        """Factory should handle None cache provider."""
        project_storage = ProjectStorageFactory.create_project_storage(
            base_path=self.temp_dir,
            project_id=self.project_id,
            cache_provider=None
        )
        
        assert isinstance(project_storage, ProjectStorage)
        assert project_storage._cache is None
    
    def test_factory_register_custom_cache_provider(self):
        """Factory should allow registering custom cache providers."""
        custom_cache = Mock(spec=CacheBackend)
        ProjectStorageFactory.register_cache_provider("custom", custom_cache)
        
        retrieved = ProjectStorageFactory.get_cache_provider("custom")
        assert retrieved is custom_cache


class TestIntegratedCaching:
    """Test integrated caching in ProjectStorage."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_id = "test_project"
        
        # Create project_storage with memory cache
        self.project_storage = ProjectStorageFactory.create_project_storage(
            base_path=self.temp_dir,
            project_id=self.project_id,
            cache_provider="memory"
        )
        
        # Setup test data
        self.test_plan = {
            "goal": "Test task",
            "tasks": [
                {"id": "task1", "name": "Task 1", "status": "completed"},
                {"id": "task2", "name": "Task 2", "status": "in_progress"}
            ]
        }
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_plan_caching(self):
        """Plan should be cached after first read."""
        # Store plan
        await self.project_storage.store_plan(self.test_plan)
        
        # First read (cache miss)
        plan1 = await self.project_storage.get_plan()
        assert plan1 is not None
        assert plan1["goal"] == "Test task"
        
        # Second read (cache hit) - mock file storage to verify cache is used
        original_read_text = self.project_storage.file_storage.read_text
        self.project_storage.file_storage.read_text = AsyncMock(side_effect=Exception("Should not be called"))
        
        plan2 = await self.project_storage.get_plan()
        assert plan2 is not None
        assert plan2["goal"] == "Test task"
        
        # Restore original method
        self.project_storage.file_storage.read_text = original_read_text
    
    @pytest.mark.asyncio
    async def test_plan_cache_invalidation(self):
        """Plan cache should be invalidated on update."""
        # Store and read plan
        await self.project_storage.store_plan(self.test_plan)
        plan1 = await self.project_storage.get_plan()
        assert plan1["goal"] == "Test task"
        
        # Update plan
        updated_plan = self.test_plan.copy()
        updated_plan["goal"] = "Updated task"
        await self.project_storage.store_plan(updated_plan)
        
        # Read again - should get updated version
        plan2 = await self.project_storage.get_plan()
        assert plan2["goal"] == "Updated task"
    
    @pytest.mark.asyncio
    async def test_artifact_caching(self):
        """Artifacts should be cached after first read."""
        # Store artifact
        await self.project_storage.store_artifact("test.txt", "test content")
        
        # First read (cache miss)
        content1 = await self.project_storage.get_artifact("test.txt")
        assert content1 == "test content"
        
        # Second read (cache hit) - verify cache is used
        original_read_text = self.project_storage.file_storage.read_text
        self.project_storage.file_storage.read_text = AsyncMock(side_effect=Exception("Should not be called"))
        
        content2 = await self.project_storage.get_artifact("test.txt")
        assert content2 == "test content"
        
        # Restore original method
        self.project_storage.file_storage.read_text = original_read_text
    
    @pytest.mark.asyncio
    async def test_artifact_list_caching(self):
        """Artifact list should be cached."""
        # Store some artifacts
        await self.project_storage.store_artifact("test1.txt", "content1")
        await self.project_storage.store_artifact("test2.txt", "content2")
        
        # First list (cache miss)
        artifacts1 = await self.project_storage.list_artifacts()
        assert len(artifacts1) == 2
        
        # Second list (cache hit)
        original_read_text = self.project_storage.file_storage.read_text
        self.project_storage.file_storage.read_text = AsyncMock(side_effect=Exception("Should not be called"))
        
        artifacts2 = await self.project_storage.list_artifacts()
        assert len(artifacts2) == 2
        
        # Restore original method
        self.project_storage.file_storage.read_text = original_read_text
    
    @pytest.mark.asyncio
    async def test_artifact_cache_invalidation_on_store(self):
        """Artifact caches should be invalidated when storing new artifacts."""
        # Store initial artifact and list
        await self.project_storage.store_artifact("test1.txt", "content1")
        artifacts1 = await self.project_storage.list_artifacts()
        assert len(artifacts1) == 1
        
        # Store new artifact (should invalidate cache)
        await self.project_storage.store_artifact("test2.txt", "content2")
        
        # List again - should see new artifact
        artifacts2 = await self.project_storage.list_artifacts()
        assert len(artifacts2) == 2
    
    @pytest.mark.asyncio
    async def test_conversation_caching(self):
        """Conversation history should be cached."""
        # Store messages
        await self.project_storage.store_message({"role": "user", "content": "Hello"})
        await self.project_storage.store_message({"role": "assistant", "content": "Hi there"})
        
        # First read (cache miss)
        history1 = await self.project_storage.get_conversation_history()
        assert len(history1) == 2
        
        # Second read (cache hit)
        original_list_directory = self.project_storage.file_storage.list_directory
        self.project_storage.file_storage.list_directory = AsyncMock(side_effect=Exception("Should not be called"))
        
        history2 = await self.project_storage.get_conversation_history()
        assert len(history2) == 2
        
        # Restore original method
        self.project_storage.file_storage.list_directory = original_list_directory
    
    @pytest.mark.asyncio
    async def test_conversation_cache_invalidation(self):
        """Conversation cache should be invalidated when storing new messages."""
        # Store initial message and read
        await self.project_storage.store_message({"role": "user", "content": "Hello"})
        history1 = await self.project_storage.get_conversation_history()
        assert len(history1) == 1
        
        # Store new message (should invalidate cache)
        await self.project_storage.store_message({"role": "assistant", "content": "Hi"})
        
        # Read again - should see new message
        history2 = await self.project_storage.get_conversation_history()
        assert len(history2) == 2
    
    @pytest.mark.asyncio
    async def test_summary_caching(self):
        """Taskspace summary should be cached."""
        # Store some data
        await self.project_storage.store_plan(self.test_plan)
        await self.project_storage.store_artifact("test.txt", "content")
        
        # First summary (cache miss)
        summary1 = await self.project_storage.get_project_summary()
        assert summary1 is not None
        
        # Second summary (cache hit)
        original_list_directory = self.project_storage.file_storage.list_directory
        self.project_storage.file_storage.list_directory = AsyncMock(side_effect=Exception("Should not be called"))
        
        summary2 = await self.project_storage.get_project_summary()
        assert summary2 is not None
        
        # Restore original method
        self.project_storage.file_storage.list_directory = original_list_directory


class TestCachePerformance:
    """Test cache performance improvements."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_id = "perf_test"
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_cache_performance_improvement(self):
        """Caching should provide significant performance improvement."""
        # Create taskspaces with and without cache
        no_cache_taskspace = ProjectStorageFactory.create_project_storage(
            base_path=self.temp_dir,
            project_id=f"{self.project_id}_nocache",
            cache_provider=None
        )
        
        cached_taskspace = ProjectStorageFactory.create_project_storage(
            base_path=self.temp_dir,
            project_id=f"{self.project_id}_cached",
            cache_provider="memory"
        )
        
        # Setup test data
        test_plan = {"goal": "Performance test", "tasks": []}
        await no_cache_taskspace.store_plan(test_plan)
        await cached_taskspace.store_plan(test_plan)
        
        # Test without cache (multiple reads)
        start = time.time()
        for _ in range(20):
            await no_cache_taskspace.get_plan()
        no_cache_time = time.time() - start
        
        # Test with cache (first read populates cache, rest are from cache)
        start = time.time()
        for _ in range(20):
            await cached_taskspace.get_plan()
        cache_time = time.time() - start
        
        # Cache should be significantly faster
        # Allow some variance but expect at least 3x speedup
        assert no_cache_time > cache_time
        speedup = no_cache_time / cache_time
        assert speedup > 3.0, f"Expected >3x speedup, got {speedup:.2f}x"


class TestNoOpCache:
    """Test that NoOp cache doesn't break functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_id = "noop_test"
        
        self.project_storage = ProjectStorageFactory.create_project_storage(
            base_path=self.temp_dir,
            project_id=self.project_id,
            cache_provider="noop"
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_noop_cache_plan_operations(self):
        """Plan operations should work with NoOp cache."""
        test_plan = {"goal": "NoOp test", "tasks": []}
        
        # Store plan
        result = await self.project_storage.store_plan(test_plan)
        assert result.success
        
        # Get plan
        plan = await self.project_storage.get_plan()
        assert plan is not None
        assert plan["goal"] == "NoOp test"
    
    @pytest.mark.asyncio
    async def test_noop_cache_artifact_operations(self):
        """Artifact operations should work with NoOp cache."""
        # Store artifact
        result = await self.project_storage.store_artifact("test.txt", "test content")
        assert result.success
        
        # Get artifact
        content = await self.project_storage.get_artifact("test.txt")
        assert content == "test content"
        
        # List artifacts
        artifacts = await self.project_storage.list_artifacts()
        assert len(artifacts) >= 1
        assert any(a["name"] == "test.txt" for a in artifacts)