#!/usr/bin/env python3
"""
Test Research Synthesizer Agent
"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
from agentx import execute_task

async def test_research_synthesizer():
    """Test research synthesizer integrates extracted content"""
    
    print("🧪 Testing Research Synthesizer Agent...")
    print("=" * 50)
    
    # Create mock extracted content files
    content1 = """# Content Extraction: Remote Work Productivity Studies

## Primary Evidence Extracted
- Study 1: 23% productivity increase in remote workers (Stanford, 2023)
- Study 2: 15% decrease in collaboration effectiveness (MIT, 2023)
- Case Study: Microsoft Japan - 40% productivity boost with 4-day week
"""
    
    content2 = """# Content Extraction: Remote Work Challenges

## Primary Evidence Extracted  
- Survey: 67% report communication difficulties (Gallup, 2023)
- Research: 31% increase in burnout rates (APA, 2023)
- Case Study: Twitter remote policy - mixed results on team cohesion
"""
    
    with open("content_extraction_1.md", "w") as f:
        f.write(content1)
    with open("content_extraction_2.md", "w") as f:
        f.write(content2)
    
    test_prompt = """You are the Research Synthesizer Agent.

Read the content extraction files (content_extraction_1.md and content_extraction_2.md) and synthesize the findings into a comprehensive research synthesis.

Save your synthesis as 'research_synthesis.md'."""

    try:
        await execute_task(
            prompt=test_prompt,
            config_path="tests/research_synthesizer_config.yaml",
            stream=False
        )
        
        print("\n" + "=" * 50)
        print("Test Results:")
        print("=" * 50)
        
        # Find the synthesis file in workspace
        synthesis_files = []
        for root, dirs, files in os.walk("workspace"):
            for file in files:
                if "research_synthesis.md" in file:
                    synthesis_files.append(os.path.join(root, file))
        
        if synthesis_files:
            latest_file = max(synthesis_files, key=os.path.getctime)
            with open(latest_file, "r") as f:
                content = f.read()
                print(f"✅ Research synthesis created ({len(content)} chars)")
                
                # Check for synthesis indicators
                indicators = ["synthesis", "findings", "patterns", "integration"]
                found = [ind for ind in indicators if ind.lower() in content.lower()]
                print(f"📊 Found {len(found)}/{len(indicators)} synthesis elements: {found}")
                
                print(f"\n📋 Preview:\n{content[:400]}...")
        else:
            print("❌ No research synthesis created")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    finally:
        # Cleanup
        for file in ["content_extraction_1.md", "content_extraction_2.md"]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    asyncio.run(test_research_synthesizer()) 