#!/usr/bin/env python3
"""
Test Search Specialist Agent
"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
from agentx import execute_task

async def test_search_specialist():
    """Test search specialist performs web searches and saves results"""
    
    print("🧪 Testing Search Specialist Agent...")
    print("=" * 50)
    
    test_prompt = """You are the Search Specialist Agent.

Search for information about: "artificial intelligence healthcare applications"

Use web_search to find authoritative sources and save your search results as 'search_results_test.md'."""

    # Construct the absolute path to the config file
    config_path = os.path.join(os.path.dirname(__file__), "single_agent_config.yaml")

    try:
        await execute_task(
            prompt=test_prompt,
            config_path=config_path,
            stream=False
        )
        
        print("\n" + "=" * 50)
        print("Test Results:")
        print("=" * 50)
        
        # Find the search results file in workspace
        search_files = []
        for root, dirs, files in os.walk("workspace"):
            for file in files:
                if "search_results" in file and file.endswith(".md"):
                    search_files.append(os.path.join(root, file))
        
        if search_files:
            latest_file = max(search_files, key=os.path.getctime)
            with open(latest_file, "r") as f:
                content = f.read()
                print(f"✅ Search results created ({len(content)} chars)")
                
                # Check for search indicators
                indicators = ["search", "source", "url", "found"]
                found = [ind for ind in indicators if ind.lower() in content.lower()]
                print(f"📊 Found {len(found)}/{len(indicators)} search elements: {found}")
                
                print(f"\n📋 Preview:\n{content[:400]}...")
        else:
            print("❌ No search results created")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    asyncio.run(test_search_specialist()) 