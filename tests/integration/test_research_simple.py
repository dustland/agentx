#!/usr/bin/env python3
"""
Simple test to verify research error handling works.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agentx.builtin_tools.research import ResearchTool


async def main():
    research_tool = ResearchTool()
    
    print("Test 1: URL that doesn't exist")
    result = await research_tool.research_topic(
        query="Test error handling",
        start_urls=["https://this-site-definitely-does-not-exist-12345.com"],
        max_pages=2,
        search_first=False
    )
    
    print(f"\nSuccess: {result.success}")
    if not result.success:
        print("✅ GOOD: Correctly reported failure")
        print(f"Error: {result.metadata.get('error')}")
        print(f"Failed URLs: {result.metadata.get('failed_urls')}")
    else:
        print("❌ BAD: Should have failed but didn't")
        if hasattr(result.result, 'pages_crawled'):
            pages = result.result.pages_crawled
        elif isinstance(result.result, dict):
            pages = result.result.get('pages_crawled', 0)
        else:
            pages = 0
        print(f"Pages crawled: {pages}")
    
    print("\n" + "-" * 50)
    
    print("\nTest 2: Empty response URL")
    result2 = await research_tool.research_topic(
        query="Find technical content",
        start_urls=["https://httpbin.org/status/200"],
        max_pages=2,
        search_first=False
    )
    
    print(f"\nSuccess: {result2.success}")
    if not result2.success:
        print("✅ GOOD: Correctly reported no content")
        print(f"Error: {result2.metadata.get('error')}")
    else:
        print("Checking if it found content...")
        if isinstance(result2.result, dict):
            content = result2.result.get('relevant_content', [])
            files = result2.result.get('saved_files', [])
            print(f"Content items: {len(content)}")
            print(f"Files saved: {len(files)}")


if __name__ == "__main__":
    asyncio.run(main())