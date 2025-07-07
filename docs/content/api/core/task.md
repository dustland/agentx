# Task Management

*Module: [`agentx.core.task`](https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py)*

Task execution class - the primary interface for AgentX task execution.

Clean API:
    # One-shot execution (Lead-driven)
    await execute_task(prompt, config_path)

    # Step-by-step execution (Lead-driven)
    task = start_task(prompt, config_path)
    await task.run()

## Task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L43" class="source-link" title="View source code">source</a>

Represents the state and context of a single task being executed.
This class is a data container and does not have execution logic.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L49" class="source-link" title="View source code">source</a>

```python
def __init__(self, task_id: str, config: TaskConfig, history: TaskHistory, message_queue: MessageQueue, agents: Dict[str, Agent], workspace: WorkspaceStorage, orchestrator: Orchestrator, initial_prompt: str)
```
### get_agent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L88" class="source-link" title="View source code">source</a>

```python
def get_agent(self, name: str) -> Agent
```

Retrieves an agent by name.

### complete <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L94" class="source-link" title="View source code">source</a>

```python
def complete(self)
```

Marks the task as complete.

### get_context <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L99" class="source-link" title="View source code">source</a>

```python
def get_context(self) -> Dict[str, Any]
```

Returns a dictionary with the task's context.

## TaskExecutor <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L112" class="source-link" title="View source code">source</a>

The main engine for executing a task. It coordinates the agents, tools,
and orchestrator to fulfill the user's request.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L118" class="source-link" title="View source code">source</a>

```python
def __init__(self, team_config: Union[TeamConfig, str], task_id: Optional[str] = None, workspace_dir: Optional[Path] = None)
```
### start <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L176" class="source-link" title="View source code">source</a>

```python
async def start(self, prompt: str, stream: bool = False) -> AsyncGenerator[Message, None]
```

Starts the task execution and streams back events.

## Functions

## execute_task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L212" class="source-link" title="View source code">source</a>

```python
async def execute_task(prompt: str, config_path: str, stream: bool = False) -> AsyncGenerator[Message, None]
```

High-level function to execute a task from a prompt and config file.
This function runs the task to completion autonomously.

## start_task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/task.py#L230" class="source-link" title="View source code">source</a>

```python
def start_task(prompt: str, config_path: str, task_id: Optional[str] = None, workspace_dir: Optional[Path] = None) -> TaskExecutor
```

High-level function to start a task and return the TaskExecutor for step-by-step execution.

This function is ideal for interactive scenarios where you want to:
- Execute tasks step by step
- Inspect task state between steps
- Modify task configuration during execution
- Build interactive UIs with manual control

**Args:**
    prompt: The initial task prompt
    config_path: Path to the team configuration file
    task_id: Optional custom task ID
    workspace_dir: Optional custom workspace directory

**Returns:**
    TaskExecutor: The initialized executor ready for step-by-step execution

**Example:**
    ```python
    # Start a task for step-by-step execution
    executor = start_task(
        prompt="Write a research report",
        config_path="config/team.yaml"
    )

    # Execute steps manually
    async for message in executor.start(prompt, stream=True):
        print(f"Agent: {message.agent_name}")
        print(f"Content: {message.content}")

        # You can inspect state, pause, or modify between steps
        if some_condition:
            break
    ```
