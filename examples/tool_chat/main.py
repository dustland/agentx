#!/usr/bin/env python3
"""
Tool Chat Example - Demonstrates using built-in search and custom weather tools
"""

import asyncio
import sys
from pathlib import Path
import litellm

# Add the src directory to Python path
# This allows importing vibex module from the source code
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from vibex import VibeX
from weather_tool import WeatherTool


async def main():
    """Main function to run the tool chat example."""
    print("🔧 Tool Chat Example - Multiple Tool Calls Test")
    print("This example tests multiple weather tool calls in one conversation.")
    print("-" * 60)

    # Check if DeepSeek supports function calling
    model_name = "deepseek/deepseek-chat"
    supports_fc = litellm.supports_function_calling(model=model_name)
    print(f"🔍 Function calling support for {model_name}: {supports_fc}")

    # Test multiple cities to see parallel tool execution
    user_prompt = "What's the weather like in New York, London, Tokyo, and Sydney? Please get the current weather for all four cities."
    print(f"Test question: {user_prompt}")
    print()

    config_path = Path(__file__).parent / "config" / "team.yaml"

    try:
        # Start task with VibeX - creates a conversational interface
        x = await VibeX.start(
            project_id="tool_chat_project",
            goal=user_prompt,
            config_path=str(config_path),
        )

        # Register custom weather tool
        weather_tool = WeatherTool()
        x.register_tool(weather_tool)

        # Debug: Check what tools are registered
        print(f"🔧 Registered tools: {x.list_tools()}")

        # Get the agent to check tool schemas
        agent = list(x.specialist_agents.values())[0]
        tool_schemas = agent.get_tools_json()
        print(f"🔧 Agent has access to {len(tool_schemas)} tools")

        print(f"🎬 Processing: {user_prompt}")
        print()

        # Execute the task autonomously first
        while not x.is_complete():
            response = await x.step()
            print(f"🤖 X: {response}")
            print("-" * 60)

        # Demonstrate follow-up questions
        follow_ups = [
            "Which city has the best weather right now?",
            "What's the temperature difference between the warmest and coldest city?",
            "Can you create a summary table of all the weather data?"
        ]

        for question in follow_ups:
            print(f"💬 User: {question}")
            response = await x.chat(question)
            print(f"🤖 X: {response}")

            if response.preserved_steps:
                print(f"   ✅ Preserved {len(response.preserved_steps)} completed tool calls")

            print("-" * 60)

        print("✅ Tool chat example completed successfully!")

        # Demonstrate conversational capabilities
        print("\n💬 You can continue chatting with X:")
        print("   Example: x.chat('Get weather for Paris and Berlin too')")
        print("   Example: x.chat('What should I wear in each city?')")
        print("   Example: x.chat('Which cities are good for outdoor activities?')")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
