# Debug Commands

*Module: [`agentx.cli.debug`](https://github.com/dustland/agentx/blob/main/src/agentx/cli/debug.py)*

AgentX Debugging CLI

Provides step-through debugging capabilities for AgentX tasks including
breakpoints, state inspection, and context modification.

## DebugSession <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/debug.py#L20" class="source-link" title="View source code">source</a>

Interactive debugging session for AgentX tasks.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/debug.py#L23" class="source-link" title="View source code">source</a>

```python
def __init__(self, orchestrator: Orchestrator, task_id: str)
```
### start <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/debug.py#L28" class="source-link" title="View source code">source</a>

```python
async def start(self)
```

Start the interactive debugging session.

## Functions

## debug_task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/debug.py#L308" class="source-link" title="View source code">source</a>

```python
async def debug_task(team_config_path: str, task_id: str)
```

Start a debugging session for a task.
