# Orchestrator

*Module: [`agentx.core.orchestrator`](https://github.com/dustland/agentx/blob/main/src/agentx/core/orchestrator.py)*

## Orchestrator <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/orchestrator.py#L22" class="source-link" title="View source code">source</a>
### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/orchestrator.py#L23" class="source-link" title="View source code">source</a>

```python
def __init__(self, team_config: TeamConfig, message_queue: MessageQueue, tool_manager: ToolManager, agents: Dict[str, Agent])
```
### run <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/orchestrator.py#L43" class="source-link" title="View source code">source</a>

```python
async def run(self, task: 'Task') -> AsyncGenerator[Message, None]
```