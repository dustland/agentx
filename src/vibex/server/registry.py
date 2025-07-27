"""
User-Project Registry Management

Manages the mapping between users and their projects.
This keeps the framework layer pure and user-agnostic.
"""

import asyncio
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING, Dict, Any
from datetime import datetime
from ..storage.factory import ProjectStorageFactory
from ..storage.interfaces import FileStorage
from ..utils.logger import get_logger
from .models import ProjectRegistryInfo

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


class Registry:
    """Abstract base class for user-project indexing"""
    
    async def add_project(self, user_id: str, project_id: str, config_path: Optional[str] = None) -> None:
        """Add a project to a user's index"""
        raise NotImplementedError
    
    async def remove_project(self, user_id: str, project_id: str) -> None:
        """Remove a project from a user's index"""
        raise NotImplementedError
    
    async def get_user_projects(self, user_id: str) -> List[str]:
        """Get all project IDs for a user"""
        raise NotImplementedError
    
    async def user_owns_project(self, user_id: str, project_id: str) -> bool:
        """Check if a user owns a specific project"""
        raise NotImplementedError
    
    async def get_project_owner(self, project_id: str) -> Optional[str]:
        """Get the owner of a project"""
        raise NotImplementedError
    
    async def get_project_info(self, project_id: str) -> Optional[ProjectRegistryInfo]:
        """Get project information including config_path"""
        raise NotImplementedError


class FileRegistry(Registry):
    """File-based implementation of user-project index"""
    
    def __init__(self, users_path: Optional[Path] = None):
        """
        Initialize file-based registry.
        
        Args:
            users_path: Path to store user data. Defaults to {base_path}/users
        """
        if users_path is None:
            from ..utils.paths import get_base_path
            users_path = get_base_path() / "users"
        
        # Use FileStorage abstraction instead of direct file manipulation
        self.storage: FileStorage = ProjectStorageFactory.create_file_storage(users_path)
        self._lock = asyncio.Lock()
    
    def _get_user_file(self, user_id: str) -> str:
        """Get the file path for a user"""
        return f"{user_id}.json"
    

    
    async def _read_user_data(self, user_id: str) -> dict:
        """Read user data from file"""
        user_file = self._get_user_file(user_id)
        
        if not await self.storage.exists(user_file):
            return {
                "user_id": user_id, 
                "projects": [],
                "created_at": datetime.now().isoformat()
            }
        
        try:
            data = await self.storage.read_json(user_file)
            if not data:
                return {
                    "user_id": user_id, 
                    "projects": [],
                    "created_at": datetime.now().isoformat()
                }
            
            return data
        except Exception as e:
            logger.error(f"Failed to read user data for {user_id}: {e}")
            return {
                "user_id": user_id, 
                "projects": [],
                "created_at": datetime.now().isoformat()
            }
    
    async def _write_user_data(self, user_id: str, data: dict) -> None:
        """Write user data to file"""
        user_file = self._get_user_file(user_id)
        data["updated_at"] = datetime.now().isoformat()
        
        try:
            result = await self.storage.write_json(user_file, data)
            if not result.success:
                raise Exception(f"Failed to write user data: {result.error}")
        except Exception as e:
            logger.error(f"Failed to write user data for {user_id}: {e}")
            raise
    

    
    async def add_project(self, user_id: str, project_id: str, config_path: Optional[str] = None) -> None:
        """Add a project to a user's index"""
        async with self._lock:
            user_data = await self._read_user_data(user_id)
            
            # Check if project already exists
            existing_project = None
            for project in user_data.get("projects", []):
                if isinstance(project, dict) and project.get("project_id") == project_id:
                    existing_project = project
                    break
                elif isinstance(project, str) and project == project_id:
                    # Convert old string format to new object format
                    existing_project = {"project_id": project_id}
                    break
            
            if not existing_project:
                if "projects" not in user_data:
                    user_data["projects"] = []
                
                # Preserve existing created_at if project already exists
                created_at = existing_project.get("created_at") if existing_project else datetime.now().isoformat()
                
                project_obj = {
                    "project_id": project_id,
                    "user_id": user_id,
                    "config_path": config_path,
                    "created_at": created_at,
                    "updated_at": datetime.now().isoformat()
                }
                
                user_data["projects"].append(project_obj)
                await self._write_user_data(user_id, user_data)
                
                logger.info(f"Added project {project_id} to user {user_id}")
    
    async def remove_project(self, user_id: str, project_id: str) -> None:
        """Remove a project from a user's index"""
        async with self._lock:
            user_data = await self._read_user_data(user_id)
            
            # Remove project if present
            projects = user_data.get("projects", [])
            for i, project in enumerate(projects):
                if isinstance(project, dict) and project.get("project_id") == project_id:
                    projects.pop(i)
                    break
                elif isinstance(project, str) and project == project_id:
                    projects.pop(i)
                    break
            
            await self._write_user_data(user_id, user_data)
            logger.info(f"Removed project {project_id} from user {user_id}")
    
    async def get_user_projects(self, user_id: str) -> List[str]:
        """Get all project IDs for a user"""
        user_data = await self._read_user_data(user_id)
        projects = user_data.get("projects", [])
        
        # Convert to list of project IDs (handle both old string format and new object format)
        project_ids = []
        for project in projects:
            if isinstance(project, dict):
                project_ids.append(project.get("project_id"))
            elif isinstance(project, str):
                project_ids.append(project)
        
        return project_ids
    
    async def user_owns_project(self, user_id: str, project_id: str) -> bool:
        """Check if a user owns a specific project"""
        user_projects = await self.get_user_projects(user_id)
        return project_id in user_projects
    
    async def get_project_owner(self, project_id: str) -> Optional[str]:
        """Get the owner of a project"""
        try:
            # List all user files and search for the project
            user_files_info = await self.storage.list_directory(".")
            
            for file_info in user_files_info:
                user_file = file_info.path
                if not user_file.endswith(".json") or user_file == "_project_index.json":  # Skip the old index file
                    continue
                
                try:
                    user_data = await self.storage.read_json(user_file)
                    if user_data and "projects" in user_data:
                        # Check if project_id exists in the projects list
                        projects = user_data["projects"]
                        for project in projects:
                            if isinstance(project, dict) and project.get("project_id") == project_id:
                                return user_data["user_id"]
                            elif isinstance(project, str) and project == project_id:
                                return user_data["user_id"]
                except Exception as e:
                    logger.warning(f"Failed to read user file {user_file}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get project owner for {project_id}: {e}")
            return None
    
    async def get_project_info(self, project_id: str) -> Optional[ProjectRegistryInfo]:
        """Get project information including config_path"""
        try:
            # First find which user owns this project
            owner = await self.get_project_owner(project_id)
            if not owner:
                return None
            
            # Read the user's data to get project details
            user_data = await self._read_user_data(owner)
            projects = user_data.get("projects", [])
            
            # Find the project object
            project_obj = None
            for project in projects:
                if isinstance(project, dict) and project.get("project_id") == project_id:
                    project_obj = project
                    break
            
            if not project_obj:
                return None
            
            # Handle both created_at and updated_at fields for backward compatibility
            created_at_str = project_obj.get("created_at") or project_obj.get("updated_at")
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str)
            else:
                created_at = datetime.now()  # Fallback to current time
            
            return ProjectRegistryInfo(
                user_id=project_obj["user_id"],
                config_path=project_obj.get("config_path"),
                created_at=created_at
            )
            
        except Exception as e:
            logger.error(f"Failed to get project info for {project_id}: {e}")
            return None


class RedisRegistry(Registry):
    """Redis-based implementation of user-project index"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional['Redis'] = None
    
    async def _get_redis(self) -> 'Redis':
        """Get Redis connection"""
        if self._redis is None:
            if not HAS_REDIS:
                raise ImportError("Redis is not available. Install with: pip install redis")
            self._redis = redis.from_url(self.redis_url)
        return self._redis
    
    async def add_project(self, user_id: str, project_id: str, config_path: Optional[str] = None) -> None:
        """Add a project to a user's index"""
        r = await self._get_redis()
        
        # Add to user's project list
        await r.sadd(f"user:{user_id}:projects", project_id)
        
        # Store project info
        project_info = {
            "user_id": user_id,
            "config_path": config_path,
            "created_at": datetime.now().isoformat()
        }
        await r.hset(f"project:{project_id}", mapping=project_info)
        
        logger.info(f"Added project {project_id} to user {user_id} in Redis")
    
    async def remove_project(self, user_id: str, project_id: str) -> None:
        """Remove a project from a user's index"""
        r = await self._get_redis()
        
        # Remove from user's project list
        await r.srem(f"user:{user_id}:projects", project_id)
        
        # Remove project info
        await r.delete(f"project:{project_id}")
        
        logger.info(f"Removed project {project_id} from user {user_id} in Redis")
    
    async def get_user_projects(self, user_id: str) -> List[str]:
        """Get all project IDs for a user"""
        r = await self._get_redis()
        projects = await r.smembers(f"user:{user_id}:projects")
        return [p.decode() if isinstance(p, bytes) else p for p in projects]
    
    async def user_owns_project(self, user_id: str, project_id: str) -> bool:
        """Check if a user owns a specific project"""
        r = await self._get_redis()
        return await r.sismember(f"user:{user_id}:projects", project_id)
    
    async def get_project_owner(self, project_id: str) -> Optional[str]:
        """Get the owner of a project"""
        r = await self._get_redis()
        user_id = await r.hget(f"project:{project_id}", "user_id")
        return user_id.decode() if user_id and isinstance(user_id, bytes) else user_id
    
    async def get_project_info(self, project_id: str) -> Optional[ProjectRegistryInfo]:
        """Get project information including config_path"""
        r = await self._get_redis()
        project_data = await r.hgetall(f"project:{project_id}")
        
        if not project_data:
            return None
        
        # Convert bytes to strings
        data = {k.decode() if isinstance(k, bytes) else k: 
                v.decode() if isinstance(v, bytes) else v 
                for k, v in project_data.items()}
        
        return ProjectRegistryInfo(
            user_id=data["user_id"],
            config_path=data.get("config_path"),
            created_at=datetime.fromisoformat(data["created_at"])
        )
    
    async def close(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None


def get_project_registry() -> Registry:
    """Get the project registry instance"""
    # For now, use file-based registry
    # In production, you might want to use Redis or a database
    return FileRegistry()