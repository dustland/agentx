"""
Comprehensive tests for FileTool - Testing project_storage abstraction and artifact storage.

These tests systematically verify that FileTool properly uses the project_storage layer
instead of bypassing it, and handles file operations correctly.
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
    async def project_storage(self):
        """Create a test project storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_task_id"
            storage = ProjectStorageFactory.create_project_storage(project_path)
            yield storage

    @pytest.fixture
    def file_tool(self, project_storage):
        """Create FileTool with test project storage."""
        return FileTool(project_storage)

    def test_file_tool_initialization(self, project_storage):
        """Test FileTool initializes with project storage."""
        tool = FileTool(project_storage)
        assert tool.project_storage == project_storage
        assert tool.project_storage.get_project_path() == project_storage.get_project_path()

    async def test_write_file_uses_project_storage_layer(self, file_tool):
        """Test write_file uses project_storage.store_artifact() not direct file operations."""
        # Mock the project_storage storage
        file_tool.project_storage.store_artifact = AsyncMock(return_value=StorageResult(
            success=True,
            path="test.md",
            size=100,
            data={"version": "abc123"}
        ))

        result = await file_tool.write_file("test.md", "# Test Content")

        # Verify project_storage layer was used
        file_tool.project_storage.store_artifact.assert_called_once_with(
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

    async def test_read_file_uses_project_storage_layer(self, file_tool):
        """Test read_file uses project_storage.get_artifact() not direct file operations."""
        # Mock the project_storage storage
        file_tool.project_storage.get_artifact = AsyncMock(return_value="# Test Content")

        result = await file_tool.read_file("test.md")

        # Verify project_storage layer was used
        file_tool.project_storage.get_artifact.assert_called_once_with("test.md", None)

        assert "📄 Contents of test.md:" in result
        assert "# Test Content" in result

    async def test_list_files_uses_project_storage_layer(self, file_tool):
        """Test list_files uses project_storage.list_artifacts() not direct file operations."""
        # Mock the project_storage storage
        file_tool.project_storage.list_artifacts = AsyncMock(return_value=[
            {"name": "test1.md", "size": 100, "created_at": "2025-01-01"},
            {"name": "test2.md", "size": 200, "created_at": "2025-01-02"}
        ])

        result = await file_tool.list_files()

        # Verify project_storage layer was used
        file_tool.project_storage.list_artifacts.assert_called_once()

        assert "📂 Project files:" in result
        assert "test1.md" in result
        assert "test2.md" in result


class TestFileToolContentTypes:
    """Test FileTool content type handling and extension logic."""

    @pytest.fixture
    def mock_project_storage(self):
        """Create mock project storage."""
        mock = MagicMock()
        mock.store_artifact = AsyncMock(return_value=StorageResult(success=True))
        return mock

    @pytest.fixture
    def file_tool(self, mock_project_storage):
        """Create FileTool with mock project storage."""
        return FileTool(mock_project_storage)

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
        call_args = file_tool.project_storage.store_artifact.call_args
        assert call_args[1]["content_type"] == expected_content_type
        assert call_args[1]["metadata"]["content_type"] == expected_content_type


class TestFileToolTaskIntegration:
    """Test FileTool integration with TaskExecutor and proper task project_storage paths."""

    # Tests that use create_file_tool have been removed since the function no longer exists
    pass


class TestFileToolErrorHandling:
    """Test FileTool error handling and edge cases."""

    @pytest.fixture
    def failing_project_storage(self):
        """Create project storage that fails operations for testing error handling."""
        mock = MagicMock()
        mock.store_artifact = AsyncMock(return_value=StorageResult(
            success=False,
            error="Storage failed"
        ))
        mock.get_artifact = AsyncMock(return_value=None)
        mock.list_artifacts = AsyncMock(side_effect=Exception("Network error"))
        return mock

    @pytest.fixture
    def file_tool(self, failing_project_storage):
        """Create FileTool with failing project storage."""
        return FileTool(failing_project_storage)

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
    """Test FileTool directory operations use project_storage file_storage correctly."""

    @pytest.fixture
    def mock_taskspace(self):
        """Create mock project_storage with file_storage."""
        mock = MagicMock()
        mock.file_storage = MagicMock()
        mock.file_storage.create_directory = AsyncMock(return_value=StorageResult(success=True))
        mock.file_storage.list_directory = AsyncMock(return_value=[])
        return mock

    @pytest.fixture
    def file_tool(self, mock_project_storage):
        """Create FileTool with mock project storage."""
        return FileTool(mock_project_storage)

    async def test_create_directory_uses_file_storage(self, file_tool):
        """Test create_directory uses project_storage.file_storage correctly."""
        result = await file_tool.create_directory("reports")

        file_tool.project_storage.file_storage.create_directory.assert_called_once_with("reports")
        assert "✅ Successfully created directory" in result

    async def test_list_directory_uses_file_storage(self, file_tool):
        """Test list_directory uses project_storage.file_storage correctly."""
        result = await file_tool.list_directory("reports")

        file_tool.project_storage.file_storage.list_directory.assert_called_once_with("reports")
        assert "📂 Directory 'reports' is empty" in result


class TestFileToolIntegrationReal:
    """Integration tests with real project_storage storage (slower but comprehensive)."""

    @pytest.fixture
    async def real_project_storage(self):
        """Create real project storage for integration testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "integration_test"
            storage = ProjectStorageFactory.create_project_storage(project_path, use_git_artifacts=False)
            yield storage

    @pytest.fixture
    def file_tool(self, real_project_storage):
        """Create FileTool with real project storage."""
        return FileTool(real_project_storage)

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

    async def test_project_storage_organization(self, file_tool):
        """Test that files are properly organized in project storage structure."""
        # Create directories and files
        await file_tool.create_directory("reports")
        await file_tool.create_directory("data")
        await file_tool.write_file("report.md", "# Main Report")

        # List project storage contents
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
        """Setup test environment with proper project storage."""
        self.task_id = "test_task_123"
        self.project_path = Path("/tmp/test_taskspace")

        # Create mock project storage that behaves correctly
        self.project_storage = Mock(spec=ProjectStorage)
        self.project_storage.task_id = self.task_id
        self.project_storage.base_path = self.project_path
        self.project_storage.artifacts_dir = self.project_path / self.task_id / "artifacts"

        # FileTool should receive a properly configured project storage
        self.file_tool = FileTool(project_storage=self.project_storage)

    def test_write_file_stores_in_correct_location(self):
        """Files should be stored in project storage/{task_id}/artifacts/ directory."""
        filename = "test_report.md"
        content = "# Test Report\n\nThis is a test report."

        # Expected behavior: file should be stored in artifacts directory
        expected_path = self.project_storage.artifacts_dir / filename

        # Mock the project_storage storage method
        self.project_storage.store_artifact = Mock()

        # Execute the tool
        result = self.file_tool.write_file(filename, content)

        # Verify correct behavior
        self.project_storage.store_artifact.assert_called_once_with(filename, content)
        assert result["status"] == "success"
        assert result["filename"] == filename
        assert "successfully written" in result["message"].lower()

    def test_write_file_no_double_extensions(self):
        """Files should not get double extensions when stored."""
        filename = "document.md"
        content = "Some content"

        # Mock project_storage to verify the exact filename passed
        self.project_storage.store_artifact = Mock()

        self.file_tool.write_file(filename, content)

        # The project_storage should receive the original filename, not "document.md.md"
        self.project_storage.store_artifact.assert_called_once_with("document.md", content)

    def test_read_file_from_artifacts(self):
        """Files should be read from the artifacts directory."""
        filename = "existing_file.txt"
        expected_content = "File content here"

        # Mock project_storage to return content
        self.project_storage.read_artifact = Mock(return_value=expected_content)

        result = self.file_tool.read_file(filename)

        # Verify correct behavior
        self.project_storage.read_artifact.assert_called_once_with(filename)
        assert result["content"] == expected_content
        assert result["filename"] == filename

    def test_read_nonexistent_file_handling(self):
        """Reading non-existent files should return appropriate error."""
        filename = "nonexistent.txt"

        # Mock project_storage to raise FileNotFoundError
        self.project_storage.read_artifact = Mock(side_effect=FileNotFoundError("File not found"))

        result = self.file_tool.read_file(filename)

        # Should handle error gracefully
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    def test_list_files_returns_artifacts(self):
        """List files should return all artifacts in the project_storage."""
        expected_files = ["report.md", "data.json", "summary.txt"]

        # Mock project_storage to return file list
        self.project_storage.list_artifacts = Mock(return_value=expected_files)

        result = self.file_tool.list_files()

        # Verify correct behavior
        self.project_storage.list_artifacts.assert_called_once()
        assert result["files"] == expected_files
        assert len(result["files"]) == 3

    def test_project_storage_summary_integration(self):
        """FileTool should integrate properly with project storage summary."""
        # Mock project_storage methods
        self.project_storage.list_artifacts = Mock(return_value=["report.md", "data.json"])
        self.project_storage.get_storage_info = Mock(return_value={"total_files": 2, "total_size": 1024})

        # This should work without errors
        files = self.file_tool.list_files()

        assert len(files["files"]) == 2
        assert "report.md" in files["files"]
        assert "data.json" in files["files"]

    def test_file_tool_initialization(self):
        """FileTool should initialize correctly with project storage."""
        # Should accept project_storage parameter
        tool = FileTool(project_storage=self.project_storage)

        assert tool.project_storage == self.project_storage
        assert hasattr(tool, 'write_file')
        assert hasattr(tool, 'read_file')
        assert hasattr(tool, 'list_files')

    def test_file_content_encoding(self):
        """Files should handle different content encodings properly."""
        filename = "unicode_test.txt"
        content = "Test with émojis: 🚀 and special chars: ñáéíóú"

        self.project_storage.store_artifact = Mock()

        result = self.file_tool.write_file(filename, content)

        # Should handle unicode content without issues
        self.project_storage.store_artifact.assert_called_once_with(filename, content)
        assert result["status"] == "success"


# Run the tests
if __name__ == "__main__":
    import asyncio

    async def run_basic_test():
        """Quick test runner for development."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_task"
            storage = ProjectStorageFactory.create_project_storage(project_path)
            tool = FileTool(storage)

            # Test basic operations
            write_result = await tool.write_file("test.md", "# Test")
            print(f"Write result: {write_result}")

            read_result = await tool.read_file("test.md")
            print(f"Read result: {read_result}")

            list_result = await tool.list_files()
            print(f"List result: {list_result}")

    asyncio.run(run_basic_test())
