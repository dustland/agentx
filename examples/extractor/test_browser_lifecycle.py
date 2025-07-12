#!/usr/bin/env python3
"""
Test to reproduce browser lifecycle errors
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

async def test_direct_crawl4ai():
    """Test Crawl4AI directly to see browser errors."""
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

    print("🧪 Testing Crawl4AI Browser Lifecycle")
    print("=" * 60)

    # Test different configurations
    configs = [
        {
            "name": "Default (causes crashes)",
            "config": BrowserConfig(
                browser_type="chromium",
                headless=True,
            )
        },
        {
            "name": "Dedicated mode workaround",
            "config": BrowserConfig(
                browser_type="chromium",
                headless=True,
                browser_mode="dedicated",
                use_persistent_context=False,
            )
        },
        {
            "name": "Managed browser mode",
            "config": BrowserConfig(
                browser_type="chromium",
                headless=True,
                browser_mode="managed",
                use_managed_browser=True,
            )
        }
    ]

    for test_config in configs:
        print(f"\n🔧 Testing: {test_config['name']}")
        print("-" * 40)

        try:
            async with AsyncWebCrawler(config=test_config['config']) as crawler:
                result = await crawler.arun(url="https://example.com")
                if result.success:
                    print(f"✅ Success! Content length: {len(result.markdown) if result.markdown else 0}")
                else:
                    print(f"❌ Failed: {result.error_message}")
        except Exception as e:
            print(f"💥 Exception: {type(e).__name__}: {e}")

        # Small delay between tests
        await asyncio.sleep(1)

    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(test_direct_crawl4ai())
