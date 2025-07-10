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

            return {"success": True, "message": f"✅ Memory added successfully (ID: {memory_id})"}

        except Exception as e:
            return {"success": False, "error": f"❌ Failed to add memory: {str(e)}"}

    async def _search_memory(self, query: str, limit: int = 5, **kwargs) -> dict:
        """Search for relevant memories using semantic similarity."""
        try:
            results = await self.memory.search_async(
                query=query,
                limit=limit
            )

            if not results:
                return {"success": True, "message": "🔍 No relevant memories found for your query."}

            # Format results for display
            formatted_results = []
            for i, memory in enumerate(results, 1):
                content = memory.content
                timestamp = memory.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                formatted_results.append(f"{i}. {content} (created: {timestamp})")

            message = f"🔍 Found {len(results)} relevant memories:\n\n" + "\n".join(formatted_results)
            return {"success": True, "message": message}

        except Exception as e:
            return {"success": False, "error": f"❌ Failed to search memories: {str(e)}"}

    async def _list_memories(self, limit: int = 10, **kwargs) -> dict:
        """List recent memories."""
        try:
            memories = self.memory.get_recent(limit=limit)

            if not memories:
                return {"success": True, "message": f"📝 No memories found for agent: {self.memory.agent.name}"}

            # Format memories for display
            formatted_memories = []
            for i, memory in enumerate(memories, 1):
                content = memory.content
                timestamp = memory.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                formatted_memories.append(f"{i}. {content} (created: {timestamp})")

            message = f"📝 Recent memories for {self.memory.agent.name}:\n\n" + "\n".join(formatted_memories)
            return {"success": True, "message": message}

        except Exception as e:
            return {"success": False, "error": f"❌ Failed to list memories: {str(e)}"}

    async def _get_memory_stats(self, **kwargs) -> dict:
        """Get statistics about the memory system."""
        try:
            stats = self.memory.get_stats()

            stats_lines = [
                f"📊 Memory System Statistics:",
                f"",
                f"Agent: {self.memory.agent.name}",
                f"Total memories: {stats.get('total_memories', 0)}",
                f"Memory types: {stats.get('memory_types', {})}",
                f"Average importance: {stats.get('average_importance', 0):.2f}",
            ]

            if stats.get('oldest_memory'):
                stats_lines.append(f"Oldest memory: {stats['oldest_memory']}")
            if stats.get('newest_memory'):
                stats_lines.append(f"Newest memory: {stats['newest_memory']}")

            message = "\n".join(stats_lines)
            return {"success": True, "message": message}

        except Exception as e:
            return {"success": False, "error": f"❌ Failed to get memory stats: {str(e)}"}

    async def _clear_memories(self, **kwargs) -> dict:
        """Clear all memories for the current agent."""
        try:
            self.memory.clear()
            return {"success": True, "message": f"✅ Successfully cleared all memories for {self.memory.agent.name}"}

        except Exception as e:
            return {"success": False, "error": f"❌ Failed to clear memories: {str(e)}"}

def create_memory_tools(memory: MemoryBackend) -> list[MemoryTool]:
    """Factory function to create memory tools."""
    return [MemoryTool(memory=memory)]

# Export the tool class
__all__ = ['MemoryTool', 'create_memory_tools']
