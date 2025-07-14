#!/usr/bin/env python3
"""
Simple Team Demo - Writer + Reviewer Collaboration

Shows basic multi-agent collaboration with handoffs.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from agentx import start_task


async def main():
    """Simple team collaboration demo."""
    print("🤖 Simple Team Demo - Writer + Reviewer\n")

    # Configuration and prompt
    config_path = str(Path(__file__).parent / "config" / "team.yaml")
    prompt = """Write a short article about remote work benefits."""

    print("🎬 Starting collaboration...\n")

    try:
        # Start task with XAgent - creates a conversational interface
        x = await start_task(prompt, config_path)

        print(f"📋 Task ID: {x.task_id}")
        print(f"📁 Taskspace: {x.taskspace.get_taskspace_path()}")
        print("-" * 60)

        # Execute the team collaboration autonomously
        print("🤖 X: Starting writer + reviewer collaboration...")
        while not x.is_complete:
            response = await x.step()
            print(f"🤖 X: {response}")
            print("-" * 60)

        # Demonstrate follow-up collaboration
        follow_ups = [
            "Make the article more engaging with personal anecdotes",
            "Add statistics about remote work productivity",
            "Create a summary section with key takeaways"
        ]

        for question in follow_ups:
            print(f"💬 User: {question}")
            response = await x.chat(question)
            print(f"🤖 X: {response.text}")

            if response.preserved_steps:
                print(f"   ✅ Preserved {len(response.preserved_steps)} completed steps")

            print("-" * 60)

        print("✅ Team collaboration completed!")
        print(f"📁 Check taskspace for collaboration artifacts: {x.taskspace.get_taskspace_path()}")

        # Demonstrate conversational team capabilities
        print("\n💬 You can continue chatting with the team:")
        print("   Example: x.chat('Rewrite this for a technical audience')")
        print("   Example: x.chat('Create a presentation version')")
        print("   Example: x.chat('Add a section about challenges of remote work')")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
