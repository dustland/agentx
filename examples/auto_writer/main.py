#!/usr/bin/env python3
"""
AutoWriter - Deep Research Writing System

A Google-inspired multi-agent system for generating comprehensive research reports.
Uses systematic decomposition and specialized agent orchestration.
"""

import asyncio
import os
from pathlib import Path
from agentx import TaskExecutor

# Set the API key
# os.environ["DEEPSEEK_API_KEY"] = "YOUR_API_KEY"

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
    prompt = "Write a comprehensive report on the current state of AI in 2024."

    # The executor will now use the Lead to run the entire workflow.
    final_result = await executor.execute_task(prompt, planner_agent="Planner")

    print("\n--- TASK COMPLETE ---")
    print("Final Result:", final_result.output)
    print("Check the workspace for the full report and artifacts.")

if __name__ == "__main__":
    asyncio.run(main())