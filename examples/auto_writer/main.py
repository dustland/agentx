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
    It uses start_task to get access to the workspace and artifacts.
    """
    # Get the absolute path to the configuration file
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "team.yaml"

    # The user's goal for the task
    prompt = "Generate a comprehensive and visually stunning report on the key trends shaping web development in 2025. The report must be an interactive HTML page, covering topics like new frontend frameworks, backend technologies, AI integration in development, and modern UX/UI design paradigms. The final output must be professional, polished, and suitable for a C-suite audience, surpassing the quality of leading industry examples."

    print("🚀 AutoWriter - Starting comprehensive report generation...")
    print(f"📋 Task: {prompt[:100]}...")
    print("-" * 80)

    # Start the task (creates executor and initializes conversation in one call)
    executor = await start_task(prompt, str(config_path))

    print(f"📋 Task ID: {executor.task.task_id}")
    print(f"📁 Workspace: {executor.workspace.get_workspace_path()}")
    print("-" * 80)

    # Execute the task step by step
    while not executor.is_complete:
        response = await executor.step()

        # Print agent responses with better formatting
        if response.strip():
            print(f"🤖 Agent Response: {response[:200]}...")
            print("-" * 40)

    print("\n✅ TASK COMPLETE")
    print(f"📁 Workspace: {executor.workspace.get_workspace_path()}")
    print(f"📋 Task ID: {executor.task.task_id}")

    # Check for artifacts in the workspace
    workspace_path = executor.workspace.get_workspace_path()
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

if __name__ == "__main__":
    asyncio.run(main())
