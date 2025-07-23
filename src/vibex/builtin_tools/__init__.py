"""
This directory contains the implementations of the builtin tools.

This __init__.py file is special. It contains the function that
registers all the builtin tools with the core ToolRegistry.
"""

from .context import ContextTool
from .file import FileTool
from .memory import MemoryTool
from .search import SearchTool
from .web import WebTool
from .document import DocumentTool
from .research import ResearchTool
from typing import Optional, Any
from vibex.tool.registry import ToolRegistry
from ..storage.factory import TaskspaceFactory

def register_builtin_tools(registry: ToolRegistry, taskspace_storage: Optional[Any] = None, memory_system: Optional[Any] = None):
    """Register all built-in tools with the tool registry.
    
    Args:
        registry: The tool registry to register tools with
        taskspace_storage: Optional TaskspaceStorage instance to use for tools
        memory_system: Optional memory system for memory tools
    """
    
    # Register tools with taskspace support
    if taskspace_storage:
        file_tool = FileTool(taskspace_storage)
        registry.register_tool(file_tool)
        
        search_tool = SearchTool(taskspace_storage=taskspace_storage)
        registry.register_tool(search_tool)
        
        web_tool = WebTool(taskspace_storage=taskspace_storage)
        registry.register_tool(web_tool)
        
        document_tool = DocumentTool(taskspace_storage=taskspace_storage)
        registry.register_tool(document_tool)
        
        context_tool = ContextTool(taskspace_path=str(taskspace_storage.taskspace_path))
        registry.register_tool(context_tool)
        
        research_tool = ResearchTool(taskspace_storage=taskspace_storage)
        registry.register_tool(research_tool)
        
        if memory_system:
            memory_tool = MemoryTool(memory_system=memory_system)
            registry.register_tool(memory_tool)

__all__ = [
    "ContextTool",
    "FileTool", 
    "MemoryTool",
    "SearchTool",
    "WebTool",
    "DocumentTool",
    "ResearchTool",
    "create_file_tool",
    "register_builtin_tools",
]
