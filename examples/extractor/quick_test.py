#!/usr/bin/env python3
"""
Quick Crawl4AI Test - Simple extraction test to verify fixes
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from agentx.builtin_tools.web import WebTool

async def test_crawl4ai():
    """Quick test of Crawl4AI extraction with the browser fixes."""

    print("🧪 Quick Crawl4AI Test")
    print("=" * 50)

    # Initialize web tool
    web_tool = WebTool()

    # Test URLs - start with simple ones
    test_urls = [
        "https://httpbin.org/html",  # Simple HTML
        "https://example.com",       # Basic site
    ]

    print(f"Testing extraction from {len(test_urls)} URLs...")

    try:
        result = await web_tool.extract_content(test_urls)

        if result.success:
            print("✅ Extraction successful!")
            print(f"📊 Results: {result.metadata}")

            # Show content previews
            for item in result.result:
                print(f"\n📄 {item['title']}")
                print(f"🔗 {item['url']}")
                print(f"📝 Length: {item['content_length']} chars")
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
    asyncio.run(test_crawl4ai())
