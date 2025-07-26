#!/usr/bin/env python3
"""
Test that mimics the actual auto_writer heavy load pattern.
This should reproduce the crashes you're experiencing.
"""

import asyncio
import os
import sys
import time
from typing import List
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from vibex.builtin_tools.web import WebTool
from vibex.builtin_tools.research import ResearchTool
from vibex.builtin_tools.file import FileTool
from vibex.storage.project import ProjectStorage
from vibex.project import start_project, resume_project


async def simulate_researcher_agent():
    """Simulate the researcher agent's heavy workload."""
    print("\n🔬 SIMULATING RESEARCHER AGENT")
    print("=" * 60)
    
    # Create tools with project_storage
    temp_dir = tempfile.mkdtemp()
    project_storage = ProjectStorage(project_path=temp_dir)
    web_tool = WebTool(taskspace_storage=project_storage)
    research_tool = ResearchTool(taskspace_storage=project_storage)
    file_tool = FileTool(taskspace_storage=project_storage)
    
    # Heavy URLs like auto_writer uses
    heavy_urls = [
        "https://medium.com/@danieltaylor2120/the-future-of-backend-development-frameworks-whats-coming-next-in-2025-5b32385b75d0",
        "https://www.wisp.blog/blog/where-is-serverless-going-in-2025",
        "https://citrusbug.com/blog/backend-development-trends/",
        "https://dev.to/hamzakhan/nextjs-vs-qwik-who-wins-the-performance-race-in-2025-21m9",
        "https://medium.com/front-end-weekly/next-js-trends-2025-essential-insights-every-business-should-know-3c49c25641fb"
    ]
    
    # Research queries like in auto_writer
    research_queries = [
        "Next.js performance and trends 2025",
        "Vue.js framework features 2025", 
        "Backend development frameworks 2025",
        "AI integration in web development 2025"
    ]
    
    print("\n📋 Phase 1: Parallel Web Extraction (mimics search_and_extract)")
    print(f"Extracting {len(heavy_urls)} heavy URLs in parallel...")
    
    # Create parallel extraction tasks
    extract_tasks = []
    for url in heavy_urls:
        print(f"  - Queuing: {url[:60]}...")
        extract_tasks.append(web_tool.extract_urls(url))
    
    # Execute all extractions in parallel (this is where crashes happen)
    print(f"\n🔥 Executing {len(extract_tasks)} parallel extractions...")
    start_time = time.time()
    
    try:
        results = await asyncio.gather(*extract_tasks, return_exceptions=True)
        
        # Count successes/failures
        successes = sum(1 for r in results if not isinstance(r, Exception) and getattr(r, 'success', False))
        failures = len(results) - successes
        
        print(f"⏱️  Extraction completed in {time.time() - start_time:.1f}s")
        print(f"📊 Results: {successes} successful, {failures} failed")
        
        # Check for specific errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_str = str(result)
                if "Target page, context or browser has been closed" in error_str:
                    print(f"  ⚠️  URL {i+1}: BROWSER CONTEXT CRASH!")
                elif "timeout" in error_str.lower():
                    print(f"  ⚠️  URL {i+1}: TIMEOUT!")
                else:
                    print(f"  ❌ URL {i+1}: {type(result).__name__}")
    
    except Exception as e:
        print(f"\n💥 PARALLEL EXTRACTION CRASHED: {type(e).__name__}: {str(e)}")
        raise
    
    print("\n📋 Phase 2: Parallel Research Topics (mimics research_topic calls)")
    print(f"Researching {len(research_queries)} topics in parallel...")
    
    # Create parallel research tasks
    research_tasks = []
    for query in research_queries:
        print(f"  - Queuing research: {query}")
        research_tasks.append(research_tool.research_topic(
            query=query,
            max_pages=5,
            search_first=False,
            start_urls=heavy_urls[:2]  # Use some heavy URLs as starting points
        ))
    
    # Execute research in parallel
    print(f"\n🔥 Executing {len(research_tasks)} parallel research tasks...")
    start_time = time.time()
    
    try:
        research_results = await asyncio.gather(*research_tasks, return_exceptions=True)
        
        # Analyze results
        for i, result in enumerate(research_results):
            if isinstance(result, Exception):
                print(f"  ❌ Research {i+1}: {type(result).__name__}: {str(result)[:100]}...")
                if "Maximum concurrent executions exceeded" in str(result):
                    print("    ⚠️  CONCURRENCY LIMIT HIT!")
            elif hasattr(result, 'success') and not result.success:
                print(f"  ❌ Research {i+1}: Failed - {result.metadata.get('error', 'Unknown')}")
            else:
                print(f"  ✅ Research {i+1}: Success")
        
        print(f"⏱️  Research completed in {time.time() - start_time:.1f}s")
        
    except Exception as e:
        print(f"\n💥 RESEARCH PHASE CRASHED: {type(e).__name__}: {str(e)}")
        raise
    
    print("\n📋 Phase 3: File Operations (mimics project_storage saves)")
    print("Simulating file writes that happen during research...")
    
    # Simulate file operations
    for i in range(5):
        try:
            await file_tool.write_file(
                file_path=f"research_result_{i}.md",
                content=f"# Research Result {i}\n\n" + "Lorem ipsum " * 1000
            )
            print(f"  ✅ Wrote research_result_{i}.md")
        except Exception as e:
            print(f"  ❌ File write failed: {e}")
    
    print("\n✅ Researcher simulation complete")
    return project_storage


async def simulate_full_auto_writer_load():
    """Simulate the full auto_writer multi-agent load."""
    print("\n🤖 SIMULATING FULL AUTO_WRITER LOAD")
    print("This mimics: Researcher → Writer → Web Designer → Reviewer")
    print("=" * 60)
    
    # Simulate multiple agent steps
    for step in range(3):
        print(f"\n📍 Step {step + 1}/3")
        
        try:
            # Each step involves heavy parallel operations
            project_storage = await simulate_researcher_agent()
            
            # Brief pause between steps (like agent handoffs)
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"\n💥 STEP {step + 1} CRASHED: {type(e).__name__}")
            print(f"Details: {str(e)}")
            raise
    
    print("\n✅ Full auto_writer simulation complete")


async def test_concurrent_limit():
    """Test hitting the concurrent execution limit."""
    print("\n🔨 TESTING CONCURRENT EXECUTION LIMIT")
    print("=" * 60)
    
    web_tool = WebTool()
    
    # Try to run more than MAX_CONCURRENT_EXECUTIONS (5)
    urls = [
        "https://example.com",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2", 
        "https://httpbin.org/delay/3",
        "https://httpbin.org/delay/4",
        "https://httpbin.org/delay/5"
    ]
    
    print(f"Attempting {len(urls)} concurrent extractions (limit is 5)...")
    
    tasks = [web_tool.extract_urls(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    limit_errors = sum(1 for r in results if isinstance(r, Exception) and "concurrent" in str(r).lower())
    print(f"Concurrent limit errors: {limit_errors}")
    
    if limit_errors > 0:
        print("⚠️  CONCURRENCY LIMIT DETECTED - This is what auto_writer hits!")


async def main():
    """Run all load tests."""
    print("🧪 AUTO_WRITER HEAVY LOAD REPRODUCTION TEST")
    print(f"Simulating the exact conditions that cause crashes...")
    print("-" * 60)
    
    # Check system
    import platform
    if platform.system() == "Darwin":
        print(f"macOS version: {platform.mac_ver()[0]}")
    
    try:
        # Test 1: Concurrent limit
        await test_concurrent_limit()
        
        # Test 2: Full auto_writer simulation
        await simulate_full_auto_writer_load()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed without crashes")
        print("(Your environment may still crash due to macOS beta + heavy load)")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"💥 CRASH REPRODUCED!")
        print(f"Type: {type(e).__name__}")
        print(f"Details: {str(e)}")
        
        if "Target page, context or browser has been closed" in str(e):
            print("\n⚠️  This is the EXACT browser context crash you're experiencing!")
        
        return 1
    
    return 0


async def test_auto_writer_load_and_resume():
    """Test auto_writer load and resume functionality."""
    # --- Setup ---
    # Use a predefined project ID to ensure we can resume it
    project_id = "test_auto_writer_load_resume"
    config_path = Path(__file__).parent.parent.parent / "examples/auto_writer/config/team.yaml"

    # --- Initial Run (to create a project to resume) ---
    print(f"--- Creating initial project '{project_id}' ---")
    initial_project = await start_project(
        goal="This is a test project to be resumed.",
        config_path=config_path,
        project_id=project_id,
    )
    # Run one step to generate some state
    await initial_project.step()
    print("--- Initial project created. ---")

    # --- Test Resumption ---
    print(f"--- Resuming project '{project_id}' ---")
    resumed_project = await resume_project(
        project_id=project_id,
        config_path=config_path,
    )

    # --- Verification ---
    # 1. Check if the project ID is the same
    assert resumed_project.project_id == project_id, "Resumed project should have the same ID."

    # 2. Check if the initial goal is loaded correctly
    assert "test project to be resumed" in resumed_project.goal, "Goal not loaded correctly."

    # 3. Check if the plan was loaded
    assert resumed_project.plan is not None, "Plan should be loaded from the resumed project."
    assert len(resumed_project.plan.tasks) > 0, "Plan should have tasks."
    
    # 4. Check if conversation history is loaded (at least the initial prompt)
    assert len(resumed_project.history.messages) > 0, "Conversation history should not be empty."

    print("✅ Auto-writer load and resume test passed!")

if __name__ == "__main__":
    print("Starting heavy load test in 3 seconds...")
    print("This will create significant browser load like auto_writer does.")
    print("Watch for crashes, timeouts, and browser context errors!\n")
    
    asyncio.run(asyncio.sleep(3))
    exit_code = asyncio.run(main())
    sys.exit(exit_code)