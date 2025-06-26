#!/usr/bin/env python3
"""
Debug Tools Script

Check what tools are actually available to the agent.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / ".env")

# Add src to path
sys.path.insert(0, str(project_root / "src"))

from agentx import start_task


async def debug_tools():
    """Debug what tools are available to the agent."""
    
    print("🔍 Debugging Available Tools")
    print("=" * 50)
    
    try:
        # Start a task to get access to the agent
        task_executor = start_task("debug", "test_single_agent.yaml")
        
        print(f"🆔 Task ID: {task_executor.task.task_id}")
        
        # Get the agent
        agent = task_executor.task.get_agent("test_agent")
        
        # Check tool manager
        print(f"\n🔧 Tool Manager:")
        print(f"   Available tools: {task_executor.tool_manager.list_tools()}")
        
        # Check agent tools
        print(f"\n🤖 Agent Tools:")
        tool_schemas = agent.get_tools_json()
        print(f"   Number of tools: {len(tool_schemas)}")
        
        for i, tool in enumerate(tool_schemas, 1):
            name = tool.get("function", {}).get("name", "unknown")
            description = tool.get("function", {}).get("description", "no description")
            print(f"   {i}. {name}: {description}")
        
        # Check builtin tools specifically
        print(f"\n🔨 Builtin Tools:")
        builtin_tools = task_executor.tool_manager.registry.get_builtin_tools()
        print(f"   Builtin tools: {builtin_tools}")
        
        # Check if specific tools exist
        target_tools = ["web_search", "extract_content", "write_file"]
        print(f"\n🎯 Target Tools Check:")
        for tool_name in target_tools:
            tool_func = task_executor.tool_manager.registry.get_tool_function(tool_name)
            if tool_func:
                print(f"   ✅ {tool_name}: Available")
            else:
                print(f"   ❌ {tool_name}: NOT FOUND")
        
        print(f"\n✅ Debug completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_tools()) 