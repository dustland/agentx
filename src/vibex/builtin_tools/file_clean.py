"""
Clean file operations tools - returns structured data without UI elements.

This module provides file operation tools that return clean structured data
suitable for API consumption, without mixing presentation concerns.
"""
from pathlib import Path
from typing import Optional, Dict, Any, List
from ..tool import tool, ToolMetadata, ToolResult
from ..storage.artifacts import get_artifacts_storage
from vibex.utils.logger import get_logger

logger = get_logger()


class FileTools:
    """File operation tools that return clean structured data."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.storage = get_artifacts_storage(project_id)
    
    @tool(
        metadata=ToolMetadata(
            name="write_file",
            description="Write content to a file",
            parameters={
                "filename": {"type": "string", "description": "Name of the file to write"},
                "content": {"type": "string", "description": "Content to write to the file"}
            },
            required=["filename", "content"]
        )
    )
    async def write_file(self, filename: str, content: str) -> ToolResult:
        """Write content to a file, returning structured result."""
        try:
            # Prepare metadata
            metadata = {
                "filename": filename,
                "content_type": "text/plain",
                "size": len(content)
            }
            
            # Store the artifact
            result = await self.storage.store_artifact(
                filename=filename,
                content=content,
                metadata=metadata,
                artifact_type="file"
            )
            
            if result.success:
                version = result.data.get("version", "unknown") if result.data else "unknown"
                logger.info(f"Wrote file artifact: {filename} (version: {version})")
                
                return ToolResult(
                    success=True,
                    result={
                        "action": "write",
                        "path": filename,
                        "size": len(content),
                        "version": version
                    },
                    metadata=metadata
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Failed to write file: {result.error}",
                    metadata={"filename": filename}
                )
                
        except Exception as e:
            logger.error(f"Error writing file {filename}: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"filename": filename}
            )
    
    @tool(
        metadata=ToolMetadata(
            name="read_file",
            description="Read content from a file",
            parameters={
                "filename": {"type": "string", "description": "Name of the file to read"}
            },
            required=["filename"]
        )
    )
    async def read_file(self, filename: str) -> ToolResult:
        """Read file content, returning raw content."""
        try:
            # Retrieve from artifact storage
            result = await self.storage.retrieve_artifact(filename)
            
            if not result.success:
                return ToolResult(
                    success=False,
                    error=f"File not found: {filename}",
                    metadata={"filename": filename}
                )
            
            content = result.data["content"]
            version = result.data.get("version", "unknown")
            
            logger.info(f"Read file artifact: {filename}")
            return ToolResult(
                success=True,
                result={
                    "content": content,
                    "path": filename,
                    "size": len(content),
                    "lines": len(content.splitlines()),
                    "version": version
                },
                metadata={
                    "filename": filename,
                    "size": len(content),
                    "version": version
                }
            )
            
        except Exception as e:
            logger.error(f"Error reading file {filename}: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"filename": filename}
            )
    
    @tool(
        metadata=ToolMetadata(
            name="list_files",
            description="List all files in the project",
            parameters={}
        )
    )
    async def list_files(self) -> ToolResult:
        """List files, returning structured data."""
        try:
            files = await self.storage.list_artifacts()
            
            if not files:
                return ToolResult(
                    success=True,
                    result={
                        "files": [],
                        "count": 0
                    },
                    metadata={"count": 0}
                )
            
            files_data = []
            for file_info in files:
                files_data.append({
                    "path": file_info.path,
                    "size": file_info.size,
                    "modified": file_info.modified_at.isoformat() if file_info.modified_at else None,
                    "version": file_info.version
                })
            
            return ToolResult(
                success=True,
                result={
                    "files": files_data,
                    "count": len(files_data)
                },
                metadata={"count": len(files_data)}
            )
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={}
            )
    
    @tool(
        metadata=ToolMetadata(
            name="edit_file",
            description="Edit a file by replacing specific content",
            parameters={
                "filename": {"type": "string", "description": "Name of the file to edit"},
                "old_content": {"type": "string", "description": "Content to replace"},
                "new_content": {"type": "string", "description": "New content to insert"}
            },
            required=["filename", "old_content", "new_content"]
        )
    )
    async def edit_file(self, filename: str, old_content: str, new_content: str) -> ToolResult:
        """Edit file content, returning structured result."""
        try:
            # Read current content
            read_result = await self.read_file(filename)
            if not read_result.success:
                return read_result
            
            current_content = read_result.result["content"]
            
            # Replace content
            if old_content not in current_content:
                return ToolResult(
                    success=False,
                    error="Content to replace not found in file",
                    metadata={
                        "filename": filename,
                        "search_text": old_content[:50] + "..." if len(old_content) > 50 else old_content
                    }
                )
            
            updated_content = current_content.replace(old_content, new_content, 1)
            
            # Write back
            write_result = await self.write_file(filename, updated_content)
            if write_result.success:
                return ToolResult(
                    success=True,
                    result={
                        "action": "edit",
                        "path": filename,
                        "changes": {
                            "removed": len(old_content),
                            "added": len(new_content),
                            "delta": len(new_content) - len(old_content)
                        },
                        "size": len(updated_content)
                    },
                    metadata={
                        "filename": filename,
                        "edit_type": "replace"
                    }
                )
            else:
                return write_result
                
        except Exception as e:
            logger.error(f"Error editing file {filename}: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"filename": filename}
            )


def create_file_tools(project_id: str) -> FileTools:
    """Factory function to create FileTools instance."""
    return FileTools(project_id)