"""
Integration tests for WorkspaceStorage with real storage backends.
"""

import pytest
import tempfile
from pathlib import Path

from agentx.storage import WorkspaceStorage
from agentx.storage.git_storage import GitArtifactStorage


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

        # Verify data is accessible
        get_result = await workspace2.get_artifact("persistent.txt")
        assert get_result == "persistent data"

        # Verify file list
        files = await workspace2.list_artifacts()
        assert len(files) == 1
        assert files[0]["name"] == "persistent.txt"
