# Planning System

*Module: [`vibex.core.plan`](https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py)*

Planning system for VibeX framework - Version 2.

This module provides a comprehensive planning system that allows projects to break down
complex goals into manageable tasks, track progress, and coordinate execution.

Key changes in v2:
- PlanItem renamed to Task (clearer terminology)
- Each Task is executed by a single agent
- Plan belongs to a Project (not a Task)

## Plan <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L22" class="source-link" title="View source code">source</a>

The execution plan for a project.

A plan defines how to achieve a project's goal as a series of interconnected tasks.
Each task is executed by a single agent, and tasks can be executed in parallel
when their dependencies are met.

### get_task_by_id <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L45" class="source-link" title="View source code">source</a>

```python
def get_task_by_id(self, task_id: str) -> Optional[Task]
```

Get a task by its ID.

### get_next_actionable_task <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L52" class="source-link" title="View source code">source</a>

```python
def get_next_actionable_task(self) -> Optional[Task]
```

Find the next task that can be executed.
A task is actionable if it's pending and all its dependencies are completed.

### get_all_actionable_tasks <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L65" class="source-link" title="View source code">source</a>

```python
def get_all_actionable_tasks(self, max_tasks: Optional[int] = None) -> List[Task]
```

Find all tasks that can be executed in parallel.

**Args:**
    max_tasks: Maximum number of tasks to return (None for no limit)

**Returns:**
    List of tasks that can be executed concurrently

### update_task_status <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L87" class="source-link" title="View source code">source</a>

```python
def update_task_status(self, task_id: str, status: TaskStatus) -> bool
```

Update the status of a task by ID.

### assign_task <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L96" class="source-link" title="View source code">source</a>

```python
def assign_task(self, task_id: str, agent_name: str) -> bool
```

Assign a task to an agent.

### is_complete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L105" class="source-link" title="View source code">source</a>

```python
def is_complete(self) -> bool
```

Check if all tasks in the plan are completed.

### has_failed_tasks <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L109" class="source-link" title="View source code">source</a>

```python
def has_failed_tasks(self) -> bool
```

Check if any tasks have failed.

### get_progress_summary <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L113" class="source-link" title="View source code">source</a>

```python
def get_progress_summary(self) -> Dict[str, Any]
```

Get a summary of the plan's progress.

### get_task_graph <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L137" class="source-link" title="View source code">source</a>

```python
def get_task_graph(self) -> Dict[str, List[str]]
```

Get the task dependency graph.

**Returns:**
    Dict mapping task IDs to their dependent task IDs

### validate_dependencies <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/plan.py#L153" class="source-link" title="View source code">source</a>

```python
def validate_dependencies(self) -> List[str]
```

Validate that all task dependencies exist in the plan.

**Returns:**
    List of error messages (empty if valid)
