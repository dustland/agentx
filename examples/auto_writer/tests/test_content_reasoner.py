#!/usr/bin/env python3
"""
Test Content Reasoner Agent
"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
from agentx import execute_task

async def test_content_reasoner():
    """Test content reasoner performs deep analytical reasoning"""
    
    print("🧪 Testing Content Reasoner Agent...")
    print("=" * 50)
    
    # Create mock synthesis file
    synthesis_content = """# Research Synthesis: Remote Work Impact

## Key Findings Integration
- Productivity metrics show mixed results: 23% increase vs 15% collaboration decrease
- Communication challenges affect 67% of remote workers
- Burnout rates increased 31% in remote settings
- Successful implementations require structured approaches (Microsoft Japan case)

## Cross-Source Patterns
- Technology adoption is critical for success
- Management style must adapt to remote contexts
- Work-life balance becomes more complex
"""
    
    with open("research_synthesis.md", "w") as f:
        f.write(synthesis_content)
    
    test_prompt = """You are the Content Reasoner Agent.

Read the research synthesis file (research_synthesis.md) and perform deep analytical reasoning to generate insights, implications, and recommendations.

Save your analytical reasoning as 'content_analysis.md'."""

    try:
        await execute_task(
            prompt=test_prompt,
            config_path="config/team.yaml",
            stream=False
        )
        
        print("\n" + "=" * 50)
        print("Test Results:")
        print("=" * 50)
        
        if os.path.exists("content_analysis.md"):
            with open("content_analysis.md", "r") as f:
                content = f.read()
                print(f"✅ Content analysis created ({len(content)} chars)")
                
                # Check for reasoning indicators
                indicators = ["analysis", "insights", "implications", "recommendations"]
                found = [ind for ind in indicators if ind.lower() in content.lower()]
                print(f"📊 Found {len(found)}/{len(indicators)} reasoning elements: {found}")
                
                print(f"\n📋 Preview:\n{content[:400]}...")
        else:
            print("❌ No content analysis created")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    finally:
        # Cleanup
        if os.path.exists("research_synthesis.md"):
            os.remove("research_synthesis.md")

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    asyncio.run(test_content_reasoner()) 