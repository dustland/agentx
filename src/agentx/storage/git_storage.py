"""
Git-based artifact storage - Uses Git for proper versioning.

Provides Git-based versioning for artifacts, especially useful for code generation
where we need proper diffs, branching, and version history.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor

try:
    import git
    from git import Repo, InvalidGitRepositoryError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    git = None
    Repo = None
    InvalidGitRepositoryError = Exception

from .interfaces import StorageResult
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GitArtifactStorage:
    """
    Git-based artifact storage with proper version control.

    Uses Git for versioning artifacts, providing:
    - Proper diffs and history
    - Branching and merging capabilities
    - Standard Git tooling integration
    - Efficient storage with delta compression
    - Meaningful commit messages
    """

    def __init__(self, workspace_path: Union[str, Path] = None, base_path: Union[str, Path] = None, task_id: str = None):
        if not GIT_AVAILABLE:
            raise ImportError("GitPython is required for Git-based artifact storage")

        # Support both old API (workspace_path) and new API (base_path + task_id)
        if workspace_path is not None:
            # Old API: workspace_path directly
            self.workspace_path = Path(workspace_path)
        elif base_path is not None and task_id is not None:
            # New API: base_path + task_id for workspace isolation
            self.workspace_path = Path(base_path) / task_id
        else:
            raise ValueError("Either workspace_path or (base_path + task_id) must be provided")

        self.artifacts_path = self.workspace_path / "artifacts"
        self.artifacts_path.mkdir(parents=True, exist_ok=True)

        # Thread pool for Git operations (Git operations are not async)
        self.executor = ThreadPoolExecutor(max_workers=2)

        # Initialize or open Git repository
        self.repo = self._init_repository()

        logger.info(f"GitArtifactStorage initialized: {self.artifacts_path}")

    def _init_repository(self) -> Repo:
        """Initialize or open Git repository."""
        try:
            # Try to open existing repository
            repo = Repo(self.artifacts_path)
            logger.info("Opened existing Git repository for artifacts")
            return repo
        except InvalidGitRepositoryError:
            # Initialize new repository
            repo = Repo.init(self.artifacts_path)

            # Configure repository
            with repo.config_writer() as config:
                config.set_value("user", "name", "AgentX")
                config.set_value("user", "email", "agentx@dustland.ai")

            # Git repository initialized - no initial commit needed

            logger.info("Initialized new Git repository for artifacts")
            return repo

    async def store_artifact(
        self,
        name: str,
        content: Union[str, bytes],
        content_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None,
        commit_message: Optional[str] = None
    ) -> StorageResult:
        """Store an artifact with Git versioning."""
        try:
            # Determine file extension based on content type
            extension = self._should_add_extension(name, content_type)
            artifact_path = self.artifacts_path / f"{name}{extension}"

            # Ensure parent directories exist
            artifact_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content to file
            if isinstance(content, str):
                artifact_path.write_text(content, encoding='utf-8')
            else:
                artifact_path.write_bytes(content)

            # Store metadata if provided
            if metadata:
                # Put metadata file next to the artifact file
                metadata_path = artifact_path.with_suffix(artifact_path.suffix + ".meta.json")
                # Ensure parent directories exist for metadata
                metadata_path.parent.mkdir(parents=True, exist_ok=True)
                metadata_with_info = {
                    "name": name,
                    "content_type": content_type,
                    "created_at": datetime.now().isoformat(),
                    "size": len(content) if isinstance(content, (str, bytes)) else 0,
                    **metadata
                }
                metadata_path.write_text(json.dumps(metadata_with_info, indent=2))

            # Commit to Git
            # Use relative path from artifacts directory for git operations
            relative_path = artifact_path.relative_to(self.artifacts_path)

            files_to_commit = [str(relative_path)]
            if metadata:
                # Metadata path is next to the artifact file
                metadata_relative_path = relative_path.with_suffix(relative_path.suffix + ".meta.json")
                files_to_commit.append(str(metadata_relative_path))

            commit_hash = await self._commit_changes(
                files=files_to_commit,
                message=commit_message or f"Store artifact: {name}",
                artifact_name=name
            )

            return StorageResult(
                success=True,
                path=str(artifact_path.relative_to(self.workspace_path)),
                size=len(content) if isinstance(content, (str, bytes)) else 0,
                data={"commit_hash": commit_hash, "version": commit_hash[:8]},
                metadata={"git_commit": commit_hash, "content_type": content_type}
            )

        except Exception as e:
            logger.error(f"Failed to store artifact {name}: {e}")
            return StorageResult(
                success=False,
                error=str(e)
            )

    async def get_artifact(self, name: str, version: Optional[str] = None) -> Optional[str]:
        """Get artifact content at specific version (commit)."""
        try:
            extension = self._find_artifact_extension(name)
            if extension is None:  # Only return None if no artifact was found, not for empty extension
                return None

            artifact_path = f"{name}{extension}"

            if version is None:
                # Get latest version (HEAD)
                file_path = self.artifacts_path / artifact_path
                if not file_path.exists():
                    return None
                return file_path.read_text(encoding='utf-8')
            else:
                # Get specific version from Git
                return await self._get_file_at_commit(artifact_path, version)

        except Exception as e:
            logger.error(f"Failed to get artifact {name}: {e}")
            return None

    async def list_artifacts(self) -> List[Dict[str, Any]]:
        """List all artifacts with their Git history."""
        try:
            artifacts = []

            # Get all artifact files (excluding metadata files)
            for file_path in self.artifacts_path.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.') and not file_path.name.endswith('.meta.json'):
                    name = file_path.name  # Use full filename instead of stem

                    # Get Git history for this file
                    commits = await self._get_file_history(file_path.name)

                    for commit in commits:
                        # Load metadata if available
                        metadata = await self._get_metadata_at_commit(file_path.stem, commit['hash'])

                        artifact_info = {
                            "name": name,
                            "version": commit['hash'][:8],
                            "commit_hash": commit['hash'],
                            "content_type": metadata.get('content_type', 'text/plain') if metadata else 'text/plain',
                            "created_at": commit['date'],
                            "message": commit['message'],
                            "size": metadata.get('size', 0) if metadata else 0,
                            "metadata": metadata or {}
                        }
                        artifacts.append(artifact_info)

            # Sort by creation time (newest first)
            artifacts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return artifacts

        except Exception as e:
            logger.error(f"Failed to list artifacts: {e}")
            return []

    async def get_artifact_versions(self, name: str) -> List[str]:
        """Get all versions (commits) of an artifact."""
        try:
            extension = self._find_artifact_extension(name)
            if extension is None:  # Only return empty if no artifact was found, not for empty extension
                return []

            artifact_path = f"{name}{extension}"
            commits = await self._get_file_history(artifact_path)

            # Return commit hashes (short form)
            return [commit['hash'][:8] for commit in commits]

        except Exception as e:
            logger.error(f"Failed to get versions for artifact {name}: {e}")
            return []

    async def delete_artifact(self, name: str, version: Optional[str] = None) -> StorageResult:
        """Delete an artifact or specific version."""
        try:
            if version is not None:
                return StorageResult(
                    success=False,
                    error="Cannot delete specific Git commits. Use git revert or reset manually."
                )

            # Delete current version (remove file and commit)
            extension = self._find_artifact_extension(name)
            if extension is None:  # Only return error if no artifact was found, not for empty extension
                return StorageResult(success=False, error="Artifact not found")

            artifact_path = self.artifacts_path / f"{name}{extension}"
            metadata_path = self.artifacts_path / f"{name}.meta.json"

            # Use relative paths from artifacts directory
            files_to_remove = [str(artifact_path.relative_to(self.artifacts_path))]
            if metadata_path.exists():
                files_to_remove.append(str(metadata_path.relative_to(self.artifacts_path)))

            # Remove files
            artifact_path.unlink(missing_ok=True)
            metadata_path.unlink(missing_ok=True)

            # Commit deletion
            commit_hash = await self._commit_changes(
                files=files_to_remove,
                message=f"Delete artifact: {name}",
                artifact_name=name,
                is_deletion=True
            )

            return StorageResult(
                success=True,
                metadata={"git_commit": commit_hash, "deleted_files": files_to_remove}
            )

        except Exception as e:
            logger.error(f"Failed to delete artifact {name}: {e}")
            return StorageResult(
                success=False,
                error=str(e)
            )

    async def get_artifact_diff(self, name: str, version1: str, version2: str) -> Optional[str]:
        """Get diff between two versions of an artifact."""
        try:
            extension = self._find_artifact_extension(name)
            if extension is None:  # Only return None if no artifact was found, not for empty extension
                return None

            artifact_path = f"{name}{extension}"

            def _get_diff():
                try:
                    # Get diff between commits
                    commit1 = self.repo.commit(version1)
                    commit2 = self.repo.commit(version2)

                    diff = self.repo.git.diff(commit1, commit2, artifact_path)
                    return diff
                except Exception as e:
                    logger.error(f"Failed to get diff: {e}")
                    return None

            return await asyncio.get_event_loop().run_in_executor(self.executor, _get_diff)

        except Exception as e:
            logger.error(f"Failed to get diff for artifact {name}: {e}")
            return None

    # Helper methods
    def _get_extension_for_content_type(self, content_type: str) -> str:
        """Get file extension based on content type."""
        extensions = {
            "text/plain": ".txt",
            "text/markdown": ".md",
            "application/json": ".json",
            "text/python": ".py",
            "text/javascript": ".js",
            "text/typescript": ".ts",
            "text/html": ".html",
            "text/css": ".css",
            "text/yaml": ".yaml",
            "text/xml": ".xml",
        }
        return extensions.get(content_type, ".txt")

    def _should_add_extension(self, filename: str, content_type: str) -> str:
        """Determine if we should add an extension to the filename."""
        # Check if filename already has an extension
        if "." in filename:
            return ""  # Don't add extension if filename already has one

        # Add extension based on content type
        return self._get_extension_for_content_type(content_type)

    def _find_artifact_extension(self, name: str) -> Optional[str]:
        """Find the extension of an existing artifact."""
        for file_path in self.artifacts_path.iterdir():
            if file_path.is_file() and not file_path.name.endswith('.meta.json'):
                # Check if the full filename matches (for names with extensions)
                if file_path.name == name:
                    return ""  # No additional extension needed

                # Check if the stem matches (for names without extensions)
                if file_path.stem == name:
                    return file_path.suffix
        return None

    async def _commit_changes(
        self,
        files: List[str],
        message: str,
        artifact_name: str,
        is_deletion: bool = False
    ) -> str:
        """Commit changes to Git repository."""
        def _commit():
            try:
                if is_deletion:
                    # Remove files from index
                    self.repo.index.remove(files)
                else:
                    # Add files to index
                    self.repo.index.add(files)

                # Commit changes
                commit = self.repo.index.commit(message)
                return commit.hexsha
            except Exception as e:
                logger.error(f"Failed to commit changes: {e}")
                raise

        return await asyncio.get_event_loop().run_in_executor(self.executor, _commit)

    async def _get_file_at_commit(self, file_path: str, commit_hash: str) -> Optional[str]:
        """Get file content at specific commit."""
        def _get_content():
            try:
                commit = self.repo.commit(commit_hash)
                blob = commit.tree[file_path]
                return blob.data_stream.read().decode('utf-8')
            except Exception as e:
                logger.error(f"Failed to get file at commit: {e}")
                return None

        return await asyncio.get_event_loop().run_in_executor(self.executor, _get_content)

    async def _get_file_history(self, file_path: str) -> List[Dict[str, Any]]:
        """Get Git history for a file."""
        def _get_history():
            try:
                commits = []
                for commit in self.repo.iter_commits(paths=file_path):
                    commits.append({
                        "hash": commit.hexsha,
                        "message": commit.message.strip(),
                        "date": commit.committed_datetime.isoformat(),
                        "author": str(commit.author)
                    })
                return commits
            except Exception as e:
                logger.error(f"Failed to get file history: {e}")
                return []

        return await asyncio.get_event_loop().run_in_executor(self.executor, _get_history)

    async def _get_metadata_at_commit(self, name: str, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Get metadata at specific commit."""
        metadata_path = f"{name}.meta.json"
        metadata_content = await self._get_file_at_commit(metadata_path, commit_hash)

        if metadata_content:
            try:
                return json.loads(metadata_content)
            except json.JSONDecodeError:
                return None

        return None

    def __del__(self):
        """Cleanup thread pool."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

    # FileStorage interface methods for compatibility
    async def list_directory(self, path: str = "") -> List[Any]:
        """List directory contents (returns artifacts for compatibility)."""
        try:
            # For compatibility, return artifacts as file-like objects
            artifacts = await self.list_artifacts()
            from agentx.storage.interfaces import FileInfo
            from datetime import datetime

            file_infos = []
            for artifact in artifacts:
                file_info = FileInfo(
                    path=artifact["name"],
                    size=artifact.get("size", 0),
                    created_at=datetime.fromisoformat(artifact["created_at"]) if artifact.get("created_at") else datetime.now(),
                    modified_at=datetime.fromisoformat(artifact["created_at"]) if artifact.get("created_at") else datetime.now()
                )
                file_infos.append(file_info)

            return file_infos

        except Exception as e:
            logger.error(f"Failed to list directory: {e}")
            return []

    async def create_directory(self, path: str) -> Any:
        """Create directory (no-op for git storage)."""
        from agentx.storage.interfaces import StorageResult
        return StorageResult(success=True, path=path, metadata={"message": "Directory creation is implicit in Git storage"})

    async def exists(self, path: str) -> bool:
        """Check if artifact exists."""
        try:
            content = await self.get_artifact(path)
            return content is not None
        except Exception:
            return False

    async def read_text(self, path: str) -> str:
        """Read text content (alias for get_artifact)."""
        try:
            content = await self.get_artifact(path)
            return content or ""
        except Exception:
            return ""

    async def write_text(self, path: str, content: str) -> Any:
        """Write text content (alias for store_artifact)."""
        try:
            return await self.store_artifact(path, content)
        except Exception as e:
            from agentx.storage.interfaces import StorageResult
            return StorageResult(success=False, error=str(e))

    async def write_bytes(self, path: str, content: bytes) -> Any:
        """Write bytes content (alias for store_artifact)."""
        try:
            return await self.store_artifact(path, content)
        except Exception as e:
            from agentx.storage.interfaces import StorageResult
            return StorageResult(success=False, error=str(e))
