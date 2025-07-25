#!/usr/bin/env python3
"""
Comprehensive benchmark test for Taskspace System.

This script measures performance across different cache providers and operations
to provide data for the design document.
"""

import asyncio
import json
import time
import statistics
from pathlib import Path
import tempfile
import shutil
from typing import Dict, List, Any

from vibex.storage.factory import ProjectStorageFactory


class ProjectBenchmark:
    """Benchmark suite for Project System."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.results = {}
        
    async def cleanup(self):
        """Clean up benchmark resources."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def setup_project(self, cache_provider: str = None) -> Any:
        """Create a project storage with specified cache provider."""
        return ProjectStorageFactory.create_project_storage(
            base_path=self.temp_dir,
            project_id=f"bench_{cache_provider or 'none'}",
            use_git_artifacts=False,  # Simplify for consistent results
            cache_provider=cache_provider
        )
    
    async def setup_test_data(self, project_storage):
        """Setup realistic test data."""
        # Create a realistic plan
        plan = {
            "goal": "Implement microservices architecture",
            "description": "Break down monolithic application into microservices",
            "status": "in_progress",
            "priority": "high",
            "tasks": [
                {"id": f"task_{i}", "name": f"Task {i}", "status": "pending", "priority": "medium"}
                for i in range(50)  # Realistic plan size
            ],
            "metadata": {
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T14:30:00Z",
                "team": "backend",
                "estimated_hours": 160
            }
        }
        
        await project_storage.store_plan(plan)
        
        # Create realistic artifacts
        artifacts = [
            ("service_design.md", "# Service Design\n" + "Design content\n" * 200),
            ("api_spec.yaml", "openapi: 3.0.0\n" + "spec: content\n" * 150),
            ("database_schema.sql", "CREATE TABLE users (\n" + "  column definitions\n" * 100),
            ("config.json", json.dumps({"service": f"config_{i}" for i in range(20)})),
            ("deployment.yaml", "apiVersion: apps/v1\n" + "kubernetes: config\n" * 80)
        ]
        
        for name, content in artifacts:
            await project_storage.store_artifact(name, content, metadata={"size": len(content)})
        
        # Create conversation history
        messages = []
        for i in range(20):
            messages.extend([
                {"role": "user", "content": f"Question {i} about the implementation"},
                {"role": "assistant", "content": f"Answer {i} with detailed explanation" * 10}
            ])
        
        for msg in messages:
            await project_storage.store_message(msg)
    
    async def benchmark_operation(self, operation_name: str, operation_func, iterations: int = 100) -> Dict[str, float]:
        """Benchmark a single operation."""
        times = []
        
        # Warm-up
        for _ in range(5):
            await operation_func()
        
        # Actual benchmark
        for _ in range(iterations):
            start_time = time.time()
            await operation_func()
            times.append(time.time() - start_time)
        
        return {
            "avg_ms": statistics.mean(times) * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
            "median_ms": statistics.median(times) * 1000,
            "std_ms": statistics.stdev(times) * 1000 if len(times) > 1 else 0
        }
    
    async def benchmark_cache_provider(self, cache_provider: str = None) -> Dict[str, Any]:
        """Benchmark all operations for a specific cache provider."""
        print(f"Benchmarking cache provider: {cache_provider or 'None'}")
        
        project_storage = await self.setup_project(cache_provider)
        await self.setup_test_data(project_storage)
        
        operations = {
            "get_plan": lambda: project_storage.get_plan(),
            "store_plan": lambda: project_storage.store_plan({"goal": "Updated goal", "tasks": []}),
            "list_artifacts": lambda: project_storage.list_artifacts(),
            "get_artifact": lambda: project_storage.get_artifact("service_design.md"),
            "store_artifact": lambda: project_storage.store_artifact("temp.txt", "temp content"),
            "get_conversation": lambda: project_storage.get_conversation_history(),
            "get_summary": lambda: project_storage.get_project_summary()
        }
        
        results = {}
        
        for op_name, op_func in operations.items():
            print(f"  - {op_name}...")
            results[op_name] = await self.benchmark_operation(op_name, op_func)
        
        return results
    
    async def run_comprehensive_benchmark(self):
        """Run comprehensive benchmark across all cache providers."""
        print("=== Project System Comprehensive Benchmark ===\n")
        
        cache_providers = [
            None,        # No cache
            "noop",      # NoOp cache
            "memory",    # Memory cache
        ]
        
        # Test Redis availability
        try:
            redis_project = await self.setup_project("redis")
            await redis_project._cache.set("test", "value")
            result = await redis_project._cache.get("test")
            if result == "value":
                cache_providers.append("redis")
                print("✓ Redis cache available for benchmarking")
            else:
                print("⚠️  Redis cache not responding correctly")
        except Exception as e:
            print(f"⚠️  Redis cache not available: {e}")
        
        # Run benchmarks
        for provider in cache_providers:
            provider_name = provider or "none"
            self.results[provider_name] = await self.benchmark_cache_provider(provider)
        
        # Calculate speedup ratios
        self.calculate_speedups()
        
        # Print results
        self.print_results()
        
        # Generate table for documentation
        self.generate_doc_table()
    
    def calculate_speedups(self):
        """Calculate speedup ratios compared to no-cache baseline."""
        baseline = self.results.get("none", {})
        
        for provider, provider_results in self.results.items():
            if provider == "none":
                continue
                
            speedups = {}
            for operation, metrics in provider_results.items():
                baseline_time = baseline.get(operation, {}).get("avg_ms", 0)
                cached_time = metrics.get("avg_ms", 0)
                
                if cached_time > 0 and baseline_time > 0:
                    speedups[operation] = baseline_time / cached_time
                else:
                    speedups[operation] = 1.0
            
            provider_results["speedups"] = speedups
    
    def print_results(self):
        """Print benchmark results in readable format."""
        print("\n=== Benchmark Results ===")
        
        for provider, results in self.results.items():
            print(f"\n{provider.upper()} Cache Provider:")
            print(f"{'Operation':<20} {'Avg (ms)':<10} {'Min (ms)':<10} {'Max (ms)':<10} {'Speedup':<10}")
            print("-" * 70)
            
            for operation, metrics in results.items():
                if operation == "speedups":
                    continue
                    
                avg = metrics.get("avg_ms", 0)
                min_time = metrics.get("min_ms", 0)
                max_time = metrics.get("max_ms", 0)
                speedup = results.get("speedups", {}).get(operation, 1.0)
                
                print(f"{operation:<20} {avg:<10.2f} {min_time:<10.2f} {max_time:<10.2f} {speedup:<10.1f}x")
    
    def generate_doc_table(self):
        """Generate markdown table for documentation."""
        print("\n=== Documentation Table ===")
        
        # Header
        operations = ["get_plan", "list_artifacts", "get_artifact", "get_conversation", "get_summary"]
        
        print("| Operation | No Cache | Memory Cache | Redis Cache | Memory Speedup | Redis Speedup |")
        print("|-----------|----------|--------------|-------------|----------------|---------------|")
        
        for operation in operations:
            none_time = self.results.get("none", {}).get(operation, {}).get("avg_ms", 0)
            memory_time = self.results.get("memory", {}).get(operation, {}).get("avg_ms", 0)
            redis_time = self.results.get("redis", {}).get(operation, {}).get("avg_ms", 0) if "redis" in self.results else 0
            
            memory_speedup = self.results.get("memory", {}).get("speedups", {}).get(operation, 1.0)
            redis_speedup = self.results.get("redis", {}).get("speedups", {}).get(operation, 1.0) if "redis" in self.results else 0
            
            operation_display = operation.replace("_", " ").title()
            
            if redis_time > 0:
                print(f"| {operation_display:<9} | {none_time:>6.2f}ms | {memory_time:>8.2f}ms | {redis_time:>7.2f}ms | {memory_speedup:>10.1f}x | {redis_speedup:>9.1f}x |")
            else:
                print(f"| {operation_display:<9} | {none_time:>6.2f}ms | {memory_time:>8.2f}ms | N/A | {memory_speedup:>10.1f}x | N/A |")
        
        # Summary statistics
        print("\n=== Summary Statistics ===")
        
        for provider in ["memory", "redis"]:
            if provider not in self.results:
                continue
                
            speedups = list(self.results[provider].get("speedups", {}).values())
            if speedups:
                avg_speedup = statistics.mean(speedups)
                max_speedup = max(speedups)
                min_speedup = min(speedups)
                
                print(f"{provider.upper()} Cache:")
                print(f"  Average speedup: {avg_speedup:.1f}x")
                print(f"  Maximum speedup: {max_speedup:.1f}x")
                print(f"  Minimum speedup: {min_speedup:.1f}x")


async def main():
    """Run the comprehensive benchmark."""
    benchmark = ProjectBenchmark()
    
    try:
        await benchmark.run_comprehensive_benchmark()
    finally:
        await benchmark.cleanup()


if __name__ == "__main__":
    asyncio.run(main())