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
def __init__(self, task_id: str, config: TaskConfig, history: TaskHistory, message_queue: MessageQueue, agents: Dict[str, Agent], workspace: WorkspaceStorage, orchestrator: Orchestrator, initial_prompt: str)
```
### get_agent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L75" class="source-link" title="View source code">source</a>

```python
def get_agent(self, name: str) -> Agent
```

Retrieves an agent by name.

### complete <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L81" class="source-link" title="View source code">source</a>

```python
def complete(self)
```

Marks the task as complete.

### get_context <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L86" class="source-link" title="View source code">source</a>

```python
def get_context(self) -> Dict[str, Any]
```

Returns a dictionary with the task's context.

### create_plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L108" class="source-link" title="View source code">source</a>

```python
def create_plan(self, plan: Plan) -> None
```

Creates a new plan for the task.

### update_plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L114" class="source-link" title="View source code">source</a>

```python
def update_plan(self, plan: Plan) -> None
```

Updates the current plan.

### get_plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L120" class="source-link" title="View source code">source</a>

```python
def get_plan(self) -> Optional[Plan]
```

Returns the current plan.

### load_plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L138" class="source-link" title="View source code">source</a>

```python
def load_plan(self) -> Optional[Plan]
```

Loads a plan from the workspace if it exists.

## TaskExecutor <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L155" class="source-link" title="View source code">source</a>

The main engine for executing a task. It coordinates the agents, tools,
and orchestrator to fulfill the user's request.

Two execution modes:
1. Fire-and-forget: execute() runs task to completion autonomously
2. Step-by-step: start() + step() for conversational interaction

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L165" class="source-link" title="View source code">source</a>

```python
def __init__(self, team_config: Union[TeamConfig, str], task_id: Optional[str] = None, workspace_dir: Optional[Path] = None)
```
### execute <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L229" class="source-link" title="View source code">source</a>

```python
async def execute(self, prompt: str, stream: bool = False) -> AsyncGenerator[Message, None]
```

Fire-and-forget execution - runs task to completion autonomously.
This is the method called by execute_task() for autonomous execution.

### start <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L274" class="source-link" title="View source code">source</a>

```python
async def start(self, prompt: str) -> None
```

Initialize the conversation with the given prompt.
This sets up the task but doesn't execute any agent responses yet.

### step <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L300" class="source-link" title="View source code">source</a>

```python
async def step(self) -> str
```

Execute one conversation step - get a response from the current agent.
Returns the agent's response as a string.

### is_complete <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L335" class="source-link" title="View source code">source</a>

```python
def is_complete(self) -> bool
```

Check if the task is complete.

### add_user_message <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L339" class="source-link" title="View source code">source</a>

```python
def add_user_message(self, content: str) -> None
```

Add a user message to the conversation history.

## Functions

## execute_task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L347" class="source-link" title="View source code">source</a>

```python
async def execute_task(prompt: str, config_path: str, stream: bool = False) -> AsyncGenerator[Message, None]
```

High-level function to execute a task from a prompt and config file.
This function runs the task to completion autonomously.

## start_task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L365" class="source-link" title="View source code">source</a>

```python
def start_task(prompt: str, config_path: str, task_id: Optional[str] = None, workspace_dir: Optional[Path] = None) -> TaskExecutor
```

High-level function to start a task and return the TaskExecutor for step-by-step execution.

This function is ideal for interactive scenarios where you want to:
- Execute conversations step by step
- Build interactive chat interfaces
- Have manual control over the conversation flow

**Args:**
    prompt: The initial task prompt
    config_path: Path to the team configuration file
    task_id: Optional custom task ID
    workspace_dir: Optional custom workspace directory

**Returns:**
    TaskExecutor: The initialized executor ready for step-by-step execution

**Example:**
    ```python
    # Start a conversational task
    executor = start_task(
        prompt="Hello, how are you?",
        config_path="config/team.yaml"
    )

    # Initialize the conversation
    await executor.start(prompt)

    # Get agent response
    response = await executor.step()
    print(f"Agent: {response}")

    # Continue conversation
    executor.add_user_message("Tell me a joke")
    response = await executor.step()
    print(f"Agent: {response}")
    ```
