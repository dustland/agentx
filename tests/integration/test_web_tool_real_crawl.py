#!/usr/bin/env python3
"""
Integration test for WebTool with real crawl4ai browser operations.
This test actually launches browsers and makes real web requests.
"""

import pytest
import asyncio
import time
from vibex.builtin_tools.web import WebTool

class TestWebToolRealCrawl:
    """Test web tool with real browser operations (no mocks)."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_parallel_browser_stability(self):
        """Test parallel browser operations with real URLs to verify stability."""
        web_tool = WebTool()
        
        # Use lightweight URLs that should load quickly
        test_urls = [
            "https://httpbin.org/html",
            "https://example.com",
            "https://httpbin.org/delay/1"
        ]
        
        print(f"\nTesting parallel extraction of {len(test_urls)} URLs with real browsers...")
        start_time = time.time()
        
        # Create parallel tasks
        tasks = []
        for url in test_urls:
            print(f"Creating task for: {url}")
            tasks.append(web_tool.extract_urls(url))
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful = 0
        failed = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Task {i+1} ({test_urls[i]}) FAILED with exception: {result}")
                failed += 1
            elif hasattr(result, 'success') and result.success:
                print(f"✅ Task {i+1} ({test_urls[i]}) SUCCESS")
                successful += 1
            else:
                error = getattr(result, 'error', 'Unknown error')
                print(f"❌ Task {i+1} ({test_urls[i]}) FAILED: {error}")
                failed += 1
        
        elapsed = time.time() - start_time
        print(f"\nParallel execution completed in {elapsed:.2f}s")
        print(f"Results: {successful} successful, {failed} failed")
        
        # Verify reasonable timing (should take at least a few seconds for real web requests)
        assert elapsed > 2.0, f"Test completed too quickly ({elapsed:.2f}s), likely not making real requests"
        
        # At least 2 out of 3 should succeed
        assert successful >= 2, f"Too many failures: {failed} out of {len(test_urls)}"
        
        return successful == len(test_urls)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_browser_reuse_vs_new_instance(self):
        """Compare performance of reusing browser vs creating new instances."""
        web_tool = WebTool()
        test_url = "https://example.com"
        
        print("\nTesting browser instance reuse...")
        
        # Test 1: Multiple requests with same tool (should reuse browser)
        start1 = time.time()
        for i in range(3):
            result = await web_tool.extract_urls(test_url)
            assert result.success, f"Request {i+1} failed"
        time1 = time.time() - start1
        print(f"3 sequential requests with reuse: {time1:.2f}s")
        
        # Test 2: Multiple requests with new tool instances
        start2 = time.time()
        for i in range(3):
            new_tool = WebTool()
            result = await new_tool.extract_urls(test_url)
            assert result.success, f"Request {i+1} with new tool failed"
        time2 = time.time() - start2
        print(f"3 sequential requests with new instances: {time2:.2f}s")
        
        # Reusing should be faster (or at least not significantly slower)
        print(f"Time difference: {time2 - time1:.2f}s")
        
        # Both methods should work
        assert time1 > 1.0, "Requests completed too quickly, likely not real"
        assert time2 > 1.0, "Requests completed too quickly, likely not real"