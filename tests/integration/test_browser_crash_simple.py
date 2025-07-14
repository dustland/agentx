#!/usr/bin/env python3
"""
Simplified test to reproduce browser crashes with minimal setup.
Focus on the exact conditions that cause crashes.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


async def test_single_browser_instance():
    """Test single browser instance - should work."""
    print("=== Test 1: Single Browser Instance ===")
    
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        verbose=False
    )
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print("✓ Browser created successfully")
            
            result = await crawler.arun(
                url="https://example.com",
                config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
            )
            
            print(f"✓ Crawled successfully: {result.success}")
            
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {str(e)}")
        if "Target page, context or browser has been closed" in str(e):
            print("  ⚠️ BROWSER CONTEXT CRASH DETECTED!")


async def test_multiple_urls_same_browser():
    """Test multiple URLs with same browser - might crash."""
    print("\n=== Test 2: Multiple URLs, Same Browser ===")
    
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        verbose=False
    )
    
    urls = [
        "https://medium.com",
        "https://dev.to",
        "https://github.com"
    ]
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print("✓ Browser created")
            
            for i, url in enumerate(urls):
                print(f"\nCrawling URL {i+1}: {url}")
                try:
                    result = await crawler.arun(
                        url=url,
                        config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
                    )
                    print(f"  ✓ Success: {result.success}")
                except Exception as e:
                    print(f"  ✗ FAILED: {type(e).__name__}: {str(e)[:100]}...")
                    if "closed" in str(e).lower():
                        print("    ⚠️ BROWSER CRASH!")
                        raise
                        
    except Exception as e:
        print(f"\n✗ Browser instance failed: {type(e).__name__}")


async def test_new_browser_per_url():
    """Test new browser per URL - current 'fix'."""
    print("\n=== Test 3: New Browser Per URL ===")
    
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        verbose=False
    )
    
    urls = [
        "https://medium.com",
        "https://dev.to",
        "https://github.com"
    ]
    
    for i, url in enumerate(urls):
        print(f"\nURL {i+1}: {url}")
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                print("  ✓ New browser created")
                
                result = await crawler.arun(
                    url=url,
                    config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
                )
                print(f"  ✓ Crawled: {result.success}")
                
        except Exception as e:
            print(f"  ✗ FAILED: {type(e).__name__}: {str(e)[:100]}...")


async def test_parallel_browser_instances():
    """Test parallel browser instances - stress test."""
    print("\n=== Test 4: Parallel Browser Instances ===")
    
    async def crawl_url(url: str, index: int):
        browser_config = BrowserConfig(
            browser_type="chromium",
            headless=True,
            verbose=False
        )
        
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                print(f"  Browser {index}: Created for {url}")
                
                result = await crawler.arun(
                    url=url,
                    config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
                )
                
                print(f"  Browser {index}: Success = {result.success}")
                return result.success
                
        except Exception as e:
            print(f"  Browser {index}: FAILED - {type(e).__name__}")
            return False
    
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://www.python.org"
    ]
    
    print(f"Starting {len(urls)} parallel browsers...")
    
    tasks = [crawl_url(url, i) for i, url in enumerate(urls)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = sum(1 for r in results if r is True)
    print(f"\nResults: {success_count}/{len(urls)} successful")


async def main():
    """Run all tests."""
    print("🧪 BROWSER CRASH REPRODUCTION TESTS")
    print("Testing different browser usage patterns...\n")
    print("-" * 50)
    
    tests = [
        test_single_browser_instance,
        test_multiple_urls_same_browser,
        test_new_browser_per_url,
        test_parallel_browser_instances
    ]
    
    for test in tests:
        try:
            await test()
        except Exception as e:
            print(f"\n💥 Test crashed: {type(e).__name__}: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Tests completed")


if __name__ == "__main__":
    # Check if we're on macOS
    import platform
    if platform.system() == "Darwin":
        mac_ver = platform.mac_ver()[0]
        print(f"Running on macOS {mac_ver}")
    
    asyncio.run(main())