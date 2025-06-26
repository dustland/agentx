#!/usr/bin/env python3
"""
Test Content Extractor Agent - tests actual URL content extraction
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import agentx
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from agentx import execute_task

async def test_content_extractor():
    """Test content extractor with real URL extraction"""
    
    print("🧪 Testing Content Extractor Agent with real URLs...")
    print("=" * 60)
    
    # Test prompt - directly test the content extractor
    test_prompt = """Extract content from this URL: https://www.who.int/news-room/fact-sheets/detail/artificial-intelligence-(ai)-in-health

Use the extract_content tool to get detailed information about AI in healthcare from WHO.

Save your extraction results as 'content_extraction_test.md'."""

    try:
        await execute_task(
            prompt=test_prompt,
            config_path="tests/content_extractor_config.yaml", 
            stream=False
        )
        
        print("\n" + "=" * 60)
        print("Test Results:")
        print("=" * 60)
        
        # Find the extraction file in workspace
        extraction_files = []
        for root, dirs, files in os.walk("workspace"):
            for file in files:
                if "content_extraction_test.md" in file:
                    extraction_files.append(os.path.join(root, file))
        
        if extraction_files:
            latest_file = max(extraction_files, key=os.path.getctime)
            with open(latest_file, "r") as f:
                content = f.read()
                print(f"✅ Content extracted successfully ({len(content)} chars)")
                print(f"\n📋 Preview:\n{content[:300]}...")
        else:
            print("❌ No extraction file created - agent may have failed")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    asyncio.run(test_content_extractor()) 