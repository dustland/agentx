#!/usr/bin/env python3
"""
AutoWriter - Deep Research Writing System

A Google-inspired multi-agent system for generating comprehensive research reports.
Uses systematic decomposition and specialized agent orchestration.
"""

import asyncio
from pathlib import Path
from agentx import start_task

async def main():
    """
    This is the main entry point for the auto_writer example.
    It uses the new XAgent interface for conversational task management.
    """
    # Get the absolute path to the configuration file
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "team.yaml"

    # The user's goal for the task
    prompt = "Generate a comprehensive and visually stunning report on the key trends shaping web development in 2025. The report must be an interactive HTML page, covering topics like new frontend frameworks, backend technologies, AI integration in development, and modern UX/UI design paradigms. The final output must be professional, polished, and suitable for a C-suite audience, surpassing the quality of leading industry examples."

    print("🚀 AutoWriter - Starting comprehensive report generation...")
    print(f"📋 Task: {prompt[:100]}...")
    print("-" * 80)

    # Start the task with XAgent - creates a conversational interface
    x = await start_task(prompt, str(config_path))

    print(f"📋 Task ID: {x.task_id}")
    print(f"📁 Workspace: {x.workspace.get_workspace_path()}")
    print("-" * 80)

    # Chat with X to execute the task
    print("🤖 X: Starting the comprehensive report generation...")
    response = await x.chat(prompt)
    print(f"🤖 X: {response.text[:200]}...")

    if response.preserved_steps:
        print(f"   ✅ Preserved {len(response.preserved_steps)} completed steps")
    if response.regenerated_steps:
        print(f"   🔄 Regenerated {len(response.regenerated_steps)} steps")

    print("-" * 40)

    # Continue chatting until the task is complete
    while not x.is_complete:
        # Let X continue with the next steps
        response = await x.chat("Continue with the next step")

        if response.text.strip():
            print(f"🤖 X: {response.text[:200]}...")
            print("-" * 40)

    print("\n✅ TASK COMPLETE")
    print(f"📁 Workspace: {x.workspace.get_workspace_path()}")
    print(f"📋 Task ID: {x.task_id}")

    # Check for artifacts in the workspace
    workspace_path = x.workspace.get_workspace_path()
    artifacts_path = workspace_path / "artifacts"

    if artifacts_path.exists():
        artifact_files = list(artifacts_path.glob("*"))
        if artifact_files:
            print(f"📄 Generated artifacts:")
            for artifact in artifact_files:
                print(f"   - {artifact.name}")
        else:
            print("📄 No artifacts found in artifacts directory")
    else:
        print("📄 No artifacts directory found")

    print(f"\n🔗 Full workspace path: {workspace_path}")
    print("📁 Check the workspace directory for the generated report and artifacts.")

    # Demonstrate conversational interaction
    print("\n💬 You can also chat with X to modify the report:")
    print("   Example: x.chat('Make the report more visual with charts')")
    print("   Example: x.chat('Add a section about security trends')")
    print("   Example: x.chat('Generate an executive summary')")

if __name__ == "__main__":
    asyncio.run(main())
