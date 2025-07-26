# Task Management

*Module: [`vibex.core.task`](https://github.com/dustland/vibex/blob/main/src/vibex/core/task.py)*

Task module - Defines the Task class and related functionality.

In VibeX v2.0+:
- Project: Top-level container for work
- Task: Execution unit within a project (formerly PlanItem)
- TaskStep: Individual actions within a task

A Task represents a single unit of work that can be assigned to an agent
and executed as part of a project's plan.

## Task <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/task.py#L26" class="source-link" title="View source code">source</a>

Represents a single task in a project plan.

A task is the atomic unit of work in VibeX. Each task:
- Has a clear goal/objective
- Can be assigned to a single agent
- May depend on other tasks
- Produces a result upon completion

### assign_to_agent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/task.py#L47" class="source-link" title="View source code">source</a>

```python
def assign_to_agent(self, agent_name: str)
```

Assigns the task to an agent.

### can_start <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/task.py#L51" class="source-link" title="View source code">source</a>

```python
def can_start(self, completed_task_ids: List[str]) -> bool
```

Check if this task can start based on completed dependencies.

### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/task.py#L55" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert the task to a dictionary.

### from_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/task.py#L60" class="source-link" title="View source code">source</a>

```python
def from_dict(cls, data: Dict[str, Any]) -> 'Task'
```

Create a Task instance from a dictionary.
