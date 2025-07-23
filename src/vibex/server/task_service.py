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
from .streaming import send_task_update, send_complete_message, send_message_object

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
    
    async def verify_task_ownership(self, user_id: str, task_id: str) -> bool:
        """
        Verify that a user owns a task without loading the full task.
        
        This is a lightweight check that doesn't create any log entries
        or initialize the task, making it safe to use for read-only
        operations like fetching logs.
        
        Args:
            user_id: The user to check
            task_id: The task to check
            
        Returns:
            True if user owns the task
            
        Raises:
            PermissionError: If user doesn't own the task
            ValueError: If task doesn't exist
        """
        # Check if task directory exists
        task_path = Path(f".vibex/tasks/{task_id}")
        if not task_path.exists():
            raise ValueError(f"Task {task_id} not found")
        
        # Verify ownership
        if not await self.user_index.user_owns_task(user_id, task_id):
            # Don't log permission failures to avoid feedback loops in logs endpoint
            # logger.warning(f"User {user_id} attempted to access task {task_id} without permission")
            raise PermissionError("Access denied")
        
        return True
    
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
            # Don't log permission failures to avoid feedback loops in logs endpoint
            # logger.warning(f"User {user_id} attempted to access task {task_id} without permission")
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
                task_path = Path(f".vibex/tasks/{task_id}")
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
        task_path = Path(f".vibex/tasks/{task_id}")
        if task_path.exists():
            shutil.rmtree(task_path)
        
        # Remove from index
        await self.user_index.remove_task(user_id, task_id)
        
        logger.info(f"Deleted task {task_id} for user {user_id}")
    
    async def send_message(self, user_id: str, task_id: str, content: str, mode: str = "agent") -> Dict[str, Any]:
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
        logger.info(f"[CHAT] Starting send_message for task {task_id} from user {user_id} in {mode} mode")
        logger.info(f"[CHAT] Message content: {content[:100]}...")
        
        # Get task with ownership check
        logger.info(f"[CHAT] Getting task instance for task_id: {task_id}")
        task = await self.get_task(user_id, task_id)
        logger.info(f"[CHAT] Task instance retrieved successfully")
        
        # Send message and get response with mode
        logger.info(f"[CHAT] Calling task.chat() to process message in {mode} mode")
        response = await task.chat(content, mode=mode)
        logger.info(f"[CHAT] Received response from task.chat()")
        
        # Send the actual Message objects via SSE
        if hasattr(response, 'user_message') and response.user_message:
            logger.info(f"[CHAT] Sending user Message object to SSE stream")
            await send_message_object(task_id, response.user_message)
            logger.info(f"[CHAT] User Message object sent successfully")
        
        if hasattr(response, 'assistant_message') and response.assistant_message:
            logger.info(f"[CHAT] Sending assistant Message object to SSE stream")
            await send_message_object(task_id, response.assistant_message)
            logger.info(f"[CHAT] Assistant Message object sent successfully")
        
        # Send task status update to indicate chat is complete
        await send_task_update(
            task_id=task_id,
            status="pending",  # Back to pending after chat response
            result={"message": "Chat response complete"}
        )
        logger.info(f"[CHAT] Task status updated to pending")
        
        result = {
            "message_id": f"msg_{datetime.now().timestamp():.0f}",
            "response": response.text if response else "",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"[CHAT] Returning response with message_id: {result['message_id']}")
        return result
    
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
        
        # Read messages from task storage (JSONL format)
        messages_file = Path(f".vibex/tasks/{task_id}/history/messages.jsonl")
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
        task_path = Path(f".vibex/tasks/{task_id}/artifacts")
        
        if task_path.exists():
            for item in task_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(task_path)
                    # Skip any files under .git
                    if any(part == ".git" for part in relative_path.parts):
                        continue
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