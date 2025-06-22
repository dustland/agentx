#!/usr/bin/env python3
"""
Debug script to check tool registration and availability.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agentx.core.tool import get_tool_registry, print_available_tools
from agentx.builtin_tools.storage_tools import create_storage_tools
from agentx.core.tool import register_tool

def debug_tools():
    """Debug tool registration."""
    
    print("🔍 Debug: Tool Registration Analysis")
    print("=" * 50)
    
    # Get current registry
    registry = get_tool_registry()
    
    print(f"📊 Tools currently registered: {len(registry.list_tools())}")
    print(f"📋 Tool list: {registry.list_tools()}")
    
    # Create and register storage tools
    print("\n🗄️ Creating storage tools...")
    workspace_path = str(Path.cwd() / "workspace" / "debug")
    storage_tools = create_storage_tools(workspace_path)
    
    print(f"📦 Created {len(storage_tools)} storage tools")
    for i, tool in enumerate(storage_tools):
        print(f"  {i+1}. {tool.__class__.__name__}")
        methods = tool.get_callable_methods()
        print(f"     Methods: {list(methods.keys())}")
    
    # Register storage tools
    print("\n📝 Registering storage tools...")
    for tool in storage_tools:
        register_tool(tool)
    
    print(f"\n📊 Tools after registration: {len(registry.list_tools())}")
    print(f"📋 Updated tool list: {registry.list_tools()}")
    
    # Print detailed tool information
    print("\n📄 Detailed Tool Information:")
    print_available_tools()
    
    # Test getting a specific storage tool
    print("\n🧪 Testing specific tool retrieval:")
    write_file_tool = registry.get_tool('write_file')
    if write_file_tool:
        tool_instance, method, pydantic_model = write_file_tool
        print(f"✅ write_file found:")
        print(f"   Tool: {tool_instance}")
        print(f"   Method: {method}")
        print(f"   Pydantic Model: {pydantic_model}")
    else:
        print("❌ write_file not found")

if __name__ == "__main__":
    debug_tools() 