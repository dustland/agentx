"""
Integration tests for ProjectStorage with real storage backends.
"""

import pytest
import tempfile
from pathlib import Path

from vibex.storage import ProjectStorage
from vibex.storage.git_storage import GitArtifactStorage


class TestProjectStorageIntegration:
    """Test ProjectStorage integration with real storage."""

    def setup_method(self):
        """Setup test environment with real storage."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_id = "integration_test"
        self.file_storage = GitArtifactStorage(
            base_path=self.temp_dir,
            project_id=self.project_id
        )
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
    async def test_full_project_lifecycle_integration(self):
        """Test complete project storage operations with real storage."""
        # Store an artifact
        store_result = await self.project_storage.store_artifact(
            "test_report.md",
            "# Test Report\n\nThis is a test report.",
            content_type="text/markdown"
        )
        assert store_result.success is True

        # Retrieve the artifact
        get_result = await self.project_storage.get_artifact("test_report.md")
        assert get_result == "# Test Report\n\nThis is a test report."

        # List artifacts
        list_result = await self.project_storage.list_artifacts()
        assert len(list_result) >= 1
        artifact_names = [a["name"] for a in list_result]
        assert "test_report.md" in artifact_names

        # Create a directory manually (directories are created automatically when files are written)
        analysis_dir = self.temp_dir / self.project_id / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)

        # List directory contents
        list_dir_result = await self.project_storage.list_directory(".")
        assert list_dir_result["success"] is True

        # Get project storage summary
        summary_result = await self.project_storage.get_project_summary()
        assert "error" not in summary_result
        assert summary_result["total_artifacts"] >= 1

    @pytest.mark.asyncio
    async def test_project_isolation_integration(self):
        """Test that different projects are properly isolated."""
        # Create second project storage
        project2 = ProjectStorage(
            project_id="other_project",
            base_path=self.temp_dir,
            file_storage=GitArtifactStorage(
                base_path=self.temp_dir,
                project_id="other_project"
            )
        )

        # Store different artifacts in each project storage
        await self.project_storage.store_artifact("file1.txt", "content1")
        await project2.store_artifact("file2.txt", "content2")

        # Verify isolation
        files1 = await self.project_storage.list_artifacts()
        files2 = await project2.list_artifacts()

        assert len(files1) == 1
        assert len(files2) == 1
        assert files1[0]["name"] == "file1.txt"
        assert files2[0]["name"] == "file2.txt"

        # Verify each project storage can't access the other's files
        get_result1 = await self.project_storage.get_artifact("file2.txt")
        get_result2 = await project2.get_artifact("file1.txt")

        assert get_result1 is None
        assert get_result2 is None

    @pytest.mark.asyncio
    async def test_project_persistence_integration(self):
        """Test that project data persists across instances."""
        # Store data in project storage
        await self.project_storage.store_artifact("persistent.txt", "persistent data")

        # Create new project storage instance with same project_id
        project2 = ProjectStorage(
            project_id=self.project_id,
            base_path=self.temp_dir,
            file_storage=GitArtifactStorage(
                base_path=self.temp_dir,
                project_id=self.project_id
            )
        )

        # Verify data is accessible
        get_result = await project2.get_artifact("persistent.txt")
        assert get_result == "persistent data"

        # Verify file list
        files = await project2.list_artifacts()
        assert len(files) == 1
        assert files[0]["name"] == "persistent.txt"
