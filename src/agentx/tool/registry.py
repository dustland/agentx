"""
Tool registry for managing tool definitions and discovery.

The registry is responsible for:
- Registering tools and their metadata
- Tool discovery and lookup
- Schema generation
- NOT for execution (that's ToolExecutor's job)
"""

from typing import Dict, List, Any, Optional, Callable
import inspect
from ..utils.logger import get_logger
from .base import Tool, ToolFunction
from .models import ToolRegistry, Tool
from ..builtin_tools.search import SearchTool
from ..builtin_tools.web import WebTool
from ..builtin_tools.planning import PlanningTool
from ..builtin_tools.context import ContextTool
from ..builtin_tools.file import create_file_tool

logger = get_logger(__name__)


_tool_registry_instance = None


def get_tool_registry() -> "ToolRegistry":
    """
    Get the master tool registry. This is a singleton.
    """
    global _tool_registry_instance
    if _tool_registry_instance is None:
        _tool_registry_instance = ToolRegistry()
    return _tool_registry_instance


def register_tool(tool: Tool) -> None:
    """
    Register a tool in the global registry.
    
    Args:
        tool: Tool instance to register
    """
    get_tool_registry().register_tool(tool)


def register_function(func: Callable, name: Optional[str] = None) -> None:
    """
    Register a function as a tool in the global registry.
    
    Args:
        func: Function to register
        name: Optional name override
    """
    get_tool_registry().register_function(func, name)


def list_tools() -> List[str]:
    """List all registered tool names."""
    return get_tool_registry().list_tools()


def validate_agent_tools(tool_names: List[str]) -> tuple[List[str], List[str]]:
    """
    Validate a list of tool names against the registry.
    
    Returns:
        A tuple of (valid_tools, invalid_tools)
    """
    available_tools = get_tool_registry().list_tools()
    
    valid = [name for name in tool_names if name in available_tools]
    invalid = [name for name in tool_names if name not in available_tools]
    
    return valid, invalid


def suggest_tools_for_agent(agent_name: str, agent_description: str = "") -> List[str]:
    """
    Suggest a list of relevant tools for a new agent.
    (This is a placeholder for a more intelligent suggestion mechanism)
    """
    # For now, just return a few basic tools
    return ['read_file', 'write_file', 'list_directory']


def print_available_tools():
    """Prints a formatted table of all available tools."""
    registry = get_tool_registry()
    tool_list = registry.list_tools()
    
    if not tool_list:
        print("No tools are registered.")
        return
        
    print(f"{'Tool Name':<30} {'Description':<70}")
    print("-" * 100)
    
    for tool_name in sorted(tool_list):
        tool_func = registry.get_tool_function(tool_name)
        if tool_func:
            description = tool_func.description.splitlines()[0] if tool_func.description else 'No description available.'
            print(f"{tool_name:<30} {description:<70}") 