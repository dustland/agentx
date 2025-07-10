# Xagent

*Module: [`agentx.core.xagent`](https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py)*

XAgent - The unified conversational interface for AgentX

XAgent merges TaskExecutor and Orchestrator functionality into a single,
user-friendly interface that users can chat with to manage complex multi-agent tasks.

Key Features:
- Rich message handling with attachments and multimedia
- LLM-driven plan adjustment that preserves completed work
- Single point of contact for all user interactions
- Automatic workspace and tool management

## XAgentResponse <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L45" class="source-link" title="View source code">source</a>

Response from XAgent chat interactions.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L48" class="source-link" title="View source code">source</a>

```python
def __init__(self, text: str, artifacts: List[Any] = None, preserved_steps: List[str] = None, regenerated_steps: List[str] = None, plan_changes: Dict[str, Any] = None, metadata: Dict[str, Any] = None)
```
## XAgent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L65" class="source-link" title="View source code">source</a>

XAgent - The unified conversational interface for AgentX.

XAgent combines TaskExecutor's execution context management with
Orchestrator's agent coordination logic into a single, user-friendly
interface that users can chat with naturally.

Key capabilities:
- Rich message handling (text, attachments, multimedia)
- LLM-driven plan adjustment preserving completed work
- Automatic workspace and tool management
- Conversational task management

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L80" class="source-link" title="View source code">source</a>

```python
def __init__(self, team_config: Union[TeamConfig, str], task_id: Optional[str] = None, workspace_dir: Optional[Path] = None, initial_prompt: Optional[str] = None)
```
### chat <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L213" class="source-link" title="View source code">source</a>

```python
async def chat(self, message: Union[str, Message]) -> XAgentResponse
```

Send a message to X and get a response.

This is the main conversational interface that handles:
- Simple text messages
- Rich messages with attachments
- Plan adjustments based on user requests
- Preserving completed work while regenerating only necessary steps

**Args:**
    message: Either a simple text string or a rich Message with parts

**Returns:**
    XAgentResponse with text, artifacts, and execution details

### execute <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L595" class="source-link" title="View source code">source</a>

```python
async def execute(self, prompt: str, stream: bool = False) -> AsyncGenerator[TaskStep, None]
```

Compatibility method for TaskExecutor.execute().

### start <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L607" class="source-link" title="View source code">source</a>

```python
async def start(self, prompt: str) -> None
```

Compatibility method for TaskExecutor.start().

### step <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L611" class="source-link" title="View source code">source</a>

```python
async def step(self) -> str
```

Compatibility method for TaskExecutor.step().
