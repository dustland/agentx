#!/usr/bin/env python3
"""
Test the fixed error handling in research_topic.
This should properly report failures when browser crashes occur.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agentx.builtin_tools.research import ResearchTool


async def test_research_with_problematic_urls():
    """Test research with URLs that might cause browser issues."""
    print("🧪 TESTING RESEARCH ERROR HANDLING")
    print("=" * 60)
    
    research_tool = ResearchTool()
    
    # Test 1: Known problematic URLs
    print("\n📋 Test 1: URLs that often cause browser issues")
    problematic_urls = [
        "https://medium.com/@someuser/very-long-article-that-might-crash",
        "https://heavy-javascript-site.com",
        "https://site-that-does-not-exist-12345.com"
    ]
    
    result = await research_tool.research_topic(
        query="Test browser crash handling",
        start_urls=problematic_urls,
        max_pages=5,
        search_first=False
    )
    
    print(f"Success: {result.success}")
    print(f"Metadata: {result.metadata}")
    
    if not result.success:
        print("\n✅ GOOD: Properly reported failure")
        print(f"Error: {result.metadata.get('error')}")
        print(f"Failed URLs: {result.metadata.get('failed_urls')}")
        print(f"Browser errors: {result.metadata.get('browser_errors')}")
    else:
        print(f"\n⚠️  Research claimed success")
        print(f"Pages crawled: {result.metadata.get('pages_crawled', 0)}")
        print(f"Files saved: {result.metadata.get('files_saved', 0)}")
        
        # Check if it's a fake success
        if result.metadata.get('pages_crawled', 0) == 0:
            print("❌ BAD: Fake success with 0 pages crawled!")
    
    print("\n" + "-" * 60)
    
    # Test 2: Mix of good and bad URLs
    print("\n📋 Test 2: Mix of working and failing URLs")
    mixed_urls = [
        "https://example.com",  # Should work
        "https://httpbin.org/html",  # Should work
        "https://site-that-will-fail-99999.com"  # Will fail
    ]
    
    result2 = await research_tool.research_topic(
        query="Test partial failure handling",
        start_urls=mixed_urls,
        max_pages=5,
        search_first=False
    )
    
    print(f"Success: {result2.success}")
    print(f"Metadata: {result2.metadata}")
    
    # Check for partial failure info
    failed_urls = result2.metadata.get('failed_urls') if result2.success else result2.metadata.get('failed_urls')
    if failed_urls:
        print(f"\n⚠️  Some URLs failed: {failed_urls}")
        browser_errors = result2.metadata.get('browser_errors')
        if browser_errors:
            print(f"Browser errors: {browser_errors}")
    
    if result2.success:
        # Get the result data properly
        if hasattr(result2.result, 'pages_crawled'):
            pages = result2.result.pages_crawled
        elif isinstance(result2.result, dict):
            pages = result2.result.get('pages_crawled', 0)
        else:
            pages = 0
            
        print(f"\n✅ Partial success: {pages} pages crawled")
    
    print("\n" + "-" * 60)
    
    # Test 3: Empty/lightweight URL that returns no content
    print("\n📋 Test 3: URL with no relevant content")
    empty_urls = ["https://httpbin.org/status/200"]  # Returns empty 200 response
    
    result3 = await research_tool.research_topic(
        query="Find detailed technical documentation",
        start_urls=empty_urls,
        max_pages=2,
        search_first=False
    )
    
    print(f"Success: {result3.success}")
    
    if not result3.success:
        print("✅ GOOD: Properly reported no content found")
        print(f"Error: {result3.metadata.get('error')}")
    else:
        # Check if it found any content
        if isinstance(result3.result, dict):
            content_count = len(result3.result.get('relevant_content', []))
            files_count = len(result3.result.get('saved_files', []))
        else:
            content_count = 0
            files_count = 0
            
        print(f"Content found: {content_count} items")
        print(f"Files saved: {files_count}")
        
        if content_count == 0 and files_count == 0:
            print("⚠️  Success with no actual content - might be incorrect")


async def test_browser_crash_simulation():
    """Test with heavy load that might trigger browser crashes."""
    print("\n\n📋 Test 4: Heavy load (might trigger real crashes on macOS beta)")
    
    research_tool = ResearchTool()
    
    # Heavy sites that caused crashes before
    heavy_urls = [
        "https://medium.com/@danieltaylor2120/the-future-of-backend-development-frameworks-whats-coming-next-in-2025-5b32385b75d0",
        "https://dev.to/hamzakhan/nextjs-vs-qwik-who-wins-the-performance-race-in-2025-21m9"
    ]
    
    print("Starting research on heavy sites...")
    print("Watch for browser context errors...\n")
    
    result = await research_tool.research_topic(
        query="Backend development trends 2025",
        start_urls=heavy_urls,
        max_pages=10,  # Lower limit to reduce load
        search_first=False
    )
    
    print(f"\nSuccess: {result.success}")
    
    if not result.success:
        print("Research failed (as expected on problematic systems)")
        error_details = result.metadata
        
        # Check for browser crash indicators
        if error_details.get('browser_errors'):
            for error in error_details['browser_errors']:
                if "browser has been closed" in error.lower() or "context" in error.lower():
                    print(f"\n🎯 BROWSER CRASH DETECTED: {error}")
        
        print(f"\nFull error details: {error_details}")
    else:
        print("Research succeeded (system is stable)")
        if isinstance(result.result, dict):
            print(f"Pages crawled: {result.result.get('pages_crawled', 0)}")
            print(f"Files saved: {len(result.result.get('saved_files', []))}")


async def main():
    """Run all tests."""
    try:
        await test_research_with_problematic_urls()
        await test_browser_crash_simulation()
        
        print("\n" + "=" * 60)
        print("✅ Error handling tests completed")
        print("\nThe research tool should now:")
        print("- Return success=False when all URLs fail")
        print("- Return success=False when no content is extracted")
        print("- Include browser crash details in error messages")
        print("- Report partial failures in metadata")
        
    except Exception as e:
        print(f"\n💥 Test failed with exception: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Testing research tool error handling...")
    print("This will verify browser crashes are properly reported as failures.\n")
    
    asyncio.run(main())