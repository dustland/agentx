# AgentX Workspace Organization Guide

## Overview

Every AgentX task creates a structured workspace directory. This guide defines what goes where and how agents should use the storage tools.

## Workspace Structure

```
workspace/<task_id>/
├── artifacts/          # Default location for all files
├── temp/              # Temporary files (only when requested)
├── logs/              # Framework execution logs
└── history/           # Framework task history
```

## Storage Tool Usage

**StorageTool uses `artifacts/` as the default location:**

### 📄 Default Behavior: Everything Goes to `artifacts/`

**Standard file operations automatically use artifacts:**

```python
# These all save to artifacts/ automatically
await write_file("requirements.md", content)           # → artifacts/requirements.md
await write_file("report.pdf", pdf_content)           # → artifacts/report.pdf
await write_file("config.json", json_data)            # → artifacts/config.json

# Reading also defaults to artifacts
content = await read_file("requirements.md")          # ← artifacts/requirements.md

# Listing defaults to artifacts
files = await list_directory()                        # Lists artifacts/ contents
```

### 🗑️ Temporary Files: Use `temp/` When Needed

**For temporary files, explicitly specify temp path:**

```python
# Get temp directory (creates if needed)
temp_dir = await get_temp_dir()  # Returns "temp"

# Save temporary files with temp/ prefix
await write_file("temp/script.sh", bash_script)       # → temp/script.sh
await write_file("temp/working_data.json", data)      # → temp/working_data.json
await write_file("temp/cache.txt", cache_data)        # → temp/cache.txt
```

---

## Framework-Managed Folders (No Agent Access)

### 📝 `logs/` - System Execution Logs

- **Managed by:** Logging framework
- **Content:** Technical execution traces, errors, performance metrics

### 🔄 `history/` - Task Execution History

- **Managed by:** TaskExecutor
- **Content:** Conversation flow, agent interactions, tool calls

## Simple Decision Flow

```
Do you need this file temporarily?
├─ YES → Use temp/ prefix: write_file("temp/filename", content)
└─ NO → Use normal filename: write_file("filename", content)
```

## StorageTool Methods

| Method                          | Behavior                           | Example                            |
| ------------------------------- | ---------------------------------- | ---------------------------------- |
| `write_file(filename, content)` | Saves to artifacts/ by default     | `write_file("report.md", content)` |
| `read_file(filename)`           | Reads from artifacts/ by default   | `read_file("report.md")`           |
| `list_directory(path)`          | Defaults to artifacts/ directory   | `list_directory()`                 |
| `file_exists(filename)`         | Checks artifacts/ by default       | `file_exists("report.md")`         |
| `delete_file(filename)`         | Deletes from artifacts/ by default | `delete_file("old_report.md")`     |
| `get_temp_dir()`                | Returns "temp" (creates if needed) | `get_temp_dir()`                   |
| `create_directory(path)`        | Creates any directory              | `create_directory("subfolder")`    |

## Benefits

- **Zero cognitive load**: Just use normal filenames, they go to the right place
- **Explicit temp usage**: Only think about temp/ when you actually need it
- **Standard file operations**: No abstractions or special methods
- **Flexible**: Can save any file type anywhere when needed

## Example Usage

```python
# Normal workflow - everything goes to artifacts automatically
await write_file("requirements.md", requirements_doc)
await write_file("architecture.png", diagram_data)
await write_file("config.yaml", config_data)

# Check what's been created
files = await list_directory()  # Shows artifacts/ contents

# Temporary files when needed
temp_dir = await get_temp_dir()
await write_file("temp/process_data.sh", bash_script)
await write_file("temp/intermediate_results.json", temp_data)

# Read files (defaults to artifacts)
existing_requirements = await read_file("requirements.md")
```

This approach eliminates decision-making overhead - agents just work with files naturally, and the framework handles organization automatically.
