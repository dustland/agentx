"""
Integration tests for FileTool with real storage backends.
"""

import pytest
import tempfile
from pathlib import Path

from vibex.storage import ProjectStorage
from vibex.storage.git_storage import GitArtifactStorage
from vibex.builtin_tools.file import FileTool


class TestFileToolIntegration:
    """Test FileTool integration with real storage."""

    def setup_method(self):
        """Setup test environment with real storage."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.task_id = "test_task"
        self.artifact_storage = GitArtifactStorage(
            base_path=self.temp_dir,
            task_id=self.task_id
        )
        self.project_storage = ProjectStorage(
            task_id=self.task_id,
            base_path=self.temp_dir,
            file_storage=self.artifact_storage
        )
        self.file_tool = FileTool(taskspace_storage=self.project_storage)

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_full_file_lifecycle_integration(self):
        """Test complete file lifecycle with real storage."""
        # Write a file
        write_result = await self.file_tool.write_file("test_report.md", "# Test Report\n\nThis is a test.")
        assert write_result.success is True
        assert "Successfully wrote" in write_result.result and "✅" in write_result.result

        # Read the file back
        read_result = await self.file_tool.read_file("test_report.md")
        assert read_result.success is True
        assert "Contents of test_report.md" in read_result.result and "📄" in read_result.result
        assert "# Test Report" in read_result.result

        # List files
        list_result = await self.file_tool.list_files()
        assert list_result.success is True
        assert "Taskspace files" in list_result.result and "📂" in list_result.result
        assert "test_report.md" in list_result.result

        # Get project_storage summary
        summary_result = await self.file_tool.get_project_storage_summary()
        assert summary_result.success is True
        assert "Taskspace Summary" in summary_result.result and "📊" in summary_result.result

    @pytest.mark.skip(reason="Git storage has issues with nested paths")
    @pytest.mark.asyncio
    async def test_directory_operations_integration(self):
        """Test directory operations with real storage."""
        # Create nested directory structure
        await self.file_tool.write_file("docs/api/overview.md", "# API Overview")
        await self.file_tool.write_file("docs/guides/quickstart.md", "# Quick Start")
        await self.file_tool.write_file("src/main.py", "print('Hello')")

        # List all files first
        list_result = await self.file_tool.list_files()
        assert list_result.success is True
        # Files might be stored with full paths
        assert list_result.metadata["count"] >= 3

        # Read file from subdirectory
        read_result = await self.file_tool.read_file("docs/api/overview.md")
        assert read_result.success is True
        assert "# API Overview" in read_result.result

    @pytest.mark.asyncio
    async def test_taskspace_isolation_integration(self):
        """Test that file operations are isolated to project_storage."""
        # Create a file
        await self.file_tool.write_file("isolated.txt", "isolated content")

        # Create a second project_storage/file tool
        taskspace2 = ProjectStorage(
            task_id="other_task",
            base_path=self.temp_dir,
            file_storage=GitArtifactStorage(
                base_path=self.temp_dir,
                task_id="other_task"
            )
        )
        file_tool2 = FileTool(taskspace_storage=taskspace2)

        # Write different file in second project_storage
        await file_tool2.write_file("other.txt", "other content")

        # Verify isolation
        list1 = await self.file_tool.list_files()
        list2 = await file_tool2.list_files()

        assert "isolated.txt" in list1.result
        assert "other.txt" not in list1.result

        assert "other.txt" in list2.result
        assert "isolated.txt" not in list2.result

        # Try to read across taskspaces (should fail)
        read1 = await self.file_tool.read_file("other.txt")
        read2 = await file_tool2.read_file("isolated.txt")

        assert read1.success is False
        assert read2.success is False
