"""
Project Service Layer

Provides business logic orchestration for project management.
Handles user-project relationships while keeping the framework pure.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from vibex.core.xagent import XAgent
from vibex.core.project import start_project, resume_project
from vibex.utils.logger import get_logger
from .project_registry import get_project_registry, ProjectRegistry
from .streaming import send_project_update, send_message_object
from .models import ProjectResponse, ProjectStatus

logger = get_logger(__name__)


class ProjectService:
    """
    Service layer for project management.
    
    This service handles:
    - User-project relationship management
    - Project access control
    - High-level project operations
    
    It does NOT handle:
    - Storage paths (framework's responsibility)
    - HTTP concerns (API layer's responsibility)
    """
    
    def __init__(self):
        self.registry: ProjectRegistry = get_project_registry()
        self._running_projects: set = set()  # Track currently running projects
    
    async def create_project(
        self,
        user_id: str,
        description: str,
        config_path: str = "examples/simple_chat/config/team.yaml",
        context: Optional[Dict[str, Any]] = None,
    ) -> ProjectResponse:
        """
        Create a new project for a user.
        
        Args:
            user_id: The user creating the project
            description: The initial project goal
            config_path: Path to team configuration
            context: Additional context for the project
            
        Returns:
            ProjectResponse object
        """
        try:
            # Create project (framework doesn't know about user)
            project = await start_project(
                goal=description,
                config_path=config_path
            )
            
            # Map user to project with config_path
            await self.registry.add_project(user_id, project.project_id, config_path)
            
            logger.info(f"Created project {project.project_id} for user {user_id}")
            
            return ProjectResponse(
                project_id=project.project_id,
                status=ProjectStatus.PENDING,
                user_id=user_id,
                description=description,
                config_path=config_path,
                context=context,
                created_at=datetime.now(),
            )
            
        except Exception as e:
            logger.error(f"Failed to create project for user {user_id}: {e}")
            raise
    
    async def verify_project_ownership(self, user_id: str, project_id: str) -> bool:
        """
        Verify that a user owns a project without loading the full project.
        
        This is a lightweight check that doesn't create any log entries
        or initialize the project, making it safe to use for read-only
        operations like fetching logs.
        
        Args:
            user_id: The user to check
            project_id: The project to check
            
        Returns:
            True if user owns the project
            
        Raises:
            PermissionError: If user doesn't own the project
            ValueError: If project doesn't exist
        """
        # Check if project directory exists
        project_path = Path(f".vibex/projects/{project_id}")
        if not project_path.exists():
            raise ValueError(f"Project {project_id} not found")
        
        # Verify ownership
        if not await self.registry.user_owns_project(user_id, project_id):
            # Don't log permission failures to avoid feedback loops in logs endpoint
            # logger.warning(f"User {user_id} attempted to access project {project_id} without permission")
            raise PermissionError("Access denied")
        
        return True
    
    async def get_project(self, user_id: str, project_id: str) -> XAgent:
        """
        Get the project's X agent, verifying user ownership.
        
        Args:
            user_id: The user requesting the project
            project_id: The project to retrieve
            
        Returns:
            The project's XAgent instance
            
        Raises:
            PermissionError: If user doesn't own the project
            ValueError: If project doesn't exist
        """
        # Verify ownership
        if not await self.registry.user_owns_project(user_id, project_id):
            # Don't log permission failures to avoid feedback loops in logs endpoint
            # logger.warning(f"User {user_id} attempted to access project {project_id} without permission")
            raise PermissionError("Access denied")
        
        # Get project info including config_path
        project_info = await self.registry.get_project_info(project_id)
        if not project_info:
            raise ValueError(f"Project {project_id} not found in registry")
        
        config_path = project_info.get('config_path', 'examples/simple_chat/config/team.yaml')
        
        # Load project with config_path
        project = await resume_project(project_id, config_path)
        return project.x_agent
    
    async def list_user_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all projects for a user.
        
        Args:
            user_id: The user whose projects to list
            
        Returns:
            List of project information dictionaries
        """
        project_ids = await self.registry.get_user_projects(user_id)
        projects = []
        
        for project_id in project_ids:
            try:
                # Check if task still exists
                task_path = Path(f".vibex/projects/{project_id}")
                if task_path.exists():
                    # Determine status from filesystem
                    status = "active"
                    if (task_path / "error.log").exists():
                        status = "failed"
                    elif any(task_path.glob("artifacts/*")):
                        status = "completed"
                    
                    tasks.append({
                        "project_id": project_id,
                        "status": status,
                        "created_at": datetime.fromtimestamp(task_path.stat().st_ctime).isoformat()
                    })
                else:
                    # Project was deleted, remove from registry
                    await self.registry.remove_project(user_id, project_id)
                    
            except Exception as e:
                logger.error(f"Error checking task {project_id}: {e}")
        
        return tasks
    
    async def delete_project(self, user_id: str, project_id: str) -> None:
        """
        Delete a task, verifying user ownership.
        
        Args:
            user_id: The user deleting the task
            project_id: The task to delete
            
        Raises:
            PermissionError: If user doesn't own the project
        """
        # Verify ownership
        if not await self.registry.user_owns_project(user_id, project_id):
            raise PermissionError("Access denied")
        
        # Delete project directory
        import shutil
        project_path = Path(f".vibex/projects/{project_id}")
        if project_path.exists():
            shutil.rmtree(project_path)
        
        # Remove from registry
        await self.registry.remove_project(user_id, project_id)
        
        logger.info(f"Deleted project {project_id} for user {user_id}")
    
    async def send_message(self, user_id: str, project_id: str, content: str, mode: str = "agent") -> Dict[str, Any]:
        """
        Send a message to the project's X agent.
        
        Args:
            user_id: The user sending the message
            project_id: The project to send to
            content: The message content
            
        Returns:
            Response information
            
        Raises:
            PermissionError: If user doesn't own the project
        """
        logger.info(f"[CHAT] Starting send_message for project {project_id} from user {user_id} in {mode} mode")
        logger.info(f"[CHAT] Message content: {content[:100]}...")
        
        # Get project's X agent with ownership check
        logger.info(f"[CHAT] Getting X agent for project_id: {project_id}")
        x_agent = await self.get_project(user_id, project_id)
        logger.info(f"[CHAT] X agent retrieved successfully")
        
        # Send message to X agent and get response with mode
        logger.info(f"[CHAT] Calling x_agent.chat() to process message in {mode} mode")
        response = await x_agent.chat(content, mode=mode)
        logger.info(f"[CHAT] Received response from x_agent.chat()")
        
        # Send the actual Message objects via SSE
        if hasattr(response, 'user_message') and response.user_message:
            logger.info(f"[CHAT] Sending user Message object to SSE stream")
            await send_message_object(project_id, response.user_message)
            logger.info(f"[CHAT] User Message object sent successfully")
        
        if hasattr(response, 'assistant_message') and response.assistant_message:
            logger.info(f"[CHAT] Sending assistant Message object to SSE stream")
            await send_message_object(project_id, response.assistant_message)
            logger.info(f"[CHAT] Assistant Message object sent successfully")
        
        # Send project status update to indicate chat is complete
        await send_project_update(
            project_id=project_id,
            status="pending",  # Back to pending after chat response
            result={"message": "Chat response complete"}
        )
        logger.info(f"[CHAT] Project status updated to pending")
        
        result = {
            "message_id": f"msg_{datetime.now().timestamp():.0f}",
            "response": response.text if response else "",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"[CHAT] Returning response with message_id: {result['message_id']}")
        return result
    
    async def get_project_messages(self, user_id: str, project_id: str) -> List[Dict[str, Any]]:
        """
        Get messages for a project.
        
        Args:
            user_id: The user requesting messages
            project_id: The project whose messages to retrieve
            
        Returns:
            List of messages
            
        Raises:
            PermissionError: If user doesn't own the project
        """
        # Verify ownership
        if not await self.registry.user_owns_project(user_id, project_id):
            raise PermissionError("Access denied")
        
        # Read messages from project storage (JSONL format)
        messages_file = Path(f".vibex/projects/{project_id}/history/messages.jsonl")
        messages = []
        
        if messages_file.exists():
            import json
            with open(messages_file, 'r') as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        try:
                            message = json.loads(line)
                            # Convert to API format
                            messages.append({
                                "message_id": message.get("id"),
                                "role": message.get("role"),
                                "content": message.get("content"),
                                "timestamp": message.get("timestamp"),
                                "metadata": {}
                            })
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse message line: {line}")
        
        return messages
    
    async def get_project_artifacts(self, user_id: str, project_id: str) -> List[Dict[str, Any]]:
        """
        Get artifacts for a project.
        
        Args:
            user_id: The user requesting artifacts
            project_id: The project whose artifacts to retrieve
            
        Returns:
            List of artifact information
            
        Raises:
            PermissionError: If user doesn't own the project
        """
        # Verify ownership
        if not await self.registry.user_owns_project(user_id, project_id):
            raise PermissionError("Access denied")
        
        artifacts = []
        project_path = Path(f".vibex/projects/{project_id}/artifacts")
        
        if project_path.exists():
            for item in project_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(project_path)
                    # Skip any files under .git
                    if any(part == ".git" for part in relative_path.parts):
                        continue
                    artifacts.append({
                        "path": str(relative_path),
                        "size": item.stat().st_size,
                        "modified_at": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
        
        return artifacts
    
    async def execute_project_step(self, user_id: str, project_id: str) -> str:
        """
        Execute a single step of a project.
        This is a placeholder for more complex project execution logic.
        
        Args:
            user_id (str): The ID of the user executing the project.
            project_id (str): The ID of the project.

        Returns:
            str: A message indicating the result of the execution step.
        """
        logger.info(f"Executing step for project {project_id} by user {user_id}")

        # Placeholder logic: advance the project state
        project = await self.get_project(user_id, project_id)
        if not project:
            raise PermissionError(status_code=404, detail="Project not found")

        # Simulate work being done
        await asyncio.sleep(2)  # Simulate I/O or processing delay

        # Update project status (example)
        # In a real scenario, you'd have more sophisticated state transitions
        if project.status == "pending":
            project.status = "running"
        elif project.status == "running":
            project.status = "completed"
            
        # For now, just return a confirmation
        return f"Step executed for project {project_id}. New status: {project.status}"
    
    def start_run(self, project_id: str) -> bool:
        """
        Try to start running a project.
        Returns True if run started, False if already running.
        """
        if project_id in self._running_projects:
            return False
        self._running_projects.add(project_id)
        return True
    
    def finish_run(self, project_id: str) -> None:
        """Mark project run as finished."""
        self._running_projects.discard(project_id)


# Global instance
_project_service: Optional[ProjectService] = None


def get_project_service() -> ProjectService:
    """Get the global project service instance"""
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service