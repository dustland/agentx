"""
VibeX Server API v2 - Clean Architecture

A thin API layer that only handles HTTP concerns.
All business logic is delegated to XAgent instances.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from .xagent_service import XAgentService, get_xagent_service
from .models import CreateXAgentRequest, XAgentResponse, TaskStatus, XAgentListResponse
from .streaming import event_stream_manager
from ..utils.logger import get_logger
# Authentication temporarily disabled
# from .auth import get_user_id
from ..core.exceptions import AgentNotFoundError

# Temporary stub for authentication
async def get_user_id() -> str:
    """Temporary stub that returns a default user ID."""
    return "default-user"

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
        active_agents = len(await xagent_service.list_for_user("_health_check"))
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "service_type": "vibex-agent-orchestration",
            "service_name": "VibeX API",
            "active_agents": active_agents,
            "api_endpoints": [
                "/agents", 
                "/agents/{agent_id}", 
                "/agents/{agent_id}/messages",
                "/agents/{agent_id}/artifacts/{artifact_path}",
                "/agents/{agent_id}/logs",
                "/agents/{agent_id}/plan",
                "/agents/{agent_id}/stream",
                "/chat",
                "/health", 
                "/monitor"
            ]
        }
    
    def _xagent_to_response(xagent, user_id: str) -> XAgentResponse:
        """Convert XAgent instance to XAgentResponse DTO for API serialization."""
        return XAgentResponse(
            agent_id=xagent.project_id,
            status=TaskStatus.COMPLETED if xagent.is_complete() else TaskStatus.RUNNING,
            user_id=user_id,
            created_at=datetime.now(),  # TODO: Get actual creation time from XAgent
            goal=xagent.initial_prompt or "",
            config_path=getattr(xagent, 'config_path', None),
            plan=xagent.plan.model_dump() if xagent.plan else None,
        )
    
    @app.get("/test-sse/{agent_id}")
    async def test_sse(agent_id: str):
        """Test SSE endpoint to verify streaming is working"""
        from .streaming import send_message_object
        from ..core.message import Message
        
        async def generate_test_events():
            logger.info(f"[TEST-SSE] Starting test event stream for agent {agent_id}")
            
            # Send a test system message
            system_message = Message.system_message("This is a test SSE message")
            await send_message_object(agent_id, system_message)
            
            # Wait a bit
            await asyncio.sleep(1)
            
            # Send another message
            assistant_message = Message.assistant_message("SSE is working correctly!")
            await send_message_object(agent_id, assistant_message)
            
            logger.info(f"[TEST-SSE] Test events sent for agent {agent_id}")
        
        # Run in background
        asyncio.create_task(generate_test_events())
        
        return {"message": "Test SSE events triggered", "agent_id": agent_id}
    
    # ===== Agent Management =====
    
    @app.post("/agents", response_model=XAgentResponse)
    async def create_agent_run(
        request: CreateXAgentRequest,
        user_id: str = Depends(get_user_id),
        xagent_service: XAgentService = Depends(get_xagent_service),
    ):
        """
        Creates a new XAgent instance.
        Returns a DTO representation for API compatibility.
        """
        logger.info(f"[/agents] Received request to create XAgent for user: {user_id}")
        logger.debug(f"Request details: {request}")

        try:
            # Create XAgent instance
            xagent = await xagent_service.create(
                user_id=user_id,
                goal=request.goal,
                config_path=request.config_path,
                context=request.context,
            )

            # Convert to DTO for API response
            return _xagent_to_response(xagent, user_id)
            
        except Exception as e:
            logger.error(f"Failed to create XAgent: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/agents", response_model=XAgentListResponse)
    async def list_agent_runs(x_user_id: Optional[str] = Header(None, alias="X-User-ID")):
        """List all XAgent instances for the authenticated user."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            xagents = await xagent_service.list_for_user(x_user_id)
            runs = [_xagent_to_response(xagent, x_user_id) for xagent in xagents]
            return XAgentListResponse(runs=runs)
        except Exception as e:
            logger.error(f"Failed to list XAgents: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/agents/{agent_id}", response_model=XAgentResponse)
    async def get_agent_run(
        agent_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get XAgent information."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            xagent = await xagent_service.get(agent_id)
            return _xagent_to_response(xagent, x_user_id)
            
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            logger.error(f"Failed to get XAgent: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/agents/{agent_id}")
    async def delete_agent_run(
        agent_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Delete an XAgent instance."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            deleted = await xagent_service.delete(agent_id)
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
        request: Dict[str, Any],
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Chat with an XAgent."""
        agent_id = request.get("agent_id")
        if not agent_id:
            raise HTTPException(status_code=400, detail="agent_id is required")
            
        logger.info(f"[API] POST /chat - User: {x_user_id}, Agent: {agent_id}")
        logger.info(f"[API] Chat request: {request}")
        
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            content = request.get("content", "")
            mode = request.get("mode", "agent")  # Default to agent mode
            
            # Get XAgent instance and chat directly
            xagent = await xagent_service.get(agent_id)
            response = await xagent.chat(content, mode=mode)
            
            logger.info(f"[API] Response from XAgent: {response.text[:100]}...")
            return {"response": response.text}
            
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            logger.error(f"[API] Failed to send message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/agents/{agent_id}/messages")
    async def get_messages(
        agent_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get messages for an XAgent."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            xagent = await xagent_service.get(agent_id)
            messages = [msg.model_dump() for msg in xagent.conversation_history]
            return {"messages": messages}
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return {"messages": []}  # Return empty on error for compatibility
    
    # ===== Agent Resources =====
    
    @app.get("/agents/{agent_id}/artifacts/{artifact_path:path}")
    async def get_agent_artifact(
        agent_id: str,
        artifact_path: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get artifact from XAgent's project storage."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            xagent = await xagent_service.get(agent_id)
            
            # Access artifact through XAgent's project storage
            if hasattr(xagent, 'project_storage') and xagent.project_storage:
                artifact_content = await xagent.project_storage.get_artifact(artifact_path)
                if artifact_content is None:
                    raise HTTPException(status_code=404, detail="Artifact not found")
                return {"artifact_path": artifact_path, "content": artifact_content}
            else:
                raise HTTPException(status_code=404, detail="No project storage available")
                
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            logger.error(f"Failed to get artifact: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/agents/{agent_id}/logs")
    async def get_agent_logs(
        agent_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get logs from XAgent."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            xagent = await xagent_service.get(agent_id)
            
            # Access logs through XAgent
            if hasattr(xagent, 'get_logs'):
                logs = await xagent.get_logs()
                return {"logs": logs}
            elif hasattr(xagent, 'project_storage') and xagent.project_storage:
                # Fallback to project storage logs
                logs = await xagent.project_storage.get_logs()
                return {"logs": logs}
            else:
                return {"logs": []}
                
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return {"logs": []}  # Return empty on error for compatibility
    
    @app.get("/agents/{agent_id}/plan")
    async def get_agent_plan(
        agent_id: str,
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Get plan from XAgent."""
        if not x_user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            xagent = await xagent_service.get(agent_id)
            
            # Access plan directly from XAgent
            if xagent.plan:
                return {"plan": xagent.plan.model_dump()}
            else:
                return {"plan": None}
                
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="XAgent not found")
        except Exception as e:
            logger.error(f"Failed to get plan: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ===== Streaming =====
    
    @app.get("/agents/{agent_id}/stream")
    async def stream_agent_events(
        agent_id: str,
        user_id: str,  # Required query parameter for SSE
        x_user_id: Optional[str] = Header(None, alias="X-User-ID")
    ):
        """Stream real-time events for an XAgent."""
        logger.info(f"[API] GET /agents/{agent_id}/stream - User: {user_id} establishing SSE connection")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID required")
        
        try:
            # Verify XAgent exists
            await xagent_service.get(agent_id)
            logger.info(f"[API] SSE connection authorized for agent {agent_id}")
            
            # Stream events
            async def event_generator():
                logger.info(f"[API] Starting event stream for agent {agent_id}")
                event_count = 0
                async for event in event_stream_manager.stream_events(agent_id):
                    event_count += 1
                    logger.debug(f"[API] Yielding event #{event_count} for agent {agent_id}: {event.get('event')}")
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