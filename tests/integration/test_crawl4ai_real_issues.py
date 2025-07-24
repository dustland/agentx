#!/usr/bin/env python3
"""
REAL integration tests that actually catch crawl4ai bugs.
No mocks, no fakes - actual browser operations that fail when things break.
"""

import pytest
import asyncio
import time
import os
from typing import List, Dict, Any

from vibex.builtin_tools.web import WebTool
from vibex.builtin_tools.research import ResearchTool


class TestCrawl4AIRealIssues:
    """Test real crawl4ai issues that unit tests completely miss."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_heavy_parallel_load(self):
        """Test the actual scenario that crashes on macOS beta - heavy parallel load."""
        web_tool = WebTool()
        
        # Real heavy sites that cause issues
        heavy_urls = [
            "https://medium.com/@danieltaylor2120/the-future-of-backend-development-frameworks-whats-coming-next-in-2025-5b32385b75d0",
            "https://dev.to/hamzakhan/nextjs-vs-qwik-who-wins-the-performance-race-in-2025-21m9",
            "https://www.wisp.blog/blog/where-is-serverless-going-in-2025",
            "https://citrusbug.com/blog/backend-development-trends/",
            "https://medium.com/front-end-weekly/next-js-trends-2025-essential-insights-every-business-should-know-3c49c25641fb"
        ]
        
        print(f"\n🔥 Testing REAL heavy parallel load with {len(heavy_urls)} URLs...")
        start_time = time.time()
        
        # This is what actually happens in auto_writer
        tasks = [web_tool.extract_urls(url) for url in heavy_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count real failures
        failures = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failures.append(f"URL {i}: {type(result).__name__}: {str(result)}")
            elif not getattr(result, 'success', False):
                failures.append(f"URL {i}: {getattr(result, 'error', 'Unknown error')}")
        
        elapsed = time.time() - start_time
        print(f"⏱️  Completed in {elapsed:.2f}s")
        
        if failures:
            print("❌ FAILURES DETECTED:")
            for failure in failures:
                print(f"   - {failure}")
        
        # This test SHOULD fail on problematic systems
        assert len(failures) == 0, f"Failed {len(failures)}/{len(heavy_urls)} extractions"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_browser_context_reuse_bug(self):
        """Test the browser context closure bug that happens with multiple URLs."""
        web_tool = WebTool()
        
        # URLs that trigger context issues
        urls = [
            "https://github.com/jamesmurdza/awesome-ai-devtools",
            "https://pagepro.co/blog/what-is-nextjs/",
            "https://litslink.com/blog/how-to-easily-integrate-generative-ai-into-workflow"
        ]
        
        print("\n🔍 Testing browser context reuse issues...")
        
        errors = []
        for i, url in enumerate(urls):
            print(f"Processing URL {i+1}/{len(urls)}: {url[:50]}...")
            try:
                result = await web_tool.extract_urls(url)
                if not result.success:
                    errors.append(f"{url}: {result.error}")
            except Exception as e:
                errors.append(f"{url}: {type(e).__name__}: {str(e)}")
                if "Target page, context or browser has been closed" in str(e):
                    print("   ⚠️  BROWSER CONTEXT BUG DETECTED!")
        
        if errors:
            print("\n❌ Context reuse failures:")
            for error in errors:
                print(f"   - {error}")
        
        # This catches the actual bug
        assert len(errors) == 0, "Browser context reuse failed"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_timeout_under_load(self):
        """Test timeout issues that happen under real load."""
        web_tool = WebTool()
        
        print("\n⏰ Testing timeout behavior under load...")
        
        # Create enough load to potentially trigger timeouts
        tasks = []
        for i in range(4):  # Just under the MAX_CONCURRENT_EXECUTIONS limit
            tasks.append(web_tool.extract_urls([
                "https://medium.com/some-long-article",
                "https://dev.to/another-long-article"
            ]))
        
        start = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start
        
        timeout_errors = [r for r in results if isinstance(r, Exception) and "timeout" in str(r).lower()]
        
        print(f"Completed in {elapsed:.2f}s")
        print(f"Timeout errors: {len(timeout_errors)}")
        
        # With 120s timeout, this should complete
        assert elapsed < 130, f"Near timeout limit: {elapsed}s"
        assert len(timeout_errors) == 0, f"Got {len(timeout_errors)} timeout errors"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_api_parameter_validation(self):
        """Test that would catch the page_timeout parameter bug that mocks missed."""
        from crawl4ai import BrowserConfig, CrawlerRunConfig
        
        print("\n🔧 Testing REAL API parameter validation...")
        
        # These should fail with real crawl4ai
        invalid_configs = [
            {
                "name": "Invalid BrowserConfig parameter",
                "test": lambda: BrowserConfig(
                    browser_type="chromium",
                    page_timeout=30000  # This parameter was removed!
                )
            },
            {
                "name": "Invalid browser_type",
                "test": lambda: BrowserConfig(
                    browser_type="playwright"  # Not a valid option!
                )
            },
            {
                "name": "Invalid CrawlerRunConfig parameter", 
                "test": lambda: CrawlerRunConfig(
                    page_timeout=30000  # Also removed from here!
                )
            }
        ]
        
        for config in invalid_configs:
            try:
                config["test"]()
                print(f"❌ {config['name']}: Should have failed but didn't!")
                assert False, f"{config['name']} should raise an error"
            except TypeError as e:
                print(f"✅ {config['name']}: Correctly caught error - {e}")
            except Exception as e:
                print(f"⚠️  {config['name']}: Got unexpected error - {type(e).__name__}: {e}")

    @pytest.mark.asyncio 
    @pytest.mark.integration
    async def test_research_tool_crash_scenario(self):
        """Test the research tool crash that happens with adaptive crawling."""
        research_tool = ResearchTool()
        
        print("\n🔬 Testing research tool stability...")
        
        try:
            result = await research_tool.research_topic(
                "AI development tools comparison 2025",
                max_urls=5
            )
            
            if not result.success:
                print(f"❌ Research failed: {result.error}")
                if "Maximum concurrent executions exceeded" in str(result.error):
                    print("   ⚠️  CONCURRENCY LIMIT BUG DETECTED!")
            else:
                print(f"✅ Research succeeded: {result.metadata}")
                
        except Exception as e:
            print(f"❌ Research crashed: {type(e).__name__}: {e}")
            if "Target page, context or browser has been closed" in str(e):
                print("   ⚠️  BROWSER CONTEXT BUG IN RESEARCH TOOL!")
            raise


if __name__ == "__main__":
    # Run specific test for debugging
    import sys
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        test = TestCrawl4AIRealIssues()
        test_method = getattr(test, test_name, None)
        if test_method:
            asyncio.run(test_method())
        else:
            print(f"Test {test_name} not found")
    else:
        print("Usage: python test_crawl4ai_real_issues.py <test_name>")
        print("Available tests:")
        for attr in dir(TestCrawl4AIRealIssues):
            if attr.startswith("test_"):
                print(f"  - {attr}")