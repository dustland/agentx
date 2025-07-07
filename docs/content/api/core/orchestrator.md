# Orchestrator

*Module: [`agentx.core.orchestrator`](https://github.com/dustland/agentx/blob/main/src/agentx/core/orchestrator.py)*

## Orchestrator <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/orchestrator.py#L22" class="source-link" title="View source code">source</a>

The central process manager of the system. It executes the Plan with unwavering precision,
operating as a state machine that moves the system from one task to the next according to
the instructions in the Plan.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/orchestrator.py#L29" class="source-link" title="View source code">source</a>

```python
def __init__(self, team_config: TeamConfig, message_queue: MessageQueue, tool_manager: ToolManager, agents: Dict[str, Agent])
```
### step <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/orchestrator.py#L50" class="source-link" title="View source code">source</a>

```python
async def step(self, messages: list[dict], task: 'Task') -> str
```

Execute one step of the plan-driven orchestration loop.

This implements the 8-step loop described in the design docs:
1. Initialize and Generate Plan (If Needed)
2. Identify Next Actionable Task
3. Select Agent (and Route If Needed)
4. Prepare Task Briefing
5. Dispatch and Monitor
6. Process Completion Signal
7. Persist State
8. Continue or Terminate
