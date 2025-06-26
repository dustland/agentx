#!/usr/bin/env python3
"""
Test Enhanced AutoWriter System

Quick test to validate the enhanced professional research system.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

# Add src to path
sys.path.insert(0, str(project_root / "src"))

from agentx import start_task


async def test_enhanced_autowriter():
    """Test the enhanced AutoWriter system with a focused topic."""
    
    # Use a focused topic that should generate good results
    topic = "ROI and Productivity Impact of AI Code Assistants in Software Development Teams"
    
    print(f"🧪 Testing Enhanced AutoWriter System")
    print(f"📋 Topic: {topic}")
    print(f"🎯 Expected: Professional HTML report with charts and quantitative analysis")
    print("=" * 80)
    
    # Create focused task description
    task_description = f"""
Generate a comprehensive, professional research report on: {topic}

Requirements:
- Focus on quantitative data, statistics, and measurable outcomes
- Include case studies with specific ROI calculations
- Gather authoritative sources from industry reports and academic research
- Create professional HTML output with interactive charts
- Provide strategic recommendations for different organization sizes

The final deliverable should be a publication-quality HTML report comparable to professional consulting reports, with:
- Executive summary with key quantitative findings
- Interactive data visualizations and charts
- Detailed case studies with measurable outcomes
- Strategic recommendations with implementation guidance
- Professional formatting and responsive design
"""
    
    try:
        print("🚀 Starting enhanced research workflow...\n")
        
        # Execute with the enhanced configuration
        config_path = str(Path(__file__).parent / "config" / "team.yaml")
        task_executor = start_task(task_description, config_path)
        
        print(f"📋 Task ID: {task_executor.task.task_id}")
        print(f"📁 Workspace: {task_executor.task.workspace_dir}")
        print()
        
        # Execute step by step
        step_count = 0
        while not task_executor.task.is_complete and task_executor.task.round_count < task_executor.task.max_rounds:
            try:
                async for update in task_executor.step(stream=True):
                    update_type = update.get("type")
                    
                    if update_type == "content":
                        print(update["content"], end="", flush=True)
                        
                    elif update_type == "handoff":
                        step_count += 1
                        from_agent = update["from_agent"]
                        to_agent = update["to_agent"]
                        print(f"\n\n🔄 STEP {step_count} - HANDOFF: {from_agent} → {to_agent}\n")
                        
                        # Break out of the step loop to start next step
                        break
                        
                    elif update_type == "routing_decision":
                        if update["action"] == "complete":
                            print(f"\n\n🎉 Enhanced AutoWriter test completed!")
                            print(f"📁 Check workspace directory: {task_executor.task.workspace_dir}")
                            print(f"🌐 Look for final_report.html with professional formatting and charts")
                            return
                            
            except KeyboardInterrupt:
                print("\n\n🛑 Test stopped by user")
                return
        
        print(f"\n\n✅ Enhanced AutoWriter test finished!")
        print(f"📁 Check workspace: {task_executor.task.workspace_dir}")
        print(f"📊 Expected files:")
        print(f"   - research_plan.md (comprehensive planning)")
        print(f"   - search_results_*.md (authoritative sources)")
        print(f"   - content_extraction_*.md (quantitative data)")
        print(f"   - synthesis_document.md (integrated analysis)")
        print(f"   - reasoning_document.md (deep insights)")
        print(f"   - final_report.html (professional output with charts)")

    except Exception as e:
        print(f"\n❌ Test Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_enhanced_autowriter()) 