#!/usr/bin/env python3
"""
AutoWriter - Deep Research Writing System

A Google-inspired multi-agent system for generating comprehensive research reports.
Uses systematic decomposition and specialized agent orchestration.
"""

import asyncio
from pathlib import Path
from agentx import TaskExecutor

async def main():
    """
    This is the main entry point for the auto_writer example.
    It initializes the TaskExecutor and runs the task using the default Lead.
    """
    # Get the absolute path to the configuration file
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "team.yaml"

    # Initialize the TaskExecutor. It will automatically load the default Lead
    # and the standard agents specified in the config.
    executor = TaskExecutor(config_path=str(config_path))

    # Debug: Print available agents
    print("Available agents:", list(executor.task.agents.keys()))

    # The user's goal for the task
    prompt = "Generate a comprehensive and visually stunning report on the key trends shaping web development in 2025. The report must be an interactive HTML page, covering topics like new frontend frameworks, backend technologies, AI integration in development, and modern UX/UI design paradigms. The final output must be professional, polished, and suitable for a C-suite audience, surpassing the quality of leading industry examples."

    # The executor will now use the Lead to run the entire workflow.
    final_result = await executor.execute_task(prompt, planner_agent="planner")

    print("\n--- TASK COMPLETE ---")
    print(f"Task ID: {final_result.task_id}")
    print(f"Task Status: {'Complete' if final_result.is_complete else 'In Progress'}")
    print(f"Workspace: {final_result.workspace_dir}")
    print(f"Artifacts: {list(final_result.artifacts.keys())}")
    print("Check the workspace for the full report and artifacts.")

if __name__ == "__main__":
    asyncio.run(main())