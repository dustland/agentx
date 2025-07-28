"""
Task module - Defines the Task class and related functionality.

In VibeX v2.0+:
- Project: Top-level container for work
- Task: Execution unit within a project (formerly PlanItem)
- TaskStep: Individual actions within a task

A Task represents a single unit of work that can be assigned to an agent
and executed as part of a project's plan.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

# Task status represents the execution state of individual tasks
TaskStatus = Literal["pending", "running", "completed", "failed", "skipped"]

# Failure policy for task execution
FailurePolicy = Literal["halt", "proceed"]


class Task(BaseModel):
    """
    Represents a single task in a project plan.
    
    A task is the atomic unit of work in VibeX. Each task:
    - Has a clear goal/objective
    - Can be assigned to a single agent
    - May depend on other tasks
    - Produces a result upon completion
    """
    id: str = Field(
        description="Unique identifier for the task.", 
        default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}"
    )
    action: str = Field(description="The action to be performed by this task.")
    status: TaskStatus = Field("pending", description="The current status of the task.")
    dependencies: List[str] = Field([], description="A list of task IDs that this task depends on.")
    result: Optional[str] = Field(None, description="The result or output of the task upon completion.")
    assigned_to: Optional[str] = Field(None, description="The agent assigned to this task.")

    def assign_to_agent(self, agent_name: str):
        """Assigns the task to an agent."""
        self.assigned_to = agent_name

    def can_start(self, completed_task_ids: List[str]) -> bool:
        """Check if this task can start based on completed dependencies."""
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create a Task instance from a dictionary."""
        return cls(**data)


# Export all public APIs
__all__ = [
    'Task',
    'TaskStatus',
    'FailurePolicy',
]