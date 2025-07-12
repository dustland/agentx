#!/usr/bin/env python3
"""
Test Playwright directly to see if the issue is with Crawl4AI or Playwright itself
"""

import asyncio
import sys
import os

async def test_playwright_direct():
    """Test Playwright directly without Crawl4AI."""

    print("🧪 Testing Playwright directly...")

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            print("✅ Playwright imported successfully")

            # Launch browser
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            print("✅ Browser launched successfully")

            # Create context and page
            context = await browser.new_context()
            page = await context.new_page()
            print("✅ Page created successfully")

            # Navigate to a test URL
            await page.goto('https://example.com')
            title = await page.title()
            content = await page.content()

            print(f"✅ Successfully extracted from example.com:")
            print(f"   Title: {title}")
            print(f"   Content length: {len(content)} chars")

            # Clean up
            await page.close()
            await context.close()
            await browser.close()
            print("✅ Browser closed cleanly")

    except ImportError:
        print("❌ Playwright not installed")
        print("Install with: uv add playwright")
        print("Then run: uv run playwright install chromium")
    except Exception as e:
        print(f"❌ Playwright test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_crawl4ai_minimal():
    """Test Crawl4AI with minimal configuration."""

    print("\n🧪 Testing Crawl4AI with minimal config...")

    try:
        from crawl4ai import AsyncWebCrawler

        config = {
            "headless": True,
            "verbose": True,  # Enable verbose logging
        }

        async with AsyncWebCrawler(**config) as crawler:
            print("✅ Crawl4AI crawler created")

            result = await crawler.arun("https://example.com")

            if result.success:
                print(f"✅ Crawl4AI extraction successful:")
                print(f"   Content length: {len(result.cleaned_html or '')} chars")
            else:
                print(f"❌ Crawl4AI extraction failed: {result.error_message}")

    except ImportError:
        print("❌ Crawl4AI not installed")
    except Exception as e:
        print(f"❌ Crawl4AI test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_playwright_direct())
    asyncio.run(test_crawl4ai_minimal())
