"""
Storage factory - Creates storage providers using factory pattern.

Separates pure filesystem abstraction from business logic.
"""

from typing import Union
from pathlib import Path

from .interfaces import FileStorage
from .backends import LocalFileStorage
from .taskspace import TaskspaceStorage
from ..utils.logger import get_logger

logger = get_logger(__name__)


class StorageFactory:
    """
    Factory for creating storage providers.

    Creates filesystem abstractions that can be swapped for different backends
    (local, S3, Azure, etc.) and taskspace storage for business logic.
    """

    @staticmethod
    def create_file_storage(base_path: Union[str, Path]) -> FileStorage:
        """
        Create a filesystem abstraction.

        This can be swapped for different backends like S3FileStorage,
        AzureFileStorage, etc. without changing the business logic.

        Args:
            base_path: Base path for the filesystem

        Returns:
            FileStorage implementation
        """
        base_path = Path(base_path)
        base_path.mkdir(parents=True, exist_ok=True)

        provider = LocalFileStorage(base_path)
        logger.info(f"Created file storage provider: {base_path}")
        return provider

    @staticmethod
    def create_taskspace_storage(
        workspace_path: Union[str, Path] = None,
        use_git_artifacts: bool = True,
        base_path: Union[str, Path] = None,
        task_id: str = None,
        user_id: str = None
    ) -> TaskspaceStorage:
        """
        Create a taskspace storage for business logic.

        Handles business concepts like artifacts, messages, execution plans
        using the filesystem abstraction underneath.

        Args:
            workspace_path: Path to the taskspace directory (old API)
            use_git_artifacts: Whether to use Git for artifact versioning
            base_path: Base path for multi-tenant taskspaces (new API)
            task_id: Task ID for taskspace isolation (new API)
            user_id: User ID for multi-tenant isolation (new API)

        Returns:
            TaskspaceStorage instance
        """
        if workspace_path is not None:
            # Old API: direct workspace path
            workspace_path = Path(workspace_path)
            workspace_path.mkdir(parents=True, exist_ok=True)

            # Create the filesystem abstraction
            file_storage = StorageFactory.create_file_storage(workspace_path)

            # Create the taskspace with business logic
            workspace = TaskspaceStorage(workspace_path, file_storage, use_git_artifacts)
            logger.info(f"Created taskspace storage: {workspace_path} (Git artifacts: {use_git_artifacts})")
            return workspace
        else:
            # New API: base_path + task_id + optional user_id
            if base_path is None or task_id is None:
                raise ValueError("base_path and task_id are required when workspace_path is not provided")
            
            # Create taskspace using new API
            workspace = TaskspaceStorage(
                workspace_path=None,
                file_storage=None,
                use_git_artifacts=use_git_artifacts,
                base_path=base_path,
                task_id=task_id,
                user_id=user_id
            )
            
            # Create the filesystem abstraction for the computed taskspace path
            file_storage = StorageFactory.create_file_storage(workspace.workspace_path)
            workspace.file_storage = file_storage
            
            logger.info(f"Created taskspace storage: {workspace.workspace_path} (Git artifacts: {use_git_artifacts}, User: {user_id})")
            return workspace
