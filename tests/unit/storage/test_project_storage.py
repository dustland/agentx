"""
Tests for ProjectStorage.

These tests define the expected correct behavior for project_storage
management and storage abstraction in the VibeX framework.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List

from vibex.storage import ProjectStorage, StorageBackend
from vibex.storage.git_storage import GitArtifactStorage


class TestProjectStorageBasics:
    """Test basic project storage functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_id = "test_project"
        self.mock_storage = Mock(spec=StorageBackend)
        self.project_storage = ProjectStorage(
            project_id=self.project_id,
            base_path=self.temp_dir,
            file_storage=self.mock_storage
        )

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_project_path_initialization(self):
        """ProjectStorage should initialize with correct paths."""
        assert self.project_storage.get_project_path() == self.temp_dir / self.project_id
        assert self.project_storage.project_id == self.project_id

    @pytest.mark.asyncio
    async def test_store_artifact_success(self):
        """store_artifact should store content and return success."""
        self.mock_storage.store = AsyncMock(return_value={"success": True, "path": "test.txt"})

        result = await self.project_storage.store_artifact("test.txt", "Hello World")

        assert result.success is True
        assert "test.txt" in result.result
        self.mock_storage.store.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_artifact_success(self):
        """get_artifact should retrieve content successfully."""
        self.mock_storage.retrieve = AsyncMock(return_value={"success": True, "content": "Hello World"})

        result = await self.project_storage.get_artifact("test.txt")

        assert result == "Hello World"
        self.mock_storage.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_artifact_not_found(self):
        """get_artifact should return None for non-existent files."""
        self.mock_storage.retrieve = AsyncMock(return_value={"success": False, "error": "Not found"})

        result = await self.project_storage.get_artifact("missing.txt")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_artifacts_success(self):
        """list_artifacts should return list of files."""
        mock_files = [
            {"name": "file1.txt", "size": 100},
            {"name": "file2.md", "size": 200}
        ]
        self.mock_storage.list_files = AsyncMock(return_value={"success": True, "files": mock_files})

        result = await self.project_storage.list_artifacts()

        assert len(result) == 2
        assert result[0]["name"] == "file1.txt"
        assert result[1]["name"] == "file2.md"

    @pytest.mark.asyncio
    async def test_list_artifacts_empty(self):
        """list_artifacts should return empty list when no files."""
        self.mock_storage.list_files = AsyncMock(return_value={"success": True, "files": []})

        result = await self.project_storage.list_artifacts()

        assert result == []

    @pytest.mark.asyncio
    async def test_list_directory_success(self):
        """list_directory should return directory contents."""
        # Create some actual directories
        project_path = self.temp_dir / self.project_id
        project_path.mkdir(parents=True, exist_ok=True)
        (project_path / "docs").mkdir()
        (project_path / "src").mkdir()
        (project_path / "test.txt").touch()

        result = await self.project_storage.list_directory(".")

        assert result["success"] is True
        assert len(result["directories"]) == 2
        assert "docs" in result["directories"]
        assert "src" in result["directories"]
        assert len(result["files"]) == 1
        assert "test.txt" in result["files"]

    @pytest.mark.asyncio
    async def test_list_directory_not_found(self):
        """list_directory should handle non-existent directories."""
        result = await self.project_storage.list_directory("nonexistent")

        assert result["success"] is False
        assert "not found" in result["error"].lower()


class TestProjectStorageSummary:
    """Test project storage summary functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_id = "test_project"
        self.file_storage = Mock(spec=StorageBackend)
        self.file_storage.list_files = AsyncMock()
        self.project_storage = ProjectStorage(
            project_id=self.project_id,
            base_path=self.temp_dir,
            file_storage=self.file_storage
        )

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_get_project_summary_aggregates_information(self):
        """get_project_summary should aggregate project information."""
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
        project_path = self.temp_dir / self.project_id
        (project_path / "reports").mkdir(parents=True)
        (project_path / "data").mkdir()

        result = await self.project_storage.get_project_summary()

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
    async def test_get_project_summary_handles_errors(self):
        """get_project_summary should handle errors gracefully."""
        self.file_storage.list_files.side_effect = Exception("Storage error")

        result = await self.project_storage.get_project_summary()

        assert result["success"] is False
        assert "error" in result
        assert "Storage error" in result["error"]


# Integration tests moved to tests/integration/test_taskspace_storage_integration.py
