"""
File operations for AgentX.
"""

import os
import mimetypes
from pathlib import Path
from typing import Annotated, Optional, Dict, Any
from agentx.core.tool import tool, Tool
from agentx.storage.workspace import WorkspaceStorage
from agentx.storage.factory import StorageFactory
from agentx.utils.logger import get_logger

logger = get_logger(__name__)


class FileTool(Tool):
    """File tool that works with workspace artifacts and provides simple file operations."""
    
    def __init__(self, workspace_storage: WorkspaceStorage):
        super().__init__()
        
        # Validate required parameter
        if workspace_storage is None:
            raise TypeError("FileTool requires a WorkspaceStorage instance, got None")
        
        if not hasattr(workspace_storage, 'get_workspace_path'):
            raise TypeError(f"FileTool requires a WorkspaceStorage instance, got {type(workspace_storage)}")
        
        self.workspace = workspace_storage
        logger.info(f"FileTool initialized with workspace: {self.workspace.get_workspace_path()}")
    
    @tool(description="Write content to a file")
    async def write_file(
        self,
        filename: Annotated[str, "Name of the file (e.g., 'report.html', 'requirements.md')"],
        content: Annotated[str, "Content to write to the file"]
    ) -> Dict[str, Any]:
        """Write content to file as a workspace artifact with versioning."""
        try:
            # Store as artifact with metadata
            metadata = {
                "filename": filename,
                "content_type": self._get_content_type(filename),
                "tool": "file_tool"
            }
            
            result = await self.workspace.store_artifact(
                name=filename,
                content=content,
                content_type=metadata["content_type"],
                metadata=metadata,
                commit_message=f"Updated {filename}"
            )
            
            if result.success:
                version = result.data.get("version", "unknown") if result.data else "unknown"
                logger.info(f"Wrote file artifact: {filename} (version: {version})")
                return {
                    "success": True,
                    "filename": filename,
                    "size": len(content),
                    "version": version,
                    "message": f"Successfully wrote {len(content)} characters to {filename}"
                }
            else:
                return {
                    "success": False,
                    "filename": filename,
                    "error": result.error,
                    "message": f"Failed to write file: {result.error}"
                }
                
        except Exception as e:
            logger.error(f"Error writing file {filename}: {e}")
            return {
                "success": False,
                "filename": filename,
                "error": str(e),
                "message": f"Error writing file: {str(e)}"
            }
    
    @tool(description="Read the contents of a file")
    async def read_file(
        self,
        filename: Annotated[str, "Name of the file to read"],
        version: Annotated[Optional[str], "Specific version to read (optional, defaults to latest)"] = None
    ) -> Dict[str, Any]:
        """Read file contents from workspace artifacts."""
        try:
            content = await self.workspace.get_artifact(filename, version)
            
            if content is None:
                return {
                    "success": False,
                    "filename": filename,
                    "error": f"File not found: {filename}",
                    "message": f"File not found: {filename}"
                }
            
            logger.info(f"Read file artifact: {filename}")
            return {
                "success": True,
                "filename": filename,
                "content": content,
                "size": len(content),
                "version": version,
                "message": f"Successfully read {filename}"
            }
            
        except Exception as e:
            logger.error(f"Error reading file {filename}: {e}")
            return {
                "success": False,
                "filename": filename,
                "error": str(e),
                "message": f"Error reading file: {str(e)}"
            }
    
    @tool(description="List all files in the workspace")
    async def list_files(self) -> Dict[str, Any]:
        """List all file artifacts in the workspace."""
        try:
            artifacts = await self.workspace.list_artifacts()
            
            if not artifacts:
                return {
                    "success": True,
                    "files": [],
                    "count": 0,
                    "message": "No files found in workspace"
                }
            
            # Group by filename (artifacts can have multiple versions)
            files_by_name = {}
            for artifact in artifacts:
                name = artifact["name"]
                if name not in files_by_name:
                    files_by_name[name] = []
                files_by_name[name].append(artifact)
            
            files = []
            for name, versions in files_by_name.items():
                latest_version = sorted(versions, key=lambda x: x.get("created_at", ""))[-1]
                size = latest_version.get("size", 0)
                version_count = len(versions)
                
                file_info = {
                    "name": name,
                    "size": size,
                    "versions": version_count,
                    "latest_version": latest_version.get("version", "unknown"),
                    "created_at": latest_version.get("created_at"),
                    "content_type": latest_version.get("content_type", "text/plain")
                }
                files.append(file_info)
            
            logger.info(f"Listed {len(files_by_name)} file artifacts")
            return {
                "success": True,
                "files": files,
                "count": len(files),
                "message": f"Found {len(files)} files in workspace"
            }
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return {
                "success": False,
                "files": [],
                "count": 0,
                "error": str(e),
                "message": f"Error listing files: {str(e)}"
            }
    
    @tool(description="Check if a file exists in the workspace")
    async def file_exists(
        self,
        filename: Annotated[str, "Name of the file to check"]
    ) -> str:
        """Check if a file artifact exists in the workspace."""
        try:
            content = await self.workspace.get_artifact(filename)
            
            if content is not None:
                # Get artifact metadata
                artifacts = await self.workspace.list_artifacts()
                file_artifacts = [a for a in artifacts if a["name"] == filename]
                
                if file_artifacts:
                    latest = sorted(file_artifacts, key=lambda x: x.get("created_at", ""))[-1]
                    size = latest.get("size", 0)
                    created_at = latest.get("created_at", "unknown")
                    version_count = len(file_artifacts)
                    
                    info = f"✅ File exists: {filename} ({size} bytes, created: {created_at}"
                    if version_count > 1:
                        info += f", {version_count} versions"
                    info += ")"
                    
                    logger.info(f"File exists: {filename}")
                    return info
                else:
                    return f"✅ File exists: {filename}"
            else:
                return f"❌ File does not exist: {filename}"
                
        except Exception as e:
            logger.error(f"Error checking file {filename}: {e}")
            return f"❌ Error checking file: {str(e)}"
    
    @tool(description="Delete a file from the workspace")
    async def delete_file(
        self,
        filename: Annotated[str, "Name of the file to delete"],
        version: Annotated[Optional[str], "Specific version to delete (optional, deletes all versions if not specified)"] = None
    ) -> str:
        """Delete a file artifact from the workspace."""
        try:
            result = await self.workspace.delete_artifact(filename, version)
            
            if result.success:
                if version:
                    logger.info(f"Deleted file artifact version: {filename} (version: {version})")
                    return f"✅ Successfully deleted {filename} version {version}"
                else:
                    logger.info(f"Deleted file artifact: {filename}")
                    return f"✅ Successfully deleted {filename}"
            else:
                return f"❌ Failed to delete file: {result.error}"
                
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return f"❌ Error deleting file: {str(e)}"
    
    @tool(description="Get version history of a file")
    async def get_file_versions(
        self,
        filename: Annotated[str, "Name of the file to get versions for"]
    ) -> str:
        """Get version history of a file artifact."""
        try:
            versions = await self.workspace.get_artifact_versions(filename)
            
            if not versions:
                return f"❌ No versions found for file: {filename}"
            
            # Get detailed info for each version
            artifacts = await self.workspace.list_artifacts()
            file_artifacts = [a for a in artifacts if a["name"] == filename]
            
            if not file_artifacts:
                return f"❌ No artifact metadata found for file: {filename}"
            
            # Sort by creation time
            file_artifacts.sort(key=lambda x: x.get("created_at", ""))
            
            version_list = []
            for i, artifact in enumerate(file_artifacts):
                version = artifact.get("version", f"v{i+1}")
                size = artifact.get("size", 0)
                created_at = artifact.get("created_at", "unknown")
                
                version_list.append(f"  {version} - {size} bytes, created: {created_at}")
            
            logger.info(f"Retrieved {len(versions)} versions for {filename}")
            return f"📋 Version history for {filename}:\n\n" + "\n".join(version_list)
            
        except Exception as e:
            logger.error(f"Error getting versions for {filename}: {e}")
            return f"❌ Error getting versions: {str(e)}"
    
    @tool(description="Get workspace summary with file statistics")
    async def get_workspace_summary(self) -> Dict[str, Any]:
        """Get a summary of the workspace contents."""
        try:
            summary = await self.workspace.get_workspace_summary()
            
            if "error" in summary:
                return {
                    "success": False,
                    "error": summary["error"],
                    "message": f"Error getting workspace summary: {summary['error']}"
                }
            
            logger.info("Retrieved workspace summary")
            return {
                "success": True,
                "summary": summary,
                "message": "Successfully retrieved workspace summary"
            }
            
        except Exception as e:
            logger.error(f"Error getting workspace summary: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error getting workspace summary: {str(e)}"
            }
    
    @tool(description="Create a directory in the workspace")
    async def create_directory(
        self,
        path: Annotated[str, "Directory path to create (e.g., 'reports', 'data/sources')"]
    ) -> str:
        """Create a directory in the workspace using the underlying file storage."""
        try:
            result = await self.workspace.file_storage.create_directory(path)
            
            if result.success:
                if result.metadata and result.metadata.get("already_exists"):
                    logger.info(f"Directory already exists: {path}")
                    return f"ℹ️ Directory already exists: {path}"
                else:
                    logger.info(f"Created directory: {path}")
                    return f"✅ Successfully created directory: {path}"
            else:
                return f"❌ Failed to create directory: {result.error}"
                
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")
            return f"❌ Error creating directory: {str(e)}"
    
    @tool(description="List contents of a directory in the workspace")
    async def list_directory(
        self,
        path: Annotated[str, "Directory path to list (defaults to workspace root)"] = ""
    ) -> str:
        """List the contents of a directory in the workspace."""
        try:
            # Use empty string for root, or the specified path
            directory_path = path if path else ""
            
            files = await self.workspace.file_storage.list_directory(directory_path)
            
            if not files:
                display_path = directory_path if directory_path else "workspace root"
                return f"📂 Directory '{display_path}' is empty"
            
            items = []
            for file_info in files:
                # Check if it's a directory (ends with /) or file
                if file_info.path.endswith('/'):
                    items.append(f"📁 {file_info.path}")
                else:
                    items.append(f"📄 {file_info.path} ({file_info.size} bytes)")
            
            display_path = directory_path if directory_path else "workspace root"
            logger.info(f"Listed directory: {display_path}")
            return f"📂 Contents of '{display_path}':\n\n" + "\n".join(items)
            
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return f"❌ Error listing directory: {str(e)}"
    
    def _get_content_type(self, filename: str) -> str:
        """Determine content type from filename."""
        if filename.endswith('.html'):
            return 'text/html'
        elif filename.endswith('.md'):
            return 'text/markdown'
        elif filename.endswith('.json'):
            return 'application/json'
        elif filename.endswith('.txt'):
            return 'text/plain'
        elif filename.endswith('.py'):
            return 'text/x-python'
        elif filename.endswith('.js'):
            return 'text/javascript'
        elif filename.endswith('.css'):
            return 'text/css'
        else:
            return 'text/plain'


def create_file_tool(workspace_path: str) -> FileTool:
    """
    Create a file tool for workspace operations.
    
    Args:
        workspace_path: Path to the workspace directory
        
    Returns:
        FileTool instance that properly uses workspace abstraction
    """
    workspace = StorageFactory.create_workspace_storage(workspace_path)
    file_tool = FileTool(workspace)
    
    logger.info(f"Created file tool for workspace: {workspace_path}")
    return file_tool 