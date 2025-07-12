#!/usr/bin/env python3
"""
Test Crawl4AI with Reddit - a challenging site that usually blocks scrapers
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from agentx.builtin_tools.web import WebTool

async def test_reddit():
    """Test extraction from Reddit."""

    print("🧪 Testing Crawl4AI with Reddit")
    print("=" * 60)

    # Initialize web tool with Crawl4AI enabled
    web_tool = WebTool(use_crawl4ai=True)

    # Test Reddit URLs
    test_urls = [
        "https://www.reddit.com/r/webdev/comments/1ioekud/whats_the_current_state_of_web_development_in_2025/",
    ]

    print(f"Testing extraction from Reddit (usually blocks scrapers)...")

    try:
        result = await web_tool.extract_content(test_urls)

        if result.success:
            print("✅ Reddit extraction successful!")
            print(f"📊 Results: {result.metadata}")

            # Show content preview
            item = result.result[0] if isinstance(result.result, list) else result.result
            print(f"\n📄 {item['title']}")
            print(f"🔗 {item['url']}")
            print(f"📝 Length: {item['content_length']} chars")
            if item['extraction_successful']:
                preview = item['content_preview'][:300] + "..." if len(item['content_preview']) > 300 else item['content_preview']
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
    asyncio.run(test_reddit())
