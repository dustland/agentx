# Xagent

*Module: [`vibex.core.xagent`](https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py)*

XAgent - The project's conversational representative

X is the interface between users and their projects. Each project has an X agent
that acts as its representative. When you need to interact with a project, you
talk to X. XAgent merges TaskExecutor and Orchestrator functionality into a 
single, user-friendly interface.

Key Features:
- Acts as the project's representative for all interactions
- Rich message handling with attachments and multimedia
- LLM-driven plan adjustment that preserves completed work
- Single point of contact for all user interactions
- Automatic workspace and tool management

API Design:
- chat(message) - Talk to X about the project (adjustments, Q&A, etc.)
- step() - Let X autonomously execute the next project step

## XAgentResponse <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L54" class="source-link" title="View source code">source</a>

Response from XAgent chat interactions.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L57" class="source-link" title="View source code">source</a>

```python
def __init__(self, text: str, artifacts: Optional[List[Any]] = None, preserved_steps: Optional[List[str]] = None, regenerated_steps: Optional[List[str]] = None, plan_changes: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None, user_message: Optional['Message'] = None, assistant_message: Optional['Message'] = None, message_id: Optional[str] = None)
```
## XAgent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L80" class="source-link" title="View source code">source</a>

XAgent - The project's conversational representative.

XAgent (X) acts as the interface between users and their projects. When you
need to interact with a project, you talk to its X agent. X combines 
TaskExecutor's execution context management with Orchestrator's agent 
coordination logic into a single, user-friendly interface.

Key capabilities:
- Acts as the project's representative for all interactions
- Rich message handling (text, attachments, multimedia)
- LLM-driven plan adjustment preserving completed work
- Automatic workspace and tool management
- Conversational project management

Usage Pattern:
    ```python
    # Start a project
    x = await XAgent.start("Build a web app", "config/team.yaml")

    # Execute the project autonomously
    while not x.is_complete():
        response = await x.step()  # Autonomous execution
        print(response)

    # Chat for refinements and adjustments
    response = await x.chat("Make it more colorful")  # User conversation
    print(response)
    ```

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L112" class="source-link" title="View source code">source</a>

```python
def __init__(self, team_config: TeamConfig, project_id: Optional[str] = None, workspace_dir: Optional[Path] = None, initial_prompt: Optional[str] = None)
```
### chat <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L318" class="source-link" title="View source code">source</a>

```python
async def chat(self, message: Union[str, Message], mode: str = 'agent') -> XAgentResponse
```

Send a conversational message to X and get a response.

This is the conversational interface that handles:
- User questions and clarifications
- Plan adjustments and modifications
- Rich messages with attachments
- Preserving completed work while regenerating only necessary steps

This method is for USER INPUT and conversation, not for autonomous project execution.
For autonomous project execution, use step() method instead.

**Args:**
    message: Either a simple text string or a rich Message with parts
    mode: Execution mode - "agent" (multi-agent with plan) or "chat" (direct response)

**Returns:**
    XAgentResponse with text, artifacts, and execution details

### execute <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L1187" class="source-link" title="View source code">source</a>

```python
async def execute(self, prompt: str, stream: bool = False) -> AsyncGenerator[Task, None]
```

Compatibility method for TaskExecutor.execute().

### is_complete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L1205" class="source-link" title="View source code">source</a>

```python
def is_complete(self) -> bool
```

Check if the project is complete.

### start <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L1211" class="source-link" title="View source code">source</a>

```python
async def start(self, prompt: str) -> None
```

Compatibility method for TaskExecutor.start().

### set_parallel_execution <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L1215" class="source-link" title="View source code">source</a>

```python
def set_parallel_execution(self, enabled: bool = True, max_concurrent: int = 3) -> None
```

Configure parallel execution settings.

**Args:**
    enabled: Whether to enable parallel execution
    max_concurrent: Maximum number of tasks to execute simultaneously

### get_parallel_settings <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L1227" class="source-link" title="View source code">source</a>

```python
def get_parallel_settings(self) -> Dict[str, Any]
```

Get current parallel execution settings.

### step <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L1234" class="source-link" title="View source code">source</a>

```python
async def step(self) -> str
```

Execute one step of autonomous project execution.

This method is for AUTONOMOUS TASK EXECUTION, not for user conversation.
It moves the plan forward by executing the next available task.

For user conversation and plan adjustments, use chat() method instead.

**Returns:**
    str: Status message about the step execution
