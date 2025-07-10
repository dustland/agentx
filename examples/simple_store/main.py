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

from agentx import start_task

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
        # Start the task with XAgent - creates a conversational interface
        x = await start_task(
            prompt=prompt,
            config_path="config/simple_agent.yaml"
        )

        print(f"📋 Task ID: {x.task_id}")
        print(f"📁 Workspace: {x.workspace.get_workspace_path()}")

        # Chat with X to create the file
        print("\n🤖 X: Starting file creation...")
        response = await x.chat(prompt)
        print(f"🤖 X: {response.text}")

        # Check if file was created
        workspace_path = x.workspace.get_workspace_path()
        artifact_file = workspace_path / "artifacts" / "hello.txt"

        if artifact_file.exists():
            print(f"\n✅ SUCCESS: hello.txt created as artifact!")
            content = artifact_file.read_text()
            print(f"📄 Content: '{content}'")
        else:
            print(f"\n❌ FAILED: hello.txt not found in artifacts")
            print(f"  Checked: {artifact_file}")

        # List all files created
        print(f"\n📁 All files in workspace:")
        if workspace_path.exists():
            for f in workspace_path.rglob("*"):
                if f.is_file() and not f.name.startswith('.'):
                    print(f"  📄 {f.relative_to(workspace_path)}")

        # Demonstrate conversational file operations
        print("\n💬 Testing conversational file operations...")

        # Create another file
        response = await x.chat("Now create a second file called 'goodbye.txt' with 'Goodbye, World!'")
        print(f"🤖 X: {response.text}")

        # Modify the first file
        response = await x.chat("Update hello.txt to include the current date and time")
        print(f"🤖 X: {response.text}")

        if response.preserved_steps:
            print(f"   ✅ Preserved {len(response.preserved_steps)} completed file operations")

        print("\n💬 You can continue chatting with X:")
        print("   Example: x.chat('Create a JSON file with sample data')")
        print("   Example: x.chat('List all files in the workspace')")
        print("   Example: x.chat('Create a folder structure for a project')")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_storage())
