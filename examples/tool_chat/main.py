#!/usr/bin/env python3
"""
Tool Chat Example - Demonstrates using built-in search and custom weather tools
"""

import asyncio
import sys
from pathlib import Path
import litellm

# Add the src directory to Python path
# This allows importing agentx module from the source code
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agentx import start_task
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
        # Start task and get executor
        executor = start_task(user_prompt, config_path)
        
        # Register custom weather tool
        weather_tool = WeatherTool()
        executor.tool_manager.register_tool(weather_tool)
        
        # Debug: Check what tools are registered
        print(f"🔧 Registered tools: {executor.tool_manager.list_tools()}")
        
        # Start the conversation
        await executor.start(user_prompt)
        
        # Get the agent to check tool schemas
        agent = list(executor.agents.values())[0]
        tool_schemas = agent.get_tools_json()
        print(f"🔧 Agent has access to {len(tool_schemas)} tools")
        
        print(f"🎬 Processing: {user_prompt}")
        print()
        
        # Execute the task step by step
        while not executor.is_complete():
            response = await executor.step()
            print(f"🤖 Assistant: {response}")
            print("-" * 60)
        
        print("✅ Task completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 