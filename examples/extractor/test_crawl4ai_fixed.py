#!/usr/bin/env python3
"""
Test the fixed Crawl4AI implementation based on working Playwright patterns
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from agentx.builtin_tools.web import WebTool

async def test_crawl4ai_fixed():
    """Test the fixed Crawl4AI extraction."""

    print("🧪 Testing Fixed Crawl4AI Implementation")
    print("=" * 60)

    # Initialize web tool with Crawl4AI enabled
    web_tool = WebTool(use_crawl4ai=True)

    # Test URLs
    test_urls = [
        "https://example.com",       # Basic site
        "https://httpbin.org/html",  # Simple HTML
    ]

    print(f"Testing Crawl4AI extraction from {len(test_urls)} URLs...")
    print("(This should use the improved configuration based on your working Playwright project)")

    try:
        result = await web_tool.extract_content(test_urls)

        if result.success:
            print("✅ Crawl4AI extraction successful!")
            print(f"📊 Results: {result.metadata}")

            # Show content previews
            for item in result.result:
                print(f"\n📄 {item['title']}")
                print(f"🔗 {item['url']}")
                print(f"📝 Length: {item['content_length']} chars")
                print(f"🔧 Method: {item.get('extraction_method', 'unknown')}")
                if item['extraction_successful']:
                    preview = item['content_preview'][:200] + "..." if len(item['content_preview']) > 200 else item['content_preview']
                    print(f"📋 Preview: {preview}")
                else:
                    print(f"❌ Error: {item.get('error', 'Unknown error')}")
        else:
            print("❌ Extraction failed!")
            print(f"Error: {result.error}")

    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_crawl4ai_fixed())
