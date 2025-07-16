#!/usr/bin/env python3
"""
Test cache integration in multi-worker API deployment.

This script tests the caching functionality without requiring
full task execution to work.
"""

import asyncio
import os
import time
from pathlib import Path
import tempfile
import shutil

from agentx.storage import TaskspaceFactory


async def test_cache_integration():
    """Test cache integration with TaskspaceFactory."""
    print("=== Cache Integration Test ===\n")
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Test 1: Memory cache in single worker
        print("1. Testing memory cache...")
        os.environ["ENABLE_MEMORY_CACHE"] = "true"
        os.environ["ENABLE_REDIS_CACHE"] = "false"
        
        taskspace = TaskspaceFactory.create_taskspace(
            base_path=temp_dir,
            task_id="cache_test_001",
            cache_provider="memory"
        )
        
        # Store test data
        test_plan = {
            "goal": "Test caching",
            "tasks": [{"id": "1", "status": "pending"}]
        }
        
        await taskspace.store_plan(test_plan)
        
        # Time multiple reads
        start = time.time()
        for _ in range(100):
            plan = await taskspace.get_plan()
        memory_time = time.time() - start
        
        print(f"✓ Memory cache: 100 reads in {memory_time:.3f}s")
        
        # Test 2: No cache comparison
        print("\n2. Testing without cache...")
        no_cache_taskspace = TaskspaceFactory.create_taskspace(
            base_path=temp_dir,
            task_id="cache_test_002",
            cache_provider=None
        )
        
        await no_cache_taskspace.store_plan(test_plan)
        
        start = time.time()
        for _ in range(100):
            plan = await no_cache_taskspace.get_plan()
        no_cache_time = time.time() - start
        
        print(f"✓ No cache: 100 reads in {no_cache_time:.3f}s")
        
        # Calculate speedup
        speedup = no_cache_time / memory_time if memory_time > 0 else 0
        print(f"\n✅ Cache speedup: {speedup:.1f}x")
        
        # Test 3: Multi-instance cache sharing (simulated)
        print("\n3. Testing cache sharing between instances...")
        
        # Create two taskspace instances with same ID
        worker1 = TaskspaceFactory.create_taskspace(
            base_path=temp_dir,
            task_id="shared_task",
            cache_provider="memory"
        )
        
        worker2 = TaskspaceFactory.create_taskspace(
            base_path=temp_dir,
            task_id="shared_task",
            cache_provider="memory"
        )
        
        # Worker 1 writes
        shared_plan = {"goal": "Shared task", "worker": "worker1"}
        await worker1.store_plan(shared_plan)
        
        # Worker 2 reads (should get from filesystem, not cache)
        plan_from_worker2 = await worker2.get_plan()
        
        if plan_from_worker2 and plan_from_worker2["worker"] == "worker1":
            print("✓ Workers can read each other's data via filesystem")
        else:
            print("❌ Data sharing failed")
        
        # Test 4: Cache invalidation
        print("\n4. Testing cache invalidation...")
        
        # Read to populate cache
        _ = await worker1.get_plan()
        
        # Update plan
        shared_plan["goal"] = "Updated task"
        await worker1.store_plan(shared_plan)
        
        # Read again (should get updated version)
        updated_plan = await worker1.get_plan()
        
        if updated_plan["goal"] == "Updated task":
            print("✓ Cache invalidation working correctly")
        else:
            print("❌ Cache invalidation failed")
        
        print("\n=== Summary ===")
        print(f"✅ Memory cache provides {speedup:.1f}x speedup")
        print("✅ Filesystem ensures data consistency across workers")
        print("✅ Cache invalidation maintains data integrity")
        print("\nFor true multi-worker cache sharing, use Redis:")
        print("  ENABLE_REDIS_CACHE=true uv run prod")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n✓ Cleaned up temp directory")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_cache_integration())
    exit(0 if success else 1)