"""
Storage Tools - Clean LLM-facing tools that use the storage layer.

These tools provide a clean interface for LLM agents to interact with storage
without directly manipulating the filesystem.
"""

from typing import Annotated, Optional, Dict, Any
from ..tool.models import Tool, tool, ToolResult
from ..storage.factory import StorageFactory, WorkspaceStorage
from ..utils.logger import get_logger

logger = get_logger(__name__)


class StorageTool(Tool):
    """Simple storage tool with artifacts as default location and temp when requested."""
    
    def __init__(self, workspace_storage: WorkspaceStorage):
        super().__init__()
        self.workspace = workspace_storage
        logger.info(f"StorageTool initialized with workspace: {self.workspace.get_workspace_path()}")
    
    @tool(description="Get the temp directory path for temporary files")
    async def get_temp_dir(self) -> str:
        """Get the temp directory path for temporary files (automatically cleaned up)."""
        # Ensure temp directory exists
        try:
            result = await self.workspace.file_storage.create_directory("temp")
            if result.success:
                logger.info("Temp directory ready")
            return "temp"
        except Exception as e:
            logger.warning(f"Could not ensure temp directory exists: {e}")
            return "temp"
    
    @tool(description="Write content to a file (saves to artifacts by default)")
    async def write_file(
        self,
        filename: Annotated[str, "Name of the file (e.g., 'requirements.md', 'temp/script.sh')"],
        content: Annotated[str, "Content to write to the file"]
    ) -> str:
        """Write content to file. Uses artifacts/ by default unless path specifies temp/."""
        try:
            # If path doesn't specify a directory, default to artifacts/
            if '/' not in filename:
                path = f"artifacts/{filename}"
            else:
                path = filename
            
            result = await self.workspace.file_storage.write_text(path, content)
            
            if result.success:
                logger.info(f"Wrote file: {path}")
                return f"✅ Successfully wrote {len(content)} characters ({result.size} bytes) to {path}"
            else:
                return f"❌ Failed to write file: {result.error}"
                
        except PermissionError as e:
            return f"❌ Permission denied: {str(e)}"
        except Exception as e:
            return f"❌ Error writing file: {str(e)}"
    
    @tool(description="Read the contents of a file")
    async def read_file(
        self,
        filename: Annotated[str, "Name of the file to read (e.g., 'requirements.md', 'temp/script.sh')"]
    ) -> str:
        """Read file contents. Looks in artifacts/ by default unless path specifies otherwise."""
        try:
            # If path doesn't specify a directory, default to artifacts/
            if '/' not in filename:
                path = f"artifacts/{filename}"
            else:
                path = filename
                
            content = await self.workspace.file_storage.read_text(path)
            logger.info(f"Read file: {path}")
            return f"📄 Contents of {path}:\n\n{content}"
            
        except FileNotFoundError:
            return f"❌ File not found: {path}"
        except IsADirectoryError:
            return f"❌ Path is not a file: {path}"
        except PermissionError as e:
            return f"❌ Permission denied: {str(e)}"
        except Exception as e:
            return f"❌ Error reading file: {str(e)}"
    
    @tool(description="List the contents of a directory")
    async def list_directory(
        self,
        path: Annotated[str, "Directory path to list (defaults to artifacts)"] = "artifacts"
    ) -> str:
        """List directory contents. Defaults to artifacts/ directory."""
        try:
            files = await self.workspace.file_storage.list_directory(path)
            
            if not files:
                return f"📂 Directory {path} is empty"
            
            items = []
            for file_info in files:
                if file_info.path.endswith('/') or '/' not in file_info.path:
                    # It's a directory or file in current directory
                    if file_info.size == 0 and file_info.path.endswith('/'):
                        items.append(f"📁 {file_info.path}")
                    else:
                        items.append(f"📄 {file_info.path} ({file_info.size} bytes)")
            
            logger.info(f"Listed directory: {path}")
            return f"📂 Contents of {path}:\n\n" + "\n".join(items)
            
        except PermissionError as e:
            return f"❌ Permission denied: {str(e)}"
        except Exception as e:
            return f"❌ Error listing directory: {str(e)}"
    
    @tool(description="Check if a file or directory exists")
    async def file_exists(
        self,
        filename: Annotated[str, "Name of the file to check (e.g., 'requirements.md', 'temp/script.sh')"]
    ) -> str:
        """Check if a file exists. Looks in artifacts/ by default unless path specifies otherwise."""
        try:
            # If path doesn't specify a directory, default to artifacts/
            if '/' not in filename:
                path = f"artifacts/{filename}"
            else:
                path = filename
                
            exists = await self.workspace.file_storage.exists(path)
            
            if exists:
                info = await self.workspace.file_storage.get_info(path)
                if info:
                    logger.info(f"Path exists: {path}")
                    return f"✅ Path exists: {path} ({info.size} bytes, modified: {info.modified_at.strftime('%Y-%m-%d %H:%M:%S')})"
                else:
                    logger.info(f"Path exists: {path}")
                    return f"✅ Path exists: {path}"
            else:
                return f"❌ Path does not exist: {path}"
                
        except PermissionError as e:
            return f"❌ Permission denied: {str(e)}"
        except Exception as e:
            return f"❌ Error checking path: {str(e)}"
    
    @tool(description="Create a directory")
    async def create_directory(
        self,
        path: Annotated[str, "Directory path to create (relative to workspace)"]
    ) -> str:
        """Create a directory safely within workspace."""
        try:
            result = await self.workspace.file_storage.create_directory(path)
            
            if result.success:
                if result.metadata and result.metadata.get("already_exists"):
                    logger.info(f"Directory already exists: {path}")
                    return f"ℹ️ Directory already exists: {path}"
                else:
                    logger.info(f"Successfully created directory: {path}")
                    return f"✅ Successfully created directory: {path}"
            else:
                return f"❌ Failed to create directory: {result.error}"
                
        except PermissionError as e:
            return f"❌ Permission denied: {str(e)}"
        except Exception as e:
            return f"❌ Error creating directory: {str(e)}"
    
    @tool(description="Delete a file")
    async def delete_file(
        self,
        filename: Annotated[str, "Name of the file to delete (e.g., 'requirements.md', 'temp/script.sh')"]
    ) -> str:
        """Delete a file. Looks in artifacts/ by default unless path specifies otherwise."""
        try:
            # If path doesn't specify a directory, default to artifacts/
            if '/' not in filename:
                path = f"artifacts/{filename}"
            else:
                path = filename
                
            result = await self.workspace.file_storage.delete(path)
            
            if result.success:
                logger.info(f"Deleted file: {path}")
                return f"✅ Successfully deleted file: {path}"
            else:
                return f"❌ Failed to delete file: {result.error}"
                
        except PermissionError as e:
            return f"❌ Permission denied: {str(e)}"
        except Exception as e:
            return f"❌ Error deleting file: {str(e)}"


def create_storage_tool(workspace_path: str) -> StorageTool:
    """
    Create a storage tool for workspace file operations.
    
    Args:
        workspace_path: Path to the workspace directory
        
    Returns:
        StorageTool instance
    """
    workspace = StorageFactory.create_workspace_storage(workspace_path)
    storage_tool = StorageTool(workspace)
    
    logger.info(f"Created storage tool for workspace: {workspace_path}")
    return storage_tool


# Legacy factory functions for backward compatibility
def create_intent_based_storage_tools(workspace_path: str) -> tuple[StorageTool, StorageTool]:
    """Legacy function - returns the same StorageTool twice for backward compatibility."""
    tool = create_storage_tool(workspace_path)
    return tool, tool


def create_storage_tools(workspace_path: str) -> tuple[StorageTool, StorageTool]:
    """Legacy function - returns the same StorageTool twice for backward compatibility.""" 
    tool = create_storage_tool(workspace_path)
    return tool, tool 