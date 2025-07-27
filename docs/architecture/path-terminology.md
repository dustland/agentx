# Path Terminology in VibeX

This document defines the standard path terminology used throughout the VibeX codebase. These terms are consistently applied across all modules to avoid confusion.

## Standard Terms

### base_path
- **Definition**: Root directory for all VibeX data
- **Default**: `.vibex` in the current working directory
- **Configuration**: Can be overridden via `VIBEX_BASE_PATH` environment variable
- **Example**: `/home/user/.vibex` or `/opt/vibex-data`

### project_root
- **Definition**: Directory containing all projects
- **Formula**: `{base_path}/projects`
- **Example**: `/home/user/.vibex/projects`
- **Purpose**: Parent directory for all project-specific data

### project_path
- **Definition**: Path to a specific project's directory
- **Formula**: `{project_root}/{project_id}`
- **Example**: `/home/user/.vibex/projects/abc123`
- **Contents**: All data for a specific project (artifacts, logs, history, etc.)

## Usage Guidelines

1. **Always use the path functions from `vibex.utils.paths`**:
   ```python
   from vibex.utils.paths import get_base_path, get_project_root, get_project_path
   
   # Get paths
   base = get_base_path()                    # e.g., /home/user/.vibex
   root = get_project_root()                 # e.g., /home/user/.vibex/projects
   project = get_project_path("abc123")      # e.g., /home/user/.vibex/projects/abc123
   ```

2. **Never hardcode paths**:
   ```python
   # ❌ WRONG
   project_path = Path(".vibex/projects/abc123")
   
   # ✅ CORRECT
   project_path = get_project_path("abc123")
   ```

3. **Storage classes use full paths**:
   ```python
   # ProjectStorage expects the full project path
   storage = ProjectStorage(
       project_path=get_project_path(project_id),
       project_id=project_id,
       ...
   )
   ```

## Directory Structure

```
base_path (.vibex)/
├── projects/                    # project_root
│   ├── abc123/                  # project_path for project "abc123"
│   │   ├── artifacts/           # Project artifacts (code, documents, etc.)
│   │   ├── history/             # Conversation history
│   │   ├── logs/                # Execution logs
│   │   └── project.json         # Project metadata
│   └── def456/                  # project_path for project "def456"
│       └── ...
└── config/                      # Global configuration
    └── ...
```

## Implementation Notes

- The `ProjectStorageFactory` constructs the full project path before passing it to `ProjectStorage`
- Service layer handles user-to-project mapping; storage layer only deals with project paths
- All path construction should happen through the centralized functions in `vibex.utils.paths`