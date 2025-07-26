# Task Executor

*Module: [`vibex.core.task_executor`](https://github.com/dustland/vibex/blob/main/src/vibex/core/task_executor.py)*

Task execution module.

This module defines TaskExecutor for managing the execution of tasks within a project.
Tasks now contain both descriptive and runtime information, eliminating the need
for a separate TaskRun class.

## TaskExecutor <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/task_executor.py#L19" class="source-link" title="View source code">source</a>

Manages the execution of individual tasks.

TaskExecutor is responsible for:
1. Starting task execution
2. Coordinating with agents
3. Collecting execution steps
4. Handling errors
5. Updating task state

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/task_executor.py#L31" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### execute <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/task_executor.py#L34" class="source-link" title="View source code">source</a>

```python
async def execute(self, task: Task, agent: Agent) -> Task
```

Execute a task with the given agent.

**Args:**
    task: The task to execute (will be updated with execution state)
    agent: The agent that will execute the task

**Returns:**
    Task: The same task object, now updated with execution results

### get_current_task <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/task_executor.py#L114" class="source-link" title="View source code">source</a>

```python
def get_current_task(self) -> Optional[Task]
```

Get the currently executing task, if any.
