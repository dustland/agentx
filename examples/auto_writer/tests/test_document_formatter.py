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
    
    test_dir = os.path.dirname(__file__)
    analysis_path = os.path.join(test_dir, "content_analysis.md")

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
    
    with open(analysis_path, "w") as f:
        f.write(analysis_content)
    
    test_prompt = f"""You are the Document Formatter Agent.

Read the content analysis file ({analysis_path}) and create a professional HTML report with appropriate styling and structure.

Save your HTML report as 'final_report.html'."""

    config_path = os.path.join(test_dir, "..", "config", "team.yaml")

    try:
        await execute_task(
            prompt=test_prompt,
            config_path=config_path,
            stream=False
        )
        
        print("\n" + "=" * 50)
        print("Test Results:")
        print("=" * 50)
        
        report_files = []
        for root, dirs, files in os.walk("workspace"):
            for file in files:
                if file == "final_report.html":
                    report_files.append(os.path.join(root, file))

        if report_files:
            latest_file = max(report_files, key=os.path.getctime)
            with open(latest_file, "r") as f:
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
        if os.path.exists(analysis_path):
            os.remove(analysis_path)

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    asyncio.run(test_document_formatter()) 