# Debug Commands

*Module: [`vibex.cli.debug`](https://github.com/dustland/vibex/blob/main/src/vibex/cli/debug.py)*

VibeX Debugging CLI

Provides step-through debugging capabilities for VibeX tasks including
breakpoints, state inspection, and context modification.

## DebugSession <a href="https://github.com/dustland/vibex/blob/main/src/vibex/cli/debug.py#L20" class="source-link" title="View source code">source</a>

Interactive debugging session for VibeX tasks.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/cli/debug.py#L23" class="source-link" title="View source code">source</a>

```python
def __init__(self, xagent: XAgent)
```
### start <a href="https://github.com/dustland/vibex/blob/main/src/vibex/cli/debug.py#L28" class="source-link" title="View source code">source</a>

```python
async def start(self)
```

Start the interactive debugging session.

## Functions

## debug_task <a href="https://github.com/dustland/vibex/blob/main/src/vibex/cli/debug.py#L263" class="source-link" title="View source code">source</a>

```python
async def debug_task(team_config_path: str, project_id: Optional[str] = None, workspace_dir: Optional[str] = None)
```

Start a debugging session for a task.
