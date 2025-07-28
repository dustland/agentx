"""
VibeX Server API v2 - Clean Architecture

A thin API layer that only handles HTTP concerns.
All business logic is delegated to XAgent instances.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import importlib.metadata
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from .service import XAgentService, get_xagent_service
from .models import CreateXAgentRequest, XAgentResponse, TaskStatus, XAgentListResponse, ChatRequest
from .streaming import event_stream_manager
from ..utils.logger import get_logger
# Authentication temporarily disabled
# from .auth import get_user_id
from ..core.exceptions import AgentNotFoundError
from ..utils.paths import get_project_path

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create the FastAPI application with clean architecture."""
    app = FastAPI(
        title="VibeX API v2",
        description="Clean REST API for VibeX agent execution",
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
    xagent_service = get_xagent_service()
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        # Get agent count for health info
        active_agents = len(await xagent_service.list("_health_check"))
        
        # Get version from package metadata
        try:
            version = importlib.metadata.version("vibex")
        except Exception:
            version = "unknown"
        
        return {
            "status": "healthy",
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "service_type": "vibex-agent-orchestration",
            "service_name": "VibeX API",
            "active_agents": active_agents,
            "api_endpoints": [
                "/xagents", 
                "/xagents/{xagent_id}", 
                "/xagents/{xagent_id}/messages",
                "/xagents/{xagent_id}/artifacts",
                "/xagents/{xagent_id}/artifacts/{artifact_path}",
                "/xagents/{xagent_id}/logs",
                "/xagents/{xagent_id}/stream",
                "/chat",
                "/health", 
                "/monitor"
            ]
        }
    
    async def _xagent_to_response(xagent, user_id: str) -> XAgentResponse:
        """Convert XAgent instance to XAgentResponse DTO for API serialization."""
        # Ensure plan is loaded before creating response
        await xagent._ensure_plan_initialized()
        
        # Determine status from task states in the plan
        status = TaskStatus.PENDING
        if xagent.plan and xagent.plan.tasks:
            # Check task statuses
            has_failed = any(t.status == "failed" for t in xagent.plan.tasks)
            has_running = any(t.status == "running" for t in xagent.plan.tasks)
            all_completed = all(t.status == "completed" for t in xagent.plan.tasks)
            
            if has_failed:
                status = TaskStatus.FAILED
            elif all_completed:
                status = TaskStatus.COMPLETED
            elif has_running:
                status = TaskStatus.RUNNING
            else:
                status = TaskStatus.PENDING
        
        goal_value = xagent.initial_prompt or ""
        logger.debug(f"[_xagent_to_response] XAgent {xagent.project_id} - initial_prompt: '{xagent.initial_prompt}', goal: '{goal_value}'")
        
        return XAgentResponse(
            xagent_id=xagent.project_id,
            user_id=user_id,
            status=status,
            created_at=datetime.now(),  # TODO: Get actual creation time from XAgent
            updated_at=datetime.now(),  # TODO: Get actual update time from XAgent
            goal=goal_value,
            name=getattr(xagent, 'name', f"Project {xagent.project_id}"),
            config_path=getattr(xagent, 'config_path', None),
            plan=xagent.plan.model_dump() if xagent.plan else None,
        )
    
    @app.get("/test-sse/{xagent_id}")
    async def test_sse(xagent_id: str):
        """Test SSE endpoint to verify streaming is working"""
        from .streaming import send_message_object
        from ..core.message import Message
        
        async def generate_test_events():
            logger.info(f"[TEST-SSE] Starting test event stream for xagent {xagent_id}")
            
            # Send a test system message
            system_message = Message.system_message("This is a test SSE message")
            await send_message_object(xagent_id, system_message)
            
            # Wait a bit
            await asyncio.sleep(1)
            
            # Send another message
            assistant_message = Message.assistant_message("SSE is working correctly!")
            await send_message_object(xagent_id, assistant_message)
            
            logger.info(f"[TEST-SSE] Test events sent for xagent {xagent_id}")
        
        # Run in background
        asyncio.create_task(generate_test_events())
        
        return {"message": "Test SSE events triggered", "xagent_id": xagent_id}
    
    # ===== Agent Management =====
    
    @app.post("/xagents", response_model=XAgentResponse)
    async def create_agent_run(
        request: CreateXAgentRequest,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
        xagent_service: XAgentService = Depends(get_xagent_service),
    ):
        """
        Creates a new XAgent instance.
        Returns a DTO representation for API compatibility.
        """
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
            
        logger.info(f"[/xagents] Received request to create XAgent for user: {x_user_id}")
        logger.info(f"[/xagents] Goal: '{request.goal}'")
        logger.debug(f"Request details: {request}")

        try:
            # Create XAgent instance
            xagent = await xagent_service.create(
                user_id=x_user_id,
                goal=request.goal,
                config_path=request.config_path,
                context=request.context,
            )

            # Convert to DTO for API response
            return await _xagent_to_response(xagent, x_user_id)
            
        except Exception as e:
            logger.error(f"Failed to create XAgent: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/xagents", response_model=XAgentListResponse)
    async def list_agent_runs(x_user_id: Optional[str] = Header(None, alias="X-User-ID")):
        """List all XAgent instances for the authenticated user."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Get list of ProjectInfo objects
            project_infos = await xagent_service.list(x_user_id)
            runs = []
            
            # For each project, load the XAgent and convert to response
            for project_info in project_infos:
                try:
                    # Load the actual XAgent instance
                    xagent = await xagent_service.get(project_info.project_id)
                    response = await _xagent_to_response(xagent, x_user_id)
                    runs.append(response)
                except Exception as e:
                    logger.warning(f"Failed to load XAgent {project_info.project_id}: {e}")
                    # Create minimal response for failed loads
                    runs.append(XAgentResponse(
                        xagent_id=project_info.project_id,
                        goal="",
                        status=project_info.status,
                        name=f"Project {project_info.project_id}",
                        created_at=project_info.created_at,
                        plan=None,
                        artifacts=[]
                    ))
            
            return XAgentListResponse(xagents=runs)
        except Exception as e:
            logger.error(f"Failed to list XAgents: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/xagents/{xagent_id}", response_model=XAgentResponse)
    async def get_agent_run(
        xagent_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get XAgent information."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            xagent = await xagent_service.get(xagent_id)
            return await _xagent_to_response(xagent, x_user_id)
            
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            logger.error(f"Failed to get XAgent: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/xagents/{xagent_id}")
    async def delete_agent_run(
        xagent_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Delete an XAgent instance."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            deleted = await xagent_service.delete(xagent_id)
            if deleted:
                return {"message": "XAgent deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            logger.error(f"Failed to delete XAgent: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ===== Chat/Messaging =====
    
    @app.post("/chat")
    async def chat_with_agent(
        request: ChatRequest,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Chat with an XAgent."""
        logger.info(f"[API] POST /chat - User: {x_user_id}, XAgent: {request.xagent_id}")
        logger.info(f"[API] Chat request: {request}")
        
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Get XAgent instance and chat directly
            xagent = await xagent_service.get(request.xagent_id)
            response = await xagent.chat(request.content, mode=request.mode)
            
            logger.info(f"[API] Response from XAgent: {response.text[:100]}...")
            return {"response": response.text}
            
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            logger.error(f"[API] Failed to send message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/xagents/{xagent_id}/messages")
    async def get_messages(
        xagent_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get messages for an XAgent."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Use service method which returns typed MessageInfo objects
            messages = await xagent_service.get_messages(x_user_id, xagent_id)
            # Serialize to dicts for API response
            return {"messages": [msg.model_dump() for msg in messages]}
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            # Don't log errors for read-only operations to avoid feedback loops
            return {"messages": []}  # Return empty on error for compatibility
    
    # ===== Agent Resources =====
    
    @app.get("/xagents/{xagent_id}/artifacts")
    async def list_agent_artifacts(
        xagent_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """List all artifacts for an XAgent."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            artifacts = await xagent_service.get_artifacts(x_user_id, xagent_id)
            # Convert ArtifactInfo to dict for JSON response
            return {
                "artifacts": [
                    {
                        "path": artifact.path,
                        "size": artifact.size,
                        "modified_at": artifact.modified_at.isoformat(),
                        "type": "file"  # All items from get_artifacts are files
                    }
                    for artifact in artifacts
                ]
            }
        except PermissionError:
            raise HTTPException(status_code=403, detail="Access denied")
        except Exception as e:
            logger.error(f"Failed to list artifacts for {xagent_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/xagents/{xagent_id}/artifacts/{artifact_path:path}")
    async def get_agent_artifact(
        xagent_id: str,
        artifact_path: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get artifact directly from filesystem to avoid logging feedback loops."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Access artifact directly from filesystem
            artifact_file = get_project_path(xagent_id) / "artifacts" / artifact_path
            
            if not artifact_file.exists():
                raise HTTPException(status_code=404, detail="Artifact not found")
            
            # Read artifact content
            if artifact_file.is_file():
                try:
                    with open(artifact_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Handle binary files
                    with open(artifact_file, 'rb') as f:
                        content = f.read().decode('utf-8', errors='replace')
                
                return {"artifact_path": artifact_path, "content": content}
            else:
                raise HTTPException(status_code=404, detail="Artifact path is not a file")
                
        except HTTPException:
            raise  # Re-raise HTTP exceptions as-is
        except Exception as e:
            # Don't log errors for read-only operations to avoid feedback loops
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/xagents/{xagent_id}/logs")
    async def get_agent_logs(
        xagent_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get logs directly from filesystem to avoid logging feedback loops."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Access logs directly from filesystem
            log_file = get_project_path(xagent_id) / "logs" / "project.log"
            
            if not log_file.exists():
                return {"logs": []}  # Return empty if no logs yet
            
            # Read log content as raw lines (frontend expects strings for .match())
            logs = []
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    if line:  # Skip empty lines
                        logs.append(line)
            
            return {"logs": logs}
                
        except Exception as e:
            # Don't log errors for read-only operations to avoid feedback loops
            return {"logs": []}  # Return empty on error for compatibility
    


    # ===== Streaming =====
    
    @app.get("/xagents/{xagent_id}/stream")
    async def stream_agent_events(
        xagent_id: str,
        user_id: str,  # Required query parameter for SSE
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Stream real-time events for an XAgent."""
        logger.info(f"[API] GET /xagents/{xagent_id}/stream - User: {user_id} establishing SSE connection")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Verify XAgent exists
            await xagent_service.get(xagent_id)
            logger.info(f"[API] SSE connection authorized for xagent {xagent_id}")
            
            # Stream events
            async def event_generator():
                logger.info(f"[API] Starting event stream for xagent {xagent_id}")
                event_count = 0
                async for event in event_stream_manager.stream_events(xagent_id):
                    event_count += 1
                    logger.debug(f"[API] Yielding event #{event_count} for xagent {xagent_id}: {event.get('event')}")
                    yield event
            
            return EventSourceResponse(event_generator())
            
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            logger.warning(f"[API] SSE connection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


# Create default app instance
app = create_app()