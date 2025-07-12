"""
Planning system for AgentX framework.

This module provides a comprehensive planning system that allows agents to break down
complex tasks into manageable steps, track progress, and coordinate execution.

# Test comment to verify pre-commit hooks work
"""
from __future__ import annotations

from typing import Literal, List, Optional
from pydantic import BaseModel, Field

# A list of valid statuses for a task.
# pending: The task has not yet been started.
# in_progress: The task has been started but is not yet complete.
# completed: The task has been completed successfully.
# failed: The task execution resulted in an error.
# cancelled: The task was cancelled before it could be completed.
TaskStatus = Literal["pending", "in_progress", "completed", "failed", "cancelled"]

# Defines the policy for how the Orchestrator should proceed when a task fails.
# halt: Stop all execution immediately.
# escalate_to_user: Pause execution and wait for user input.
# proceed: Mark the task as failed and move on to the next independent task.
FailurePolicy = Literal["halt", "escalate_to_user", "proceed"]


class PlanItem(BaseModel):
    """
    A single item within a plan, representing one unit of work to be performed by an agent.
    """

    id: str = Field(..., description="A unique identifier for the task.")
    name: str = Field(
        ..., description="A short, human-readable name for the task."
    )
    goal: str = Field(
        ...,
        description="A clear and concise description of what needs to be achieved for this task to be considered complete.",
    )
    agent: Optional[str] = Field(
        None,
        description="The specific agent assigned to this task. If null, the Orchestrator will route it to the best available agent.",
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="A list of task IDs that must be completed before this task can start.",
    )
    status: TaskStatus = Field(
        "pending", description="The current status of the task."
    )
    on_failure: FailurePolicy = Field(
        "halt",
        description="The policy for how to proceed if this task fails.",
    )

class Plan(BaseModel):
    """
    The central data structure for the Orchestration System. It defines the entire workflow
    for achieving a high-level goal as a series of interconnected tasks.
    """

    goal: str = Field(
        ...,
        description="The high-level objective that this entire plan is designed to achieve.",
    )
    tasks: List[PlanItem] = Field(
        default_factory=list, description="The list of tasks that make up the plan."
    )

    def get_next_actionable_task(self) -> Optional[PlanItem]:
        """
        Find the next task that can be executed.
        A task is actionable if it's pending and all its dependencies are completed.
        """
        for task in self.tasks:
            if task.status != "pending":
                continue

            # Check if all dependencies are completed
            dependencies_met = True
            for dep_id in task.dependencies:
                dep_task = self.get_task_by_id(dep_id)
                if not dep_task or dep_task.status != "completed":
                    dependencies_met = False
                    break

            if dependencies_met:
                return task

        return None

    def get_task_by_id(self, task_id: str) -> Optional[PlanItem]:
        """Get a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update the status of a task by ID."""
        task = self.get_task_by_id(task_id)
        if task:
            task.status = status
            return True
        return False

    def is_complete(self) -> bool:
        """Check if all tasks in the plan are completed."""
        return all(task.status == "completed" for task in self.tasks)

    def has_failed_tasks(self) -> bool:
        """Check if any tasks have failed."""
        return any(task.status == "failed" for task in self.tasks)

    def get_progress_summary(self) -> dict:
        """Get a summary of plan progress."""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.status == "completed")
        failed = sum(1 for task in self.tasks if task.status == "failed")
        in_progress = sum(1 for task in self.tasks if task.status == "in_progress")
        pending = sum(1 for task in self.tasks if task.status == "pending")

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": pending,
            "completion_percentage": (completed / total * 100) if total > 0 else 0
        }
