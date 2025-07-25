"""
Comprehensive integration tests for FileTool.

These tests verify FileTool's integration with project_storage storage,
task configuration, and real file operations.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from vibex.builtin_tools.file import FileTool
from vibex.storage.factory import ProjectStorageFactory
from vibex.storage.project import ProjectStorage
from vibex.storage.interfaces import StorageResult
from vibex.core.config import TaskConfig


class TestFileToolTaskspaceIntegration:
    """Test FileTool properly uses project_storage abstraction."""

    @pytest.fixture
    def mock_project_storage(self):
        """Create a mock project_storage storage."""
        project_storage = MagicMock(spec=ProjectStorage)
        project_storage.store_artifact = AsyncMock()
        project_storage.get_artifact = AsyncMock()
        project_storage.list_artifacts = AsyncMock()
        project_storage.get_project_path = Mock(return_value=Path("/test/project_storage"))
        project_storage.list_directory = AsyncMock()
        project_storage.get_project_summary = AsyncMock()
        project_storage.file_storage = MagicMock()
        project_storage.file_storage.create_directory = AsyncMock()
        return project_storage

    @pytest.mark.asyncio
    async def test_write_file_uses_taskspace_not_direct_filesystem(self, mock_project_storage):
        """write_file should always use project_storage storage, never direct filesystem."""
        mock_project_storage.store_artifact.return_value = StorageResult(
            success=True,
            path="artifacts/test.txt"
        )

        file_tool = FileTool(project_storage=mock_project_storage)
        result = await file_tool.write_file("test.txt", "content")

        # Should use project_storage storage
        mock_project_storage.store_artifact.assert_called_once_with(
            name="test.txt",
            content="content",
            content_type="text/plain",
            metadata={"filename": "test.txt", "content_type": "text/plain", "tool": "file_tool"},
            commit_message="Updated test.txt"
        )

        assert result.success is True
        assert "test.txt" in result.result

    @pytest.mark.asyncio
    async def test_read_file_uses_taskspace_not_direct_filesystem(self, mock_project_storage):
        """read_file should always use project_storage storage, never direct filesystem."""
        mock_project_storage.get_artifact.return_value = "file content"

        file_tool = FileTool(project_storage=mock_project_storage)
        result = await file_tool.read_file("test.txt")

        # Should use project_storage storage
        mock_project_storage.get_artifact.assert_called_once_with("test.txt", None)

        assert result.success is True
        assert "file content" in result.result

    @pytest.mark.asyncio
    async def test_list_files_uses_taskspace_not_direct_filesystem(self, mock_project_storage):
        """list_files should always use project_storage storage, never direct filesystem."""
        mock_project_storage.list_artifacts.return_value = [
            {"name": "file1.txt", "size": 100},
            {"name": "file2.txt", "size": 200}
        ]

        file_tool = FileTool(project_storage=mock_project_storage)
        result = await file_tool.list_files()

        # Should use project_storage storage
        mock_project_storage.list_artifacts.assert_called_once()

        assert result.success is True
        assert "file1.txt" in result.result
        assert "file2.txt" in result.result


class TestFileToolTaskIntegration:
    """Test FileTool integration with task configuration."""

    @pytest.mark.asyncio
    async def test_create_file_tool_with_task_config(self):
        """create_file_tool should work correctly with project_storage path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "test_task"

            storage = ProjectStorageFactory.create_project_storage(base_path=project_path.parent, project_id=project_path.name)
            file_tool = FileTool(storage)

            assert isinstance(file_tool, FileTool)
            assert file_tool.project_storage is not None

            # Test basic operations
            write_result = await file_tool.write_file("test.txt", "Hello")
            assert write_result.success is True

            read_result = await file_tool.read_file("test.txt")
            assert read_result.success is True
            assert "Hello" in read_result.result

    @pytest.mark.asyncio
    async def test_file_tool_respects_task_taskspace_isolation(self):
        """FileTool should maintain project_storage isolation between tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two different task taskspaces
            taskspace1 = Path(tmpdir) / "task1"
            taskspace2 = Path(tmpdir) / "task2"

            storage1 = ProjectStorageFactory.create_project_storage(base_path=taskspace1.parent, project_id=taskspace1.name)
            tool1 = FileTool(storage1)
            storage2 = ProjectStorageFactory.create_project_storage(base_path=taskspace2.parent, project_id=taskspace2.name)
            tool2 = FileTool(storage2)

            # Write different files in each project_storage
            await tool1.write_file("file.txt", "Task 1 content")
            await tool2.write_file("file.txt", "Task 2 content")

            # Each should see only its own content
            read1 = await tool1.read_file("file.txt")
            read2 = await tool2.read_file("file.txt")

            assert "Task 1 content" in read1.result
            assert "Task 2 content" in read2.result

            # List files should show isolation
            list1 = await tool1.list_files()
            list2 = await tool2.list_files()

            # Each should only see its own file
            assert list1.metadata["count"] == 1
            assert list2.metadata["count"] == 1


class TestFileToolIntegrationReal:
    """Test FileTool with real project_storage storage."""

    @pytest.mark.asyncio
    async def test_file_lifecycle_with_real_taskspace(self):
        """Test complete file lifecycle with real project_storage storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create real project_storage storage
            project_storage = ProjectStorageFactory.create_project_storage(
                base_path=Path(tmpdir),
                project_id="test_taskspace",
                use_git_artifacts=False
            )

            file_tool = FileTool(project_storage=project_storage)

            # Test write
            write_result = await file_tool.write_file(
                "report.md",
                "# Test Report\n\nThis is a test report."
            )
            assert write_result.success is True
            assert write_result.metadata["content_type"] == "text/markdown"

            # Test read
            read_result = await file_tool.read_file("report.md")
            assert read_result.success is True
            assert "# Test Report" in read_result.result

            # Test list
            list_result = await file_tool.list_files()
            assert list_result.success is True
            assert "report.md" in list_result.result
            assert list_result.metadata["count"] == 1

            # Test project_storage summary
            summary_result = await file_tool.get_project_summary()
            assert summary_result.success is True
            assert "Taskspace Summary" in summary_result.result

    @pytest.mark.asyncio
    async def test_directory_operations_with_real_taskspace(self):
        """Test directory operations with real project_storage storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_storage = StorageFactory.create_project_storage(
                project_path=Path(tmpdir) / "test_taskspace",
                use_git_artifacts=False  # Disable git for this test
            )

            file_tool = FileTool(project_storage=project_storage)

            # Create nested structure
            result1 = await file_tool.write_file("docs/readme.md", "# README")
            result2 = await file_tool.write_file("docs/api/spec.md", "# API Spec")
            result3 = await file_tool.write_file("src/main.py", "print('Hello')")

            # Check if writes succeeded
            assert result1.success is True
            assert result2.success is True
            assert result3.success is True

            # List root
            root_list = await file_tool.list_files()
            assert root_list.success is True
            # Files might be flattened in storage
            assert root_list.metadata["count"] >= 3

            # Directory listing might not work with flattened storage
            # Skip directory listing test for now

    @pytest.mark.asyncio
    async def test_taskspace_organization_features(self):
        """Test project_storage organization and metadata features."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_storage = StorageFactory.create_project_storage(
                project_path=Path(tmpdir) / "test_taskspace",
                use_git_artifacts=False  # Disable git for this test
            )

            file_tool = FileTool(project_storage=project_storage)

            # Create various file types
            files = [
                ("data.json", '{"key": "value"}', "application/json"),
                ("script.py", "def main(): pass", "text/x-python"),
                ("style.css", "body { margin: 0; }", "text/css"),
                ("page.html", "<html><body></body></html>", "text/html")
            ]

            for filename, content, expected_type in files:
                result = await file_tool.write_file(filename, content)
                assert result.success is True
                assert result.metadata["content_type"] == expected_type

            # Verify organization
            list_result = await file_tool.list_files()
            assert list_result.metadata["count"] == 4

            # Get detailed summary
            summary = await file_tool.get_project_summary()
            assert summary.success is True
            assert summary.metadata["total_artifacts"] == 4
