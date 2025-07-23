"""
User-Task Index Management

Manages the mapping between users and their tasks.
This keeps the framework layer pure and user-agnostic.
"""

import json
import asyncio
from pathlib import Path
from typing import List, Optional, Set, TYPE_CHECKING
from datetime import datetime
import aiofiles
from ..utils.logger import get_logger

if TYPE_CHECKING:
    from redis.asyncio import Redis

# Optional Redis support
try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    redis = None
    HAS_REDIS = False

logger = get_logger(__name__)


class UserTaskIndex:
    """Abstract base class for user-task indexing"""
    
    async def add_task(self, user_id: str, task_id: str, config_path: Optional[str] = None) -> None:
        """Add a task to a user's index"""
        raise NotImplementedError
    
    async def remove_task(self, user_id: str, task_id: str) -> None:
        """Remove a task from a user's index"""
        raise NotImplementedError
    
    async def get_user_tasks(self, user_id: str) -> List[str]:
        """Get all task IDs for a user"""
        raise NotImplementedError
    
    async def user_owns_task(self, user_id: str, task_id: str) -> bool:
        """Check if a user owns a specific task"""
        raise NotImplementedError
    
    async def get_task_owner(self, task_id: str) -> Optional[str]:
        """Get the owner of a task"""
        raise NotImplementedError
    
    async def get_task_info(self, task_id: str) -> Optional[dict]:
        """Get task information including config_path"""
        raise NotImplementedError


class FileUserTaskIndex(UserTaskIndex):
    """File-based implementation of user-task index"""
    
    def __init__(self, base_path: Path = Path("./.vibex/users")):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
    
    def _get_user_file(self, user_id: str) -> Path:
        """Get the index file path for a user"""
        return self.base_path / f"{user_id}.json"
    
    def _get_task_index_file(self) -> Path:
        """Get the reverse index file (task -> user mapping)"""
        return self.base_path / "_task_index.json"
    
    async def _read_user_data(self, user_id: str) -> dict:
        """Read user data from file"""
        user_file = self._get_user_file(user_id)
        if not user_file.exists():
            return {"user_id": user_id, "tasks": [], "created_at": datetime.now().isoformat()}
        
        try:
            async with aiofiles.open(user_file, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to read user data for {user_id}: {e}")
            return {"user_id": user_id, "tasks": [], "created_at": datetime.now().isoformat()}
    
    async def _write_user_data(self, user_id: str, data: dict) -> None:
        """Write user data to file"""
        user_file = self._get_user_file(user_id)
        data["updated_at"] = datetime.now().isoformat()
        
        try:
            async with aiofiles.open(user_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Failed to write user data for {user_id}: {e}")
            raise
    
    async def _update_task_index(self, task_id: str, user_id: Optional[str], config_path: Optional[str] = None) -> None:
        """Update the reverse task index"""
        index_file = self._get_task_index_file()
        
        try:
            if index_file.exists():
                async with aiofiles.open(index_file, 'r') as f:
                    content = await f.read()
                    index = json.loads(content)
            else:
                index = {}
            
            if user_id:
                index[task_id] = {
                    "user_id": user_id, 
                    "created_at": datetime.now().isoformat(),
                    "config_path": config_path
                }
            else:
                index.pop(task_id, None)
            
            async with aiofiles.open(index_file, 'w') as f:
                await f.write(json.dumps(index, indent=2))
        except Exception as e:
            logger.error(f"Failed to update task index: {e}")
    
    async def add_task(self, user_id: str, task_id: str, config_path: Optional[str] = None) -> None:
        """Add a task to a user's index"""
        async with self._lock:
            data = await self._read_user_data(user_id)
            
            if task_id not in data["tasks"]:
                data["tasks"].append(task_id)
                await self._write_user_data(user_id, data)
                await self._update_task_index(task_id, user_id, config_path)
                logger.info(f"Added task {task_id} to user {user_id}")
    
    async def remove_task(self, user_id: str, task_id: str) -> None:
        """Remove a task from a user's index"""
        async with self._lock:
            data = await self._read_user_data(user_id)
            
            if task_id in data["tasks"]:
                data["tasks"].remove(task_id)
                await self._write_user_data(user_id, data)
                await self._update_task_index(task_id, None)
                logger.info(f"Removed task {task_id} from user {user_id}")
    
    async def get_user_tasks(self, user_id: str) -> List[str]:
        """Get all task IDs for a user"""
        data = await self._read_user_data(user_id)
        return data.get("tasks", [])
    
    async def user_owns_task(self, user_id: str, task_id: str) -> bool:
        """Check if a user owns a specific task"""
        tasks = await self.get_user_tasks(user_id)
        return task_id in tasks
    
    async def get_task_owner(self, task_id: str) -> Optional[str]:
        """Get the owner of a task from reverse index"""
        index_file = self._get_task_index_file()
        
        if not index_file.exists():
            return None
        
        try:
            async with aiofiles.open(index_file, 'r') as f:
                content = await f.read()
                index = json.loads(content)
                task_data = index.get(task_id)
                return task_data["user_id"] if task_data else None
        except Exception as e:
            logger.error(f"Failed to get task owner: {e}")
            return None
    
    async def get_task_info(self, task_id: str) -> Optional[dict]:
        """Get task information including config_path"""
        index_file = self._get_task_index_file()
        
        if not index_file.exists():
            return None
        
        try:
            async with aiofiles.open(index_file, 'r') as f:
                content = await f.read()
                index = json.loads(content)
                return index.get(task_id)
        except Exception as e:
            logger.error(f"Failed to get task info: {e}")
            return None


class RedisUserTaskIndex(UserTaskIndex):
    """Redis-based implementation of user-task index"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional['Redis'] = None
    
    async def _get_redis(self) -> 'Redis':
        """Get or create Redis connection"""
        if not self._redis:
            if not HAS_REDIS:
                raise ImportError("Redis is not installed. Install it with: pip install redis[asyncio]")
            self._redis = await redis.from_url(self.redis_url)  # type: ignore
        return self._redis
    
    async def add_task(self, user_id: str, task_id: str, config_path: Optional[str] = None) -> None:
        """Add a task to a user's index"""
        r = await self._get_redis()
        
        # Add to user's task set
        await r.sadd(f"user:{user_id}:tasks", task_id)
        
        # Add reverse mapping
        await r.set(f"task:{task_id}:owner", user_id)
        
        # Track creation time
        await r.set(f"task:{task_id}:created_at", datetime.now().isoformat())
        
        # Store config path if provided
        if config_path:
            await r.set(f"task:{task_id}:config_path", config_path)
        
        logger.info(f"Added task {task_id} to user {user_id} in Redis")
    
    async def remove_task(self, user_id: str, task_id: str) -> None:
        """Remove a task from a user's index"""
        r = await self._get_redis()
        
        # Remove from user's task set
        await r.srem(f"user:{user_id}:tasks", task_id)
        
        # Remove reverse mapping
        await r.delete(f"task:{task_id}:owner")
        await r.delete(f"task:{task_id}:created_at")
        await r.delete(f"task:{task_id}:config_path")
        
        logger.info(f"Removed task {task_id} from user {user_id} in Redis")
    
    async def get_user_tasks(self, user_id: str) -> List[str]:
        """Get all task IDs for a user"""
        r = await self._get_redis()
        tasks = await r.smembers(f"user:{user_id}:tasks")
        return [task.decode() for task in tasks]
    
    async def user_owns_task(self, user_id: str, task_id: str) -> bool:
        """Check if a user owns a specific task"""
        r = await self._get_redis()
        return await r.sismember(f"user:{user_id}:tasks", task_id)
    
    async def get_task_owner(self, task_id: str) -> Optional[str]:
        """Get the owner of a task"""
        r = await self._get_redis()
        owner = await r.get(f"task:{task_id}:owner")
        return owner.decode() if owner else None
    
    async def get_task_info(self, task_id: str) -> Optional[dict]:
        """Get task information including config_path"""
        r = await self._get_redis()
        
        owner = await r.get(f"task:{task_id}:owner")
        if not owner:
            return None
            
        created_at = await r.get(f"task:{task_id}:created_at")
        config_path = await r.get(f"task:{task_id}:config_path")
        
        return {
            "user_id": owner.decode(),
            "created_at": created_at.decode() if created_at else None,
            "config_path": config_path.decode() if config_path else None
        }
    
    async def close(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()


def get_user_task_index() -> UserTaskIndex:
    """Factory function to get the appropriate index implementation"""
    import os
    
    if os.getenv("REDIS_URL"):
        if not HAS_REDIS:
            logger.warning("REDIS_URL is set but redis.asyncio is not installed. Using file-based index instead.")
            logger.warning("To use Redis, install it with: pip install redis[asyncio]")
            return FileUserTaskIndex()
        logger.info("Using Redis for user-task index")
        return RedisUserTaskIndex(os.getenv("REDIS_URL"))
    else:
        logger.info("Using file-based user-task index")
        return FileUserTaskIndex()