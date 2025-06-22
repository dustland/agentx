#!/usr/bin/env python3
"""
SuperWriter - Advanced Research Report Generation System

A streamlined multi-agent system for generating comprehensive research reports.
Uses AgentX framework's start_task for step-by-step execution.
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

from agentx.core.task import start_task


async def run_super_writer(topic: str, config_path: str, interactive: bool = False):
    """Run the SuperWriter research report generation."""
    
    print(f"🚀 SuperWriter: Generating comprehensive research report on '{topic}'")
    print(f"📁 Using config: {config_path}")
    print("=" * 60)
    
    # Create a focused task that demands concrete deliverables
    task_description = f"""
Create a comprehensive research report on: {topic}

DELIVERABLE REQUIREMENTS:
1. Create a complete research report document (minimum 2000 words)
2. Save the final report as 'research_report.md' in the workspace
3. Include proper sections: Executive Summary, Introduction, Main Content, Analysis, Conclusions
4. Use credible information and provide insights
5. Format with proper markdown structure

The report must be saved as an actual file that can be read and reviewed.
Start by researching the topic thoroughly, then write the complete report.
"""
    
    try:
        # Start the task and get executor
        executor = start_task(
            prompt=task_description,
            config_path=config_path
        )
        
        # Print task information including task ID and workspace path
        task_id = executor.task.task_id
        workspace_path = executor.task.workspace_dir
        print(f"\n📋 Task ID: {task_id}")
        print(f"📁 Workspace: {workspace_path}")
        print(f"🔗 Full path: {workspace_path.absolute()}")
        print("-" * 60)
        
        if interactive:
            print("\n🎮 Interactive Mode - Press Enter to continue each step, 'q' to quit")
            step_count = 0
            
            while not executor.is_complete:
                step_count += 1
                print(f"\n--- Step {step_count} ---")
                
                # Get user input
                user_input = input("Press Enter to continue (or 'q' to quit): ").strip()
                if user_input.lower() == 'q':
                    print("Stopping execution...")
                    break
                
                # Execute one step
                await executor.step()
                
                # Check for artifacts in the correct workspace
                if workspace_path.exists():
                    files = list(workspace_path.glob("*"))
                    if files:
                        print(f"📄 Files created: {[f.name for f in files]}")
        else:
            print("\n🤖 Autonomous Mode - Running to completion...")
            
            # Run to completion using _execute since task is already started
            await executor._execute()
            
            print(f"\n✅ Task completed!")
        
        # Check final output in the correct workspace
        report_path = workspace_path / "research_report.md"
        
        if report_path.exists():
            print(f"\n📊 SUCCESS: Research report created!")
            print(f"📁 Location: {report_path}")
            print(f"📏 Size: {report_path.stat().st_size} bytes")
            
            # Show first few lines
            with open(report_path, 'r') as f:
                preview = f.read(500)
                print(f"\n📖 Preview:\n{preview}...")
        else:
            print(f"\n❌ WARNING: No research report found at {report_path}")
            print("Available files:")
            if workspace_path.exists():
                for file in workspace_path.glob("*"):
                    print(f"  - {file.name}")
            
            # Also check subdirectories
            print("\nChecking subdirectories:")
            for subdir in ["artifacts", "logs", "history"]:
                subdir_path = workspace_path / subdir
                if subdir_path.exists():
                    files = list(subdir_path.glob("*"))
                    if files:
                        print(f"  📁 {subdir}/: {[f.name for f in files]}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SuperWriter - Advanced Research Report Generation")
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
    
    # Run the super writer
    asyncio.run(run_super_writer(args.topic, config_path, args.interactive))


if __name__ == "__main__":
    main()