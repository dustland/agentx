"""
Tests for WorkspaceStorage.

These tests define the expected correct behavior for workspace
management and storage abstraction in the AgentX framework.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from agentx.storage.workspace import WorkspaceStorage
from agentx.storage.git_storage import GitArtifactStorage
from agentx.storage.interfaces import StorageBackend


class TestWorkspaceStorageInitialization:
    """Test WorkspaceStorage initialization."""
    
    def test_workspace_storage_requires_task_id(self):
        """WorkspaceStorage should require a task_id."""
        file_storage = Mock(spec=StorageBackend)
        
        workspace = WorkspaceStorage(
            task_id="test_task",
            base_path=Path("/tmp"),
            file_storage=file_storage
        )
        
        assert workspace.task_id == "test_task"
        assert workspace.file_storage is file_storage
    
    def test_workspace_storage_creates_directories(self):
        """WorkspaceStorage should create necessary directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_storage = Mock(spec=StorageBackend)
            workspace = WorkspaceStorage(
                task_id="test_task",
                base_path=Path(temp_dir),
                file_storage=file_storage
            )
            
            # Should create task-specific directory
            expected_path = Path(temp_dir) / "test_task"
            assert expected_path.exists()
            assert expected_path.is_dir()


class TestWorkspaceStorageArtifacts:
    """Test artifact management operations."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.task_id = "test_task"
        self.file_storage = Mock(spec=StorageBackend)
        self.file_storage.store = AsyncMock()
        self.file_storage.retrieve = AsyncMock()
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
    async def test_store_artifact_delegates_to_file_storage(self):
        """store_artifact should delegate to file storage."""
        self.file_storage.store.return_value = {
            "success": True,
            "path": "artifacts/test.txt"
        }
        
        result = await self.workspace.store_artifact(
            "test.txt", 
            "content", 
            content_type="text/plain"
        )
        
        self.file_storage.store.assert_called_once_with(
            "test.txt", 
            "content", 
            content_type="text/plain"
        )
        assert result["success"] is True
        assert result["path"] == "artifacts/test.txt"
    
    @pytest.mark.asyncio
    async def test_get_artifact_delegates_to_file_storage(self):
        """get_artifact should delegate to file storage."""
        self.file_storage.retrieve.return_value = {
            "success": True,
            "content": "file content",
            "metadata": {"content_type": "text/plain"}
        }
        
        result = await self.workspace.get_artifact("test.txt")
        
        self.file_storage.retrieve.assert_called_once_with("test.txt")
        assert result["success"] is True
        assert result["content"] == "file content"
    
    @pytest.mark.asyncio
    async def test_list_artifacts_delegates_to_file_storage(self):
        """list_artifacts should delegate to file storage."""
        self.file_storage.list_files.return_value = {
            "success": True,
            "files": [
                {"name": "file1.txt", "size": 100},
                {"name": "file2.md", "size": 200}
            ]
        }
        
        result = await self.workspace.list_artifacts()
        
        self.file_storage.list_files.assert_called_once()
        assert result["success"] is True
        assert len(result["files"]) == 2
    
    @pytest.mark.asyncio
    async def test_store_artifact_handles_storage_errors(self):
        """store_artifact should handle storage errors gracefully."""
        self.file_storage.store.side_effect = Exception("Storage failed")
        
        result = await self.workspace.store_artifact("test.txt", "content")
        
        assert result["success"] is False
        assert "error" in result
        assert "Storage failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_artifact_handles_storage_errors(self):
        """get_artifact should handle storage errors gracefully."""
        self.file_storage.retrieve.side_effect = Exception("Retrieval failed")
        
        result = await self.workspace.get_artifact("test.txt")
        
        assert result["success"] is False
        assert "error" in result
        assert "Retrieval failed" in result["error"]


class TestWorkspaceStorageDirectories:
    """Test directory operations."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.task_id = "test_task"
        self.file_storage = Mock(spec=StorageBackend)
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
    async def test_list_directory_lists_contents(self):
        """list_directory should list directory contents."""
        # Create test structure
        workspace_path = self.temp_dir / self.task_id
        test_dir = workspace_path / "test_dir"
        test_dir.mkdir(parents=True)
        
        # Create some files and subdirs
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.md").write_text("content2")
        (test_dir / "subdir").mkdir()
        
        result = await self.workspace.list_directory("test_dir")
        
        assert result["success"] is True
        assert len(result["items"]) == 3
        
        # Verify items
        item_names = [item["name"] for item in result["items"]]
        assert "file1.txt" in item_names
        assert "file2.md" in item_names
        assert "subdir" in item_names
    
    @pytest.mark.asyncio
    async def test_list_directory_handles_nonexistent_directory(self):
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
        
        # Verify summary includes directory information
        assert summary["total_directories"] == 2
        assert "reports" in summary["directories"]
        assert "data" in summary["directories"]
    
    @pytest.mark.asyncio
    async def test_get_workspace_summary_handles_empty_workspace(self):
        """get_workspace_summary should handle empty workspace."""
        self.file_storage.list_files.return_value = {
            "success": True,
            "files": []
        }
        
        result = await self.workspace.get_workspace_summary()
        
        assert result["success"] is True
        summary = result["summary"]
        assert summary["total_files"] == 0
        assert summary["total_size"] == 0
        assert summary["total_directories"] == 0
    
    @pytest.mark.asyncio
    async def test_get_workspace_summary_handles_storage_errors(self):
        """get_workspace_summary should handle storage errors gracefully."""
        self.file_storage.list_files.side_effect = Exception("Storage error")
        
        result = await self.workspace.get_workspace_summary()
        
        assert result["success"] is False
        assert "error" in result
        assert "Storage error" in result["error"]


class TestWorkspaceStorageIntegration:
    """Test WorkspaceStorage integration with real storage."""
    
    def setup_method(self):
        """Setup test environment with real storage."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.task_id = "integration_test"
        self.file_storage = GitArtifactStorage(
            base_path=self.temp_dir,
            task_id=self.task_id
        )
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
    async def test_full_workspace_lifecycle_integration(self):
        """Test complete workspace operations with real storage."""
        # Store an artifact
        store_result = await self.workspace.store_artifact(
            "test_report.md",
            "# Test Report\n\nThis is a test report.",
            content_type="text/markdown"
        )
        assert store_result.success is True
        
        # Retrieve the artifact
        get_result = await self.workspace.get_artifact("test_report.md")
        assert get_result == "# Test Report\n\nThis is a test report."
        
        # List artifacts
        list_result = await self.workspace.list_artifacts()
        assert len(list_result) >= 1
        artifact_names = [a["name"] for a in list_result]
        assert "test_report.md" in artifact_names
        
        # Create a directory manually (directories are created automatically when files are written)
        analysis_dir = self.temp_dir / self.task_id / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # List directory contents
        list_dir_result = await self.workspace.list_directory(".")
        assert list_dir_result["success"] is True
        
        # Get workspace summary
        summary_result = await self.workspace.get_workspace_summary()
        assert "error" not in summary_result
        assert summary_result["total_artifacts"] >= 1
    
    @pytest.mark.asyncio
    async def test_workspace_isolation_integration(self):
        """Test that different workspaces are properly isolated."""
        # Create second workspace
        workspace2 = WorkspaceStorage(
            task_id="other_task",
            base_path=self.temp_dir,
            file_storage=GitArtifactStorage(
                base_path=self.temp_dir,
                task_id="other_task"
            )
        )
        
        # Store different artifacts in each workspace
        await self.workspace.store_artifact("file1.txt", "content1")
        await workspace2.store_artifact("file2.txt", "content2")
        
        # Verify isolation
        files1 = await self.workspace.list_artifacts()
        files2 = await workspace2.list_artifacts()
        
        assert len(files1) == 1
        assert len(files2) == 1
        assert files1[0]["name"] == "file1.txt"
        assert files2[0]["name"] == "file2.txt"
        
        # Verify each workspace can't access the other's files
        get_result1 = await self.workspace.get_artifact("file2.txt")
        get_result2 = await workspace2.get_artifact("file1.txt")
        
        assert get_result1 is None
        assert get_result2 is None
    
    @pytest.mark.asyncio
    async def test_workspace_persistence_integration(self):
        """Test that workspace data persists across instances."""
        # Store data in workspace
        await self.workspace.store_artifact("persistent.txt", "persistent data")
        
        # Create new workspace instance with same task_id
        workspace2 = WorkspaceStorage(
            task_id=self.task_id,
            base_path=self.temp_dir,
            file_storage=GitArtifactStorage(
                base_path=self.temp_dir,
                task_id=self.task_id
            )
        )
        
        # Verify data is accessible from new instance
        get_result = await workspace2.get_artifact("persistent.txt")
        assert get_result == "persistent data"


class TestWorkspaceStorageErrorHandling:
    """Test error handling scenarios."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.task_id = "error_test"
        self.file_storage = Mock(spec=StorageBackend)
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
    async def test_workspace_handles_storage_backend_failures(self):
        """Workspace should handle storage backend failures gracefully."""
        # Mock various storage failures
        self.file_storage.store.side_effect = Exception("Backend failure")
        self.file_storage.retrieve.side_effect = Exception("Backend failure")
        self.file_storage.list_files.side_effect = Exception("Backend failure")
        
        # Test all operations handle the failure gracefully
        store_result = await self.workspace.store_artifact("test.txt", "content")
        get_result = await self.workspace.get_artifact("test.txt")
        list_result = await self.workspace.list_artifacts()
        summary_result = await self.workspace.get_workspace_summary()
        
        assert not store_result.success
        assert get_result is None
        assert list_result == []
        assert "error" in summary_result 