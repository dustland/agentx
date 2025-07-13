#!/usr/bin/env python3
"""
Parallel Auto Writer Test - Tests the parallel execution improvements

This test compares sequential vs parallel execution times and verifies
that parallel execution works correctly for the auto_writer workflow.
"""

import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv
from agentx import start_task

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

async def test_sequential_execution():
    """Test sequential execution (current default behavior)."""
    print("\n🔄 Testing Sequential Execution")
    print("=" * 50)
    
    start_time = time.time()
    
    task = await start_task(
        "Create a brief 3-section report: Introduction to Python web frameworks, Flask overview, and FastAPI overview. Keep each section concise.",
        "config/team.yaml"
    )
    
    step_count = 0
    max_steps = 6  # Limit for testing
    
    while not task.is_complete and step_count < max_steps:
        print(f"\n🔄 Sequential Step {step_count + 1}/{max_steps}")
        step_start = time.time()
        
        response = await task.step()
        
        step_time = time.time() - step_start
        print(f"⏱️  Step completed in {step_time:.1f}s: {response[:100]}...")
        step_count += 1
    
    total_time = time.time() - start_time
    print(f"\n📊 Sequential Execution Results:")
    print(f"   Total time: {total_time:.1f}s")
    print(f"   Steps completed: {step_count}")
    print(f"   Average time per step: {total_time/step_count:.1f}s")
    
    return total_time, step_count


async def test_parallel_execution():
    """Test parallel execution (new functionality)."""
    print("\n⚡ Testing Parallel Execution")
    print("=" * 50)
    
    start_time = time.time()
    
    task = await start_task(
        "Create a brief 3-section report: Introduction to Python web frameworks, Flask overview, and FastAPI overview. Keep each section concise.",
        "config/team.yaml"
    )
    
    step_count = 0
    max_steps = 6  # Limit for testing
    
    while not task.is_complete and step_count < max_steps:
        print(f"\n⚡ Parallel Step {step_count + 1}/{max_steps}")
        step_start = time.time()
        
        # Use the new parallel execution method
        response = await task.step_parallel(max_concurrent=3)
        
        step_time = time.time() - step_start
        print(f"⏱️  Parallel step completed in {step_time:.1f}s")
        
        # Count number of tasks executed in this step
        if "✅" in response:
            parallel_tasks = response.count("✅")
            print(f"🔥 Executed {parallel_tasks} task(s) in parallel")
        
        print(f"📝 Result: {response[:150]}...")
        step_count += 1
    
    total_time = time.time() - start_time
    print(f"\n📊 Parallel Execution Results:")
    print(f"   Total time: {total_time:.1f}s")
    print(f"   Steps completed: {step_count}")
    print(f"   Average time per step: {total_time/step_count:.1f}s")
    
    return total_time, step_count


async def main():
    """Run both tests and compare results."""
    print("🚀 Parallel vs Sequential Auto Writer Comparison")
    print("=" * 60)
    
    try:
        # Test sequential execution
        seq_time, seq_steps = await test_sequential_execution()
        
        # Wait a bit between tests
        await asyncio.sleep(2)
        
        # Test parallel execution  
        par_time, par_steps = await test_parallel_execution()
        
        # Compare results
        print("\n📈 COMPARISON RESULTS")
        print("=" * 60)
        print(f"Sequential: {seq_time:.1f}s ({seq_steps} steps)")
        print(f"Parallel:   {par_time:.1f}s ({par_steps} steps)")
        
        if par_time < seq_time:
            speedup = seq_time / par_time
            print(f"🎉 Parallel execution is {speedup:.1f}x faster!")
            time_saved = seq_time - par_time
            print(f"💰 Time saved: {time_saved:.1f} seconds")
        else:
            print("ℹ️  No significant speedup (might be due to limited parallel opportunities)")
        
        print(f"\n📋 Performance Summary:")
        print(f"   Parallel overhead: {'✅ Minimal' if abs(par_time - seq_time) < 5 else '⚠️ Some overhead detected'}")
        print(f"   Task execution: {'✅ Working' if par_steps > 0 else '❌ Failed'}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())