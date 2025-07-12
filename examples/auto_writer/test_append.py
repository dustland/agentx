#!/usr/bin/env python3
"""
Test the append_file functionality for incremental HTML building
"""

import asyncio
from pathlib import Path
from agentx import start_task

async def test_append():
    """Test incremental HTML building with append_file."""

    # Simple task to test append functionality
    prompt = """Create a simple test HTML file using incremental building:

    1. First create the basic HTML structure with write_file
    2. Then use append_file to add a header section
    3. Then use append_file to add a main content section
    4. Then use append_file to add a footer section

    Keep each section small (under 500 chars) to test the functionality.
    The file should be named 'test_append.html'."""

    print("🧪 Testing append_file functionality...")

    # Get config path
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "team.yaml"

    # Start task
    x = await start_task(prompt, str(config_path))

    print(f"📋 Task ID: {x.task_id}")
    print(f"📁 Workspace: {x.workspace.get_workspace_path()}")
    print("-" * 80)

    # Execute the task
    while not x.is_complete:
        response = await x.step()
        print(f"🤖 Response: {response[:100]}...")

    print("\n✅ Test complete!")
    print(f"Check {x.workspace.get_workspace_path()} for test_append.html")

if __name__ == "__main__":
    asyncio.run(test_append())
