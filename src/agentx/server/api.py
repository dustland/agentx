"""
AgentX Server API

FastAPI-based REST API for task execution and memory management.
Provides endpoints for creating and managing tasks, and accessing task memory.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from ..utils.logger import get_logger
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import uvicorn

from ..core.xagent import XAgent
from .models import (
    TaskRequest, TaskResponse, TaskInfo, TaskStatus,
    MemoryRequest, MemoryResponse,
    HealthResponse
)

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

    return app


def add_routes(app: FastAPI):
    """Add API routes to the FastAPI application"""
    
    # Import streaming support
    from .streaming import event_stream_manager, send_agent_message, send_agent_status, send_task_update

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
        background_tasks: BackgroundTasks
    ):
        """Create and start a new task"""
        try:
            # Create the task with user_id from request
            task = create_task(request.config_path, request.user_id)
            active_tasks[task.task_id] = task

            # Start task execution in background
            background_tasks.add_task(
                _execute_task,
                task,
                request.task_description,
                request.context
            )

            return TaskResponse(
                task_id=task.task_id,
                status=TaskStatus.PENDING,
                user_id=request.user_id
            )

        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/tasks", response_model=List[TaskInfo])
    async def list_tasks(user_id: Optional[str] = None):
        """List all tasks, optionally filtered by user_id"""
        try:
            task_infos = []
            for task in active_tasks.values():
                # Filter by user_id if provided
                if user_id is not None and getattr(task, 'user_id', None) != user_id:
                    continue
                    
                # Get task info from task object
                task_infos.append(TaskInfo(
                    task_id=task.task_id,
                    status=TaskStatus.PENDING,  # Simplified for now
                    config_path=getattr(task, 'config_path', ''),
                    task_description="",
                    context=None,
                    created_at=datetime.now(),
                    completed_at=None,
                    user_id=getattr(task, 'user_id', None)
                ))
            return task_infos

        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/tasks/{task_id}", response_model=TaskResponse)
    async def get_task(task_id: str, user_id: Optional[str] = None):
        """Get task status and result"""
        try:
            task = active_tasks.get(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            
            # Check user permissions
            if user_id is not None and getattr(task, 'user_id', None) != user_id:
                raise HTTPException(status_code=404, detail="Task not found")

            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.PENDING,  # Simplified for now
                result=None,
                error=None,
                created_at=datetime.now(),
                completed_at=None,
                user_id=getattr(task, 'user_id', None)
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/tasks/{task_id}")
    async def delete_task(task_id: str):
        """Delete a task and its memory"""
        try:
            task = active_tasks.get(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            # Remove from active tasks
            del active_tasks[task_id]

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
    async def stream_task_events(task_id: str):
        """Stream real-time events for a task using SSE"""
        task = active_tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Starting event stream for task {task_id}")
        
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
            taskspace_path = Path(task.taskspace.workspace_path)
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
                    artifacts.append({
                        "path": str(relative_path),
                        "type": "file",
                        "size": item.stat().st_size,
                        "created_at": datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
                elif item.is_dir() and not any(part.startswith('.') for part in item.parts):
                    relative_path = item.relative_to(taskspace_path)
                    artifacts.append({
                        "path": str(relative_path) + "/",
                        "type": "directory"
                    })
        
        return {"artifacts": artifacts}
    
    @app.get("/tasks/{task_id}/artifacts/{file_path:path}")
    async def get_artifact_content(task_id: str, file_path: str):
        """Get the content of a specific artifact file"""
        from pathlib import Path
        
        # Construct full path safely
        taskspace_path = Path(f"taskspace/{task_id}")
        full_path = taskspace_path / file_path
        
        # Check if task exists in active tasks or if taskspace exists
        if task_id not in active_tasks and not taskspace_path.exists():
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Security: ensure path is within taskspace
        try:
            full_path = full_path.resolve()
            taskspace_path = taskspace_path.resolve()
            if not str(full_path).startswith(str(taskspace_path)):
                raise HTTPException(status_code=403, detail="Access denied")
        except Exception:
            raise HTTPException(status_code=404, detail="File not found")
        
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            content = full_path.read_text(encoding='utf-8')
            return {
                "path": file_path,
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
    
    @app.get("/tasks/{task_id}/logs")
    async def get_task_logs(task_id: str, tail: Optional[int] = None):
        """Get the execution logs for a task"""
        from pathlib import Path
        
        # Look for log file in taskspace/{task_id}/logs/{task_id}.log
        log_file = Path(f"taskspace/{task_id}/logs/{task_id}.log")
        
        if not log_file.exists():
            # Try alternative location
            log_file = Path(f"taskspace/{task_id}/logs/execution.log")
        
        logs = []
        
        if log_file.exists():
            try:
                content = log_file.read_text(encoding='utf-8')
                lines = content.splitlines()
                if tail and tail > 0:
                    lines = lines[-tail:]
                logs = lines
            except Exception as e:
                logger.error(f"Failed to read log file: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to read log file: {str(e)}")
        else:
            logger.warning(f"Log file not found at {log_file}")
        
        return {
            "task_id": task_id,
            "logs": logs,
            "total_lines": len(logs),
            "log_path": str(log_file)
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
                    streamlit run src/agentx/observability/web.py --server.port=8502
                </div>
                <p><em>Note: Using port 8502 to avoid conflicts with the API server on 8000</em></p>

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
        
        # Start the task - this creates the plan
        response = await task.start_task(task_description)
        
        # Send plan creation message
        await send_agent_message(
            task.task_id, 
            "orchestrator", 
            f"Task started: {task_description}\n\nPlan created with {len(task.plan.items)} steps.",
            {"plan": task.plan.to_dict() if hasattr(task.plan, 'to_dict') else None}
        )
        
        # Execute the task step by step
        step_count = 0
        while not task.is_complete:
            step_count += 1
            
            # Get current agent
            current_agent = task.current_agent_name if hasattr(task, 'current_agent_name') else "orchestrator"
            
            # Send agent status update
            await send_agent_status(task.task_id, current_agent, "working", min(step_count * 10, 90))
            
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
        logger.info(f"Task {task.task_id} completed successfully")

    except Exception as e:
        logger.error(f"Task {task.task_id} failed: {e}")
        await send_task_update(task.task_id, "failed", {"error": str(e)})


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
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
        logger.info("📊 Dashboard available at: http://localhost:8000/monitor")
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
