"""
Storage interfaces - Clean abstractions for different types of storage operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, BinaryIO
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class StorageResult:
    """Result of a storage operation."""
    success: bool
    path: Optional[str] = None
    size: Optional[int] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}
        if self.data is None:
            self.data = {}


@dataclass
class FileInfo:
    """Information about a stored file."""
    path: str
    size: int
    created_at: datetime
    modified_at: datetime
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class StorageBackend(ABC):
    """Base interface for all storage backends."""

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if a path exists."""
        pass

    @abstractmethod
    async def get_info(self, path: str) -> Optional[FileInfo]:
        """Get information about a file/directory."""
        pass

    @abstractmethod
    async def list_directory(self, path: str = ".") -> List[FileInfo]:
        """List contents of a directory."""
        pass


class FileStorage(StorageBackend):
    """Interface for file storage operations."""

    @abstractmethod
    async def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """Read text content from a file."""
        pass

    @abstractmethod
    async def write_text(self, path: str, content: str, encoding: str = "utf-8") -> StorageResult:
        """Write text content to a file."""
        pass

    @abstractmethod
    async def read_bytes(self, path: str) -> bytes:
        """Read binary content from a file."""
        pass

    @abstractmethod
    async def write_bytes(self, path: str, content: bytes) -> StorageResult:
        """Write binary content to a file."""
        pass

    async def read_json(self, path: str) -> Optional[Dict[str, Any]]:
        """Read and parse JSON content from a file."""
        try:
            content = await self.read_text(path)
            import json
            return json.loads(content)
        except Exception:
            return None

    async def write_json(self, path: str, data: Dict[str, Any], indent: int = 2) -> StorageResult:
        """Write data as JSON to a file."""
        try:
            import json
            content = json.dumps(data, indent=indent)
            return await self.write_text(path, content)
        except Exception as e:
            return StorageResult(success=False, error=str(e))

    @abstractmethod
    async def append_text(self, path: str, content: str, encoding: str = "utf-8") -> StorageResult:
        """Append text content to a file."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> StorageResult:
        """Delete a file."""
        pass

    @abstractmethod
    async def create_directory(self, path: str) -> StorageResult:
        """Create a directory."""
        pass


class ArtifactStorage(StorageBackend):
    """Interface for artifact storage with versioning and metadata."""

    @abstractmethod
    async def store_artifact(
        self,
        name: str,
        content: Union[str, bytes],
        content_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None
    ) -> StorageResult:
        """Store an artifact with versioning."""
        pass

    @abstractmethod
    async def get_artifact(self, name: str, version: Optional[str] = None) -> Optional[str]:
        """Get artifact content by name and optional version."""
        pass

    @abstractmethod
    async def list_artifacts(self) -> List[Dict[str, Any]]:
        """List all artifacts with their metadata."""
        pass

    @abstractmethod
    async def get_artifact_versions(self, name: str) -> List[str]:
        """Get all versions of an artifact."""
        pass

    @abstractmethod
    async def delete_artifact(self, name: str, version: Optional[str] = None) -> StorageResult:
        """Delete an artifact or specific version."""
        pass


class StorageProvider(ABC):
    """
    Abstract interface for storage provider implementations.
    
    This is a simpler interface than FileStorage, focused on basic operations
    that can be implemented by different backends (file, S3, Azure, etc.).
    """
    
    @abstractmethod
    async def read(self, path: str) -> bytes:
        """Read binary content from storage"""
        pass
    
    @abstractmethod
    async def write(self, path: str, data: bytes) -> None:
        """Write binary content to storage"""
        pass
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if path exists in storage"""
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete from storage"""
        pass
    
    @abstractmethod
    async def list(self, prefix: str = "") -> List[str]:
        """List all paths with given prefix"""
        pass
    
    @abstractmethod
    async def makedirs(self, path: str) -> None:
        """Create directory structure"""
        pass


class CacheBackend(ABC):
    """Abstract interface for cache implementations"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL in seconds"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries"""
        pass
