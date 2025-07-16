#!/usr/bin/env python3
"""
Performance benchmarks for storage caching layer
"""

import asyncio
import time
import statistics
from pathlib import Path
from typing import List, Tuple

from agentx.storage.cache_backends import MemoryCacheBackend, NoOpCacheBackend
from agentx.storage.cached_taskspace import CachedTaskspaceStorage
from agentx.storage.factory import StorageFactory


async def benchmark_operation(name: str, func, iterations: int = 100) -> Tuple[float, float, float]:
    """Benchmark an async operation and return min, avg, max times in milliseconds"""
    times = []
    
    # Warm up
    for _ in range(10):
        await func()
    
    # Actual benchmark
    for _ in range(iterations):
        start = time.perf_counter()
        await func()
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)
    
    return min(times), statistics.mean(times), max(times)


async def run_benchmarks():
    """Run performance benchmarks comparing cached vs uncached operations"""
    
    # Find a real task to benchmark
    taskspace_root = Path("taskspace")
    task_id = None
    
    for item in taskspace_root.rglob("plan.json"):
        if item.parent.name != "taskspace":  # Skip the root itself
            task_id = item.parent.name
            print(f"Using task: {task_id}")
            break
    
    if not task_id:
        print("No tasks found. Creating a test task...")
        # Create a test task
        task_id = "benchmark-test"
        test_path = taskspace_root / task_id
        test_path.mkdir(parents=True, exist_ok=True)
        
        # Create test data
        import json
        plan_data = {
            "goal": "Benchmark test task",
            "tasks": [
                {"id": f"task{i}", "name": f"Task {i}", "status": "pending"} 
                for i in range(10)
            ]
        }
        with open(test_path / "plan.json", "w") as f:
            json.dump(plan_data, f)
    
    # Create storage instances
    base_storage = StorageFactory.create_taskspace_storage(
        base_path=Path("./taskspace"),
        task_id=task_id
    )
    
    # No cache
    no_cache_storage = CachedTaskspaceStorage(base_storage, NoOpCacheBackend())
    
    # Memory cache
    memory_cache = MemoryCacheBackend()
    cached_storage = CachedTaskspaceStorage(base_storage, memory_cache)
    
    print("\n=== Storage Caching Performance Benchmarks ===")
    print(f"Task ID: {task_id}")
    print(f"Iterations per test: 100")
    print()
    
    # Benchmark get_plan
    print("1. get_plan() Performance:")
    no_cache_min, no_cache_avg, no_cache_max = await benchmark_operation(
        "get_plan no cache",
        lambda: no_cache_storage.get_plan()
    )
    cached_min, cached_avg, cached_max = await benchmark_operation(
        "get_plan cached",
        lambda: cached_storage.get_plan()
    )
    
    print(f"   Without cache: avg={no_cache_avg:.2f}ms, min={no_cache_min:.2f}ms, max={no_cache_max:.2f}ms")
    print(f"   With cache:    avg={cached_avg:.2f}ms, min={cached_min:.2f}ms, max={cached_max:.2f}ms")
    print(f"   Speedup:       {no_cache_avg/cached_avg:.1f}x")
    print()
    
    # Benchmark task status extraction
    print("2. Task Status Extraction:")
    
    async def get_status_no_cache():
        plan = await no_cache_storage.get_plan()
        if plan:
            tasks = plan.get("tasks", [])
            return [t.get("status") for t in tasks]
    
    async def get_status_cached():
        return await cached_storage.get_task_progress()
    
    no_cache_min, no_cache_avg, no_cache_max = await benchmark_operation(
        "status no cache",
        get_status_no_cache
    )
    cached_min, cached_avg, cached_max = await benchmark_operation(
        "status cached",
        get_status_cached
    )
    
    print(f"   Without cache: avg={no_cache_avg:.2f}ms, min={no_cache_min:.2f}ms, max={no_cache_max:.2f}ms")
    print(f"   With cache:    avg={cached_avg:.2f}ms, min={cached_min:.2f}ms, max={cached_max:.2f}ms")
    print(f"   Speedup:       {no_cache_avg/cached_avg:.1f}x")
    print()
    
    # Benchmark cold vs warm cache
    print("3. Cold vs Warm Cache:")
    
    # Clear cache and test cold start
    await memory_cache.clear()
    cold_start = time.perf_counter()
    await cached_storage.get_plan()
    cold_time = (time.perf_counter() - cold_start) * 1000
    
    # Warm cache test
    warm_start = time.perf_counter()
    await cached_storage.get_plan()
    warm_time = (time.perf_counter() - warm_start) * 1000
    
    print(f"   Cold cache (first read): {cold_time:.2f}ms")
    print(f"   Warm cache (cached):     {warm_time:.2f}ms")
    print(f"   Cache effectiveness:     {cold_time/warm_time:.1f}x faster")
    print()
    
    # Summary
    print("=== Summary ===")
    print(f"Average speedup from caching: {no_cache_avg/cached_avg:.1f}x")
    print(f"Cache overhead on miss: ~{cold_time - no_cache_avg:.1f}ms")
    print(f"Typical cache hit time: <{cached_avg:.1f}ms")
    
    # Update docs with real numbers
    print("\n=== Documentation Update ===")
    print("Update docs/content/docs/design/caching.mdx with these real numbers:")
    print(f"- get_plan(): ~{no_cache_avg:.0f}ms → ~{cached_avg:.1f}ms")
    print(f"- get_task_progress(): ~{no_cache_avg:.0f}ms → ~{cached_avg:.1f}ms")


if __name__ == "__main__":
    asyncio.run(run_benchmarks())