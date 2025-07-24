"""
Comprehensive tests for FileTool - Testing taskspace abstraction and artifact storage.

These tests systematically verify that FileTool properly uses the taskspace layer
instead of bypassing it, and handles file operations correctly.
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from vibex.builtin_tools.file import FileTool, create_file_tool
from vibex.storage.factory import StorageFactory
from vibex.storage.taskspace import TaskspaceStorage
from vibex.storage.interfaces import StorageResult
from vibex.core.config import TaskConfig


class TestFileToolTaskspaceIntegration:
    """Test FileTool properly uses taskspace abstraction."""

    @pytest.fixture
    async def taskspace_storage(self):
        """Create a test taskspace storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            taskspace_path = Path(temp_dir) / "test_task_id"
            storage = StorageFactory.create_taskspace_storage(taskspace_path)
            yield storage

    @pytest.fixture
    def file_tool(self, taskspace_storage):
        """Create FileTool with test taskspace storage."""
        return FileTool(taskspace_storage)

    def test_file_tool_initialization(self, taskspace_storage):
        """Test FileTool initializes with taskspace storage."""
        tool = FileTool(taskspace_storage)
        assert tool.taskspace == taskspace_storage
        assert tool.taskspace.get_taskspace_path() == taskspace_storage.get_taskspace_path()

    async def test_write_file_uses_taskspace_layer(self, file_tool):
        """Test write_file uses taskspace.store_artifact() not direct file operations."""
        # Mock the taskspace storage
        file_tool.taskspace.store_artifact = AsyncMock(return_value=StorageResult(
            success=True,
            path="test.md",
            size=100,
            data={"version": "abc123"}
        ))

        result = await file_tool.write_file("test.md", "# Test Content")

        # Verify taskspace layer was used
        file_tool.taskspace.store_artifact.assert_called_once_with(
            name="test.md",
            content="# Test Content",
            content_type="text/markdown",
            metadata={
                "filename": "test.md",
                "content_type": "text/markdown",
                "tool": "file_tool"
            },
            commit_message="Updated test.md"
        )

        assert "✅ Successfully wrote" in result
        assert "test.md" in result

    async def test_read_file_uses_taskspace_layer(self, file_tool):
        """Test read_file uses taskspace.get_artifact() not direct file operations."""
        # Mock the taskspace storage
        file_tool.taskspace.get_artifact = AsyncMock(return_value="# Test Content")

        result = await file_tool.read_file("test.md")

        # Verify taskspace layer was used
        file_tool.taskspace.get_artifact.assert_called_once_with("test.md", None)

        assert "📄 Contents of test.md:" in result
        assert "# Test Content" in result

    async def test_list_files_uses_taskspace_layer(self, file_tool):
        """Test list_files uses taskspace.list_artifacts() not direct file operations."""
        # Mock the taskspace storage
        file_tool.taskspace.list_artifacts = AsyncMock(return_value=[
            {"name": "test1.md", "size": 100, "created_at": "2025-01-01"},
            {"name": "test2.md", "size": 200, "created_at": "2025-01-02"}
        ])

        result = await file_tool.list_files()

        # Verify taskspace layer was used
        file_tool.taskspace.list_artifacts.assert_called_once()

        assert "📂 Taskspace files:" in result
        assert "test1.md" in result
        assert "test2.md" in result


class TestFileToolContentTypes:
    """Test FileTool content type handling and extension logic."""

    @pytest.fixture
    def mock_taskspace(self):
        """Create mock taskspace storage."""
        mock = MagicMock()
        mock.store_artifact = AsyncMock(return_value=StorageResult(success=True))
        return mock

    @pytest.fixture
    def file_tool(self, mock_taskspace):
        """Create FileTool with mock taskspace."""
        return FileTool(mock_taskspace)

    @pytest.mark.parametrize("filename,expected_content_type", [
        ("report.md", "text/markdown"),
        ("data.json", "application/json"),
        ("script.py", "text/x-python"),
        ("page.html", "text/html"),
        ("readme.txt", "text/plain"),
        ("style.css", "text/css"),
        ("app.js", "text/javascript"),
        ("unknown.xyz", "text/plain"),  # fallback
    ])
    async def test_content_type_detection(self, file_tool, filename, expected_content_type):
        """Test content type is correctly detected from filename."""
        await file_tool.write_file(filename, "test content")

        # Verify correct content type was used
        call_args = file_tool.taskspace.store_artifact.call_args
        assert call_args[1]["content_type"] == expected_content_type
        assert call_args[1]["metadata"]["content_type"] == expected_content_type


class TestFileToolTaskIntegration:
    """Test FileTool integration with TaskExecutor and proper task taskspace paths."""

    def test_create_file_tool_function(self):
        """Test create_file_tool factory function creates correctly configured tool."""
        with tempfile.TemporaryDirectory() as temp_dir:
            taskspace_path = Path(temp_dir) / "task_123"

            tool = create_file_tool(str(taskspace_path))

            assert isinstance(tool, FileTool)
            assert isinstance(tool.taskspace, TaskspaceStorage)
            assert tool.taskspace.get_taskspace_path() == taskspace_path

    async def test_task_specific_taskspace_isolation(self):
        """Test that different tasks get isolated taskspaces."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create two different task taskspaces
            task1_path = Path(temp_dir) / "task_abc123"
            task2_path = Path(temp_dir) / "task_def456"

            tool1 = create_file_tool(str(task1_path))
            tool2 = create_file_tool(str(task2_path))

            # Write files to each taskspace
            await tool1.write_file("test.md", "Task 1 content")
            await tool2.write_file("test.md", "Task 2 content")

            # Verify isolation - each task should only see its own files
            content1 = await tool1.read_file("test.md")
            content2 = await tool2.read_file("test.md")

            assert "Task 1 content" in content1
            assert "Task 2 content" in content2
            assert task1_path.exists()
            assert task2_path.exists()


class TestFileToolErrorHandling:
    """Test FileTool error handling and edge cases."""

    @pytest.fixture
    def failing_taskspace(self):
        """Create taskspace that fails operations for testing error handling."""
        mock = MagicMock()
        mock.store_artifact = AsyncMock(return_value=StorageResult(
            success=False,
            error="Storage failed"
        ))
        mock.get_artifact = AsyncMock(return_value=None)
        mock.list_artifacts = AsyncMock(side_effect=Exception("Network error"))
        return mock

    @pytest.fixture
    def file_tool(self, failing_taskspace):
        """Create FileTool with failing taskspace."""
        return FileTool(failing_taskspace)

    async def test_write_file_storage_failure(self, file_tool):
        """Test write_file handles storage failures gracefully."""
        result = await file_tool.write_file("test.md", "content")

        assert "❌ Failed to write file" in result
        assert "Storage failed" in result

    async def test_read_file_not_found(self, file_tool):
        """Test read_file handles missing files gracefully."""
        result = await file_tool.read_file("nonexistent.md")

        assert "❌ File not found" in result
        assert "nonexistent.md" in result

    async def test_list_files_exception_handling(self, file_tool):
        """Test list_files handles exceptions gracefully."""
        result = await file_tool.list_files()

        assert "❌ Error listing files" in result
        assert "Network error" in result


class TestFileToolDirectoryOperations:
    """Test FileTool directory operations use taskspace file_storage correctly."""

    @pytest.fixture
    def mock_taskspace(self):
        """Create mock taskspace with file_storage."""
        mock = MagicMock()
        mock.file_storage = MagicMock()
        mock.file_storage.create_directory = AsyncMock(return_value=StorageResult(success=True))
        mock.file_storage.list_directory = AsyncMock(return_value=[])
        return mock

    @pytest.fixture
    def file_tool(self, mock_taskspace):
        """Create FileTool with mock taskspace."""
        return FileTool(mock_taskspace)

    async def test_create_directory_uses_file_storage(self, file_tool):
        """Test create_directory uses taskspace.file_storage correctly."""
        result = await file_tool.create_directory("reports")

        file_tool.taskspace.file_storage.create_directory.assert_called_once_with("reports")
        assert "✅ Successfully created directory" in result

    async def test_list_directory_uses_file_storage(self, file_tool):
        """Test list_directory uses taskspace.file_storage correctly."""
        result = await file_tool.list_directory("reports")

        file_tool.taskspace.file_storage.list_directory.assert_called_once_with("reports")
        assert "📂 Directory 'reports' is empty" in result


class TestFileToolIntegrationReal:
    """Integration tests with real taskspace storage (slower but comprehensive)."""

    @pytest.fixture
    async def real_taskspace(self):
        """Create real taskspace storage for integration testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            taskspace_path = Path(temp_dir) / "integration_test"
            storage = StorageFactory.create_taskspace_storage(taskspace_path, use_git_artifacts=False)
            yield storage

    @pytest.fixture
    def file_tool(self, real_taskspace):
        """Create FileTool with real taskspace storage."""
        return FileTool(real_taskspace)

    async def test_full_file_lifecycle(self, file_tool):
        """Test complete file lifecycle: write, read, list, check existence, delete."""
        # Write file
        write_result = await file_tool.write_file("lifecycle_test.md", "# Test Content")
        assert "✅ Successfully wrote" in write_result

        # Check existence
        exists_result = await file_tool.file_exists("lifecycle_test.md")
        assert "✅ File exists" in exists_result

        # Read file
        read_result = await file_tool.read_file("lifecycle_test.md")
        assert "# Test Content" in read_result

        # List files
        list_result = await file_tool.list_files()
        assert "lifecycle_test.md" in list_result

        # Delete file
        delete_result = await file_tool.delete_file("lifecycle_test.md")
        assert "✅ Successfully deleted" in delete_result

        # Verify deletion
        exists_after_delete = await file_tool.file_exists("lifecycle_test.md")
        assert "❌ File does not exist" in exists_after_delete

    async def test_taskspace_organization(self, file_tool):
        """Test that files are properly organized in taskspace structure."""
        # Create directories and files
        await file_tool.create_directory("reports")
        await file_tool.create_directory("data")
        await file_tool.write_file("report.md", "# Main Report")

        # List taskspace contents
        list_result = await file_tool.list_directory("")

        # Verify proper organization
        assert "reports" in list_result or "📁 reports" in list_result
        assert "data" in list_result or "📁 data" in list_result

        # Verify file is accessible
        files_result = await file_tool.list_files()
        assert "report.md" in files_result


class TestFileTool:
    """Test FileTool behavior - defining expected correct behavior."""

    def setup_method(self):
        """Setup test environment with proper taskspace."""
        self.task_id = "test_task_123"
        self.taskspace_path = Path("/tmp/test_taskspace")

        # Create mock taskspace storage that behaves correctly
        self.taskspace = Mock(spec=TaskspaceStorage)
        self.taskspace.task_id = self.task_id
        self.taskspace.base_path = self.taskspace_path
        self.taskspace.artifacts_dir = self.taskspace_path / self.task_id / "artifacts"

        # FileTool should receive a properly configured taskspace
        self.file_tool = FileTool(taskspace_storage=self.taskspace)

    def test_write_file_stores_in_correct_location(self):
        """Files should be stored in taskspace/{task_id}/artifacts/ directory."""
        filename = "test_report.md"
        content = "# Test Report\n\nThis is a test report."

        # Expected behavior: file should be stored in artifacts directory
        expected_path = self.taskspace.artifacts_dir / filename

        # Mock the taskspace storage method
        self.taskspace.store_artifact = Mock()

        # Execute the tool
        result = self.file_tool.write_file(filename, content)

        # Verify correct behavior
        self.taskspace.store_artifact.assert_called_once_with(filename, content)
        assert result["status"] == "success"
        assert result["filename"] == filename
        assert "successfully written" in result["message"].lower()

    def test_write_file_no_double_extensions(self):
        """Files should not get double extensions when stored."""
        filename = "document.md"
        content = "Some content"

        # Mock taskspace to verify the exact filename passed
        self.taskspace.store_artifact = Mock()

        self.file_tool.write_file(filename, content)

        # The taskspace should receive the original filename, not "document.md.md"
        self.taskspace.store_artifact.assert_called_once_with("document.md", content)

    def test_read_file_from_artifacts(self):
        """Files should be read from the artifacts directory."""
        filename = "existing_file.txt"
        expected_content = "File content here"

        # Mock taskspace to return content
        self.taskspace.read_artifact = Mock(return_value=expected_content)

        result = self.file_tool.read_file(filename)

        # Verify correct behavior
        self.taskspace.read_artifact.assert_called_once_with(filename)
        assert result["content"] == expected_content
        assert result["filename"] == filename

    def test_read_nonexistent_file_handling(self):
        """Reading non-existent files should return appropriate error."""
        filename = "nonexistent.txt"

        # Mock taskspace to raise FileNotFoundError
        self.taskspace.read_artifact = Mock(side_effect=FileNotFoundError("File not found"))

        result = self.file_tool.read_file(filename)

        # Should handle error gracefully
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    def test_list_files_returns_artifacts(self):
        """List files should return all artifacts in the taskspace."""
        expected_files = ["report.md", "data.json", "summary.txt"]

        # Mock taskspace to return file list
        self.taskspace.list_artifacts = Mock(return_value=expected_files)

        result = self.file_tool.list_files()

        # Verify correct behavior
        self.taskspace.list_artifacts.assert_called_once()
        assert result["files"] == expected_files
        assert len(result["files"]) == 3

    def test_taskspace_summary_integration(self):
        """FileTool should integrate properly with taskspace summary."""
        # Mock taskspace methods
        self.taskspace.list_artifacts = Mock(return_value=["report.md", "data.json"])
        self.taskspace.get_storage_info = Mock(return_value={"total_files": 2, "total_size": 1024})

        # This should work without errors
        files = self.file_tool.list_files()

        assert len(files["files"]) == 2
        assert "report.md" in files["files"]
        assert "data.json" in files["files"]

    def test_file_tool_initialization(self):
        """FileTool should initialize correctly with taskspace."""
        # Should accept taskspace_storage parameter
        tool = FileTool(taskspace_storage=self.taskspace)

        assert tool.taskspace == self.taskspace
        assert hasattr(tool, 'write_file')
        assert hasattr(tool, 'read_file')
        assert hasattr(tool, 'list_files')

    def test_file_content_encoding(self):
        """Files should handle different content encodings properly."""
        filename = "unicode_test.txt"
        content = "Test with émojis: 🚀 and special chars: ñáéíóú"

        self.taskspace.store_artifact = Mock()

        result = self.file_tool.write_file(filename, content)

        # Should handle unicode content without issues
        self.taskspace.store_artifact.assert_called_once_with(filename, content)
        assert result["status"] == "success"


# Run the tests
if __name__ == "__main__":
    import asyncio

    async def run_basic_test():
        """Quick test runner for development."""
        with tempfile.TemporaryDirectory() as temp_dir:
            taskspace_path = Path(temp_dir) / "test_task"
            storage = StorageFactory.create_taskspace_storage(taskspace_path)
            tool = FileTool(storage)

            # Test basic operations
            write_result = await tool.write_file("test.md", "# Test")
            print(f"Write result: {write_result}")

            read_result = await tool.read_file("test.md")
            print(f"Read result: {read_result}")

            list_result = await tool.list_files()
            print(f"List result: {list_result}")

    asyncio.run(run_basic_test())
