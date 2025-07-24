#!/usr/bin/env python3
"""
Test that research_topic creates files with correct naming pattern.
"""

import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from vibex.builtin_tools.research import ResearchTool
from vibex.storage.taskspace import TaskspaceStorage


async def test_research_file_naming():
    """Test that research_topic creates files with the correct naming pattern."""
    print("🧪 TESTING RESEARCH FILE NAMING PATTERN")
    print("=" * 60)
    
    # Create taskspace
    temp_dir = tempfile.mkdtemp()
    taskspace = TaskspaceStorage(taskspace_path=temp_dir)
    research_tool = ResearchTool(taskspace_storage=taskspace)
    
    # Test research with a clear topic
    query = "frontend frameworks trends 2025"
    print(f"\n📋 Researching: {query}")
    
    # Call research_topic
    result = await research_tool.research_topic(
        query=query,
        max_pages=5,  # Small number for quick test
        search_first=True
    )
    
    print(f"\nSuccess: {result.success}")
    
    if result.success:
        # Check saved files
        if isinstance(result.result, dict):
            saved_files = result.result.get('saved_files', [])
            print(f"\n📁 Files created: {len(saved_files)}")
            
            for file in saved_files:
                print(f"  - {file}")
                
                # Verify naming pattern
                if file.startswith("research_frontend_frameworks_trends"):
                    print("    ✅ Correct naming pattern!")
                else:
                    print(f"    ❌ Wrong pattern! Expected: research_frontend_frameworks_trends_XX.md")
        
        # List all files in taskspace to see what was created
        print("\n📂 All files in taskspace:")
        artifacts_dir = os.path.join(temp_dir, 'artifacts')
        if os.path.exists(artifacts_dir):
            for file in os.listdir(artifacts_dir):
                if file.endswith('.md'):
                    print(f"  - {file}")
    else:
        print(f"❌ Research failed: {result.metadata.get('error', 'Unknown')}")
    
    print("\n✅ Test completed")


async def test_multiple_topics():
    """Test multiple research topics to ensure consistent naming."""
    print("\n\n🧪 TESTING MULTIPLE RESEARCH TOPICS")
    print("=" * 60)
    
    temp_dir = tempfile.mkdtemp()
    taskspace = TaskspaceStorage(taskspace_path=temp_dir)
    research_tool = ResearchTool(taskspace_storage=taskspace)
    
    topics = [
        "AI integration development workflows",
        "backend technologies serverless edge computing",
        "Vue.js framework features adoption"
    ]
    
    expected_prefixes = [
        "research_ai_integration_development",
        "research_backend_technologies",
        "research_vuejs_framework_features"
    ]
    
    for topic, expected_prefix in zip(topics, expected_prefixes):
        print(f"\n📋 Testing: {topic}")
        print(f"   Expected prefix: {expected_prefix}")
        
        result = await research_tool.research_topic(
            query=topic,
            max_pages=3,
            search_first=True
        )
        
        if result.success and isinstance(result.result, dict):
            saved_files = result.result.get('saved_files', [])
            if saved_files:
                first_file = saved_files[0]
                if first_file.startswith(expected_prefix):
                    print(f"   ✅ Correct: {first_file}")
                else:
                    print(f"   ❌ Wrong: {first_file}")
            else:
                print("   ⚠️  No files saved")
        else:
            print(f"   ❌ Research failed")


if __name__ == "__main__":
    print("Testing research tool file naming patterns...")
    print("This verifies files are created with 'research_' prefix.\n")
    
    async def run_all_tests():
        await test_research_file_naming()
        await test_multiple_topics()
    
    asyncio.run(run_all_tests())