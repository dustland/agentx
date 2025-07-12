#!/usr/bin/env python3
"""
Test that search_and_extract properly saves artifacts
"""

import asyncio
from pathlib import Path
from agentx import start_task

async def test_search_extract():
    """Test that search_and_extract saves files to workspace."""

    prompt = """Use search_and_extract to research "Python web frameworks 2025" and verify that:
    1. The extracted content is automatically saved as files
    2. List all saved files in the workspace
    3. Read one of the saved files to confirm content was preserved

    This is a test to ensure artifact saving is working correctly."""

    print("🧪 Testing search_and_extract artifact saving...")

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
        print(f"🤖 Response: {response[:200]}...")
        print("-" * 40)

    print("\n✅ Test complete!")

    # Check workspace for artifacts
    workspace_path = x.workspace.get_workspace_path()
    artifacts_path = workspace_path / "artifacts"

    if artifacts_path.exists():
        artifacts = list(artifacts_path.glob("*.md"))
        print(f"\n📄 Found {len(artifacts)} saved artifacts:")
        for artifact in artifacts:
            print(f"   - {artifact.name}")
    else:
        print("\n❌ No artifacts directory found!")

if __name__ == "__main__":
    asyncio.run(test_search_extract())
