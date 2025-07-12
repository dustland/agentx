# Task Management

*Module: [`agentx.core.task`](https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py)*

Task execution class - the primary interface for AgentX task execution.

Clean API:
    # One-shot execution (Fire-and-forget)
    await execute_task(prompt, config_path)

    # Step-by-step execution (Conversational)
    executor = start_task(prompt, config_path)
    await executor.start(prompt)
    while not executor.is_complete():
        response = await executor.step()
        print(response)

## Task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L45" class="source-link" title="View source code">source</a>

Represents the state and context of a single task being executed.
This class is a data container and does not have execution logic.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L51" class="source-link" title="View source code">source</a>

```python
def __init__(self, task_id: str, config: TaskConfig, history: TaskHistory, message_queue: MessageQueue, agents: Dict[str, Agent], workspace: WorkspaceStorage, initial_prompt: str)
```
### get_agent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L73" class="source-link" title="View source code">source</a>

```python
def get_agent(self, name: str) -> Agent
```

Retrieves an agent by name.

### complete <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L79" class="source-link" title="View source code">source</a>

```python
def complete(self)
```

Marks the task as complete.

### get_context <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L84" class="source-link" title="View source code">source</a>

```python
def get_context(self) -> Dict[str, Any]
```

Returns a dictionary with the task's context.

### create_plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L106" class="source-link" title="View source code">source</a>

```python
def create_plan(self, plan: Plan) -> None
```

Creates a new plan for the task.

### update_plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L111" class="source-link" title="View source code">source</a>

```python
async def update_plan(self, plan: Plan) -> None
```

Updates the current plan and persists it.

### update_task_status <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L117" class="source-link" title="View source code">source</a>

```python
async def update_task_status(self, task_id: str, status: TaskStatus) -> bool
```

Update task status and automatically persist the plan.

### get_plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L127" class="source-link" title="View source code">source</a>

```python
def get_plan(self) -> Optional[Plan]
```

Returns the current plan.

### load_plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L143" class="source-link" title="View source code">source</a>

```python
async def load_plan(self) -> Optional[Plan]
```

Loads the plan from plan.json if it exists.

## Functions

## execute_task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L157" class="source-link" title="View source code">source</a>

```python
async def execute_task(prompt: str, config_path: str, stream: bool = False) -> AsyncGenerator[Message, None]
```

High-level function to execute a task from a prompt and config file.
This function runs the task to completion autonomously.

## start_task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L185" class="source-link" title="View source code">source</a>

```python
async def start_task(prompt: str, config_path: Union[str, Path, TeamConfig], task_id: Optional[str] = None, workspace_dir: Optional[Path] = None) -> XAgent
```

High-level function to start a task and return an initialized XAgent.

This function creates an XAgent instance that users can chat with
to manage complex multi-agent tasks conversationally.

**Args:**
    prompt: The initial task prompt
    config_path: Path to the team configuration file
    task_id: Optional custom task ID
    workspace_dir: Optional custom workspace directory

**Returns:**
    XAgent: The initialized XAgent ready for conversational interaction

**Example:**
    ```python
    # Start a conversational task
    x = await start_task(
        prompt="Create a market research report",
        config_path="config/team.yaml"
    )

    # Chat with X to manage the task
    response = await x.chat("Update the report with more visual appeal")
    print(response.text)

    # Send rich messages with attachments
    response = await x.chat(Message(parts=[
        TextPart("Use this style guide"),
        ArtifactPart(artifact=style_guide)
    ]))
    ```
