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
    approval_required: bool = Field(
        False,
        description="If true, the Orchestrator will pause after this task is completed and wait for user approval to proceed.",
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