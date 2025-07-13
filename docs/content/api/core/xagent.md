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

API Design:
- chat(message) - For user conversation, plan adjustments, and Q&A
- step() - For autonomous task execution, moving the plan forward
- start_task() creates a plan but doesn't execute it automatically

## XAgentResponse <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L50" class="source-link" title="View source code">source</a>

Response from XAgent chat interactions.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L53" class="source-link" title="View source code">source</a>

```python
def __init__(self, text: str, artifacts: Optional[List[Any]] = None, preserved_steps: Optional[List[str]] = None, regenerated_steps: Optional[List[str]] = None, plan_changes: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None)
```
## XAgent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L70" class="source-link" title="View source code">source</a>

XAgent - The unified conversational interface for AgentX.

XAgent combines TaskExecutor's execution context management with
Orchestrator's agent coordination logic into a single, user-friendly
interface that users can chat with naturally.

Key capabilities:
- Rich message handling (text, attachments, multimedia)
- LLM-driven plan adjustment preserving completed work
- Automatic workspace and tool management
- Conversational task management

Usage Pattern:
    ```python
    # Start a task (creates plan but doesn't execute)
    x = await start_task("Build a web app", "config/team.yaml")

    # Execute the task autonomously
    while not x.is_complete:
        response = await x.step()  # Autonomous execution
        print(response)

    # Chat for refinements and adjustments
    response = await x.chat("Make it more colorful")  # User conversation
    print(response.text)
    ```

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L100" class="source-link" title="View source code">source</a>

```python
def __init__(self, team_config: TeamConfig, task_id: Optional[str] = None, workspace_dir: Optional[Path] = None, initial_prompt: Optional[str] = None)
```
### chat <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L248" class="source-link" title="View source code">source</a>

```python
async def chat(self, message: Union[str, Message]) -> XAgentResponse
```

Send a conversational message to X and get a response.

This is the conversational interface that handles:
- User questions and clarifications
- Plan adjustments and modifications
- Rich messages with attachments
- Preserving completed work while regenerating only necessary steps

This method is for USER INPUT and conversation, not for autonomous task execution.
For autonomous task execution, use step() method instead.

**Args:**
    message: Either a simple text string or a rich Message with parts

**Returns:**
    XAgentResponse with text, artifacts, and execution details

### execute <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L776" class="source-link" title="View source code">source</a>

```python
async def execute(self, prompt: str, stream: bool = False) -> AsyncGenerator[TaskStep, None]
```

Compatibility method for TaskExecutor.execute().

### start <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L788" class="source-link" title="View source code">source</a>

```python
async def start(self, prompt: str) -> None
```

Compatibility method for TaskExecutor.start().

### step <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/xagent.py#L792" class="source-link" title="View source code">source</a>

```python
async def step(self) -> str
```

Execute one step of autonomous task execution.

This method is for AUTONOMOUS TASK EXECUTION, not for user conversation.
It moves the plan forward by executing the next available task.

For user conversation and plan adjustments, use chat() method instead.

**Returns:**
    str: Status message about the step execution
