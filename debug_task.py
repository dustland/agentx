#!/usr/bin/env python3
"""
Debug script to trace task execution and tool availability.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

# Add src to path
sys.path.insert(0, str(project_root / "src"))

from agentx.core.task import start_task

async def debug_task():
    """Debug task execution and tool availability."""
    
    print("🔍 Debug: Task Execution Analysis")
    print("=" * 50)
    
    prompt = "Create a file called 'test.txt' with content 'Hello Debug'"
    
    try:
        # Start the task
        executor = start_task(
            prompt=prompt,
            config_path="config/simple_agent.yaml"
        )
        
        print(f"📋 Task ID: {executor.task.task_id}")
        print(f"📁 Workspace: {executor.task.workspace_dir}")
        
        # Check what agents are created
        print(f"\n🤖 Agents created: {list(executor.task.agents.keys())}")
        
        # Get the agent and check its tools
        agent_name = list(executor.task.agents.keys())[0]
        agent = executor.task.agents[agent_name]
        print(f"\n🔧 Agent '{agent_name}' tools: {agent.tools}")
        
        # Check the tool manager
        print(f"\n📦 Tool manager tools: {executor.tool_manager.list_tools()}")
        
        # Get tool schemas that would be sent to LLM
        tool_schemas = agent.get_tools_json()
        print(f"\n📋 Tool schemas for LLM ({len(tool_schemas)} tools):")
        for i, schema in enumerate(tool_schemas):
            print(f"  {i+1}. {schema.get('function', {}).get('name', 'Unknown')}")
            
        # Run one step and trace what happens
        print(f"\n🚀 Running one step...")
        async for step_result in executor.step():
            print(f"📤 Step result: {step_result}")
            break
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_task()) 