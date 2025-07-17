"""
Tool Manager - Unified tool registry and execution for task isolation.

Combines ToolRegistry and ToolExecutor into a single manager class
that provides both tool registration and execution capabilities.
This simplifies the Agent interface and ensures task-level tool isolation.
"""

from typing import Dict, List, Any, Optional
from .registry import ToolRegistry
from .executor import ToolExecutor, ToolResult
from ..core.tool import Tool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ToolManager:
    """
    Unified tool manager that combines registry and execution.

    This class provides task-level tool isolation by maintaining
    its own registry and executor. Each task gets its own ToolManager
    instance to prevent tool conflicts between tasks.
    """

    def __init__(self, task_id: str = "default", taskspace_path: Optional[str] = None):
        """
        Initialize tool manager with task isolation.

        Args:
            task_id: Unique identifier for this task (for logging/debugging)
            taskspace_path: Path to task-specific taskspace (for file tools)
        """
        self.task_id = task_id
        self.taskspace_path = taskspace_path
        self.registry = ToolRegistry()

        # Register task-specific builtin tools if taskspace_path is provided
        if taskspace_path:
            self._register_builtin_tools(taskspace_path)

        self.executor = ToolExecutor(registry=self.registry)

        logger.debug(f"ToolManager initialized for task {task_id} with taskspace: {taskspace_path}")

    def _register_builtin_tools(self, taskspace_path: str):
        """Register builtin tools with correct taskspace path."""
        from ..builtin_tools import register_builtin_tools
        from ..storage.factory import TaskspaceFactory
        from pathlib import Path

        # Extract task_id from taskspace_path (assuming format: base_path/task_id)
        path = Path(taskspace_path)
        task_id = path.name
        base_path = path.parent

        # Create single taskspace storage instance for all tools using preferred method
        taskspace_storage = TaskspaceFactory.create_taskspace(
            base_path=base_path,
            task_id=task_id
        )

        # Register all builtin tools using the centralized function
        register_builtin_tools(self.registry, taskspace_storage=taskspace_storage)

        logger.info(f"Registered builtin tools for taskspace: {taskspace_path}")

    # Registry methods (delegation)
    def register_tool(self, tool: Tool) -> None:
        """Register a tool with this task's registry."""
        self.registry.register_tool(tool)
        logger.debug(f"Registered tool {tool.__class__.__name__} with task {self.task_id}")

    def list_tools(self) -> List[str]:
        """Get list of all registered tool names."""
        return self.registry.list_tools()

    def get_tool_schemas(self, tool_names: List[str] = None) -> List[Dict[str, Any]]:
        """Get JSON schemas for tools."""
        return self.registry.get_tool_schemas(tool_names)

    def get_tool_function(self, name: str):
        """Get a tool function by name."""
        return self.registry.get_tool_function(name)

    def get_tool(self, name: str):
        """Get a tool instance by name for direct access."""
        return self.registry.get_tool(name)

    def get_builtin_tools(self) -> List[str]:
        """Get list of all builtin tool names."""
        return self.registry.get_builtin_tools()

    def get_custom_tools(self) -> List[str]:
        """Get list of all custom (non-builtin) tool names."""
        return self.registry.get_custom_tools()

    # Executor methods (delegation)
    async def execute_tool(self, tool_name: str, agent_name: str = "default", **kwargs) -> ToolResult:
        """Execute a single tool."""
        return await self.executor.execute_tool(tool_name, agent_name, **kwargs)

    async def execute_tools(self, tool_calls: List[Any], agent_name: str = "default") -> List[Dict[str, Any]]:
        """Execute multiple tool calls."""
        return await self.executor.execute_tools(tool_calls, agent_name)

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return self.executor.get_execution_stats()

    # Convenience methods
    def get_tool_count(self) -> int:
        """Get the number of registered tools."""
        return len(self.registry.list_tools())

    def clear_tools(self) -> None:
        """Clear all registered tools (useful for testing)."""
        self.registry.clear()
        self.executor.clear_history()
        logger.debug(f"Cleared all tools for task {self.task_id}")

    def __str__(self) -> str:
        return f"ToolManager(task_id='{self.task_id}', tools={self.get_tool_count()})"

    def __repr__(self) -> str:
        return self.__str__()
