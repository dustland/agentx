"""
XAgent Service Layer

Manages XAgent instances and provides the service interface for the REST API.
XAgent is the primary interface - each instance represents exactly one project.
"""

import json
import asyncio
from typing import Dict, Optional, List, Any
from pathlib import Path
from datetime import datetime

from vibex.core.xagent import XAgent
from vibex.utils.logger import get_logger
from vibex.core.exceptions import AgentNotFoundError
from .registry import get_project_registry
from vibex.utils.paths import get_project_path
from .models import ProjectInfo, MessageInfo, ArtifactInfo, MessageResponse

logger = get_logger(__name__)

# In-memory storage for active XAgent instances.
# In a production environment, this would be replaced with a persistent store.
active_xagents: Dict[str, XAgent] = {}


class XAgentService:
    """
    Service for managing XAgent instances.
    
    XAgent is the primary interface to VibeX. Each XAgent instance represents
    exactly one project and uses the project's ID as its identifier.
    """

    def __init__(self):
        self.registry = get_project_registry()

    async def create(
        self,
        user_id: Optional[str] = None,
        goal: str = "",
        config_path: str = "",
        context: Optional[dict] = None,
    ) -> XAgent:
        """
        Creates a new XAgent instance.
        
        Returns the actual XAgent instance, not a DTO wrapper.
        The XAgent manages its own project internally.
        """
        logger.info(f"Creating XAgent{f' for user {user_id}' if user_id else ''} with goal: '{goal}'")
        
        try:
            # Use start_project function to create XAgent properly
            from vibex.core.project import start_project
            
            project = await start_project(
                goal=goal,
                config_path=config_path,
            )
            
            # Get the XAgent from the project
            xagent = project.x_agent
            
            # Store the active XAgent instance
            active_xagents[xagent.project_id] = xagent
            
            # Track user-project relationship in registry
            if user_id:
                await self.registry.add_project(user_id, xagent.project_id, config_path)
            
            logger.info(f"XAgent {xagent.project_id} created successfully.")
            return xagent
            
        except Exception as e:
            logger.error(f"Failed to create XAgent: {e}", exc_info=True)
            raise

    async def get(self, xagent_id: str) -> XAgent:
        """
        Get an XAgent instance by ID.
        
        Returns the actual XAgent instance for direct interaction.
        Uses lazy loading - if not in memory, tries to load from filesystem.
        """
        # Check if already loaded in memory
        if xagent_id in active_xagents:
            return active_xagents[xagent_id]
        
        # Try to load from filesystem (lazy loading)
        try:
            from pathlib import Path
            from vibex.core.project import resume_project
            
            # Check if project exists on filesystem
            project_path = get_project_path(xagent_id)
            if not project_path.exists():
                raise AgentNotFoundError(f"XAgent {xagent_id} not found")
            
            # Load project and get XAgent
            # Get config path from registry or use default
            project_info = await self.registry.get_project_info(xagent_id)
            config_path = project_info.config_path if project_info else "examples/simple_chat/config/team.yaml"
            if not config_path:
                config_path = "examples/simple_chat/config/team.yaml"
            
            project = await resume_project(xagent_id, config_path)
            xagent = project.x_agent
            
            # Cache it for future requests
            active_xagents[xagent_id] = xagent
            
            logger.info(f"Lazy loaded XAgent {xagent_id} from filesystem")
            return xagent
            
        except Exception as e:
            logger.error(f"Failed to lazy load XAgent {xagent_id}: {e}")
            raise AgentNotFoundError(f"XAgent {xagent_id} not found")

    async def list(self, user_id: str) -> List[ProjectInfo]:
        """
        Get all XAgent instances for a specific user.
        Returns project information including status.
        """
        project_ids = await self.registry.get_user_projects(user_id)
        projects = []
        
        for project_id in project_ids:
            try:
                # Check if project still exists on filesystem
                project_path = get_project_path(project_id)
                if project_path.exists():
                    # Determine status from filesystem
                    status = "active"
                    if (project_path / "error.log").exists():
                        status = "failed"
                    elif any(project_path.glob("artifacts/*")):
                        status = "completed"
                    
                    # Get project info from registry
                    project_info = await self.registry.get_project_info(project_id)
                    config_path = project_info.config_path if project_info else None
                    
                    projects.append(ProjectInfo(
                        project_id=project_id,
                        status=status,
                        created_at=datetime.fromtimestamp(project_path.stat().st_ctime),
                        config_path=config_path
                    ))
                else:
                    # Project was deleted, remove from registry
                    await self.registry.remove_project(user_id, project_id)
                    
            except Exception as e:
                logger.error(f"Error checking project {project_id}: {e}")
        
        return projects

    async def delete(self, xagent_id: str, user_id: Optional[str] = None) -> bool:
        """
        Delete an XAgent instance.
        """
        # Verify ownership if user_id provided
        if user_id and not await self.verify_ownership(user_id, xagent_id):
            raise PermissionError("Access denied")
        
        # Remove from memory
        if xagent_id in active_xagents:
            del active_xagents[xagent_id]
        
        # Remove from registry
        if user_id:
            await self.registry.remove_project(user_id, xagent_id)
        
        # Delete project directory
        import shutil
        project_path = get_project_path(xagent_id)
        if project_path.exists():
            shutil.rmtree(project_path)
        
        logger.info(f"XAgent {xagent_id} deleted")
        return True

    def exists(self, xagent_id: str) -> bool:
        """
        Check if an XAgent instance exists.
        """
        return xagent_id in active_xagents

    async def verify_ownership(self, user_id: str, xagent_id: str) -> bool:
        """
        Check if a user owns a specific project.
        """
        return await self.registry.user_owns_project(user_id, xagent_id)

    async def verify_access(self, user_id: str, xagent_id: str) -> bool:
        """
        Verify that a user owns a project without loading the full project.
        """
        # Check if project directory exists
        project_path = get_project_path(xagent_id)
        if not project_path.exists():
            raise ValueError(f"XAgent {xagent_id} not found")
        
        # Verify ownership
        if not await self.verify_ownership(user_id, xagent_id):
            raise PermissionError("Access denied")
        
        return True

    async def send_message(self, user_id: str, xagent_id: str, content: str, mode: str = "agent") -> MessageResponse:
        """
        Send a message to the project's X agent.
        """
        logger.info(f"[CHAT] Starting send_message for xagent {xagent_id} from user {user_id} in {mode} mode")
        logger.info(f"[CHAT] Message content: {content[:100]}...")
        
        # Get XAgent with ownership check
        logger.info(f"[CHAT] Getting XAgent for xagent_id: {xagent_id}")
        x_agent = await self.get(xagent_id)
        
        # Verify ownership
        if not await self.verify_ownership(user_id, xagent_id):
            raise PermissionError("Access denied")
        
        logger.info(f"[CHAT] X agent retrieved successfully")
        
        # Send message to X agent and get response with mode
        logger.info(f"[CHAT] Calling x_agent.chat() to process message in {mode} mode")
        response = await x_agent.chat(content, mode=mode)
        logger.info(f"[CHAT] Received response from x_agent.chat()")
        
        # Send the actual Message objects via SSE
        from .streaming import send_message_object, send_project_update
        
        if hasattr(response, 'user_message') and response.user_message:
            logger.info(f"[CHAT] Sending user Message object to SSE stream")
            await send_message_object(xagent_id, response.user_message)
            logger.info(f"[CHAT] User Message object sent successfully")
        
        if hasattr(response, 'assistant_message') and response.assistant_message:
            logger.info(f"[CHAT] Sending assistant Message object to SSE stream")
            await send_message_object(xagent_id, response.assistant_message)
            logger.info(f"[CHAT] Assistant Message object sent successfully")
        
        # Send project status update to indicate chat is complete
        await send_project_update(
            project_id=xagent_id,
            status="pending",  # Back to pending after chat response
            result={"message": "Chat response complete"}
        )
        logger.info(f"[CHAT] Project status updated to pending")
        
        result = MessageResponse(
            message_id=f"msg_{datetime.now().timestamp():.0f}",
            response=response.text if response else "",
            timestamp=datetime.now()
        )
        
        logger.info(f"[CHAT] Returning response with message_id: {result.message_id}")
        return result

    async def get_messages(self, user_id: str, xagent_id: str) -> List[MessageInfo]:
        """
        Get messages for a project.
        """
        # Verify ownership
        if not await self.verify_ownership(user_id, xagent_id):
            raise PermissionError("Access denied")
        
        # Read messages from project storage (JSONL format)
        messages_file = get_project_path(xagent_id) / "history" / "messages.jsonl"
        messages = []
        
        if messages_file.exists():
            with open(messages_file, 'r') as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        try:
                            message = json.loads(line)
                            # Convert to MessageInfo
                            messages.append(MessageInfo(
                                message_id=message.get("id", ""),
                                role=message.get("role", ""),
                                content=message.get("content", ""),
                                timestamp=datetime.fromisoformat(message.get("timestamp", datetime.now().isoformat())),
                                metadata=message.get("metadata", {}),
                                parts=message.get("parts", None)
                            ))
                        except (json.JSONDecodeError, ValueError) as e:
                            logger.warning(f"Failed to parse message line: {line}, error: {e}")
        
        return messages

    async def get_artifacts(self, user_id: str, xagent_id: str) -> List[ArtifactInfo]:
        """
        Get artifacts for a project.
        """
        # Verify ownership
        if not await self.verify_ownership(user_id, xagent_id):
            raise PermissionError("Access denied")
        
        artifacts = []
        artifacts_path = get_project_path(xagent_id) / "artifacts"
        
        if artifacts_path.exists():
            for item in artifacts_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(artifacts_path)
                    # Skip any files under .git
                    if any(part == ".git" for part in relative_path.parts):
                        continue
                    artifacts.append(ArtifactInfo(
                        path=str(relative_path),
                        size=item.stat().st_size,
                        modified_at=datetime.fromtimestamp(item.stat().st_mtime)
                    ))
        
        return artifacts


# Dependency injection
_xagent_service_instance = None

def get_xagent_service() -> XAgentService:
    global _xagent_service_instance
    if _xagent_service_instance is None:
        _xagent_service_instance = XAgentService()
    return _xagent_service_instance