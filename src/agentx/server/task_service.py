"""
Task Service Layer

Provides business logic orchestration for task management.
Handles user-task relationships while keeping the framework pure.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from ..core.task import start_task, resume_task
from ..core.xagent import XAgent
from ..utils.logger import get_logger
from .user_task_index import get_user_task_index, UserTaskIndex

logger = get_logger(__name__)


class TaskService:
    """
    Service layer for task management.
    
    This service handles:
    - User-task relationship management
    - Task access control
    - High-level task operations
    
    It does NOT handle:
    - Storage paths (framework's responsibility)
    - HTTP concerns (API layer's responsibility)
    """
    
    def __init__(self):
        self.user_index: UserTaskIndex = get_user_task_index()
    
    async def create_task(
        self, 
        user_id: str, 
        prompt: str, 
        config_path: str = "examples/simple_chat/config/team.yaml"
    ) -> Dict[str, Any]:
        """
        Create a new task for a user.
        
        Args:
            user_id: The user creating the task
            prompt: The initial task prompt
            config_path: Path to team configuration
            
        Returns:
            Task information dictionary
        """
        try:
            # Create task (framework doesn't know about user)
            task = await start_task(
                prompt=prompt,
                config_path=config_path
            )
            
            # Map user to task with config_path
            await self.user_index.add_task(user_id, task.task_id, config_path)
            
            logger.info(f"Created task {task.task_id} for user {user_id}")
            
            return {
                "task_id": task.task_id,
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create task for user {user_id}: {e}")
            raise
    
    async def get_task(self, user_id: str, task_id: str) -> XAgent:
        """
        Get a task, verifying user ownership.
        
        Args:
            user_id: The user requesting the task
            task_id: The task to retrieve
            
        Returns:
            XAgent instance
            
        Raises:
            PermissionError: If user doesn't own the task
            ValueError: If task doesn't exist
        """
        # Verify ownership
        if not await self.user_index.user_owns_task(user_id, task_id):
            logger.warning(f"User {user_id} attempted to access task {task_id} without permission")
            raise PermissionError("Access denied")
        
        # Get task info including config_path
        task_info = await self.user_index.get_task_info(task_id)
        if not task_info:
            raise ValueError(f"Task {task_id} not found in index")
        
        config_path = task_info.get('config_path', 'examples/simple_chat/config/team.yaml')
        
        # Load task with config_path
        return await resume_task(task_id, config_path)
    
    async def list_user_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all tasks for a user.
        
        Args:
            user_id: The user whose tasks to list
            
        Returns:
            List of task information dictionaries
        """
        task_ids = await self.user_index.get_user_tasks(user_id)
        tasks = []
        
        for task_id in task_ids:
            try:
                # Check if task still exists
                task_path = Path(f"task_data/{task_id}")
                if task_path.exists():
                    # Determine status from filesystem
                    status = "active"
                    if (task_path / "error.log").exists():
                        status = "failed"
                    elif any(task_path.glob("artifacts/*")):
                        status = "completed"
                    
                    tasks.append({
                        "task_id": task_id,
                        "status": status,
                        "created_at": datetime.fromtimestamp(task_path.stat().st_ctime).isoformat()
                    })
                else:
                    # Task was deleted, remove from index
                    await self.user_index.remove_task(user_id, task_id)
                    
            except Exception as e:
                logger.error(f"Error checking task {task_id}: {e}")
        
        return tasks
    
    async def delete_task(self, user_id: str, task_id: str) -> None:
        """
        Delete a task, verifying user ownership.
        
        Args:
            user_id: The user deleting the task
            task_id: The task to delete
            
        Raises:
            PermissionError: If user doesn't own the task
        """
        # Verify ownership
        if not await self.user_index.user_owns_task(user_id, task_id):
            raise PermissionError("Access denied")
        
        # Delete task directory
        import shutil
        task_path = Path(f"task_data/{task_id}")
        if task_path.exists():
            shutil.rmtree(task_path)
        
        # Remove from index
        await self.user_index.remove_task(user_id, task_id)
        
        logger.info(f"Deleted task {task_id} for user {user_id}")
    
    async def send_message(self, user_id: str, task_id: str, content: str) -> Dict[str, Any]:
        """
        Send a message to a task.
        
        Args:
            user_id: The user sending the message
            task_id: The task to send to
            content: The message content
            
        Returns:
            Response information
            
        Raises:
            PermissionError: If user doesn't own the task
        """
        # Get task with ownership check
        task = await self.get_task(user_id, task_id)
        
        # Send message
        response = await task.chat(content)
        
        return {
            "message_id": f"msg_{datetime.now().timestamp():.0f}",
            "response": response.text if hasattr(response, 'text') else str(response),
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_task_messages(self, user_id: str, task_id: str) -> List[Dict[str, Any]]:
        """
        Get messages for a task.
        
        Args:
            user_id: The user requesting messages
            task_id: The task whose messages to retrieve
            
        Returns:
            List of messages
            
        Raises:
            PermissionError: If user doesn't own the task
        """
        # Verify ownership
        if not await self.user_index.user_owns_task(user_id, task_id):
            raise PermissionError("Access denied")
        
        # Read messages from task storage
        messages_file = Path(f"task_data/{task_id}/messages.json")
        if messages_file.exists():
            import json
            with open(messages_file, 'r') as f:
                return json.load(f)
        
        return []
    
    async def get_task_artifacts(self, user_id: str, task_id: str) -> List[Dict[str, Any]]:
        """
        Get artifacts for a task.
        
        Args:
            user_id: The user requesting artifacts
            task_id: The task whose artifacts to retrieve
            
        Returns:
            List of artifact information
            
        Raises:
            PermissionError: If user doesn't own the task
        """
        # Verify ownership
        if not await self.user_index.user_owns_task(user_id, task_id):
            raise PermissionError("Access denied")
        
        artifacts = []
        task_path = Path(f"task_data/{task_id}")
        
        if task_path.exists():
            for item in task_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(task_path)
                    artifacts.append({
                        "path": str(relative_path),
                        "size": item.stat().st_size,
                        "modified_at": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
        
        return artifacts
    
    async def execute_task_step(self, user_id: str, task_id: str) -> str:
        """
        Execute a single step of a task.
        
        Args:
            user_id: The user executing the step
            task_id: The task to execute
            
        Returns:
            Step execution result
            
        Raises:
            PermissionError: If user doesn't own the task
        """
        # Get task with ownership check
        task = await self.get_task(user_id, task_id)
        
        # Execute step
        return await task.step()


# Global instance
_task_service: Optional[TaskService] = None


def get_task_service() -> TaskService:
    """Get the global task service instance"""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service