# Xagent

_Module: [`vibex.core.xagent`](https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py)_

XAgent - The unified conversational interface for VibeX

XAgent merges TaskExecutor and Orchestrator functionality into a single,
user-friendly interface that users can chat with to manage complex multi-agent tasks.

Key Features:

- Rich message handling with attachments and multimedia
- LLM-driven plan adjustment that preserves completed work
- Single point of contact for all user interactions
- Automatic taskspace and tool management

API Design:

- chat(message) - For user conversation, plan adjustments, and Q&A
- step() - For autonomous task execution, moving the plan forward
- start_task() creates a plan but doesn't execute it automatically

## XAgentResponse <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L50" class="source-link" title="View source code">source</a>

Response from XAgent chat interactions.

### **init** <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L53" class="source-link" title="View source code">source</a>

```python
def __init__(self, text: str, artifacts: Optional[List[Any]] = None, preserved_steps: Optional[List[str]] = None, regenerated_steps: Optional[List[str]] = None, plan_changes: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None)
```

## XAgent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L70" class="source-link" title="View source code">source</a>

XAgent - The unified conversational interface for VibeX.

XAgent combines TaskExecutor's execution context management with
Orchestrator's agent coordination logic into a single, user-friendly
interface that users can chat with naturally.

Key capabilities:

- Rich message handling (text, attachments, multimedia)
- LLM-driven plan adjustment preserving completed work
- Automatic taskspace and tool management
- Conversational task management

Usage Pattern:

````python # Start a task (creates plan but doesn't execute)
x = await start_task("Build a web app", "config/team.yaml")

    # Execute the task autonomously
    while not x.is_complete:
        response = await x.step()  # Autonomous execution
        print(response)

    # Chat for refinements and adjustments
    response = await x.chat("Make it more colorful")  # User conversation
    print(response.text)
    ```

### **init** <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L100" class="source-link" title="View source code">source</a>

```python
def __init__(self, team_config: TeamConfig, task_id: Optional[str] = None, taskspace_dir: Optional[Path] = None, initial_prompt: Optional[str] = None, user_id: Optional[str] = None)
````

### chat <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L261" class="source-link" title="View source code">source</a>

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

### execute <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L880" class="source-link" title="View source code">source</a>

```python
async def execute(self, prompt: str, stream: bool = False) -> AsyncGenerator[TaskStep, None]
```

Compatibility method for TaskExecutor.execute().

### start <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L892" class="source-link" title="View source code">source</a>

```python
async def start(self, prompt: str) -> None
```

Compatibility method for TaskExecutor.start().

### set_parallel_execution <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L896" class="source-link" title="View source code">source</a>

```python
def set_parallel_execution(self, enabled: bool = True, max_concurrent: int = 3) -> None
```

Configure parallel execution settings.

**Args:**
enabled: Whether to enable parallel execution
max_concurrent: Maximum number of tasks to execute simultaneously

### get_parallel_settings <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L908" class="source-link" title="View source code">source</a>

```python
def get_parallel_settings(self) -> Dict[str, Any]
```

Get current parallel execution settings.

### step <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/xagent.py#L915" class="source-link" title="View source code">source</a>

```python
async def step(self) -> str
```

Execute one step of autonomous task execution.

This method is for AUTONOMOUS TASK EXECUTION, not for user conversation.
It moves the plan forward by executing the next available task.

For user conversation and plan adjustments, use chat() method instead.

**Returns:**
str: Status message about the step execution
