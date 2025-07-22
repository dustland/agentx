"""
AgentX Server API v2 - Clean Architecture

A thin API layer that only handles HTTP concerns.
All business logic is delegated to the service layer.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from .task_service import get_task_service
from .models import TaskRequest, TaskResponse, TaskStatus
from .streaming import event_stream_manager
from ..utils.logger import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create the FastAPI application with clean architecture."""
    app = FastAPI(
        title="AgentX API v2",
        description="Clean REST API for AgentX task execution",
        version="2.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Get service instance
    task_service = get_task_service()
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/test-sse/{task_id}")
    async def test_sse(task_id: str):
        """Test SSE endpoint to verify streaming is working"""
        from .streaming import send_message_object
        from ..core.message import Message
        
        async def generate_test_events():
            logger.info(f"[TEST-SSE] Starting test event stream for task {task_id}")
            
            # Send a test system message
            system_message = Message.system_message("This is a test SSE message")
            await send_message_object(task_id, system_message)
            
            # Wait a bit
            await asyncio.sleep(1)
            
            # Send another message
            assistant_message = Message.assistant_message("SSE is working correctly!")
            await send_message_object(task_id, assistant_message)
            
            logger.info(f"[TEST-SSE] Test events sent for task {task_id}")
        
        # Run in background
        asyncio.create_task(generate_test_events())
        
        return {"message": "Test SSE events triggered", "task_id": task_id}
    
    # ===== Task Management =====
    
    @app.post("/tasks", response_model=TaskResponse)
    async def create_task(
        request: TaskRequest,
        background_tasks: BackgroundTasks,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Create a new task."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            task_info = await task_service.create_task(
                user_id=x_user_id,
                prompt=request.task_description or "",
                config_path=request.config_path
            )
            
            # Don't automatically start background execution
            # Tasks should be explicitly started or use chat() for interactive mode
            logger.info(f"[API] Task created without automatic background execution")
            
            return TaskResponse(
                task_id=task_info["task_id"],
                status=TaskStatus.PENDING
            )
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/tasks")
    async def list_tasks(x_user_id: Optional[str] = Header(None, alias="X-User-ID")):
        """List all tasks for the authenticated user."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            tasks = await task_service.list_user_tasks(x_user_id)
            return {"tasks": tasks}
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/tasks/{task_id}")
    async def get_task(
        task_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get task information."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Just verify ownership and return basic info
            await task_service.verify_task_ownership(x_user_id, task_id)
            
            # Get task info from filesystem (service handles this)
            tasks = await task_service.list_user_tasks(x_user_id)
            task_info = next((t for t in tasks if t["task_id"] == task_id), None)
            
            if not task_info:
                raise HTTPException(status_code=404, detail="Task not found")
            
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus(task_info["status"])
            )
            
        except PermissionError:
            raise HTTPException(status_code=403, detail="Access denied")
        except ValueError:
            raise HTTPException(status_code=404, detail="Task not found")
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/tasks/{task_id}")
    async def delete_task(
        task_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Delete a task."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            await task_service.delete_task(x_user_id, task_id)
            return {"message": "Task deleted successfully"}
        except PermissionError:
            raise HTTPException(status_code=403, detail="Access denied")
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ===== Chat/Messaging =====
    
    @app.post("/tasks/{task_id}/chat")
    async def send_message(
        task_id: str,
        message: Dict[str, Any],
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Send a message to a task."""
        logger.info(f"[API] POST /tasks/{task_id}/chat - User: {x_user_id}")
        logger.info(f"[API] Message payload: {message}")
        
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            content = message.get("content", "")
            logger.info(f"[API] Extracted content: {content[:100]}...")
            
            response = await task_service.send_message(
                x_user_id,
                task_id,
                content
            )
            logger.info(f"[API] Response from task_service: {response}")
            return response
        except PermissionError:
            logger.warning(f"[API] Permission denied for user {x_user_id} on task {task_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        except ValueError:
            logger.warning(f"[API] Task {task_id} not found")
            raise HTTPException(status_code=404, detail="Task not found")
        except Exception as e:
            logger.error(f"[API] Failed to send message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/tasks/{task_id}/messages")
    async def get_messages(
        task_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get messages for a task."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            messages = await task_service.get_task_messages(x_user_id, task_id)
            return {"messages": messages}
        except PermissionError:
            raise HTTPException(status_code=403, detail="Access denied")
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return {"messages": []}  # Return empty on error for compatibility
    
    # ===== Streaming =====
    
    @app.get("/tasks/{task_id}/stream")
    async def stream_task_events(
        task_id: str,
        user_id: str,  # Required query parameter for SSE
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Stream real-time events for a task.
        
        SSE connections cannot send custom headers, so user_id is required as a query parameter.
        """
        # Use query param for SSE (header is ignored for EventSource)
        logger.info(f"[API] GET /tasks/{task_id}/stream - User: {user_id} establishing SSE connection")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Verify ownership using lightweight check
            await task_service.verify_task_ownership(user_id, task_id)
            logger.info(f"[API] SSE connection authorized for task {task_id}")
            
            # Stream events
            async def event_generator():
                logger.info(f"[API] Starting event stream for task {task_id}")
                event_count = 0
                async for event in event_stream_manager.stream_events(task_id):
                    event_count += 1
                    logger.debug(f"[API] Yielding event #{event_count} for task {task_id}: {event.get('event')}")
                    yield event
            
            return EventSourceResponse(event_generator())
            
        except PermissionError:
            logger.warning(f"[API] SSE connection denied - permission error for user {user_id} on task {task_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        except ValueError:
            logger.warning(f"[API] SSE connection denied - task {task_id} not found")
            raise HTTPException(status_code=404, detail="Task not found")
    
    # ===== Artifacts =====
    
    @app.get("/tasks/{task_id}/artifacts")
    async def get_artifacts(
        task_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get artifacts for a task."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            artifacts = await task_service.get_task_artifacts(x_user_id, task_id)
            return {"artifacts": artifacts}
        except PermissionError:
            raise HTTPException(status_code=403, detail="Access denied")
        except Exception as e:
            logger.error(f"Failed to get artifacts: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/tasks/{task_id}/artifacts/{file_path:path}")
    async def get_artifact_content(
        task_id: str,
        file_path: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get the content of a specific artifact."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Verify ownership using lightweight check
            await task_service.verify_task_ownership(x_user_id, task_id)
            
            # Read artifact directly (service could handle this too)
            from pathlib import Path
            artifact_path = Path(f"task_data/{task_id}/artifacts/{file_path}")
            
            if not artifact_path.exists():
                raise HTTPException(status_code=404, detail="Artifact not found")
            
            try:
                content = artifact_path.read_text(encoding='utf-8')
                return {
                    "path": file_path,
                    "content": content,
                    "size": artifact_path.stat().st_size
                }
            except UnicodeDecodeError:
                return {
                    "path": file_path,
                    "content": None,
                    "is_binary": True,
                    "size": artifact_path.stat().st_size
                }
                
        except PermissionError:
            raise HTTPException(status_code=403, detail="Access denied")
        except Exception as e:
            logger.error(f"Failed to get artifact: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/tasks/{task_id}/logs")
    async def get_task_logs(
        task_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
        limit: int = 100,
        offset: int = 0,
        tail: bool = False
    ):
        """Get task execution logs with efficient pagination for large files."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Verify ownership using lightweight check (doesn't create log entries)
            await task_service.verify_task_ownership(x_user_id, task_id)
            
            # Read logs from the task's log file
            from pathlib import Path
            import os
            import glob
            
            log_dir = Path(f"task_data/{task_id}/logs")
            log_file = log_dir / "task.log"
            
            # Check for rotated log files
            rotated_files = sorted(glob.glob(str(log_dir / "task.log.*")), reverse=True)
            all_log_files = [log_file] + [Path(f) for f in rotated_files if Path(f).exists()]
            
            if not any(f.exists() for f in all_log_files):
                return {"logs": [], "total": 0, "file_size": 0}
            
            # Calculate total file size including rotated files
            file_size = sum(os.path.getsize(f) for f in all_log_files if f.exists())
            
            # Always use efficient reading to avoid memory issues
            logs = []
            
            if tail:
                # Tail mode: read last N lines from the current log file
                if log_file.exists():
                    with open(log_file, 'rb') as f:
                        # Seek to end and read backwards
                        f.seek(0, 2)  # Go to end
                        file_length = f.tell()
                        
                        # Read last chunk (up to 1MB or whole file)
                        # This ensures we get enough lines without loading too much
                        chunk_size = min(1024 * 1024, file_length)
                        f.seek(max(0, file_length - chunk_size))
                        
                        # Read and decode
                        chunk = f.read().decode('utf-8', errors='ignore')
                        lines = chunk.split('\n')
                        
                        # Filter empty lines and take last 'limit' lines
                        non_empty_lines = [line.rstrip() for line in lines if line.strip()]
                        logs = non_empty_lines[-limit:] if len(non_empty_lines) > limit else non_empty_lines
                
                return {
                    "logs": logs,
                    "total": -1,  # Unknown for tail mode
                    "offset": 0,
                    "limit": limit,
                    "file_size": file_size,
                    "mode": "tail"
                }
            else:
                # Regular pagination mode: read specific chunk
                # Use a line-based approach to avoid loading entire file
                lines_read = 0
                lines_skipped = 0
                
                # Read from all log files (current + rotated)
                for log_file_path in all_log_files:
                    if not log_file_path.exists():
                        continue
                        
                    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            # Skip lines until we reach the offset
                            if lines_skipped < offset:
                                lines_skipped += 1
                                continue
                            
                            # Collect lines up to the limit
                            if lines_read < limit:
                                line = line.rstrip()
                                if line:  # Skip empty lines
                                    logs.append(line)
                                    lines_read += 1
                            else:
                                # We've collected enough lines
                                break
                    
                    # If we've collected enough lines, stop reading files
                    if lines_read >= limit:
                        break
                
                # For pagination info, we'll estimate if there are more logs
                has_more = lines_read >= limit
                
                return {
                    "logs": logs,
                    "total": -1,  # Too expensive to count all lines
                    "offset": offset,
                    "limit": limit,
                    "file_size": file_size,
                    "mode": "chunked",
                    "has_more": has_more
                }
            
        except PermissionError:
            raise HTTPException(status_code=403, detail="Access denied")
        except Exception as e:
            # Don't log errors for the logs endpoint to avoid feedback loops
            # logger.error(f"Failed to get logs: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


async def _execute_task_async(user_id: str, task_id: str):
    """Execute a task asynchronously in the background."""
    try:
        from .streaming import send_task_update, send_message_object
        
        task_service = get_task_service()
        task = await task_service.get_task(user_id, task_id)
        
        # Send task start event
        await send_task_update(
            task_id=task_id,
            status="running",
            result={"message": "Task execution started"}
        )
        
        # Execute until complete
        step_count = 0
        max_steps = 1000  # Safety limit to prevent infinite loops
        
        while not task.is_complete and step_count < max_steps:
            step_count += 1
            logger.info(f"[BACKGROUND] Executing step {step_count} for task {task_id}")
            
            result = await task.step()
            
            # Check if task is stuck without a plan
            if "No plan available" in result:
                logger.warning(f"[BACKGROUND] Task {task_id} has no plan after {step_count} steps, stopping execution")
                await send_task_update(
                    task_id=task_id,
                    status="pending",
                    result={"message": "Task requires user input to create a plan"}
                )
                break
            
            # Send step result as system message
            from ..core.message import Message
            step_message = Message.system_message(f"Step {step_count}: {result}")
            await send_message_object(task_id, step_message)
            
            # Small delay to prevent overwhelming the system
            await asyncio.sleep(0.1)
            
        if step_count >= max_steps:
            logger.error(f"[BACKGROUND] Task {task_id} exceeded maximum steps ({max_steps}), stopping execution")
            await send_task_update(
                task_id=task_id,
                status="failed",
                result={"error": "Task exceeded maximum execution steps"}
            )
            
    except ImportError:
        # Streaming not available, just execute without events
        logger.warning("Streaming not available for background task execution")
        task_service = get_task_service()
        task = await task_service.get_task(user_id, task_id)
        while not task.is_complete:
            await task.step()
    except Exception as e:
        logger.error(f"Background task execution failed: {e}")
        try:
            from .streaming import send_task_update
            await send_task_update(
                task_id=task_id,
                status="failed",
                result={"error": str(e)}
            )
        except ImportError:
            pass


# Create default app instance
app = create_app()