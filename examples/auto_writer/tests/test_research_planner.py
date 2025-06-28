#!/usr/bin/env python3
"""
Test Research Planner Agent
"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
from agentx import execute_task

async def test_research_planner():
    """Test research planner creates comprehensive research plans"""
    
    print("🧪 Testing Research Planner Agent...")
    print("=" * 50)
    
    test_prompt = """You are the Research Planner Agent. 

Create a comprehensive research plan for: "Impact of remote work on employee productivity"

Generate 6-8 focused sub-queries and save your research plan as 'research_plan.md'."""

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
        
        # Find the research plan file in workspace
        plan_files = []
        for root, dirs, files in os.walk("workspace"):
            for file in files:
                if file == "research_plan.md":
                    plan_files.append(os.path.join(root, file))
        
        if plan_files:
            latest_file = max(plan_files, key=os.path.getctime)  # Get most recent
            with open(latest_file, "r") as f:
                content = f.read()
                print(f"✅ Research plan created ({len(content)} chars)")
                
                # Check for key indicators
                indicators = ["sub-query", "research", "methodology", "sources"]
                found = [ind for ind in indicators if ind.lower() in content.lower()]
                print(f"📊 Found {len(found)}/{len(indicators)} expected elements: {found}")
                
                print(f"\n📋 Preview:\n{content[:400]}...")
        else:
            print("❌ No research plan created")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    asyncio.run(test_research_planner()) 