#!/usr/bin/env python3
"""
Handoff Demo Example

Demonstrates the XAgent-centric handoff system where agents automatically
hand off work based on conditions without explicit handoff tools.
"""

import asyncio
from agentx import start_task

async def main():
    """Run a handoff demonstration."""

    print("🤝 Handoff Demo Example")
    print("=" * 60)
    print("This demo shows how agents automatically hand off work")
    print("based on conditions defined in the team configuration.")
    print("-" * 60)

    # Task that will trigger handoffs
    task_prompt = """
    Create a technical blog post about quantum computing:
    1. Research the topic and create an outline
    2. Write a draft based on the outline
    3. Review the draft for technical accuracy
    4. Edit for clarity and style
    5. Create a final version
    """

    print(f"📋 Task: {task_prompt.strip()}")
    print("-" * 60)

    # Start the task with handoff-enabled team
    x = await start_task(
        prompt=task_prompt,
        config_path="config/handoff_team.yaml"
    )

    print(f"🆔 Task ID: {x.task_id}")
    print(f"📁 Workspace: {x.workspace.get_workspace_path()}")
    print("-" * 60)

    # Execute the task - handoffs will happen automatically
    print("🚀 Starting execution with automatic handoffs...\n")

    step_count = 0
    while not x.is_complete and step_count < 20:
        response = await x.step()
        step_count += 1

        print(f"Step {step_count}:")
        print(f"{response}")

        # Check if a handoff occurred
        if "Handing off to" in response:
            print("✨ HANDOFF DETECTED! Work is being transferred to the next agent.")

        print("-" * 60)

    if x.is_complete:
        print("✅ Task completed successfully!")
    else:
        print(f"⚠️ Task stopped after {step_count} steps")

    # Show the final plan to see all tasks including handoffs
    if x.current_plan:
        print("\n📊 Final Execution Plan:")
        for i, task in enumerate(x.current_plan.tasks, 1):
            status_emoji = {
                "completed": "✅",
                "failed": "❌",
                "in_progress": "🔄",
                "pending": "⏳"
            }.get(task.status, "❓")

            print(f"{i}. {status_emoji} [{task.agent}] {task.name}")
            if task.id.startswith("handoff_"):
                print(f"   ↳ (Automatic handoff based on conditions)")

    print(f"\n📁 Check the workspace for outputs: {x.workspace.get_workspace_path()}")

if __name__ == "__main__":
    asyncio.run(main())
