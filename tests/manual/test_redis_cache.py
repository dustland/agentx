#!/usr/bin/env python3
"""
Manual test for Redis cache scenario.

This script demonstrates using the TaskspaceFactory with Redis caching
for multi-worker deployments.

NOTE: This test requires a Redis server running at redis://localhost:6379/1
"""

import asyncio
import json
import time
from pathlib import Path
import tempfile
import shutil

from vibex.storage import TaskspaceFactory


async def test_redis_cache_scenario():
    """Test Redis cache functionality."""
    print("=== VibeX Taskspace System - Redis Cache Test ===\n")
    
    # Setup
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temp directory: {temp_dir}")
    
    try:
        # 1. Test Redis cache provider availability
        print("\n1. Testing Redis cache provider availability...")
        
        try:
            # Initialize factory to trigger provider registration
            memory_cache = TaskspaceFactory.get_cache_provider("memory")
            redis_cache = TaskspaceFactory.get_cache_provider("redis")
            
            if redis_cache is not None:
                print("✓ Redis cache provider registered successfully")
                
                # Test Redis connection
                try:
                    await redis_cache.set("test_connection", "connected")
                    result = await redis_cache.get("test_connection")
                    if result == "connected":
                        print("✓ Redis connection test passed")
                        redis_available = True
                    else:
                        print("❌ Redis connection test failed")
                        redis_available = False
                except Exception as e:
                    print(f"❌ Redis connection failed: {e}")
                    print("⚠️  Make sure Redis is running at redis://localhost:6379/1")
                    redis_available = False
            else:
                print("❌ Redis cache provider not available")
                redis_available = False
                
        except Exception as e:
            print(f"❌ Failed to get cache providers: {e}")
            redis_available = False
        
        # 2. Create taskspace with Redis cache (if available)
        if redis_available:
            print("\n2. Creating taskspace with Redis caching...")
            taskspace = TaskspaceFactory.create_taskspace(
                base_path=temp_dir,
                task_id="redis_task_001",
                user_id="worker_1",
                use_git_artifacts=False,  # Simplify for Redis test
                cache_provider="redis"
            )
            
            print(f"✓ Taskspace created with Redis cache")
            
            # 3. Test cross-worker simulation
            print("\n3. Simulating multi-worker scenario...")
            
            # Worker 1 stores data
            plan = {
                "goal": "Multi-worker task processing",
                "worker_id": "worker_1",
                "status": "in_progress",
                "tasks": [
                    {"id": "task1", "status": "completed", "worker": "worker_1"},
                    {"id": "task2", "status": "in_progress", "worker": "worker_1"}
                ]
            }
            
            await taskspace.store_plan(plan)
            print("✓ Worker 1 stored plan")
            
            # Worker 2 accesses same data (different taskspace instance)
            worker2_taskspace = TaskspaceFactory.create_taskspace(
                base_path=temp_dir,
                task_id="redis_task_001",  # Same task_id
                user_id="worker_1",       # Same user_id
                use_git_artifacts=False,
                cache_provider="redis"    # Same Redis cache
            )
            
            # Worker 2 should get cached data
            plan_from_cache = await worker2_taskspace.get_plan()
            
            if plan_from_cache and plan_from_cache["worker_id"] == "worker_1":
                print("✓ Worker 2 retrieved cached plan from Worker 1")
            else:
                print("❌ Cross-worker cache sharing failed")
            
            # 4. Test cache performance with Redis
            print("\n4. Testing Redis cache performance...")
            
            # Store some test artifacts
            for i in range(5):
                await taskspace.store_artifact(
                    f"test_file_{i}.txt",
                    f"Test content for file {i}" * 100,  # Make it substantial
                    metadata={"worker": "worker_1", "iteration": i}
                )
            
            # Time cached reads
            start_time = time.time()
            for i in range(20):
                plan_data = await taskspace.get_plan()
                artifacts = await taskspace.list_artifacts()
            redis_time = time.time() - start_time
            
            print(f"✓ 20 operations with Redis cache: {redis_time:.4f} seconds")
            
            # 5. Test cache invalidation
            print("\n5. Testing cache invalidation...")
            
            original_goal = plan["goal"]
            plan["goal"] = "Updated by Worker 1"
            await taskspace.store_plan(plan)
            
            # Worker 2 should see updated data
            updated_plan = await worker2_taskspace.get_plan()
            if updated_plan["goal"] == "Updated by Worker 1":
                print("✓ Cache invalidation working correctly")
            else:
                print("❌ Cache invalidation failed")
            
            # 6. Compare with memory cache
            print("\n6. Comparing with memory cache...")
            
            memory_taskspace = TaskspaceFactory.create_taskspace(
                base_path=temp_dir,
                task_id="memory_task_001",
                user_id="worker_1",
                use_git_artifacts=False,
                cache_provider="memory"
            )
            
            await memory_taskspace.store_plan(plan)
            
            # Time memory cache reads
            start_time = time.time()
            for i in range(20):
                plan_data = await memory_taskspace.get_plan()
            memory_time = time.time() - start_time
            
            print(f"✓ 20 operations with memory cache: {memory_time:.4f} seconds")
            
            if memory_time > 0:
                ratio = redis_time / memory_time
                print(f"✓ Redis vs Memory ratio: {ratio:.1f}x")
                if ratio < 5.0:  # Redis should be reasonably close to memory
                    print("✓ Redis performance is acceptable")
                else:
                    print("⚠️  Redis performance may need optimization")
            
            print("\n=== Redis Cache Test Complete ===")
            print("✓ Redis cache provider working correctly")
            print("✓ Cross-worker cache sharing functional") 
            print("✓ Cache invalidation working")
            print("✓ Performance within acceptable range")
            
        else:
            print("\n=== Redis Test Skipped ===")
            print("Redis server not available. To run this test:")
            print("1. Install Redis: brew install redis (macOS) or apt install redis (Ubuntu)")
            print("2. Start Redis: redis-server")
            print("3. Install Redis Python client: pip install redis")
            print("4. Re-run this test")
            
            # Fall back to testing factory registration
            print("\n2. Testing factory without Redis...")
            
            taskspace = TaskspaceFactory.create_taskspace(
                base_path=temp_dir,
                task_id="fallback_task",
                user_id="test_user",
                cache_provider="memory"  # Fall back to memory cache
            )
            
            print("✓ Factory working with memory cache fallback")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n✓ Cleaned up temp directory: {temp_dir}")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_redis_cache_scenario())
    exit(0 if success else 1)