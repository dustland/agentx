"""
Tool execution framework for AgentX.

This module provides:
- Tool registration and discovery
- Secure tool execution with performance monitoring
- Tool result formatting and error handling
- Unified tool management for task isolation
"""

from ..core.tool import Tool, ToolResult
from .registry import ToolRegistry
from .manager import ToolManager

# Global tool registry instance
# All parts of the framework should use this instance
# for registering and discovering tools.
_registry = ToolRegistry()

def register_tool(tool: Tool):
    _registry.register_tool(tool)

def register_function(func, name=None):
    _registry.register_function(func, name=name)

def list_tools():
    return _registry.list_tools()

def get_tool_schemas(tool_names=None):
    return _registry.get_all_tool_schemas(tool_names=tool_names)

def validate_agent_tools(tool_names: list[str]) -> tuple[list[str], list[str]]:
    """
    Validate a list of tool names against the registry.

    Returns:
        A tuple of (valid_tools, invalid_tools)
    """
    available_tools = list_tools()

    valid = [name for name in tool_names if name in available_tools]
    invalid = [name for name in tool_names if name not in available_tools]

    return valid, invalid

def suggest_tools_for_agent(agent_name: str, agent_description: str = "") -> list[str]:
    """
    Suggest a list of relevant tools for a new agent.
    (This is a placeholder for a more intelligent suggestion mechanism)
    """
    # For now, just return a few basic tools
    return ['read_file', 'write_file', 'list_directory']

__all__ = [
    "Tool",
    "ToolResult",
    "ToolRegistry",
    "ToolManager",
    "register_tool",
    "register_function",
    "list_tools",
    "get_tool_schemas",
    "validate_agent_tools",
    "suggest_tools_for_agent",
]
