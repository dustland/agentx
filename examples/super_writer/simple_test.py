#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

# Add src to path
sys.path.insert(0, str(project_root / "src"))

from agentx.core.task import start_task

async def test_consultant():
    """Simple test for consultant agent."""
    
    # Create a simple prompt that should trigger the consultant
    prompt = """
I want a research report about AI in healthcare. 
Please gather the requirements and store them as requirements.md file.
"""
    
    print("🧪 Testing Consultant Agent")
    print("=" * 40)
    
    try:
        # Start the task
        executor = start_task(
            prompt=prompt,
            config_path="config/team.yaml"
        )
        
        # Print task information
        task_id = executor.task.task_id
        workspace_path = executor.task.workspace_dir
        print(f"📋 Task ID: {task_id}")
        print(f"📁 Workspace: {workspace_path}")
        
        # Run multiple steps to see what happens
        print("\n🤖 Running multiple steps...")
        for i in range(3):  # Run up to 3 steps
            print(f"\n--- Step {i+1} ---")
            try:
                async for step_result in executor.step():
                    print(f"Step result: {step_result}")
                    break  # Just run one step at a time
                
                # Check if requirements.md was created after each step
                req_file = workspace_path / "requirements.md"
                if req_file.exists():
                    print(f"✅ SUCCESS: requirements.md created after step {i+1}!")
                    print(f"📄 Content preview:")
                    content = req_file.read_text()
                    print(content[:300] + "..." if len(content) > 300 else content)
                    break
                else:
                    print(f"❌ No requirements.md found after step {i+1}")
                    
            except Exception as e:
                print(f"Error in step {i+1}: {e}")
                break
        
        # List all files created
        print(f"\n📁 Files in workspace:")
        if workspace_path.exists():
            for f in workspace_path.rglob("*"):
                if f.is_file() and not f.name.startswith('.'):
                    print(f"  📄 {f.relative_to(workspace_path)}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_consultant()) 