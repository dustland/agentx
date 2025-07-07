#!/usr/bin/env python3
"""
Simple Research Example

Demonstrates how to use web_search and extract_content tools effectively
with detailed prompts to get comprehensive, valuable research content.
"""

import asyncio
from agentx import start_task

async def main():
    """Run a simple research demonstration."""
    
    print("🔬 Simple Research Example")
    print("=" * 60)
    print("Task: 'Research quantum computing for drug discovery'")
    print("Demonstrating: How agent prompt guides proper research methodology")
    print("Key Learning: Simple task + detailed agent prompt = comprehensive research")
    print("-" * 60)
    
    # Super simple task prompt - the agent prompt will guide the methodology
    research_prompt = "Research quantum computing for drug discovery"
    
    print(f"🎯 Research Task: {research_prompt[:100]}...")
    print("-" * 60)
    
    # Start the research task and get task executor
    task_executor = start_task(
        prompt=research_prompt,
        config_path="config/simple_research.yaml"
    )
    
    # Initialize the conversation
    await task_executor.start(research_prompt)
    
    print(f"📋 Task ID: {task_executor.task.task_id}")
    print(f"📁 Workspace: {task_executor.workspace.get_workspace_path()}")
    print("-" * 60)
    
    # Execute the task step by step with a maximum number of steps
    max_steps = 5  # Allow up to 5 conversation steps
    step_count = 0
    
    while step_count < max_steps:
        response = await task_executor.step()
        if not response.strip():  # Empty response means task is done
            break
            
        print(f"🔍 Research Step {step_count + 1}:\n{response}\n")
        print("-" * 60)
        step_count += 1
    
    # Mark task as complete
    task_executor.task.complete()

if __name__ == "__main__":
    asyncio.run(main()) 