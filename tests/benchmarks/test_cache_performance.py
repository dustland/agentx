#!/usr/bin/env python3
"""
Performance benchmarks for storage caching layer
"""

import asyncio
import time
import statistics
from pathlib import Path
from typing import List, Tuple
import tempfile
import shutil
import pytest

from vibex.storage.cache_backends import MemoryCacheBackend, NoOpCacheBackend
# ProjectStorage removed - use ProjectStorage directly
from vibex.storage.project import ProjectStorage
from vibex.storage.factory import StorageFactory
from vibex.storage.project_factory import ProjectStorageFactory
from vibex.models.plan import Plan
from vibex.models.task import Task


class TestCachePerformance:
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def _create_project_storage(self, project_id, cache_provider):
        return ProjectStorageFactory.create_project_storage(
            base_path=self.temp_dir,
            project_id=project_id,
            user_id="benchmark_user",
            use_git_artifacts=False,
            cache_provider=cache_provider
        )

    @pytest.mark.parametrize("cache_provider", [None, "memory", "redis"])
    @pytest.mark.asyncio
    async def test_artifact_read_performance(self, benchmark, cache_provider):
        project_id = f"read_bench_{cache_provider or 'none'}"
        project_storage = self._create_project_storage(project_id, cache_provider)
        
        # --- Setup: Write an artifact to disk first ---
        test_content = "a" * (10 * 1024)  # 10 KB
        await project_storage.store_artifact("artifact_1", test_content)
        
        # Benchmark function
        async def read_artifact_func():
            return await project_storage.read_artifact("artifact_1")
            
        # Run the benchmark
        await benchmark.coro_call(read_artifact_func)
        
        # Verification
        assert benchmark.stats.stats.max > 0

    @pytest.mark.parametrize("cache_provider", [None, "memory", "redis"])
    @pytest.mark.asyncio
    async def test_artifact_write_performance(self, benchmark, cache_provider):
        project_id = f"write_bench_{cache_provider or 'none'}"
        project_storage = self._create_project_storage(project_id, cache_provider)
        
        # --- Data for writing ---
        test_content = "a" * (10 * 1024)  # 10 KB
        
        # Benchmark function
        async def write_artifact_func():
            await project_storage.store_artifact("artifact_write_1", test_content)
            
        # Run the benchmark
        await benchmark.coro_call(write_artifact_func)
        
        # Verification
        assert benchmark.stats.stats.max > 0

    @pytest.mark.parametrize("cache_provider", [None, "memory", "redis"])
    @pytest.mark.asyncio
    async def test_plan_read_performance(self, benchmark, cache_provider):
        project_id = f"plan_read_bench_{cache_provider or 'none'}"
        project_storage = self._create_project_storage(project_id, cache_provider)
        
        # --- Setup: Write a plan to disk first ---
        test_plan = Plan(goal="Test plan", tasks=[Task(id="t1", name="Task 1", goal="Goal 1")])
        await project_storage.store_plan(test_plan)
        
        # Benchmark function
        async def read_plan_func():
            return await project_storage.get_plan()
            
        # Run the benchmark
        await benchmark.coro_call(read_plan_func)
        
        # Verification
        assert benchmark.stats.stats.max > 0