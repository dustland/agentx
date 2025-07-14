"""
This directory contains the implementations of the builtin tools.

This __init__.py file is special. It contains the function that
registers all the builtin tools with the core ToolRegistry.
"""

from .context import ContextTool
from .file import FileTool, create_file_tool
from .memory import MemoryTool
from .search import SearchTool
from .web import WebTool
from .document import DocumentTool
from .research import ResearchTool

def register_builtin_tools(registry, taskspace_path=None, memory_system=None):
    """Register all builtin tools with the registry."""
    if taskspace_path:
        from ..storage.factory import StorageFactory
        
        # Create taskspace storage for tools that need it
        taskspace_storage = StorageFactory.create_taskspace_storage(taskspace_path)
        
        # Register tools with taskspace support
        file_tool = create_file_tool(taskspace_path=taskspace_path)
        registry.register_tool(file_tool)
        
        search_tool = SearchTool(taskspace_storage=taskspace_storage)
        registry.register_tool(search_tool)
        
        web_tool = WebTool(taskspace_storage=taskspace_storage)
        registry.register_tool(web_tool)
        
        context_tool = ContextTool(taskspace_path=taskspace_path)
        registry.register_tool(context_tool)
        
        document_tool = DocumentTool(taskspace_storage=taskspace_storage)
        registry.register_tool(document_tool)
        
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
