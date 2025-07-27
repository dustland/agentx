#!/usr/bin/env python3
"""
Handoff Demo Example

Demonstrates the XAgent-centric handoff system where agents automatically
hand off work based on conditions without explicit handoff tools.
"""

import asyncio
from vibex import VibeX
from pathlib import Path

async def main():
    """Main function to run the handoff demo."""
    # Load the team configuration from the YAML file
    config_path = Path(__file__).parent / "config/handoff_team.yaml"
    
    # Initialize VibeX with the specified configuration
    # The VibeX context manager handles session setup and cleanup
    x = await VibeX.start(
        project_id="handoff_demo_project",
        goal="Research the 'Jobs to be Done' framework and create a summary document.",
        config_path=str(config_path),
    )
        
    # Enable parallel execution for the agents
    x.set_parallel_execution(enabled=True)

    # Print out the project details
    print_header()
    print(f"🆔 Project ID: {x.project_id}")
    print(f"📁 Workspace: {x.workspace.get_path()}")
    print("-" * 80)
    
    # The initial user query that starts the process
    initial_query = "Research the 'Jobs to be Done' framework and create a summary document."
    
    # Start the process by sending the initial query to the agent team
    await x.start(initial_query)

    # Execute the task - handoffs will happen automatically
    print("🚀 Starting execution with automatic handoffs...\n")

    step_count = 0
    while not x.is_complete() and step_count < 20:
        response = await x.step()
        step_count += 1

        print(f"Step {step_count}:")
        print(f"{response}")

        # Check if a handoff occurred
        if isinstance(response, str) and "Handing off to" in response:
            print("✨ HANDOFF DETECTED! Work is being transferred to the next agent.")

        print("-" * 60)

    if x.is_complete():
        print("✅ Task completed successfully!")
    else:
        print(f"⚠️ Task stopped after {step_count} steps")

        # Show the final plan to see all tasks including handoffs
        if x.plan:
            print("\n📊 Final Execution Plan:")
            for i, task in enumerate(x.plan.tasks, 1):
                status_emoji = {
                    "completed": "✅",
                    "failed": "❌",
                    "in_progress": "🔄",
                    "pending": "⏳"
                }.get(task.status, "❓")

                print(f"{i}. {status_emoji} [{task.assigned_to}] {task.action}")
                if task.id.startswith("handoff_"):
                    print(f"   ↳ (Automatic handoff based on conditions)")

        print("\n" + "=" * 80)
        print("✅ HANDOFF DEMO COMPLETE")
        print("=" * 80)
        print(f"🆔 Project ID: {x.project_id}")
        print(f"📁 Final artifacts are in: {x.workspace.get_path() / 'artifacts'}")
        print("-" * 80)
        
        # You can now inspect the 'artifacts' folder in the generated workspace

def print_header():
    """Prints the header for the demo."""
    print("=" * 80)
    print("🚀 VibeX - Automatic Agent Handoff Demo")
    print("=" * 80)
    print("This example shows how agents can autonomously hand off work based on predefined conditions.")
    print("No explicit 'handoff' tool is used; the system manages it seamlessly.")
    print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())
