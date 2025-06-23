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
    
    # Start the research task and get task executor with task ID
    task_executor = start_task(
        prompt=research_prompt,
        config_path="config/simple_research.yaml"
    )
    
    print(f"📋 Task ID: {task_executor.task.task_id}")
    print(f"📁 Workspace: workspace/{task_executor.task.task_id}/artifacts/")
    print("-" * 60)
    
    # Execute the task step by step until completion
    while not task_executor.is_complete:
        async for result in task_executor.step():
            # The step method already handles all the printing and flow control
            pass
    
    print(f"\n✅ Research completed!")
    print(f"📄 Check workspace/{task_executor.task.task_id}/artifacts/ for research findings")

if __name__ == "__main__":
    asyncio.run(main()) 