"""
File-based storage provider implementation.

Default storage provider that uses the local filesystem.
"""

import os
from pathlib import Path
from typing import List
import aiofiles
import aiofiles.os

from ...interfaces import StorageProvider
from ....utils.logger import get_logger

logger = get_logger(__name__)


class FileStorageProvider(StorageProvider):
    """
    File-based storage provider using local filesystem.
    
    This is the default storage provider for local development.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize file storage provider.
        
        Args:
            base_path: Base directory for all storage operations
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized FileStorageProvider at {self.base_path}")
    
    def _full_path(self, path: str) -> Path:
        """Convert relative path to full path under base directory."""
        return self.base_path / path
    
    async def read(self, path: str) -> bytes:
        """Read binary content from file."""
        full_path = self._full_path(path)
        try:
            async with aiofiles.open(full_path, 'rb') as f:
                return await f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path}")
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            raise
    
    async def write(self, path: str, data: bytes) -> None:
        """Write binary content to file."""
        full_path = self._full_path(path)
        
        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temporary file first for atomicity
        temp_path = full_path.with_suffix(full_path.suffix + '.tmp')
        
        try:
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(data)
            
            # Atomic rename
            temp_path.rename(full_path)
            
        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Error writing file {path}: {e}")
            raise
    
    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        full_path = self._full_path(path)
        return full_path.exists()
    
    async def delete(self, path: str) -> None:
        """Delete file."""
        full_path = self._full_path(path)
        try:
            if full_path.is_file():
                full_path.unlink()
            elif full_path.is_dir():
                import shutil
                shutil.rmtree(full_path)
            else:
                raise FileNotFoundError(f"Path not found: {path}")
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
            raise
    
    async def list(self, prefix: str = "") -> List[str]:
        """List all files with given prefix."""
        search_path = self._full_path(prefix)
        
        if not search_path.exists():
            return []
        
        results = []
        
        if search_path.is_dir():
            # List all files recursively
            for item in search_path.rglob("*"):
                if item.is_file():
                    # Get relative path from base
                    rel_path = item.relative_to(self.base_path)
                    results.append(str(rel_path))
        elif search_path.is_file():
            # Single file
            rel_path = search_path.relative_to(self.base_path)
            results.append(str(rel_path))
        
        return sorted(results)
    
    async def makedirs(self, path: str) -> None:
        """Create directory structure."""
        full_path = self._full_path(path)
        full_path.mkdir(parents=True, exist_ok=True)