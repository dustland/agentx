"""
Tests for GitStorage double extension bug fix.

This test file specifically targets the bug where GitStorage was adding
.md extension to files that already had .md in their name, resulting in
files like "report.md.md".
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from vibex.storage.git_storage import GitArtifactStorage
from vibex.storage.interfaces import StorageResult


class TestGitStorageExtensionHandling:
    """Test GitStorage extension handling to prevent double extensions."""

    @pytest.fixture
    def git_storage(self):
        """Create GitArtifactStorage for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_git_taskspace"
            # Mock GitPython to avoid actual git operations in unit tests
            with patch('vibex.storage.git_storage.GIT_AVAILABLE', True), \
                 patch('vibex.storage.git_storage.Repo') as mock_repo:

                # Mock the repo initialization
                mock_repo_instance = mock_repo.return_value
                mock_repo_instance.config_writer.return_value.__enter__ = lambda x: mock_repo_instance.config_writer.return_value
                mock_repo_instance.config_writer.return_value.__exit__ = lambda *args: None
                mock_repo_instance.config_writer.return_value.set_value = lambda *args: None

                storage = GitArtifactStorage(project_path)
                storage.repo = mock_repo_instance  # Use the mock
                yield storage

    def test_should_add_extension_with_existing_extension(self, git_storage):
        """Test that files with extensions don't get additional extensions."""
        # Test various files that already have extensions
        test_cases = [
            ("report.md", "text/markdown", ""),
            ("data.json", "application/json", ""),
            ("script.py", "text/python", ""),
            ("page.html", "text/html", ""),
            ("style.css", "text/css", ""),
        ]

        for filename, content_type, expected_extension in test_cases:
            extension = git_storage._should_add_extension(filename, content_type)
            assert extension == expected_extension, f"File {filename} should not get additional extension, got {extension}"

    def test_should_add_extension_without_existing_extension(self, git_storage):
        """Test that files without extensions get appropriate extensions."""
        test_cases = [
            ("report", "text/markdown", ".md"),
            ("data", "application/json", ".json"),
            ("script", "text/python", ".py"),
            ("page", "text/html", ".html"),
            ("readme", "text/plain", ".txt"),
        ]

        for filename, content_type, expected_extension in test_cases:
            extension = git_storage._should_add_extension(filename, content_type)
            assert extension == expected_extension, f"File {filename} should get {expected_extension}, got {extension}"

    def test_extension_for_content_type_mapping(self, git_storage):
        """Test content type to extension mapping."""
        test_cases = [
            ("text/plain", ".txt"),
            ("text/markdown", ".md"),
            ("application/json", ".json"),
            ("text/python", ".py"),
            ("text/javascript", ".js"),
            ("text/typescript", ".ts"),
            ("text/html", ".html"),
            ("text/css", ".css"),
            ("text/yaml", ".yaml"),
            ("text/xml", ".xml"),
            ("unknown/type", ".txt"),  # fallback
        ]

        for content_type, expected_extension in test_cases:
            extension = git_storage._get_extension_for_content_type(content_type)
            assert extension == expected_extension, f"Content type {content_type} should map to {expected_extension}, got {extension}"

    @patch('vibex.storage.git_storage.asyncio.get_event_loop')
    async def test_store_artifact_no_double_extension(self, mock_get_loop, git_storage):
        """Test storing artifacts doesn't create double extensions."""
        # Mock the asyncio executor
        mock_loop = mock_get_loop.return_value
        mock_loop.run_in_executor.return_value = "abc123"  # mock commit hash

        # Mock file operations
        with patch.object(git_storage.artifacts_path, 'mkdir'), \
             patch('pathlib.Path.write_text'), \
             patch('pathlib.Path.write_bytes'):

            # Test storing a markdown file
            result = await git_storage.store_artifact(
                name="report.md",
                content="# Test Report",
                content_type="text/markdown"
            )

            # Verify the result shows correct path without double extension
            assert result.success
            assert result.path == "artifacts/report.md"  # Not "artifacts/report.md.md"

    def test_double_extension_prevention_edge_cases(self, git_storage):
        """Test edge cases for extension handling."""
        edge_cases = [
            # Filename with multiple dots
            ("my.file.with.dots.md", "text/markdown", ""),
            ("version.1.2.json", "application/json", ""),

            # Filename with extension in unusual positions
            ("md.in.middle", "text/markdown", ".md"),
            ("json.start", "application/json", ".json"),

            # Empty or unusual filenames
            ("", "text/markdown", ".md"),
            ("no_extension", "text/markdown", ".md"),
        ]

        for filename, content_type, expected_extension in edge_cases:
            extension = git_storage._should_add_extension(filename, content_type)
            assert extension == expected_extension, f"Edge case {filename} should get {expected_extension}, got {extension}"


class TestGitStorageIntegrationWithFileTool:
    """Test GitStorage integration with FileTool to ensure no double extensions in real usage."""

    @pytest.fixture
    def taskspace_with_git(self):
        """Create project_storage storage with Git artifacts enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_taskspace"

            # Mock GitPython for testing
            with patch('vibex.storage.git_storage.GIT_AVAILABLE', True), \
                 patch('vibex.storage.git_storage.Repo') as mock_repo:

                mock_repo_instance = mock_repo.return_value
                mock_repo_instance.config_writer.return_value.__enter__ = lambda x: mock_repo_instance.config_writer.return_value
                mock_repo_instance.config_writer.return_value.__exit__ = lambda *args: None
                mock_repo_instance.config_writer.return_value.set_value = lambda *args: None

                from vibex.storage.factory import StorageFactory
                storage = StorageFactory.create_project_storage_storage(project_path, use_git_artifacts=True)
                storage.artifact_storage.repo = mock_repo_instance  # Use mock
                yield storage

    @patch('vibex.storage.git_storage.asyncio.get_event_loop')
    async def test_file_tool_with_git_storage_no_double_extensions(self, mock_get_loop, taskspace_with_git):
        """Test FileTool with GitStorage doesn't create double extensions."""
        from vibex.builtin_tools.file import FileTool

        # Mock the asyncio executor
        mock_loop = mock_get_loop.return_value
        mock_loop.run_in_executor.return_value = "abc123"  # mock commit hash

        file_tool = FileTool(taskspace_with_git)

        # Mock file operations
        with patch.object(taskspace_with_git.artifact_storage.artifacts_path, 'mkdir'), \
             patch('pathlib.Path.write_text'), \
             patch('pathlib.Path.write_bytes'):

            # Test writing files with extensions
            test_files = [
                ("report.md", "# Report Content"),
                ("data.json", '{"key": "value"}'),
                ("script.py", "print('hello')"),
                ("page.html", "<h1>Hello</h1>"),
            ]

            for filename, content in test_files:
                result = await file_tool.write_file(filename, content)

                # Should succeed without double extension errors
                assert "✅ Successfully wrote" in result
                assert filename in result
                # Should not contain double extensions in logs or output
                assert ".md.md" not in result
                assert ".json.json" not in result
                assert ".py.py" not in result
                assert ".html.html" not in result


class TestGitStorageErrorScenarios:
    """Test GitStorage error handling related to extension processing."""

    @pytest.fixture
    def git_storage(self):
        """Create GitArtifactStorage for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_git_taskspace"
            with patch('vibex.storage.git_storage.GIT_AVAILABLE', True), \
                 patch('vibex.storage.git_storage.Repo') as mock_repo:

                mock_repo_instance = mock_repo.return_value
                mock_repo_instance.config_writer.return_value.__enter__ = lambda x: mock_repo_instance.config_writer.return_value
                mock_repo_instance.config_writer.return_value.__exit__ = lambda *args: None
                mock_repo_instance.config_writer.return_value.set_value = lambda *args: None

                storage = GitArtifactStorage(project_path)
                storage.repo = mock_repo_instance
                yield storage

    def test_invalid_content_types(self, git_storage):
        """Test handling of invalid or unknown content types."""
        invalid_cases = [
            (None, ".txt"),  # None content type should fallback
            ("", ".txt"),    # Empty content type should fallback
            ("invalid/type", ".txt"),  # Unknown type should fallback
            ("text/", ".txt"),  # Incomplete type should fallback
        ]

        for content_type, expected_extension in invalid_cases:
            extension = git_storage._get_extension_for_content_type(content_type)
            assert extension == expected_extension, f"Invalid content type {content_type} should fallback to {expected_extension}"

    def test_unusual_filenames(self, git_storage):
        """Test handling of unusual filenames."""
        unusual_cases = [
            ("", "text/markdown"),  # Empty filename
            (".", "text/markdown"), # Just a dot
            ("..", "text/markdown"), # Double dot
            ("...md", "text/markdown"), # Multiple leading dots
            ("file.", "text/markdown"), # Trailing dot
        ]

        for filename, content_type in unusual_cases:
            # Should not raise exceptions
            try:
                extension = git_storage._should_add_extension(filename, content_type)
                # Basic sanity check - should return some string
                assert isinstance(extension, str)
            except Exception as e:
                pytest.fail(f"Unusual filename {filename} caused exception: {e}")


class TestGitStorageCorrectBehavior:
    """Test GitArtifactStorage correct behavior - no double extensions, proper paths."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.task_id = "test_task_123"
        self.storage = GitArtifactStorage(
            base_path=self.temp_dir,
            task_id=self.task_id
        )

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_store_file_no_double_extensions(self):
        """Files with extensions should not get double extensions."""
        filename = "report.md"
        content = "# Test Report\n\nContent here"

        # Store the file
        result = await self.storage.store_artifact(filename, content)

        # Verify success
        assert result.success
        assert result.path is not None

        # The actual file should be named correctly (no double extension)
        expected_path = self.temp_dir / self.task_id / "artifacts" / "report.md"
        assert expected_path.exists()
        assert expected_path.name == "report.md"  # NOT "report.md.md"

        # Content should be correct
        assert expected_path.read_text() == content

    @pytest.mark.asyncio
    async def test_store_file_without_extension(self):
        """Files without extensions should work normally."""
        filename = "README"
        content = "This is a readme file"

        result = await self.storage.store_artifact(filename, content)

        assert result.success
        # GitArtifactStorage adds .txt extension to files without extensions
        expected_path = self.temp_dir / self.task_id / "artifacts" / "README.txt"
        assert expected_path.exists()
        assert expected_path.name == "README.txt"
        assert expected_path.read_text() == content

    @pytest.mark.asyncio
    async def test_store_file_multiple_extensions(self):
        """Files with multiple extensions should be handled correctly."""
        filename = "data.json.backup"
        content = '{"test": "data"}'

        result = await self.storage.store_artifact(filename, content)

        assert result.success
        expected_path = self.temp_dir / self.task_id / "artifacts" / "data.json.backup"
        assert expected_path.exists()
        assert expected_path.name == "data.json.backup"
        assert expected_path.read_text() == content

    @pytest.mark.asyncio
    async def test_store_file_correct_directory_structure(self):
        """Files should be stored in the correct directory structure."""
        filename = "test.txt"
        content = "Test content"

        result = await self.storage.store_artifact(filename, content)

        assert result.success

        # Should create proper directory structure
        expected_path = self.temp_dir / self.task_id / "artifacts" / "test.txt"
        assert expected_path.exists()

        # Directory structure should be correct
        assert (self.temp_dir / self.task_id).exists()
        assert (self.temp_dir / self.task_id / "artifacts").exists()

    @pytest.mark.asyncio
    async def test_read_file_correct_path(self):
        """Reading files should use the correct path."""
        filename = "existing.md"
        content = "# Existing File\n\nContent"

        # First store the file
        await self.storage.store_artifact(filename, content)

        # Then read it back
        result = await self.storage.get_artifact(filename)

        assert result is not None
        assert result == content

    @pytest.mark.asyncio
    async def test_list_files_returns_correct_names(self):
        """List files should return original filenames without path manipulation."""
        files = [
            ("report.md", "# Report"),
            ("data.json", '{"key": "value"}'),
            ("notes.txt", "Some notes"),
            ("README", "Read me")
        ]

        # Store multiple files
        for filename, content in files:
            result = await self.storage.store_artifact(filename, content)
            assert result.success

        # List files
        result = await self.storage.list_artifacts()

        assert len(result) == 4

        # GitArtifactStorage adds extensions to files without them
        expected_names = {"report.md", "data.json", "notes.txt", "README.txt"}
        actual_names = {f["name"] for f in result}
        assert actual_names == expected_names

    @pytest.mark.asyncio
    async def test_file_metadata_correct(self):
        """File metadata should be accurate."""
        filename = "test_file.md"
        content = "# Test\n\nThis is a test file with some content."

        await self.storage.store_artifact(filename, content)
        result = await self.storage.list_artifacts()

        assert len(result) == 1

        file_info = result[0]
        assert file_info["name"] == "test_file.md"
        # Size should be available in metadata
        assert file_info["size"] >= 0  # Size is available from metadata or git

    @pytest.mark.asyncio
    async def test_git_integration_works(self):
        """Git operations should work with correct file paths."""
        filename = "versioned.md"
        content = "# Version 1"

        # Store file
        result = await self.storage.store_artifact(filename, content)
        assert result.success

        # Update file
        new_content = "# Version 2\n\nUpdated content"
        result = await self.storage.store_artifact(filename, new_content)
        assert result.success

        # File should have the updated content
        read_result = await self.storage.get_artifact(filename)
        assert read_result is not None
        assert read_result == new_content

    @pytest.mark.asyncio
    async def test_unicode_filenames_and_content(self):
        """Unicode filenames and content should work correctly."""
        filename = "测试文件.md"
        content = "# Test with émojis 🚀\n\nContent with special chars: ñáéíóú"

        result = await self.storage.store_artifact(filename, content)

        assert result.success

        # Read it back
        read_result = await self.storage.get_artifact(filename)
        assert read_result is not None
        assert read_result == content


# Quick test runner for development
if __name__ == "__main__":
    import asyncio

    async def run_extension_test():
        """Quick test for extension handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_taskspace"

            # Test the extension logic directly
            with patch('vibex.storage.git_storage.GIT_AVAILABLE', True), \
                 patch('vibex.storage.git_storage.Repo'):

                storage = GitArtifactStorage(project_path)

                # Test cases
                test_cases = [
                    ("report.md", "text/markdown"),
                    ("report", "text/markdown"),
                    ("data.json", "application/json"),
                    ("data", "application/json"),
                ]

                for filename, content_type in test_cases:
                    extension = storage._should_add_extension(filename, content_type)
                    final_name = f"{filename}{extension}"
                    print(f"{filename} + {content_type} -> {final_name}")

                    # Verify no double extensions
                    assert not final_name.endswith(".md.md")
                    assert not final_name.endswith(".json.json")

    asyncio.run(run_extension_test())
    print("Extension handling tests passed!")
