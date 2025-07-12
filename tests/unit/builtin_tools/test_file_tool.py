"""
Tests for FileTool builtin tool.

These tests define the expected correct behavior for file operations
within the AgentX framework's workspace abstraction.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from agentx.builtin_tools.file import FileTool, create_file_tool
from agentx.storage.workspace import WorkspaceStorage
from agentx.storage.git_storage import GitArtifactStorage
from agentx.core.config import TaskConfig
from agentx.storage.interfaces import StorageResult


class TestFileToolInitialization:
    """Test file tool initialization."""

    def test_file_tool_requires_workspace_storage(self):
        """FileTool should require workspace storage."""
        with pytest.raises(TypeError):
            FileTool()

    def test_file_tool_invalid_initialization(self):
        """FileTool should handle invalid initialization gracefully."""
        # Should raise TypeError for None input
        with pytest.raises(TypeError):
            FileTool(workspace_storage=None)


class TestFileToolWriteOperations:
    """Test file writing operations."""

    def setup_method(self):
        """Setup test environment."""
        self.workspace = Mock(spec=WorkspaceStorage)
        self.workspace.store_artifact = AsyncMock()
        self.workspace.get_workspace_path = Mock(return_value="/test/workspace")
        self.file_tool = FileTool(workspace_storage=self.workspace)

    @pytest.mark.asyncio
    async def test_write_file_stores_as_artifact(self):
        """write_file should store content as artifact through workspace."""
        # Setup
        self.workspace.store_artifact.return_value = StorageResult(success=True, path="artifacts/test.txt")

        # Execute
        result = await self.file_tool.write_file("test.txt", "Hello World")

        # Verify
        self.workspace.store_artifact.assert_called_once_with(
            name="test.txt",
            content="Hello World",
            content_type="text/plain",
            metadata={
                "filename": "test.txt",
                "content_type": "text/plain",
                "tool": "file_tool"
            },
            commit_message="Updated test.txt"
        )
        # Check ToolResult structure
        assert result.success is True
        assert "Successfully wrote" in result.result and "✅" in result.result
        assert "test.txt" in result.result
        # Check metadata
        assert result.metadata["filename"] == "test.txt"
        assert result.metadata["size"] == 11  # len("Hello World")
        assert result.metadata["content_type"] == "text/plain"

    @pytest.mark.asyncio
    async def test_write_file_handles_different_content_types(self):
        """write_file should detect and handle different content types."""
        test_cases = [
            ("report.md", "# Title", "text/markdown"),
            ("data.json", '{"key": "value"}', "application/json"),
            ("script.py", "print('hello')", "text/x-python"),
            ("page.html", "<html></html>", "text/html"),
        ]

        for filename, content, expected_type in test_cases:
            self.workspace.store_artifact.return_value = StorageResult(success=True, path=f"artifacts/{filename}")

            result = await self.file_tool.write_file(filename, content)

            self.workspace.store_artifact.assert_called_with(
                name=filename,
                content=content,
                content_type=expected_type,
                metadata={
                    "filename": filename,
                    "content_type": expected_type,
                    "tool": "file_tool"
                },
                commit_message=f"Updated {filename}"
            )
            # Check ToolResult structure
            assert result.success is True
            assert result.metadata["content_type"] == expected_type

    @pytest.mark.asyncio
    async def test_write_file_handles_storage_errors(self):
        """write_file should handle storage errors gracefully."""
        self.workspace.store_artifact.side_effect = Exception("Storage failed")

        result = await self.file_tool.write_file("test.txt", "content")

        assert result.success is False
        assert "Failed to write file" in result.result and "❌" in result.result
        assert "Storage failed" in result.result
        assert result.error == "Storage failed"


class TestFileToolReadOperations:
    """Test file reading operations."""

    def setup_method(self):
        """Setup test environment."""
        self.workspace = Mock(spec=WorkspaceStorage)
        self.workspace.get_artifact = AsyncMock()
        self.workspace.get_workspace_path = Mock(return_value="/test/workspace")
        self.file_tool = FileTool(workspace_storage=self.workspace)

    @pytest.mark.asyncio
    async def test_read_file_retrieves_from_artifacts(self):
        """read_file should retrieve content from artifacts through workspace."""
        # Setup
        self.workspace.get_artifact.return_value = "File content"

        # Execute
        result = await self.file_tool.read_file("test.txt")

        # Verify
        self.workspace.get_artifact.assert_called_once_with("test.txt", None)
        assert result.success is True
        assert "Contents of test.txt" in result.result and "📄" in result.result
        assert "File content" in result.result
        # Check metadata
        assert result.metadata["filename"] == "test.txt"
        assert result.metadata["content"] == "File content"

    @pytest.mark.asyncio
    async def test_read_file_not_found(self):
        """read_file should handle file not found gracefully."""
        self.workspace.get_artifact.return_value = None

        result = await self.file_tool.read_file("nonexistent.txt")

        assert result.success is False
        assert "File not found" in result.result and "❌" in result.result
        assert "nonexistent.txt" in result.result
        assert result.error == "File not found: nonexistent.txt"

    @pytest.mark.asyncio
    async def test_read_file_handles_storage_errors(self):
        """read_file should handle storage errors gracefully."""
        self.workspace.get_artifact.side_effect = Exception("Storage error")

        result = await self.file_tool.read_file("test.txt")

        assert result.success is False
        assert "Error reading file" in result.result and "❌" in result.result
        assert "Storage error" in result.result
        assert result.error == "Storage error"


class TestFileToolListOperations:
    """Test file listing operations."""

    def setup_method(self):
        """Setup test environment."""
        self.workspace = Mock(spec=WorkspaceStorage)
        self.workspace.list_artifacts = AsyncMock()
        self.workspace.get_workspace_path = Mock(return_value="/test/workspace")
        self.file_tool = FileTool(workspace_storage=self.workspace)

    @pytest.mark.asyncio
    async def test_list_files_returns_artifacts(self):
        """list_files should return list of artifacts from workspace."""
        # Setup
        self.workspace.list_artifacts.return_value = [
            {"name": "file1.txt", "size": 100, "created_at": "2024-01-01"},
            {"name": "file2.md", "size": 200, "created_at": "2024-01-02"}
        ]

        # Execute
        result = await self.file_tool.list_files()

        # Verify
        self.workspace.list_artifacts.assert_called_once()
        assert result.success is True
        assert "Workspace files" in result.result and "📂" in result.result
        assert "file1.txt" in result.result
        assert "file2.md" in result.result
        # Check metadata
        assert result.metadata["count"] == 2
        assert len(result.metadata["files"]) == 2
        assert result.metadata["files"][0]["name"] == "file1.txt"

    @pytest.mark.asyncio
    async def test_list_files_empty_workspace(self):
        """list_files should handle empty workspace gracefully."""
        self.workspace.list_artifacts.return_value = []

        result = await self.file_tool.list_files()

        assert result.success is True
        assert "No files found" in result.result and "📂" in result.result
        assert result.metadata["count"] == 0
        assert result.metadata["files"] == []

    @pytest.mark.asyncio
    async def test_list_files_handles_storage_errors(self):
        """list_files should handle storage errors gracefully."""
        self.workspace.list_artifacts.side_effect = Exception("Storage error")

        result = await self.file_tool.list_files()

        assert result.success is False
        assert "Error listing files" in result.result and "❌" in result.result
        assert "Storage error" in result.result
        assert result.error == "Storage error"


class TestFileToolDirectoryOperations:
    """Test directory operations."""

    def setup_method(self):
        """Setup test environment."""
        self.workspace = Mock(spec=WorkspaceStorage)
        self.workspace.file_storage = Mock()
        self.workspace.file_storage.create_directory = AsyncMock()
        self.workspace.file_storage.list_directory = AsyncMock()
        self.workspace.get_workspace_path = Mock(return_value="/test/workspace")
        self.file_tool = FileTool(workspace_storage=self.workspace)

    @pytest.mark.asyncio
    async def test_create_directory_uses_workspace(self):
        """create_directory should use workspace file storage."""
        self.workspace.file_storage.create_directory.return_value = StorageResult(success=True, path="reports")

        result = await self.file_tool.create_directory("reports")

        self.workspace.file_storage.create_directory.assert_called_once_with("reports")
        assert result.success is True
        assert "Successfully created directory" in result.result
        assert "reports" in result.result
        assert result.metadata["path"] == "reports"
        assert result.metadata["created"] is True

    @pytest.mark.asyncio
    async def test_list_directory_uses_workspace(self):
        """list_directory should use workspace file storage."""
        from agentx.storage.interfaces import FileInfo
        from datetime import datetime

        self.workspace.file_storage.list_directory.return_value = [
            FileInfo("file1.txt", 100, datetime.now(), datetime.now()),
            FileInfo("subdir/", 0, datetime.now(), datetime.now())
        ]

        result = await self.file_tool.list_directory("reports")

        self.workspace.file_storage.list_directory.assert_called_once_with("reports")
        assert result.success is True
        assert "file1.txt" in result.result
        assert "subdir/" in result.result
        assert result.metadata["count"] == 2
        assert len(result.metadata["items"]) == 2


class TestFileToolWorkspaceSummary:
    """Test workspace summary functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.workspace = Mock(spec=WorkspaceStorage)
        self.workspace.get_workspace_summary = AsyncMock()
        self.workspace.get_workspace_path = Mock(return_value="/test/workspace")
        self.file_tool = FileTool(workspace_storage=self.workspace)

    @pytest.mark.asyncio
    async def test_get_workspace_summary_delegates_to_workspace(self):
        """get_workspace_summary should delegate to workspace storage."""
        summary_data = {
            "workspace_path": "/test/workspace",
            "total_files": 5,
            "total_size_bytes": 1024,
            "total_artifacts": 3,
            "artifact_storage": "git",
            "files": [
                {"path": "file1.txt", "size": 100},
                {"path": "file2.md", "size": 200}
            ],
            "artifacts": [
                {"name": "artifact1.txt", "version": "v1"}
            ]
        }

        self.workspace.get_workspace_summary.return_value = summary_data

        result = await self.file_tool.get_workspace_summary()

        self.workspace.get_workspace_summary.assert_called_once()
        assert result.success is True
        assert "Workspace Summary" in result.result and "📊" in result.result
        assert "/test/workspace" in result.result
        assert "total_files" in result.result
        assert result.metadata == summary_data


class TestFileToolFactory:
    """Test file tool factory functions."""

    def test_create_file_tool_function_creates_correct_instance(self):
        """create_file_tool should create FileTool with correct workspace path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_path = temp_dir

            file_tool = create_file_tool(workspace_path)

            assert isinstance(file_tool, FileTool)
            assert file_tool.workspace is not None
            assert str(file_tool.workspace.get_workspace_path()) == workspace_path

    def test_create_file_tool_function_with_task_config(self):
        """create_file_tool should work with workspace path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_path = temp_dir

            file_tool = create_file_tool(workspace_path)

            assert isinstance(file_tool, FileTool)
            assert file_tool.workspace is not None

            # Should have required tool methods
            assert hasattr(file_tool, 'write_file')
            assert hasattr(file_tool, 'read_file')
            assert hasattr(file_tool, 'list_files')


# Integration tests moved to tests/integration/test_file_tool_integration.py
