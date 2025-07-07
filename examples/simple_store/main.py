#!/usr/bin/env python3
"""
Simple Store Example - Testing File Storage Functionality

A minimal example focused on testing agent file storage capabilities.
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

from agentx.core.task import start_task

async def test_storage():
    """Test basic file storage functionality."""
    
    print("🗄️ Simple Store Test - Testing File Storage")
    print("=" * 50)
    
    # Simple, direct prompt that should result in file creation
    prompt = """
Create a simple text file called 'hello.txt' with the content 'Hello, World!' 
Use the write_file tool to save this file directly in the workspace.
"""
    
    try:
        # Start the task executor
        executor = start_task(
            prompt=prompt,
            config_path="config/simple_agent.yaml"
        )
        
        print(f"📋 Task ID: {executor.task_id}")
        print(f"📁 Workspace: {executor.workspace.get_workspace_path()}")
        
        # Run the task
        print("\n🤖 Running storage test...")
        async for message in executor.start(prompt, stream=False):
            print(f"Agent response: {message.content}")
        
        # Check if file was created
        workspace_path = executor.workspace.get_workspace_path()
        hello_file = workspace_path / "hello.txt"
        artifact_file = workspace_path / "artifacts" / "hello.txt.txt"
        
        if hello_file.exists():
            print(f"\n✅ SUCCESS: hello.txt created directly in workspace!")
            content = hello_file.read_text()
            print(f"📄 Content: '{content}'")
        elif artifact_file.exists():
            print(f"\n✅ SUCCESS: hello.txt created as artifact!")
            content = artifact_file.read_text()
            print(f"📄 Content: '{content}'")
        else:
            print(f"\n❌ FAILED: hello.txt not found in either location")
            print(f"  Checked: {hello_file}")
            print(f"  Checked: {artifact_file}")
            
        # List all files created
        print(f"\n📁 All files in workspace:")
        if workspace_path.exists():
            for f in workspace_path.rglob("*"):
                if f.is_file() and not f.name.startswith('.'):
                    print(f"  📄 {f.relative_to(workspace_path)}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_storage()) 