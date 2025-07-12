"""
Tests for WorkspaceStorage.

These tests define the expected correct behavior for workspace
management and storage abstraction in the AgentX framework.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List

from agentx.storage import WorkspaceStorage, StorageBackend
from agentx.storage.git_storage import GitArtifactStorage


class TestWorkspaceStorageBasics:
    """Test basic workspace functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.task_id = "test_task"
        self.mock_storage = Mock(spec=StorageBackend)
        self.workspace = WorkspaceStorage(
            task_id=self.task_id,
            base_path=self.temp_dir,
            file_storage=self.mock_storage
        )

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_workspace_path_initialization(self):
        """WorkspaceStorage should initialize with correct paths."""
        assert self.workspace.get_workspace_path() == self.temp_dir / self.task_id
        assert self.workspace.task_id == self.task_id

    @pytest.mark.asyncio
    async def test_store_artifact_success(self):
        """store_artifact should store content and return success."""
        self.mock_storage.store = AsyncMock(return_value={"success": True, "path": "test.txt"})

        result = await self.workspace.store_artifact("test.txt", "Hello World")

        assert result.success is True
        assert "test.txt" in result.result
        self.mock_storage.store.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_artifact_success(self):
        """get_artifact should retrieve content successfully."""
        self.mock_storage.retrieve = AsyncMock(return_value={"success": True, "content": "Hello World"})

        result = await self.workspace.get_artifact("test.txt")

        assert result == "Hello World"
        self.mock_storage.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_artifact_not_found(self):
        """get_artifact should return None for non-existent files."""
        self.mock_storage.retrieve = AsyncMock(return_value={"success": False, "error": "Not found"})

        result = await self.workspace.get_artifact("missing.txt")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_artifacts_success(self):
        """list_artifacts should return list of files."""
        mock_files = [
            {"name": "file1.txt", "size": 100},
            {"name": "file2.md", "size": 200}
        ]
        self.mock_storage.list_files = AsyncMock(return_value={"success": True, "files": mock_files})

        result = await self.workspace.list_artifacts()

        assert len(result) == 2
        assert result[0]["name"] == "file1.txt"
        assert result[1]["name"] == "file2.md"

    @pytest.mark.asyncio
    async def test_list_artifacts_empty(self):
        """list_artifacts should return empty list when no files."""
        self.mock_storage.list_files = AsyncMock(return_value={"success": True, "files": []})

        result = await self.workspace.list_artifacts()

        assert result == []

    @pytest.mark.asyncio
    async def test_list_directory_success(self):
        """list_directory should return directory contents."""
        # Create some actual directories
        workspace_path = self.temp_dir / self.task_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        (workspace_path / "docs").mkdir()
        (workspace_path / "src").mkdir()
        (workspace_path / "test.txt").touch()

        result = await self.workspace.list_directory(".")

        assert result["success"] is True
        assert len(result["directories"]) == 2
        assert "docs" in result["directories"]
        assert "src" in result["directories"]
        assert len(result["files"]) == 1
        assert "test.txt" in result["files"]

    @pytest.mark.asyncio
    async def test_list_directory_not_found(self):
        """list_directory should handle non-existent directories."""
        result = await self.workspace.list_directory("nonexistent")

        assert result["success"] is False
        assert "not found" in result["error"].lower()


class TestWorkspaceStorageSummary:
    """Test workspace summary functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.task_id = "test_task"
        self.file_storage = Mock(spec=StorageBackend)
        self.file_storage.list_files = AsyncMock()
        self.workspace = WorkspaceStorage(
            task_id=self.task_id,
            base_path=self.temp_dir,
            file_storage=self.file_storage
        )

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_get_workspace_summary_aggregates_information(self):
        """get_workspace_summary should aggregate workspace information."""
        # Mock file storage response
        self.file_storage.list_files.return_value = {
            "success": True,
            "files": [
                {"name": "file1.txt", "size": 100, "created": "2024-01-01"},
                {"name": "file2.md", "size": 200, "created": "2024-01-02"},
                {"name": "file3.json", "size": 150, "created": "2024-01-03"}
            ]
        }

        # Create some directories
        workspace_path = self.temp_dir / self.task_id
        (workspace_path / "reports").mkdir(parents=True)
        (workspace_path / "data").mkdir()

        result = await self.workspace.get_workspace_summary()

        assert result["success"] is True
        summary = result["summary"]

        # Verify summary includes file information
        assert summary["total_files"] == 3
        assert summary["total_size"] == 450  # 100 + 200 + 150
        assert len(summary["recent_files"]) <= 5  # Should limit recent files

        # Verify directory information
        assert summary["total_directories"] >= 2
        assert "reports" in summary["directory_structure"]
        assert "data" in summary["directory_structure"]

    @pytest.mark.asyncio
    async def test_get_workspace_summary_handles_errors(self):
        """get_workspace_summary should handle errors gracefully."""
        self.file_storage.list_files.side_effect = Exception("Storage error")

        result = await self.workspace.get_workspace_summary()

        assert result["success"] is False
        assert "error" in result
        assert "Storage error" in result["error"]


# Integration tests moved to tests/integration/test_workspace_storage_integration.py
