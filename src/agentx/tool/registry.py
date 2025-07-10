"""
Tool Registry - The single source of truth for tool definitions.
"""
from typing import Dict, List, Any, Optional, Callable
from ..core.tool import Tool, ToolFunction
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """A thread-safe registry for managing tools and their configurations."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self._tools: Dict[str, ToolFunction] = {}
        self._toolsets: Dict[str, List[str]] = {}
        # Note: Builtin tools are now registered by ToolManager with proper workspace context
        # This prevents duplicate registrations and ensures correct workspace paths
        self.__initialized = True

    def register_tool(self, tool: Tool):
        """
        Register all callable methods of a Tool instance.
        Each method marked with @tool is registered as a separate tool function.
        """
        tool_methods = tool.get_callable_methods()
        for tool_name in tool_methods:
            method = getattr(tool, tool_name)
            self.register_function(method, name=tool_name)

    def register_function(self, func: Callable, name: Optional[str] = None):
        """Register a standalone function as a tool."""
        if not (callable(func) and hasattr(func, '_is_tool_call')):
            raise ValueError(f"Function {func.__name__} is not a valid tool. Please decorate it with @tool.")

        tool_name = name or func.__name__
        if tool_name in self._tools:
            logger.warning(f"Tool '{tool_name}' is already registered and will be overwritten.")

        # The schema generation utilities are now in core.tool
        from ..core.tool import _create_pydantic_model_from_signature
        pydantic_model = _create_pydantic_model_from_signature(func)

        if pydantic_model:
            parameters = pydantic_model.model_json_schema()
        else:
            # Functions with no parameters need proper OpenAI schema format
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }

        self._tools[tool_name] = ToolFunction(
            name=tool_name,
            description=func._tool_description,
            parameters=parameters,
            return_description=func._return_description,
            function=func
        )
        logger.debug(f"Registered tool: '{tool_name}'")

    def register_toolset(self, name: str, tool_names: List[str]):
        """
        Register a collection of tools as a named toolset.
        """
        invalid_tools = [t_name for t_name in tool_names if t_name not in self._tools]
        if invalid_tools:
            raise ValueError(f"Cannot create toolset '{name}'. The following tools are not registered: {invalid_tools}")

        self._toolsets[name] = tool_names
        logger.debug(f"Registered toolset '{name}' with tools: {tool_names}")

    def get_tool_function(self, name: str) -> Optional[ToolFunction]:
        """Retrieve a tool function by its name."""
        return self._tools.get(name)

    def get_tool(self, name: str):
        """Get a tool instance by name for direct access."""
        tool_func = self.get_tool_function(name)
        if not tool_func:
            return None
        # Return the tool instance - the function is bound to the tool instance
        return tool_func.function.__self__ if hasattr(tool_func.function, '__self__') else tool_func.function

    def get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get the JSON schema for a single tool."""
        tool_func = self.get_tool_function(name)
        if not tool_func:
            return None

        return {
            "type": "function",
            "function": {
                "name": tool_func.name,
                "description": tool_func.description,
                "parameters": tool_func.parameters
            }
        }

    def get_tool_schemas(self, tool_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get a list of all tool schemas, optionally filtered.
        """
        schemas = []
        target_tool_names = set()

        if tool_names:
            for name in tool_names:
                if name in self._toolsets:
                    target_tool_names.update(self._toolsets[name])
                elif name in self._tools:
                    target_tool_names.add(name)
        else:
            target_tool_names = set(self._tools.keys())

        for name in sorted(list(target_tool_names)):
            schema = self.get_tool_schema(name)
            if schema:
                schemas.append(schema)

        return schemas

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def get_tool_names(self) -> List[str]:
        """Get all registered tool names (alias for list_tools)."""
        return self.list_tools()

    def list_toolsets(self) -> List[str]:
        """List all registered toolset names."""
        return list(self._toolsets.keys())

    def get_builtin_tools(self) -> List[str]:
        """Get list of all builtin tool names."""
        # For now, return all tools since we register builtin tools during init
        # In the future, we could track which tools are builtin vs custom
        return list(self._tools.keys())

    def get_custom_tools(self) -> List[str]:
        """Get list of all custom (non-builtin) tool names."""
        # For now, return empty list since we haven't implemented custom tool tracking
        # This would need to be enhanced to track which tools are custom
        return []

    def clear(self):
        """Clear all registered tools and toolsets. Useful for testing."""
        self._tools.clear()
        self._toolsets.clear()
        # Note: Builtin tools will be re-registered by ToolManager when needed


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return ToolRegistry()
