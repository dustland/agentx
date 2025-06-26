#!/usr/bin/env python3
"""
Test Document Formatter Agent
"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
from agentx import execute_task

async def test_document_formatter():
    """Test document formatter creates professional HTML reports"""
    
    print("🧪 Testing Document Formatter Agent...")
    print("=" * 50)
    
    # Create mock analysis file
    analysis_content = """# Content Analysis: Remote Work Impact

## Executive Summary
Remote work shows mixed productivity impacts requiring strategic implementation.

## Key Insights
- Technology infrastructure is the primary success factor
- Management adaptation is critical for team effectiveness
- Work-life balance requires new organizational policies

## Recommendations
1. Invest in collaboration technology platforms
2. Train managers for remote team leadership
3. Establish clear work-life boundaries
4. Implement regular team connection activities

## Data Points
- 23% productivity increase in structured remote environments
- 67% of workers report communication challenges
- 31% increase in burnout rates without proper support
"""
    
    with open("content_analysis.md", "w") as f:
        f.write(analysis_content)
    
    test_prompt = """You are the Document Formatter Agent.

Read the content analysis file (content_analysis.md) and create a professional HTML report with appropriate styling and structure.

Save your HTML report as 'final_report.html'."""

    try:
        await execute_task(
            prompt=test_prompt,
            config_path="config/team.yaml",
            stream=False
        )
        
        print("\n" + "=" * 50)
        print("Test Results:")
        print("=" * 50)
        
        if os.path.exists("final_report.html"):
            with open("final_report.html", "r") as f:
                content = f.read()
                print(f"✅ HTML report created ({len(content)} chars)")
                
                # Check for HTML indicators
                indicators = ["<html>", "<head>", "<body>", "<style>", "<h1>"]
                found = [ind for ind in indicators if ind.lower() in content.lower()]
                print(f"📊 Found {len(found)}/{len(indicators)} HTML elements: {found}")
                
                print(f"\n📋 Preview:\n{content[:400]}...")
        else:
            print("❌ No HTML report created")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    finally:
        # Cleanup
        if os.path.exists("content_analysis.md"):
            os.remove("content_analysis.md")

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    asyncio.run(test_document_formatter()) 