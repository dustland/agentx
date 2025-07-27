"""
Centralized path configuration for VibeX.

This module defines the standard path terminology used throughout the codebase:
- base_path: Root directory for all VibeX data (default: .vibex, configurable via VIBEX_BASE_PATH env var)
- project_root: Directory containing all projects ({base_path}/projects)
- project_path: Path for a specific project ({project_root}/{project_id})
"""

import os
from pathlib import Path
from typing import Optional


def get_base_path() -> Path:
    """
    Get the base path for all VibeX data.
    
    Can be overridden by VIBEX_BASE_PATH environment variable.
    Defaults to .vibex in the current working directory.
    """
    base = os.environ.get("VIBEX_BASE_PATH", ".vibex")
    base_path = Path(base).resolve()
    # Ensure base path exists
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path


def get_project_root() -> Path:
    """
    Get the root directory for all projects.
    
    This is always {base_path}/projects
    """
    return get_base_path() / "projects"


def get_project_path(project_id: str) -> Path:
    """
    Get the path for a specific project.
    
    Args:
        project_id: The unique identifier for the project
        
    Returns:
        Path to the project: {project_root}/{project_id}
    """
    return get_project_root() / project_id


def ensure_project_structure() -> None:
    """Ensure the base project directory structure exists."""
    project_root = get_project_root()
    project_root.mkdir(parents=True, exist_ok=True)


# Constants for backward compatibility and easy access
BASE_PATH = get_base_path()
PROJECT_ROOT = get_project_root()