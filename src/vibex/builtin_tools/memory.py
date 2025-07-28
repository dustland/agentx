"""
Memory Tools - Clean implementation using Memory.
"""

from typing import Annotated, Optional
from ..core.tool import Tool
from ..memory.models import MemoryBackend

class MemoryTool(Tool):
    """Memory management capabilities using Memory."""

    def __init__(self, memory: MemoryBackend):
        super().__init__(name="memory_tool", description="Memory management tool")
        self.memory = memory

    async def execute(self, action: str, **kwargs) -> dict:
        """Execute memory operations."""
        if action == "add_memory":
            return await self._add_memory(**kwargs)
        elif action == "search_memory":
            return await self._search_memory(**kwargs)
        elif action == "list_memories":
            return await self._list_memories(**kwargs)
        elif action == "get_memory_stats":
            return await self._get_memory_stats(**kwargs)
        elif action == "clear_memories":
            return await self._clear_memories(**kwargs)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    async def _add_memory(self, content: str, **kwargs) -> dict:
        """Store content in persistent memory with intelligent extraction."""
        try:
            metadata = kwargs.get("metadata", {})
            importance = kwargs.get("importance", 1.0)

            memory_id = await self.memory.save_async(
                content=content,
                metadata=metadata,
                importance=importance
            )

            return {"success": True, "memory_id": memory_id, "message": f"Memory added successfully (ID: {memory_id})"}

        except Exception as e:
            return {"success": False, "error": f"Failed to add memory: {str(e)}"}

    async def _search_memory(self, query: str, limit: int = 5, **kwargs) -> dict:
        """Search for relevant memories using semantic similarity."""
        try:
            results = await self.memory.search_async(
                query=query,
                limit=limit
            )

            if not results:
                return {"success": True, "results": [], "message": "No relevant memories found for your query."}

            # Format results for display
            formatted_results = []
            for i, memory in enumerate(results, 1):
                content = memory.content
                timestamp = memory.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                formatted_results.append(f"{i}. {content} (created: {timestamp})")

            return {
                "success": True,
                "results": [{
                    "content": memory.content,
                    "timestamp": memory.timestamp.isoformat(),
                    "metadata": getattr(memory, "metadata", {})
                } for memory in results],
                "count": len(results),
                "message": f"Found {len(results)} relevant memories"
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to search memories: {str(e)}"}

    async def _list_memories(self, limit: int = 10, **kwargs) -> dict:
        """List recent memories."""
        try:
            memories = self.memory.get_recent(limit=limit)

            if not memories:
                return {"success": True, "memories": [], "message": f"No memories found for agent: {self.memory.agent.name}"}

            # Format memories for display
            formatted_memories = []
            for i, memory in enumerate(memories, 1):
                content = memory.content
                timestamp = memory.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                formatted_memories.append(f"{i}. {content} (created: {timestamp})")

            return {
                "success": True,
                "memories": [{
                    "content": memory.content,
                    "timestamp": memory.timestamp.isoformat(),
                    "metadata": getattr(memory, "metadata", {})
                } for memory in memories],
                "count": len(memories),
                "agent_name": self.memory.agent.name,
                "message": f"Retrieved {len(memories)} recent memories"
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to list memories: {str(e)}"}

    async def _get_memory_stats(self, **kwargs) -> dict:
        """Get statistics about the memory system."""
        try:
            stats = self.memory.get_stats()

            return {
                "success": True,
                "stats": {
                    "agent_name": self.memory.agent.name,
                    "total_memories": stats.get('total_memories', 0),
                    "memory_types": stats.get('memory_types', {}),
                    "average_importance": stats.get('average_importance', 0),
                    "oldest_memory": stats.get('oldest_memory'),
                    "newest_memory": stats.get('newest_memory')
                },
                "message": "Memory statistics retrieved successfully"
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to get memory stats: {str(e)}"}

    async def _clear_memories(self, **kwargs) -> dict:
        """Clear all memories for the current agent."""
        try:
            self.memory.clear()
            return {"success": True, "agent_name": self.memory.agent.name, "message": f"Successfully cleared all memories for {self.memory.agent.name}"}

        except Exception as e:
            return {"success": False, "error": f"Failed to clear memories: {str(e)}"}

def create_memory_tools(memory: MemoryBackend) -> list[MemoryTool]:
    """Factory function to create memory tools."""
    return [MemoryTool(memory=memory)]

# Export the tool class
__all__ = ['MemoryTool', 'create_memory_tools']
