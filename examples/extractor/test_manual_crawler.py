#!/usr/bin/env python3
"""
Test manual crawler lifecycle management to avoid context errors
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

async def test_manual_lifecycle():
    """Test Crawl4AI with manual lifecycle management."""
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

    print("🧪 Testing Manual Crawler Lifecycle")
    print("=" * 60)

    # Configuration that should work
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        browser_mode="dedicated",
        use_persistent_context=False,
        verbose=True,  # Enable verbose logging
    )

    crawler = None
    try:
        # Create crawler instance
        crawler = AsyncWebCrawler(config=browser_config)

        # Manually initialize
        await crawler.__aenter__()

        # Test URL
        result = await crawler.arun(url="https://example.com")

        if result.success:
            print(f"✅ Success! Content length: {len(result.markdown) if result.markdown else 0}")
        else:
            print(f"❌ Failed: {result.error_message}")

    except Exception as e:
        print(f"💥 Exception during crawl: {type(e).__name__}: {e}")
    finally:
        # Manual cleanup with error handling
        if crawler:
            try:
                await crawler.__aexit__(None, None, None)
                print("✅ Crawler cleaned up successfully")
            except Exception as cleanup_error:
                print(f"⚠️  Error during cleanup (expected): {cleanup_error}")
                print("This is the browser lifecycle bug from PR #1211")

    print("\n" + "=" * 60)

    # Test with multiple URLs to see if error is consistent
    print("\n🧪 Testing Multiple URLs")
    print("=" * 60)

    crawler2 = AsyncWebCrawler(config=browser_config)
    try:
        await crawler2.__aenter__()

        urls = ["https://example.com", "https://httpbin.org/html"]
        for url in urls:
            try:
                result = await crawler2.arun(url=url)
                status = "✅" if result.success else "❌"
                print(f"{status} {url}: {len(result.markdown) if result.markdown else 0} chars")
            except Exception as e:
                print(f"💥 {url}: {e}")

    except Exception as e:
        print(f"💥 Setup error: {e}")
    finally:
        try:
            await crawler2.__aexit__(None, None, None)
        except Exception as e:
            print(f"⚠️  Cleanup error (expected): {e}")

if __name__ == "__main__":
    asyncio.run(test_manual_lifecycle())
