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

    # Start the research task with XAgent - creates a conversational interface
    x = await start_task(
        prompt=research_prompt,
        config_path="config/simple_research.yaml"
    )

    print(f"📋 Task ID: {x.task_id}")
    print(f"📁 Workspace: {x.workspace.get_workspace_path()}")
    print("-" * 60)

    # Chat with X to execute the research
    print("🤖 X: Starting quantum computing research...")
    response = await x.chat(research_prompt)
    print(f"🔍 Research Step 1:\n{response.text}\n")
    print("-" * 60)

    # Continue the research with follow-up questions
    follow_up_questions = [
        "What are the specific applications in molecular simulation?",
        "Which pharmaceutical companies are investing in this technology?",
        "What are the current limitations and challenges?",
        "Generate a comprehensive summary with key findings"
    ]

    step_count = 2
    for question in follow_up_questions:
        if x.is_complete:
            break

        print(f"💬 User: {question}")
        response = await x.chat(question)

        print(f"🔍 Research Step {step_count}:\n{response.text}\n")

        if response.preserved_steps:
            print(f"   ✅ Preserved {len(response.preserved_steps)} completed research steps")
        if response.regenerated_steps:
            print(f"   🔄 Updated {len(response.regenerated_steps)} research steps")

        print("-" * 60)
        step_count += 1

    print("✅ Research completed!")
    print(f"📁 Check workspace for research artifacts: {x.workspace.get_workspace_path()}")

    # Demonstrate conversational capabilities
    print("\n💬 You can continue chatting with X:")
    print("   Example: x.chat('Focus more on the timeline for commercial applications')")
    print("   Example: x.chat('Compare this with classical computing approaches')")
    print("   Example: x.chat('Create a visual diagram of the quantum advantage')")

if __name__ == "__main__":
    asyncio.run(main())
