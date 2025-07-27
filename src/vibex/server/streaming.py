"""
Streaming support for VibeX API
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime
from ..utils.logger import get_logger
from ..core.message import Message, StreamChunk
from ..storage.chat_history import chat_history_manager

logger = get_logger(__name__)

class ProjectEventStream:
    """Manages event streams for projects"""
    
    def __init__(self):
        self.streams: Dict[str, asyncio.Queue] = {}
        
    def create_stream(self, project_id: str) -> asyncio.Queue:
        """Create a new event stream for a project"""
        if project_id not in self.streams:
            self.streams[project_id] = asyncio.Queue()
        return self.streams[project_id]
        
    def get_stream(self, project_id: str) -> Optional[asyncio.Queue]:
        """Get existing stream for a project"""
        return self.streams.get(project_id)
        
    async def send_event(self, project_id: str, event_type: str, data: Any):
        """Send an event to all listeners of a project"""
        stream = self.get_stream(project_id)
        if stream:
            event = {
                "id": str(datetime.now().timestamp()),
                "event": event_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            await stream.put(event)
            logger.debug(f"[SSE] Sent {event_type} event for project {project_id} to stream (queue size: {stream.qsize()})")
            logger.debug(f"[SSE] Event data: {data}")
        else:
            logger.warning(f"[SSE] No stream found for project {project_id}, creating one")
            self.create_stream(project_id)
            await self.send_event(project_id, event_type, data)
            
    async def stream_events(self, project_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream events for a project as dictionaries for EventSourceResponse"""
        logger.info(f"[SSE] Starting event stream for task {project_id}")
        stream = self.create_stream(project_id)
        
        # Check if there are already events in the queue
        logger.info(f"[SSE] Stream created/retrieved for task {project_id}, current queue size: {stream.qsize()}")
        
        try:
            while True:
                logger.debug(f"[SSE] Waiting for events on task {project_id} (queue size: {stream.qsize()})")
                
                # Add a small timeout to check queue periodically
                try:
                    event = await asyncio.wait_for(stream.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    # Check queue size on timeout
                    logger.debug(f"[SSE] Timeout waiting for events, queue size: {stream.qsize()}")
                    continue
                
                logger.debug(f"[SSE] Streaming event for task {project_id}: type={event['event']}, id={event['id']}")
                logger.debug(f"[SSE] Event content: {event['data']}")
                
                # Yield the event as a dictionary
                # EventSourceResponse needs data as JSON string for proper formatting
                yield {
                    "id": event['id'],
                    "event": event['event'],
                    "data": json.dumps(event['data'])  # JSON encode the data
                }
                
        except asyncio.CancelledError:
            logger.info(f"[SSE] Stream cancelled for task {project_id}")
            raise
        finally:
            # Clean up stream
            if project_id in self.streams:
                del self.streams[project_id]
                logger.info(f"[SSE] Cleaned up stream for task {project_id}")
                
    def close_stream(self, project_id: str):
        """Close and remove a stream"""
        if project_id in self.streams:
            del self.streams[project_id]

# Global event stream manager
event_stream_manager = ProjectEventStream()

# send_agent_message removed - use send_message_object instead for consistency

async def send_agent_status(project_id: str, xagent_id: str, status: str, progress: int = 0):
    """Send an agent status update"""
    await event_stream_manager.send_event(
        project_id,
        "agent_status",
        {
            "xagent_id": xagent_id,
            "status": status,
            "progress": progress
        }
    )

async def send_project_update(project_id: str, status: str, result: Optional[Any] = None):
    """Send a project status update"""
    await event_stream_manager.send_event(
        project_id,
        "project_update",
        {
            "project_id": project_id,
            "status": status,
            "result": result
        }
    )


async def send_tool_call(project_id: str, xagent_id: str, tool_name: str, parameters: Dict, result: Optional[Any] = None, status: str = "pending"):
    """Send a tool call event"""
    await event_stream_manager.send_event(
        project_id,
        "tool_call",
        {
            "xagent_id": xagent_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "status": status
        }
    )

async def send_streaming_chunk(project_id: str, taskspace_path: str, chunk: StreamChunk):
    """Send a streaming message chunk and handle persistence."""
    # Send to live stream for real-time UI updates
    await event_stream_manager.send_event(
        project_id,
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
    await storage.handle_streaming_chunk(project_id, chunk)

async def send_complete_message(project_id: str, taskspace_path: str, message: Message):
    """Send a complete message and persist it."""
    # Send to live stream
    await event_stream_manager.send_event(
        project_id,
        "complete_message",
        {
            "message_id": message.id,
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.isoformat()
        }
    )
    
    # Persist immediately
    await chat_history_manager.save_message(project_id, taskspace_path, message)

async def send_message_object(project_id: str, message: Message):
    """Send a Message object directly via SSE without persistence (already handled in core)."""
    # Convert Message to dict for SSE transmission
    message_dict = {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "parts": [part.model_dump() for part in message.parts],
        "timestamp": message.timestamp.isoformat(),
        "metadata": getattr(message, 'metadata', {})
    }
    
    await event_stream_manager.send_event(
        project_id,
        "message",  # New event type for complete message objects
        message_dict
    )

async def send_stream_chunk(project_id: str, chunk: str, message_id: str, is_final: bool = False, error: Optional[str] = None):
    """Send a streaming text chunk for real-time UI updates."""
    chunk_data = {
        "message_id": message_id,
        "chunk": chunk,
        "is_final": is_final,
        "timestamp": datetime.now().isoformat()
    }
    
    if error:
        chunk_data["error"] = error
    
    await event_stream_manager.send_event(
        project_id,
        "stream_chunk",
        chunk_data
    )

async def send_tool_call_start(project_id: str, tool_call_id: str, tool_name: str, args: Dict[str, Any]):
    """Send a tool call start event for streaming."""
    await event_stream_manager.send_event(
        project_id,
        "tool_call_start",
        {
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "args": args,
            "timestamp": datetime.now().isoformat()
        }
    )

async def send_tool_call_result(project_id: str, tool_call_id: str, tool_name: str, result: Any, is_error: bool = False):
    """Send a tool call result event for streaming."""
    await event_stream_manager.send_event(
        project_id,
        "tool_call_result",
        {
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "result": result,
            "is_error": is_error,
            "timestamp": datetime.now().isoformat()
        }
    )