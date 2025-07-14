#!/usr/bin/env python3
"""
Test that exactly mimics auto_writer research pattern.
This tests search_first=True with adaptive crawling like auto_writer does.
"""

import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agentx.builtin_tools.research import ResearchTool
from agentx.storage.taskspace import TaskspaceStorage


async def test_auto_writer_research_pattern():
    """Test the exact research pattern used by auto_writer."""
    print("🧪 TESTING AUTO_WRITER RESEARCH PATTERN")
    print("This tests search_first=True with adaptive crawling")
    print("=" * 60)
    
    # Create taskspace like auto_writer does
    temp_dir = tempfile.mkdtemp()
    taskspace = TaskspaceStorage(taskspace_path=temp_dir)
    research_tool = ResearchTool(taskspace_storage=taskspace)
    
    # Test the exact queries that auto_writer uses
    test_queries = [
        "AI integration in development workflows including code generation, testing, and debugging",
        "current trends in backend development 2025 serverless edge computing database technologies",
        "Vue.js framework features, adoption rates, and community support",
        "Astro performance, use cases, and developer experience"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n📋 Test {i+1}: {query[:50]}...")
        
        # This is exactly how auto_writer calls research_topic
        result = await research_tool.research_topic(
            query=query,
            max_pages=30,
            confidence_threshold=0.75,
            search_first=True  # This is the key - auto_writer uses search_first=True
        )
        
        print(f"Success: {result.success}")
        
        if result.success:
            print(f"✅ GOOD: Research succeeded")
            if isinstance(result.result, dict):
                pages = result.result.get('pages_crawled', 0)
                files = len(result.result.get('saved_files', []))
                print(f"   Pages crawled: {pages}")
                print(f"   Files saved: {files}")
                
                if pages == 0:
                    print("   ❌ BAD: 0 pages crawled despite success")
                if files == 0:
                    print("   ⚠️  No files saved")
        else:
            print(f"❌ FAILED: {result.metadata.get('error', 'Unknown error')}")
            
            # Check specific failure details
            failed_urls = result.metadata.get('failed_urls', [])
            browser_errors = result.metadata.get('browser_errors', [])
            attempted = result.metadata.get('attempted_urls', 0)
            successful = result.metadata.get('successful_urls', 0)
            
            print(f"   URLs attempted: {attempted}")
            print(f"   URLs successful: {successful}")
            print(f"   Failed URLs: {len(failed_urls)}")
            print(f"   Browser errors: {len(browser_errors)}")
            
            if successful > 0 and len(failed_urls) < attempted:
                print("   🤔 ISSUE: Some URLs succeeded but no content extracted")
                print("   This suggests adaptive crawling threshold problems")
        
        print("-" * 60)
    
    print("\n✅ Auto_writer research pattern test completed")


if __name__ == "__main__":
    print("Testing the exact research pattern that auto_writer uses...")
    print("This will reveal if the adaptive crawling config is working.\n")
    
    asyncio.run(test_auto_writer_research_pattern())