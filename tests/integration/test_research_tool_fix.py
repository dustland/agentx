#!/usr/bin/env python3
"""
Test that research_topic now properly extracts content from pages.
"""

import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agentx.builtin_tools.research import ResearchTool
from agentx.storage.taskspace import TaskspaceStorage


async def test_research_content_extraction():
    """Test that research_topic extracts actual content, not just metadata."""
    print("🧪 TESTING RESEARCH CONTENT EXTRACTION")
    print("=" * 60)
    
    # Create taskspace
    temp_dir = tempfile.mkdtemp()
    taskspace = TaskspaceStorage(taskspace_path=temp_dir)
    research_tool = ResearchTool(taskspace_storage=taskspace)
    
    # Test with a simple query
    query = "React framework features 2025"
    print(f"\n📋 Researching: {query}")
    
    # Call research_topic with limited pages for faster testing
    result = await research_tool.research_topic(
        query=query,
        max_pages=3,  # Very small number for quick test
        search_first=True
    )
    
    print(f"\nSuccess: {result.success}")
    
    if result.success and isinstance(result.result, dict):
        saved_files = result.result.get('saved_files', [])
        print(f"\n📁 Files created: {len(saved_files)}")
        
        # Check the first file for actual content
        if saved_files:
            first_file = saved_files[0]
            print(f"\n📄 Checking content of: {first_file}")
            
            # Read the file
            content = await taskspace.get_artifact(first_file)
            
            # Check for the problematic patterns
            has_no_content = "No content available" in content
            has_no_summary = "No summary available" in content
            
            print(f"\n🔍 Content Analysis:")
            print(f"  - File size: {len(content)} characters")
            print(f"  - Has 'No content available': {has_no_content}")
            print(f"  - Has 'No summary available': {has_no_summary}")
            
            if has_no_content or has_no_summary:
                print("\n❌ PROBLEM: Files still contain placeholder text!")
                print("\nFirst 1000 characters of file:")
                print("-" * 40)
                print(content[:1000])
            else:
                print("\n✅ SUCCESS: File contains actual content!")
                print("\nFirst 500 characters of content section:")
                print("-" * 40)
                # Extract content section
                if "## Content" in content:
                    content_start = content.find("## Content") + len("## Content\n")
                    print(content[content_start:content_start + 500])
        
        # Also check file naming
        print("\n📂 File naming check:")
        for file in saved_files:
            if file.startswith("research_") and file.endswith(".md"):
                print(f"  ✅ {file} - Correct naming pattern")
            else:
                print(f"  ❌ {file} - Wrong naming pattern")
    else:
        print(f"❌ Research failed: {result.metadata}")
        if 'browser_errors' in result.metadata:
            print("\n🔧 Browser errors:")
            for error in result.metadata['browser_errors']:
                print(f"  - {error}")
    
    print("\n✅ Test completed")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("Testing fixed research tool content extraction...")
    print("This verifies that actual page content is saved, not just metadata.\n")
    
    asyncio.run(test_research_content_extraction())