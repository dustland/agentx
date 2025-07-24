#!/usr/bin/env python3
"""
Test to reproduce the exact crash scenario in research_topic.
Start with light load, exactly as research_topic does it.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from vibex.builtin_tools.research import ResearchTool


async def test_single_research_light():
    """Test a single research query - light load."""
    print("=== Testing Single Research Query (Light Load) ===\n")
    
    research_tool = ResearchTool()
    
    # Simple query that should work
    query = "Python web frameworks 2025"
    
    print(f"🔍 Researching: {query}")
    print("This mimics exactly what happens when research_topic is called...\n")
    
    try:
        result = await research_tool.research_topic(
            query=query,
            start_urls=["https://example.com"],  # Start with simple URL
            max_pages=3
        )
        
        if result.success:
            print("✅ Research completed successfully!")
            # result.result might be a dict or object
            if hasattr(result.result, 'pages_crawled'):
                print(f"   - Pages crawled: {result.result.pages_crawled}")
                print(f"   - Confidence: {result.result.confidence}")
                print(f"   - Files saved: {len(result.result.saved_files)}")
            else:
                print(f"   - Result type: {type(result.result)}")
                print(f"   - Metadata: {result.metadata}")
        else:
            print(f"❌ Research failed: {result.metadata.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"💥 CRASH DETECTED: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        if "Target page, context or browser has been closed" in str(e):
            print("   ⚠️  THIS IS THE BROWSER CONTEXT BUG!")
        raise


async def test_parallel_research_light():
    """Test parallel research queries - simulating auto_writer load."""
    print("\n=== Testing Parallel Research Queries (Light Load) ===\n")
    
    research_tool = ResearchTool()
    
    # Multiple light queries
    queries = [
        ("Vue.js features 2025", ["https://vuejs.org"]),
        ("React trends 2025", ["https://react.dev"]),
        ("Svelte adoption 2025", ["https://svelte.dev"])
    ]
    
    print(f"🔥 Running {len(queries)} research tasks in parallel...")
    print("This simulates what auto_writer does...\n")
    
    tasks = []
    for query, urls in queries:
        print(f"   - Creating task: {query}")
        tasks.append(research_tool.research_topic(
            query=query,
            start_urls=urls,
            max_pages=2
        ))
    
    # Run all in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Analyze results
    for i, (result, (query, _)) in enumerate(zip(results, queries)):
        if isinstance(result, Exception):
            print(f"\n❌ Task {i+1} ({query}) CRASHED:")
            print(f"   {type(result).__name__}: {str(result)}")
            if "Maximum concurrent executions exceeded" in str(result):
                print("   ⚠️  CONCURRENCY LIMIT HIT!")
            elif "Target page, context or browser has been closed" in str(result):
                print("   ⚠️  BROWSER CONTEXT CRASH!")
        elif result.success:
            print(f"\n✅ Task {i+1} ({query}) succeeded")
        else:
            print(f"\n❌ Task {i+1} ({query}) failed: {result.metadata.get('error', 'Unknown')}")


async def test_research_with_search():
    """Test research with search enabled (if API key available)."""
    print("\n=== Testing Research with Search ===\n")
    
    research_tool = ResearchTool()
    
    if not research_tool.SERPAPI_API_KEY:
        print("⚠️  No SERPAPI_API_KEY found, skipping search test")
        return
    
    print("🔍 Researching with search enabled...")
    
    try:
        result = await research_tool.research_topic(
            query="AI code generation tools 2025",
            search_first=True,
            max_pages=3
        )
        
        if result.success:
            print("✅ Search-based research succeeded!")
        else:
            print(f"❌ Search-based research failed: {result.metadata.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"💥 CRASH: {type(e).__name__}: {str(e)}")
        raise


async def test_browser_instance_lifecycle():
    """Test how browser instances are created/destroyed."""
    print("\n=== Testing Browser Instance Lifecycle ===\n")
    
    from crawl4ai import AsyncWebCrawler, BrowserConfig
    
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        verbose=False
    )
    
    print("Creating and destroying browser instances like research_topic does...\n")
    
    urls = ["https://example.com", "https://httpbin.org/html", "https://www.python.org"]
    
    for i, url in enumerate(urls):
        print(f"Browser instance {i+1}:")
        try:
            # This is how research_topic creates a new browser per URL
            async with AsyncWebCrawler(config=browser_config) as crawler:
                print(f"   ✓ Browser created for {url}")
                # Simulate some work
                await asyncio.sleep(0.5)
            print(f"   ✓ Browser destroyed")
        except Exception as e:
            print(f"   ✗ Browser failed: {e}")


async def main():
    """Run all tests in sequence."""
    print("🧪 REPRODUCING RESEARCH_TOPIC CRASH SCENARIO\n")
    print("Starting with light load to isolate the issue...\n")
    print("-" * 60)
    
    try:
        # Test 1: Single light query
        await test_single_research_light()
        
        # Test 2: Parallel light queries  
        await test_parallel_research_light()
        
        # Test 3: With search
        await test_research_with_search()
        
        # Test 4: Browser lifecycle
        await test_browser_instance_lifecycle()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed without crashes")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"💥 CRASH REPRODUCED: {type(e).__name__}")
        print(f"Details: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)