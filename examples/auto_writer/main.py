#!/usr/bin/env python3
"""
AutoWriter - Deep Research Writing System

A Google-inspired multi-agent system for generating comprehensive research reports.
Uses systematic decomposition and specialized agent orchestration.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

# Add src to path
sys.path.insert(0, str(project_root / "src"))

from agentx import start_task


async def run_auto_writer(topic: str, config_path: str, interactive: bool = False):
    """Run the AutoWriter research report generation."""
    
    print(f"🚀 AutoWriter: Generating comprehensive research report on '{topic}'")
    print(f"📁 Using config: {config_path}")
    print("=" * 60)
    
    # Create a focused task for professional report generation
    task_description = f"""
Generate a comprehensive, professional research report on: {topic}

Requirements for publication-quality output:
- Focus on quantitative data, statistics, and measurable outcomes
- Include case studies with specific ROI calculations and performance metrics
- Gather authoritative sources from industry reports, academic research, and government data
- Create professional HTML output with interactive charts and data visualizations
- Provide strategic recommendations for different organization sizes
- Ensure proper source attribution and professional presentation

The final deliverable should be a publication-quality HTML report comparable to professional consulting reports, with:
- Executive summary highlighting key quantitative findings
- Interactive data visualizations using Chart.js
- Detailed case studies with measurable outcomes and ROI analysis
- Strategic recommendations with implementation guidance and timelines
- Professional formatting with responsive design for mobile and desktop
- Comprehensive source citations and methodology documentation
"""
    
    try:
        print("\n🎬 Starting professional research workflow...\n")
        
        if interactive:
            print("🎮 Interactive Mode - You'll see each step of the process")
            print("Press Ctrl+C to stop at any time\n")
        
        # Execute with streaming
        task_executor = start_task(task_description, config_path)
        print(f"📋 Task ID: {task_executor.task.task_id}")
        print(f"📁 Workspace: {task_executor.task.workspace_dir}")
        print()
        
        # Execute step by step until completion
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
                        
                        # Only pause in interactive mode and if not completing
                        if interactive and to_agent != "COMPLETE":
                            try:
                                input("Press Enter to continue (Ctrl+C to stop)...")
                            except KeyboardInterrupt:
                                print("\n\n🛑 Stopping execution...")
                                return
                        
                        # Break out of the step loop to start next step
                        break
                        
                    elif update_type == "routing_decision":
                        if update["action"] == "complete":
                            print(f"\n\n🎉 Professional research report completed!")
                            print(f"📊 Generated: final_report.html with interactive charts and professional formatting")
                            return
                            
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping execution...")
                return
        
        print(f"\n\n✅ AutoWriter finished! Check the workspace directory for:")
        print(f"   📊 final_report.html - Professional HTML report with interactive charts")
        print(f"   📋 research_plan.md - Comprehensive research strategy")
        print(f"   🔍 search_results_*.md - Authoritative source analysis")
        print(f"   📈 content_extraction_*.md - Quantitative data extraction")
        print(f"   🧠 reasoning_document.md - Deep analytical insights")

    except KeyboardInterrupt:
        print(f"\n\n🛑 Execution stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AutoWriter - Deep Research Writing System")
    parser.add_argument("--topic", "-t", type=str, 
                       default="The Future of Artificial Intelligence in Healthcare",
                       help="Research topic for report generation")
    parser.add_argument("--config", "-c", type=str, 
                       help="Path to team configuration file")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive step-by-step mode")
    
    args = parser.parse_args()
    
    # Default config path
    config_path = args.config or str(Path(__file__).parent / "config" / "team.yaml")
    
    # Ensure workspace directory exists
    workspace_path = Path(__file__).parent / "workspace"
    workspace_path.mkdir(exist_ok=True)
    
    # Run the auto writer
    asyncio.run(run_auto_writer(args.topic, config_path, args.interactive))


if __name__ == "__main__":
    main()