"""
AgentX Server API v2 - Clean Architecture

A thin API layer that only handles HTTP concerns.
All business logic is delegated to the service layer.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

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
            
            # If there's a prompt, start execution in background
            if request.task_description:
                background_tasks.add_task(
                    _execute_task_async,
                    x_user_id,
                    task_info["task_id"]
                )
            
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
            await task_service.get_task(x_user_id, task_id)
            
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
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            response = await task_service.send_message(
                x_user_id,
                task_id,
                message.get("content", "")
            )
            return response
        except PermissionError:
            raise HTTPException(status_code=403, detail="Access denied")
        except ValueError:
            raise HTTPException(status_code=404, detail="Task not found")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
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
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Stream real-time events for a task."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Verify ownership
            await task_service.get_task(x_user_id, task_id)
            
            # Stream events
            async def event_generator():
                async for event in event_stream_manager.stream_events(task_id):
                    yield event
            
            return EventSourceResponse(event_generator())
            
        except PermissionError:
            raise HTTPException(status_code=403, detail="Access denied")
        except ValueError:
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
            # Verify ownership first
            await task_service.get_task(x_user_id, task_id)
            
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
        limit: int = 1000,
        offset: int = 0
    ):
        """Get task execution logs."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Verify ownership first
            await task_service.get_task(x_user_id, task_id)
            
            # Read logs from the task's log file
            from pathlib import Path
            log_file = Path(f"task_data/{task_id}/logs/{task_id}.log")
            
            if not log_file.exists():
                return {"logs": [], "total": 0}
            
            # Read all lines
            with open(log_file, 'r', encoding='utf-8') as f:
                all_logs = f.readlines()
            
            # Apply pagination
            total = len(all_logs)
            logs = all_logs[offset:offset + limit]
            
            return {
                "logs": [log.rstrip() for log in logs],
                "total": total,
                "offset": offset,
                "limit": limit
            }
            
        except PermissionError:
            raise HTTPException(status_code=403, detail="Access denied")
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


async def _execute_task_async(user_id: str, task_id: str):
    """Execute a task asynchronously in the background."""
    try:
        task_service = get_task_service()
        task = await task_service.get_task(user_id, task_id)
        
        # Execute until complete
        while not task.is_complete:
            await task.step()
            
    except Exception as e:
        logger.error(f"Background task execution failed: {e}")


# Create default app instance
app = create_app()