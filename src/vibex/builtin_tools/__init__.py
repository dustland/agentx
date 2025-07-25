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
from ..storage.factory import ProjectStorageFactory

def register_builtin_tools(registry: ToolRegistry, project_storage: Optional[Any] = None, memory_system: Optional[Any] = None):
    """Register all built-in tools with the tool registry.
    
    Args:
        registry: The tool registry to register tools with
        project_storage: Optional ProjectStorage instance to use for tools
        memory_system: Optional memory system for memory tools
    """
    
    # Register tools with project storage support
    if project_storage:
        file_tool = FileTool(project_storage)
        registry.register_tool(file_tool)
        
        search_tool = SearchTool(project_storage=project_storage)
        registry.register_tool(search_tool)
        
        web_tool = WebTool(project_storage=project_storage)
        registry.register_tool(web_tool)
        
        document_tool = DocumentTool(project_storage=project_storage)
        registry.register_tool(document_tool)
        
        context_tool = ContextTool(project_path=str(project_storage.project_path))
        registry.register_tool(context_tool)
        
        research_tool = ResearchTool(project_storage=project_storage)
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
