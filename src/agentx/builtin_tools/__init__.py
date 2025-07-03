"""
This directory contains the implementations of the builtin tools.

This __init__.py file is special. It contains the function that
registers all the builtin tools with the core ToolRegistry.
"""

def register_builtin_tools(registry, workspace_path: str, memory_system = None):
    """
    Registers all builtin tools and toolsets with the provided registry.
    """
    from .search import SearchTool
    from .web import WebTool
    from .plan import PlanTool
    from .context import ContextTool
    from .file import create_file_tool
    from .memory import create_memory_tools

    # --- Register Individual Tools ---
    search_tool = SearchTool()
    web_tool = WebTool()
    planning_tool = PlanTool(workspace_path=workspace_path)
    context_tool = ContextTool()
    file_tool = create_file_tool(workspace_path)

    # Register all tool instances
    registry.register_tool(search_tool)
    registry.register_tool(web_tool)
    registry.register_tool(planning_tool)
    registry.register_tool(context_tool)
    registry.register_tool(file_tool)

    # Register memory tools if a memory system is available
    if memory_system:
        memory_tools = create_memory_tools(memory=memory_system)
        for tool in memory_tools:
            registry.register_tool(tool)
        registry.register_toolset("memory", [t.name for t in memory_tools])

    # --- Register Toolsets ---
    registry.register_toolset("search", list(search_tool.get_callable_methods().keys()))
    registry.register_toolset("web_tools", list(web_tool.get_callable_methods().keys()))
    registry.register_toolset("planning", list(planning_tool.get_callable_methods().keys()))
    registry.register_toolset("context_tools", list(context_tool.get_callable_methods().keys()))
    registry.register_toolset("file_tools", list(file_tool.get_callable_methods().keys()))

# This file can be empty. 