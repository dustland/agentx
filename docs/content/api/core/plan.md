# Planning System

*Module: [`agentx.core.plan`](https://github.com/dustland/agentx/blob/main/src/agentx/core/plan.py)*

Planning system for AgentX framework.

This module provides a comprehensive planning system that allows agents to break down
complex tasks into manageable steps, track progress, and coordinate execution.

# Test comment to verify pre-commit hooks work

## PlanItem <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/plan.py#L29" class="source-link" title="View source code">source</a>

A single item within a plan, representing one unit of work to be performed by an agent.

## Plan <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/plan.py#L58" class="source-link" title="View source code">source</a>

The central data structure for the Orchestration System. It defines the entire workflow
for achieving a high-level goal as a series of interconnected tasks.

### get_next_actionable_task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/plan.py#L72" class="source-link" title="View source code">source</a>

```python
def get_next_actionable_task(self) -> Optional[PlanItem]
```

Find the next task that can be executed.
A task is actionable if it's pending and all its dependencies are completed.

### get_task_by_id <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/plan.py#L94" class="source-link" title="View source code">source</a>

```python
def get_task_by_id(self, task_id: str) -> Optional[PlanItem]
```

Get a task by its ID.

### update_task_status <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/plan.py#L101" class="source-link" title="View source code">source</a>

```python
def update_task_status(self, task_id: str, status: TaskStatus) -> bool
```

Update the status of a task by ID.

### is_complete <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/plan.py#L109" class="source-link" title="View source code">source</a>

```python
def is_complete(self) -> bool
```

Check if all tasks in the plan are completed.

### has_failed_tasks <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/plan.py#L113" class="source-link" title="View source code">source</a>

```python
def has_failed_tasks(self) -> bool
```

Check if any tasks have failed.

### get_progress_summary <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/plan.py#L117" class="source-link" title="View source code">source</a>

```python
def get_progress_summary(self) -> dict
```

Get a summary of plan progress.
