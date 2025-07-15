"""
AgentX Server API

FastAPI-based REST API for task execution and memory management.
Provides endpoints for creating and managing tasks, and accessing task memory.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from ..utils.logger import get_logger
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import uvicorn

from ..core.xagent import XAgent
from ..core.message import TaskHistory
from .models import (
    TaskRequest, TaskResponse, TaskInfo, TaskStatus,
    MemoryRequest, MemoryResponse,
    HealthResponse
)
from ..core.session import get_task_session_store, initialize_task_session_store

logger = get_logger(__name__)

# In-memory task storage (in production, use a proper database)
active_tasks: Dict[str, XAgent] = {}
server_start_time = datetime.now()


def create_task(config_path: str, user_id: str = None) -> XAgent:
    """Create a new XAgent task instance."""
    from ..config.team_loader import load_team_config
    
    # Load the team configuration from the path
    team_config = load_team_config(config_path)
    
    # Create XAgent with the loaded config and user_id
    return XAgent(team_config=team_config, user_id=user_id)


def create_app(
    title: str = "AgentX API",
    description: str = "REST API for AgentX task execution and memory management",
    version: str = "0.4.0",
    enable_cors: bool = True
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        title: API title
        description: API description
        version: API version
        enable_cors: Whether to enable CORS middleware

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title=title,
        description=description,
        version=version
    )

    # Add CORS middleware if enabled
    if enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add routes
    add_routes(app)
    
    # Add startup event to initialize coordinator
    @app.on_event("startup")
    async def startup_event():
        await initialize_task_session_store()
    
    # Add shutdown event to cleanup coordinator
    @app.on_event("shutdown")
    async def shutdown_event():
        store = get_task_session_store()
        await store.disconnect()

    return app


def add_routes(app: FastAPI):
    """Add API routes to the FastAPI application"""
    
    # Import streaming support
    from .streaming import event_stream_manager, send_agent_message, send_agent_status, send_task_update
    from ..storage.chat_history import chat_history_manager

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        return HealthResponse(
            status="healthy",
            active_tasks=len(active_tasks),
            service_name="AgentX API",
            service_type="agentx-task-orchestration",
            version="0.4.0"
        )

    @app.post("/tasks", response_model=TaskResponse)
    async def create_task_endpoint(
        request: TaskRequest,
        background_tasks: BackgroundTasks,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Create and start a new task"""
        try:
            # Use user_id from header if provided, otherwise from request body
            user_id = x_user_id or request.user_id
            # Create the task with user_id
            task = create_task(request.config_path, user_id)
            active_tasks[task.task_id] = task
            
            # Store task status in Redis for cross-worker coordination
            store = get_task_session_store()
            status = TaskStatus.RUNNING if request.task_description else TaskStatus.PENDING
            
            await store.set_task_status(
                task_id=task.task_id,
                status=status,
                user_id=user_id,
                metadata={
                    "config_path": request.config_path,
                    "task_description": request.task_description,
                    "context": request.context
                }
            )

            # Only start task execution if there's a task description
            if request.task_description and request.task_description.strip():
                background_tasks.add_task(
                    _execute_task,
                    task,
                    request.task_description,
                    request.context
                )

            return TaskResponse(
                task_id=task.task_id,
                status=status,
                user_id=user_id
            )

        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/tasks", response_model=List[TaskInfo])
    async def list_tasks(user_id: Optional[str] = None):
        """List all tasks, optionally filtered by user_id"""
        try:
            # Get tasks from Redis coordination system
            store = get_task_session_store()
            redis_tasks = await coordinator.list_tasks(user_id)
            
            task_infos = []
            seen_task_ids = set()
            
            # Add tasks from Redis
            for task_data in redis_tasks:
                task_infos.append(TaskInfo(
                    task_id=task_data["task_id"],
                    status=TaskStatus(task_data["status"]),
                    config_path=task_data.get("metadata", {}).get("config_path", ""),
                    task_description=task_data.get("metadata", {}).get("task_description", ""),
                    context=task_data.get("metadata", {}).get("context"),
                    created_at=datetime.fromisoformat(task_data["created_at"]) if task_data["created_at"] else datetime.now(),
                    completed_at=None,
                    user_id=task_data.get("user_id")
                ))
                seen_task_ids.add(task_data["task_id"])
            
            # Add any active tasks from memory that might not be in Redis yet
            for task in active_tasks.values():
                # Filter by user_id if provided
                if user_id is not None and getattr(task, 'user_id', None) != user_id:
                    continue
                
                if task.task_id not in seen_task_ids:
                    task_infos.append(TaskInfo(
                        task_id=task.task_id,
                        status=TaskStatus.RUNNING,  # Active tasks are running
                        config_path=getattr(task, 'config_path', ''),
                        task_description="",
                        context=None,
                        created_at=datetime.now(),
                        completed_at=None,
                        user_id=getattr(task, 'user_id', None)
                    ))
                    seen_task_ids.add(task.task_id)
            
            # Then scan filesystem for all tasks
            taskspace_root = Path("taskspace")
            if taskspace_root.exists():
                for item in taskspace_root.iterdir():
                    if not item.is_dir() or item.name.startswith("."):
                        continue
                    
                    # Check if this is a user directory or task directory
                    if user_id and item.name == user_id:
                        # User-scoped directory
                        for task_dir in item.iterdir():
                            if task_dir.is_dir() and not task_dir.name.startswith("."):
                                task_id = task_dir.name
                                if task_id not in seen_task_ids:
                                    # Determine status from filesystem
                                    status = TaskStatus.COMPLETED
                                    if (task_dir / "error.log").exists():
                                        status = TaskStatus.FAILED
                                    elif not any(task_dir.glob("artifacts/*")):
                                        status = TaskStatus.PENDING
                                    
                                    task_infos.append(TaskInfo(
                                        task_id=task_id,
                                        status=status,
                                        config_path="",
                                        task_description="",
                                        context=None,
                                        created_at=datetime.fromtimestamp(task_dir.stat().st_ctime),
                                        completed_at=None,
                                        user_id=user_id
                                    ))
                    elif not user_id:
                        # Legacy task directory (no user scoping)
                        task_id = item.name
                        if task_id not in seen_task_ids and len(task_id) == 8:  # Typical task ID length
                            # Determine status from filesystem
                            status = TaskStatus.COMPLETED
                            if (item / "error.log").exists():
                                status = TaskStatus.FAILED
                            elif not any(item.glob("artifacts/*")):
                                status = TaskStatus.PENDING
                            
                            task_infos.append(TaskInfo(
                                task_id=task_id,
                                status=status,
                                config_path="",
                                task_description="",
                                context=None,
                                created_at=datetime.fromtimestamp(item.stat().st_ctime),
                                completed_at=None,
                                user_id=None
                            ))
            
            return task_infos

        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/tasks/{task_id}", response_model=TaskResponse)
    async def get_task(task_id: str, user_id: Optional[str] = None):
        """Get task status and result"""
        try:
            # First check Redis for task status
            store = get_task_session_store()
            task_data = await coordinator.get_task_status(task_id, user_id)
            
            if task_data:
                # Task found in Redis
                return TaskResponse(
                    task_id=task_id,
                    status=TaskStatus(task_data["status"]),
                    result=task_data.get("metadata", {}).get("result"),
                    error=task_data.get("metadata", {}).get("error"),
                    created_at=datetime.fromisoformat(task_data["created_at"]) if task_data["created_at"] else datetime.now(),
                    completed_at=None,
                    user_id=task_data.get("user_id")
                )
            
            # Check if task exists in active memory
            task = active_tasks.get(task_id)
            if task:
                # Check user permissions
                if user_id is not None and getattr(task, 'user_id', None) != user_id:
                    raise HTTPException(status_code=404, detail="Task not found")

                return TaskResponse(
                    task_id=task_id,
                    status=TaskStatus.RUNNING,  # Active tasks are running
                    result=None,
                    error=None,
                    created_at=datetime.now(),
                    completed_at=None,
                    user_id=getattr(task, 'user_id', None)
                )
            
            # Fallback: Check filesystem directly
            
            # Fallback: Check if task exists in taskspace directory
            taskspace_path = None
            if user_id:
                taskspace_path = Path(f"taskspace/{user_id}/{task_id}")
            else:
                taskspace_path = Path(f"taskspace/{task_id}")
            
            if not taskspace_path.exists():
                # Try legacy path if user-scoped path doesn't exist
                if user_id:
                    legacy_path = Path(f"taskspace/{task_id}")
                    if legacy_path.exists():
                        taskspace_path = legacy_path
                    else:
                        raise HTTPException(status_code=404, detail="Task not found")
                else:
                    raise HTTPException(status_code=404, detail="Task not found")
            
            # Determine task status from filesystem
            status = TaskStatus.COMPLETED
            if (taskspace_path / "error.log").exists():
                status = TaskStatus.FAILED
            elif not any(taskspace_path.glob("artifacts/*")):
                # Check if task has logs to determine if it's running
                logs_path = taskspace_path / "logs"
                if logs_path.exists() and any(logs_path.glob("*.log")):
                    status = TaskStatus.RUNNING
                else:
                    status = TaskStatus.PENDING
            
            return TaskResponse(
                task_id=task_id,
                status=status,
                result=None,
                error=None,
                created_at=datetime.now(),
                completed_at=None,
                user_id=user_id
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/tasks/{task_id}")
    async def delete_task(task_id: str, user_id: Optional[str] = None):
        """Delete a task and its memory"""
        try:
            store = get_task_session_store()
            
            # Check if task exists in active tasks
            task = active_tasks.get(task_id)
            if task:
                # Check user permissions
                if user_id is not None and getattr(task, 'user_id', None) != user_id:
                    raise HTTPException(status_code=404, detail="Task not found")
                
                # Remove from active tasks
                del active_tasks[task_id]
            
            # Delete from Redis coordination system
            success = await coordinator.delete_task(task_id, user_id)
            if not success:
                raise HTTPException(status_code=404, detail="Task not found")

            return {"message": "Task deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/tasks/{task_id}/memory", response_model=MemoryResponse)
    async def add_memory(task_id: str, request: MemoryRequest):
        """Add content to task memory"""
        try:
            task = active_tasks.get(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            if not request.content:
                raise HTTPException(status_code=400, detail="Content is required")

            # For now, just return success - memory integration can be added later
            return MemoryResponse(
                task_id=task_id,
                agent_id=request.agent_id,
                success=True
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to add memory to task {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/tasks/{task_id}/memory", response_model=MemoryResponse)
    async def search_memory(task_id: str, query: Optional[str] = None, agent_id: Optional[str] = None):
        """Search task memory"""
        try:
            task = active_tasks.get(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            # For now, return empty results - memory integration can be added later
            return MemoryResponse(
                task_id=task_id,
                agent_id=agent_id,
                success=True,
                data=[]
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to search memory for task {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/tasks/{task_id}/memory")
    async def clear_memory(task_id: str, agent_id: Optional[str] = None):
        """Clear task memory"""
        try:
            task = active_tasks.get(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            # For now, just return success - memory integration can be added later
            return {"message": "Memory cleared successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to clear memory for task {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/tasks/{task_id}/stream")
    async def stream_task_events(task_id: str, user_id: Optional[str] = None):
        """Stream real-time events for a task using SSE"""
        task = active_tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check user permissions
        if user_id is not None and getattr(task, 'user_id', None) != user_id:
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Starting event stream for task {task_id} (user: {user_id})")
        
        async def event_generator():
            async for event in event_stream_manager.stream_events(task_id):
                yield event
        
        return EventSourceResponse(event_generator())
    
    @app.get("/tasks/{task_id}/agents")
    async def get_task_agents(task_id: str):
        """Get the list of agents for a task"""
        task = active_tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Return agent information
        agents = []
        if hasattr(task, 'specialist_agents'):
            for agent_id, agent in task.specialist_agents.items():
                agents.append({
                    "id": agent_id,
                    "name": getattr(agent, 'name', agent_id),
                    "role": getattr(agent.config, 'role', 'Agent'),
                    "status": "idle",
                    "progress": 0
                })
        
        return {"agents": agents}
    
    @app.get("/tasks/{task_id}/artifacts")
    async def get_task_artifacts(task_id: str, user_id: Optional[str] = None):
        """Get the list of artifacts (files) in the task taskspace"""
        import os
        from pathlib import Path
        
        # Check if task exists in active tasks and get user permissions
        task = active_tasks.get(task_id)
        if task:
            # Task is active - check user permissions
            if user_id is not None and getattr(task, 'user_id', None) != user_id:
                raise HTTPException(status_code=404, detail="Task not found")
            # Use the task's actual taskspace path
            taskspace_path = Path(task.taskspace.taskspace_path)
        else:
            # Task not active - check if taskspace exists
            # Try both user-scoped and legacy paths
            if user_id:
                taskspace_path = Path(f"taskspace/{user_id}/{task_id}")
            else:
                taskspace_path = Path(f"taskspace/{task_id}")
            
            if not taskspace_path.exists():
                # Try legacy path if user-scoped path doesn't exist
                if user_id:
                    legacy_path = Path(f"taskspace/{task_id}")
                    if legacy_path.exists():
                        taskspace_path = legacy_path
                    else:
                        raise HTTPException(status_code=404, detail="Task not found")
                else:
                    raise HTTPException(status_code=404, detail="Task not found")
        
        artifacts = []
        
        if taskspace_path.exists():
            for item in taskspace_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(taskspace_path)
                    # For artifacts API, return paths that can be used directly
                    path_str = str(relative_path)
                    
                    # Categorize files by their location
                    if path_str.startswith('artifacts/'):
                        # Artifact files - return path without artifacts/ prefix for clean API
                        clean_path = path_str.removeprefix('artifacts/')
                        artifacts.append({
                            "path": clean_path,
                            "type": "file",
                            "category": "artifact",
                            "size": item.stat().st_size,
                            "created_at": datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                            "modified_at": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        })
                    elif path_str.startswith('logs/'):
                        # Log files - keep logs/ prefix to distinguish from artifacts
                        artifacts.append({
                            "path": path_str,
                            "type": "file",
                            "category": "log",
                            "size": item.stat().st_size,
                            "created_at": datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                            "modified_at": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        })
                    else:
                        # Other files (plan.json, etc.) - return full path
                        artifacts.append({
                            "path": path_str,
                            "type": "file",
                            "category": "meta",
                            "size": item.stat().st_size,
                            "created_at": datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                            "modified_at": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        })
                elif item.is_dir() and not any(part.startswith('.') for part in item.parts):
                    relative_path = item.relative_to(taskspace_path)
                    path_str = str(relative_path)
                    # For directories, always show full path structure
                    artifacts.append({
                        "path": path_str + "/",
                        "type": "directory"
                    })
        
        return {"artifacts": artifacts}
    
    @app.get("/tasks/{task_id}/artifacts/{file_path:path}")
    async def get_artifact_content(task_id: str, file_path: str, user_id: Optional[str] = None):
        """Get the content of a specific artifact file"""
        from pathlib import Path
        
        # Check if task exists in active tasks and get user permissions
        task = active_tasks.get(task_id)
        if task:
            # Task is active - check user permissions and use task's actual taskspace path
            if user_id is not None and getattr(task, 'user_id', None) != user_id:
                raise HTTPException(status_code=404, detail="Task not found")
            taskspace_path = Path(task.taskspace.taskspace_path)
        else:
            # Task not active - check if taskspace exists
            # Try both user-scoped and legacy paths
            if user_id:
                taskspace_path = Path(f"taskspace/{user_id}/{task_id}")
            else:
                taskspace_path = Path(f"taskspace/{task_id}")
            
            if not taskspace_path.exists():
                # Try legacy path if user-scoped path doesn't exist
                if user_id:
                    legacy_path = Path(f"taskspace/{task_id}")
                    if legacy_path.exists():
                        taskspace_path = legacy_path
                    else:
                        raise HTTPException(status_code=404, detail="Task not found")
                else:
                    raise HTTPException(status_code=404, detail="Task not found")
        
        # Handle different path types:
        # 1. If file_path starts with 'artifacts/', use it as-is (backward compatibility)
        # 2. If file_path starts with 'logs/', use it as-is (logs are at same level as artifacts)
        # 3. Otherwise, scope it to the artifacts directory
        if file_path.startswith(('artifacts/', 'logs/')):
            full_path = taskspace_path / file_path
        else:
            full_path = taskspace_path / "artifacts" / file_path
        
        
        # Security: ensure path is within taskspace
        try:
            full_path = full_path.resolve()
            taskspace_path = taskspace_path.resolve()
            if not str(full_path).startswith(str(taskspace_path)):
                raise HTTPException(status_code=403, detail="Access denied")
        except Exception as e:
            logger.error(f"Path resolution failed for {file_path}: {e}")
            logger.error(f"Taskspace path: {taskspace_path}")
            logger.error(f"Full path attempted: {full_path}")
            raise HTTPException(status_code=404, detail="File not found")
        
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            content = full_path.read_text(encoding='utf-8')
            # Return appropriate path based on file type:
            # - For artifacts: strip artifacts/ prefix for clean API
            # - For logs: keep logs/ prefix to distinguish from artifacts
            # - For others: keep as-is
            if file_path.startswith('artifacts/'):
                clean_path = file_path.removeprefix('artifacts/')
            else:
                clean_path = file_path
                
            return {
                "path": clean_path,
                "content": content,
                "size": full_path.stat().st_size
            }
        except UnicodeDecodeError:
            # Binary file
            return {
                "path": file_path,
                "content": None,
                "is_binary": True,
                "size": full_path.stat().st_size
            }
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise HTTPException(status_code=500, detail="Failed to read file")
    
    @app.get("/tasks/{task_id}/chat")
    async def get_chat_history(task_id: str, user_id: Optional[str] = None):
        """Get the chat history for a task"""
        # Check if task exists in active tasks and get user permissions
        task = active_tasks.get(task_id)
        if task:
            # Task is active - check user permissions and use task's actual taskspace path
            if user_id is not None and getattr(task, 'user_id', None) != user_id:
                raise HTTPException(status_code=404, detail="Task not found")
            taskspace_path = task.taskspace.taskspace_path
        else:
            # Task not active - check if taskspace exists
            # Try both user-scoped and legacy paths
            if user_id:
                taskspace_path = f"taskspace/{user_id}/{task_id}"
            else:
                taskspace_path = f"taskspace/{task_id}"
            
            if not Path(taskspace_path).exists():
                # Try legacy path if user-scoped path doesn't exist
                if user_id:
                    legacy_path = f"taskspace/{task_id}"
                    if Path(legacy_path).exists():
                        taskspace_path = legacy_path
                    else:
                        raise HTTPException(status_code=404, detail="Task not found")
                else:
                    raise HTTPException(status_code=404, detail="Task not found")
        
        try:
            # Load chat history from persistent storage
            history = await chat_history_manager.load_history(task_id, taskspace_path)
            
            # Get any active streaming messages
            storage = chat_history_manager.get_storage(taskspace_path)
            active_streaming = storage.get_active_streaming_messages(task_id)
            
            # Convert to API format
            messages = []
            for msg in history.messages:
                message_data = {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "parts": [part.model_dump() for part in msg.parts],
                    "timestamp": msg.timestamp.isoformat(),
                    "type": "complete"
                }
                
                # Add agent name if this is from a TaskStep (assistant message with step_id format)
                if msg.role == "assistant" and msg.id.startswith("step_"):
                    # Extract agent name from parts if available
                    for part in msg.parts:
                        if hasattr(part, 'agent_name'):
                            message_data["agent_name"] = part.agent_name
                            break
                
                messages.append(message_data)
            
            # Steps are now stored as messages, so no need to convert them separately
            
            # Sort messages by timestamp
            messages.sort(key=lambda x: x["timestamp"])
            
            return {
                "task_id": task_id,
                "messages": messages,
                "total_messages": len(messages),
                "active_streaming": active_streaming,
                "last_updated": history.updated_at.isoformat() if history.messages or history.steps else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get chat history for task {task_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve chat history")
    
    @app.post("/tasks/{task_id}/chat")
    async def send_chat_message(
        task_id: str, 
        message_data: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Send a new message to a task's chat"""
        # Check if task exists and is active
        task = active_tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found or not active")
        
        # Check user permissions
        if user_id is not None and getattr(task, 'user_id', None) != user_id:
            raise HTTPException(status_code=404, detail="Task not found")
        
        try:
            from ..core.message import Message
            
            # Create user message
            user_message = Message.user_message(
                content=message_data.get("content", "")
            )
            
            # Add to task's history and persist
            task.history.add_message(user_message)
            await chat_history_manager.save_message(
                task_id, 
                task.taskspace.taskspace_path, 
                user_message
            )
            
            # Send to streaming for real-time updates
            from .streaming import send_complete_message
            await send_complete_message(
                task_id,
                task.taskspace.taskspace_path,
                user_message
            )
            
            return {
                "message_id": user_message.id,
                "status": "sent",
                "timestamp": user_message.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send chat message for task {task_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to send message")
    
    @app.delete("/tasks/{task_id}/chat")
    async def clear_chat_history(task_id: str, user_id: Optional[str] = None):
        """Clear the chat history for a task"""
        # Check if task exists in active tasks and get user permissions
        task = active_tasks.get(task_id)
        if task:
            # Task is active - check user permissions
            if user_id is not None and getattr(task, 'user_id', None) != user_id:
                raise HTTPException(status_code=404, detail="Task not found")
            taskspace_path = task.taskspace.taskspace_path
            # Also clear in-memory history
            task.history = TaskHistory(task_id=task_id)
        else:
            # Task not active - check if taskspace exists
            if user_id:
                taskspace_path = f"taskspace/{user_id}/{task_id}"
            else:
                taskspace_path = f"taskspace/{task_id}"
            
            if not Path(taskspace_path).exists():
                # Try legacy path
                if user_id:
                    legacy_path = f"taskspace/{task_id}"
                    if Path(legacy_path).exists():
                        taskspace_path = legacy_path
                    else:
                        raise HTTPException(status_code=404, detail="Task not found")
                else:
                    raise HTTPException(status_code=404, detail="Task not found")
        
        try:
            # Clear persistent storage
            storage = chat_history_manager.get_storage(taskspace_path)
            await storage.clear_history(task_id)
            
            return {"message": "Chat history cleared successfully"}
            
        except Exception as e:
            logger.error(f"Failed to clear chat history for task {task_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to clear chat history")

    @app.get("/tasks/{task_id}/logs")
    async def get_task_logs(task_id: str, tail: Optional[int] = None, user_id: Optional[str] = None):
        """Get the execution logs for a task"""
        from pathlib import Path
        
        # Check if task exists in active tasks and get user permissions
        task = active_tasks.get(task_id)
        if task:
            # Task is active - check user permissions
            if user_id is not None and getattr(task, 'user_id', None) != user_id:
                raise HTTPException(status_code=404, detail="Task not found")
            # Use the task's actual taskspace path
            taskspace_path = Path(task.taskspace.taskspace_path)
        else:
            # Task not active - check if taskspace exists
            # Try both user-scoped and legacy paths
            if user_id:
                taskspace_path = Path(f"taskspace/{user_id}/{task_id}")
            else:
                taskspace_path = Path(f"taskspace/{task_id}")
            
            if not taskspace_path.exists():
                # Try legacy path if user-scoped path doesn't exist
                if user_id:
                    legacy_path = Path(f"taskspace/{task_id}")
                    if legacy_path.exists():
                        taskspace_path = legacy_path
                    else:
                        raise HTTPException(status_code=404, detail="Task not found")
                else:
                    raise HTTPException(status_code=404, detail="Task not found")
        
        # Look for log files in the taskspace logs directory
        logs_dir = taskspace_path / "logs"
        log_files = []
        
        if logs_dir.exists():
            # Try multiple log file patterns
            potential_files = [
                logs_dir / f"{task_id}.log",
                logs_dir / "execution.log",
                logs_dir / "task.log"
            ]
            
            for log_file in potential_files:
                if log_file.exists():
                    log_files.append(log_file)
        
        logs = []
        
        if log_files:
            try:
                # Read all log files and combine them
                all_lines = []
                for log_file in log_files:
                    content = log_file.read_text(encoding='utf-8')
                    lines = content.splitlines()
                    # Add file identifier for multiple files
                    if len(log_files) > 1:
                        all_lines.append(f"=== {log_file.name} ===")
                    all_lines.extend(lines)
                
                if tail and tail > 0:
                    all_lines = all_lines[-tail:]
                logs = all_lines
            except Exception as e:
                logger.error(f"Failed to read log files: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to read log files: {str(e)}")
        else:
            logger.warning(f"No log files found in {logs_dir}")
        
        return {
            "task_id": task_id,
            "logs": logs,
            "total_lines": len(logs),
            "log_files": [str(f) for f in log_files]
        }

    # Simple observability route
    @app.get("/monitor", response_class=HTMLResponse)
    async def monitor_dashboard():
        """Serve observability dashboard info"""
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AgentX Observability</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .info { background: #f0f8ff; padding: 20px; border-radius: 8px; }
                .code { background: #f5f5f5; padding: 10px; border-radius: 4px; font-family: monospace; }
            </style>
        </head>
        <body>
            <h1>🤖 AgentX Observability</h1>
            <div class="info">
                <h2>Integrated Mode Active</h2>
                <p>The observability system is running in integrated mode with full features:</p>
                <ul>
                    <li>✅ Real-time event capture</li>
                    <li>✅ Task conversation history</li>
                    <li>✅ Memory inspection</li>
                    <li>✅ Dashboard metrics</li>
                </ul>

                <h3>Access the Dashboard</h3>
                <p>To access the full Streamlit dashboard, run:</p>
                <div class="code">
                                          streamlit run src/agentx/observability/web.py --server.port=7772
                </div>
                <p><em>Note: Using port 7772 to avoid conflicts with the API server on 7770</em></p>

                <h3>API Endpoints</h3>
                <ul>
                    <li><a href="/docs">📚 API Documentation</a></li>
                    <li><a href="/tasks">📋 Tasks API</a></li>
                    <li><a href="/health">❤️ Health Check</a></li>
                </ul>
            </div>
        </body>
        </html>
        """)


async def _execute_task(task: XAgent, task_description: str, context: Optional[Dict[str, Any]] = None):
    """Execute a task in the background with real streaming"""
    from .streaming import send_agent_message, send_agent_status, send_task_update, send_tool_call
    
    try:
        logger.info(f"Starting task execution {task.task_id}: {task_description}")
        
        # Send initial task update
        await send_task_update(task.task_id, "running")
        
        # Update status in coordination system to running
        coordinator = get_task_coordinator()
        await coordinator.set_task_status(
            task_id=task.task_id,
            status=TaskStatus.RUNNING,
            user_id=getattr(task, 'user_id', None),
            metadata={
                "task_description": task_description,
                "context": context
            }
        )
        
        # Start the task - this creates the plan
        response = await task.start(task_description)
        
        # Send plan creation message
        await send_agent_message(
            task.task_id, 
            "orchestrator", 
            f"Task started: {task_description}\n\nPlan created with {len(task.plan.tasks)} steps.",
            {"plan": task.plan.model_dump() if hasattr(task.plan, 'model_dump') else None}
        )
        
        # Execute the task step by step
        step_count = 0
        while not task.is_complete:
            step_count += 1
            
            # Get current agent
            current_agent = task.current_agent_name if hasattr(task, 'current_agent_name') else "orchestrator"
            
            # Send agent status update
            await send_agent_status(task.task_id, current_agent, "working", min(step_count * 10, 90))
            
            # Update task progress in coordination system
            await store.update_task_progress(
                task.task_id, 
                f"Step {step_count}: {current_agent}", 
                min(step_count * 10, 90)
            )
            
            # Execute next step
            try:
                step_response = await task.step()
                
                # Check if the response contains tool calls
                tool_calls = []
                if hasattr(step_response, 'messages'):
                    for msg in step_response.messages:
                        if hasattr(msg, 'tool_calls'):
                            for tool_call in msg.tool_calls:
                                # Send tool call event
                                await send_tool_call(
                                    task.task_id,
                                    current_agent,
                                    tool_call.name,
                                    tool_call.parameters,
                                    None,  # Result will be sent later
                                    "pending"
                                )
                                tool_calls.append({
                                    "name": tool_call.name,
                                    "parameters": tool_call.parameters
                                })
                
                # Stream the response
                if hasattr(step_response, 'text'):
                    metadata = {"step": step_count}
                    if tool_calls:
                        metadata["tool_calls"] = tool_calls
                    
                    await send_agent_message(
                        task.task_id,
                        current_agent,
                        step_response.text,
                        metadata
                    )
                    
            except Exception as step_error:
                logger.error(f"Step {step_count} failed: {step_error}")
                await send_agent_message(
                    task.task_id,
                    current_agent,
                    f"Error in step {step_count}: {str(step_error)}",
                    {"error": True}
                )
                
            # Update agent status
            await send_agent_status(task.task_id, current_agent, "completed", 100)
            
            # Small delay to avoid overwhelming
            await asyncio.sleep(0.5)
        
        # Task completed
        await send_task_update(task.task_id, "completed", {"steps_executed": step_count})
        
        # Update status in coordination system
        await coordinator.set_task_status(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            user_id=getattr(task, 'user_id', None),
            metadata={"steps_executed": step_count}
        )
        
        logger.info(f"Task {task.task_id} completed successfully")

    except Exception as e:
        logger.error(f"Task {task.task_id} failed: {e}")
        await send_task_update(task.task_id, "failed", {"error": str(e)})
        
        # Update status in coordination system
        coordinator = get_task_coordinator()
        await coordinator.set_task_status(
            task_id=task.task_id,
            status=TaskStatus.FAILED,
            user_id=getattr(task, 'user_id', None),
            metadata={"error": str(e)}
        )


def run_server(
    host: str = "0.0.0.0",
    port: int = 7770,
    reload: bool = False,
    log_level: str = "info"
):
    """
    Run the AgentX server with integrated observability.

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
        log_level: Logging level
    """
    app = create_app()

    # Initialize observability monitor in integrated mode
    try:
        from ..observability.monitor import get_monitor
        monitor = get_monitor()
        monitor.start()
        logger.info("✅ Observability monitor started in integrated mode")
        logger.info("📊 Dashboard available at: http://localhost:7770/monitor")
    except Exception as e:
        logger.warning(f"⚠️  Could not start observability monitor: {e}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )


# Create default app instance for imports
app = create_app()
