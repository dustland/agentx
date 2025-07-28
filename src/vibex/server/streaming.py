"""
Streaming support for VibeX API
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime
from ..utils.logger import get_logger
from ..core.message import Message
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

async def send_task_update(project_id: str, status: str, result: Optional[Any] = None):
    """Send a task status update"""
    await event_stream_manager.send_event(
        project_id,
        "task_update",
        {
            "project_id": project_id,
            "status": status,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    )

async def send_artifact_update(project_id: str, artifact_name: str, action: str = "created", metadata: Optional[Dict[str, Any]] = None):
    """Send an artifact update event"""
    await event_stream_manager.send_event(
        project_id,
        "artifact_update",
        {
            "project_id": project_id,
            "artifact_name": artifact_name,
            "action": action,  # "created", "updated", "deleted"
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
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

async def send_message_part(project_id: str, message_id: str, part: Any):
    """Send a message part event for streaming."""
    from ..core.message import TextPart, ToolCallPart, ToolResultPart, MonologuePart, GuardrailPart
    
    # Determine part type and send appropriate event
    part_dict = part.model_dump() if hasattr(part, 'model_dump') else part
    
    await event_stream_manager.send_event(
        project_id,
        "message_part",
        {
            "message_id": message_id,
            "part": part_dict,
            "timestamp": datetime.now().isoformat()
        }
    )

async def send_tool_call_delta(project_id: str, tool_call_id: str, args_delta: str):
    """Send a tool call delta for streaming partial arguments."""
    await event_stream_manager.send_event(
        project_id,
        "tool_call_delta",
        {
            "tool_call_id": tool_call_id,
            "args_delta": args_delta,
            "timestamp": datetime.now().isoformat()
        }
    )