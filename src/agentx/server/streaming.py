"""
Streaming support for AgentX API
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime
from ..utils.logger import get_logger
from ..core.message import Message, StreamChunk
from ..storage.chat_history import chat_history_manager

logger = get_logger(__name__)

class TaskEventStream:
    """Manages event streams for tasks"""
    
    def __init__(self):
        self.streams: Dict[str, asyncio.Queue] = {}
        
    def create_stream(self, task_id: str) -> asyncio.Queue:
        """Create a new event stream for a task"""
        if task_id not in self.streams:
            self.streams[task_id] = asyncio.Queue()
        return self.streams[task_id]
        
    def get_stream(self, task_id: str) -> Optional[asyncio.Queue]:
        """Get existing stream for a task"""
        return self.streams.get(task_id)
        
    async def send_event(self, task_id: str, event_type: str, data: Any):
        """Send an event to all listeners of a task"""
        stream = self.get_stream(task_id)
        if stream:
            event = {
                "id": str(datetime.now().timestamp()),
                "event": event_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            await stream.put(event)
            logger.debug(f"Sent {event_type} event for task {task_id}")
            
    async def stream_events(self, task_id: str) -> AsyncGenerator[str, None]:
        """Stream events for a task as SSE format"""
        stream = self.create_stream(task_id)
        
        try:
            while True:
                event = await stream.get()
                
                # Format as SSE
                sse_data = f"id: {event['id']}\n"
                sse_data += f"event: {event['event']}\n"
                sse_data += f"data: {json.dumps(event['data'])}\n\n"
                
                yield sse_data
                
        except asyncio.CancelledError:
            logger.info(f"Stream cancelled for task {task_id}")
            raise
        finally:
            # Clean up stream
            if task_id in self.streams:
                del self.streams[task_id]
                
    def close_stream(self, task_id: str):
        """Close and remove a stream"""
        if task_id in self.streams:
            del self.streams[task_id]

# Global event stream manager
event_stream_manager = TaskEventStream()

async def send_agent_message(task_id: str, agent_id: str, message: str, metadata: Optional[Dict] = None):
    """Send an agent message event"""
    await event_stream_manager.send_event(
        task_id,
        "agent_message",
        {
            "agent_id": agent_id,
            "message": message,
            "metadata": metadata or {}
        }
    )

async def send_agent_status(task_id: str, agent_id: str, status: str, progress: int = 0):
    """Send an agent status update"""
    await event_stream_manager.send_event(
        task_id,
        "agent_status",
        {
            "agent_id": agent_id,
            "status": status,
            "progress": progress
        }
    )

async def send_task_update(task_id: str, status: str, result: Optional[Any] = None):
    """Send a task status update"""
    await event_stream_manager.send_event(
        task_id,
        "task_update",
        {
            "task_id": task_id,
            "status": status,
            "result": result
        }
    )

async def send_tool_call(task_id: str, agent_id: str, tool_name: str, parameters: Dict, result: Optional[Any] = None, status: str = "pending"):
    """Send a tool call event"""
    await event_stream_manager.send_event(
        task_id,
        "tool_call",
        {
            "agent_id": agent_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "status": status
        }
    )

async def send_streaming_chunk(task_id: str, taskspace_path: str, chunk: StreamChunk):
    """Send a streaming message chunk and handle persistence."""
    # Send to live stream for real-time UI updates
    await event_stream_manager.send_event(
        task_id,
        "message_chunk",
        {
            "step_id": chunk.step_id,
            "agent_name": chunk.agent_name,
            "text": chunk.text,
            "is_final": chunk.is_final,
            "token_count": chunk.token_count,
            "timestamp": chunk.timestamp.isoformat()
        }
    )
    
    # Handle persistence (accumulate chunks, persist only when complete)
    storage = chat_history_manager.get_storage(taskspace_path)
    await storage.handle_streaming_chunk(task_id, chunk)

async def send_complete_message(task_id: str, taskspace_path: str, message: Message):
    """Send a complete message and persist it."""
    # Send to live stream
    await event_stream_manager.send_event(
        task_id,
        "complete_message",
        {
            "message_id": message.id,
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.isoformat()
        }
    )
    
    # Persist immediately
    await chat_history_manager.save_message(task_id, taskspace_path, message)