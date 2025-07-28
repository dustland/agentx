"""
Planning system for VibeX framework - Version 2.

This module provides a comprehensive planning system that allows projects to break down
complex goals into manageable tasks, track progress, and coordinate execution.

Key changes in v2:
- PlanItem renamed to Task (clearer terminology)
- Each Task is executed by a single agent
- Plan belongs to a Project (not a Task)
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Import Task and related types from task module
from .task import Task, TaskStatus, FailurePolicy


class Plan(BaseModel):
    """
    The execution plan for a project.
    
    A plan defines how to achieve a project's goal as a series of interconnected tasks.
    Each task is executed by a single agent, and tasks can be executed in parallel
    when their dependencies are met.
    """
    
    tasks: List[Task] = Field(
        default_factory=list, 
        description="The list of tasks that make up the plan."
    )
    
    # Plan metadata
    created_at: Optional[datetime] = Field(None, description="When the plan was created.")
    updated_at: Optional[datetime] = Field(None, description="When the plan was last updated.")
    version: int = Field(1, description="Plan version number for tracking changes.")
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_next_actionable_task(self) -> Optional[Task]:
        """
        Find the next task that can be executed.
        A task is actionable if it's pending and all its dependencies are completed.
        """
        completed_ids = [t.id for t in self.tasks if t.status == "completed"]
        
        for task in self.tasks:
            if task.status == "pending" and task.can_start(completed_ids):
                return task
        
        return None
    
    def get_all_actionable_tasks(self, max_tasks: Optional[int] = None) -> List[Task]:
        """
        Find all tasks that can be executed in parallel.
        
        Args:
            max_tasks: Maximum number of tasks to return (None for no limit)
            
        Returns:
            List of tasks that can be executed concurrently
        """
        completed_ids = [t.id for t in self.tasks if t.status == "completed"]
        actionable_tasks = []
        
        for task in self.tasks:
            if task.status == "pending" and task.can_start(completed_ids):
                actionable_tasks.append(task)
                
                if max_tasks and len(actionable_tasks) >= max_tasks:
                    break
        
        return actionable_tasks
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update the status of a task by ID."""
        task = self.get_task_by_id(task_id)
        if task:
            task.status = status
            self._update_timestamp()
            return True
        return False
    
    def assign_task(self, task_id: str, agent_name: str) -> bool:
        """Assign a task to an agent."""
        task = self.get_task_by_id(task_id)
        if task:
            task.assign_to_agent(agent_name)
            self._update_timestamp()
            return True
        return False
    
    def is_complete(self) -> bool:
        """Check if all tasks in the plan are completed."""
        return all(task.status == "completed" for task in self.tasks)
    
    def has_failed_tasks(self) -> bool:
        """Check if any tasks have failed."""
        return any(task.status == "failed" for task in self.tasks)
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of the plan's progress."""
        total = len(self.tasks)
        if total == 0:
            return {"percentage": 0, "status": "empty"}
        
        status_counts = {
            "pending": sum(1 for t in self.tasks if t.status == "pending"),
            "running": sum(1 for t in self.tasks if t.status == "running"),
            "completed": sum(1 for t in self.tasks if t.status == "completed"),
            "failed": sum(1 for t in self.tasks if t.status == "failed"),
            "cancelled": sum(1 for t in self.tasks if t.status == "cancelled"),
        }
        
        percentage = (status_counts["completed"] / total) * 100
        
        return {
            "total_tasks": total,
            "status_counts": status_counts,
            "percentage": round(percentage, 1),
            "is_complete": self.is_complete(),
            "has_failures": self.has_failed_tasks(),
        }
    
    def get_task_graph(self) -> Dict[str, List[str]]:
        """
        Get the task dependency graph.
        
        Returns:
            Dict mapping task IDs to their dependent task IDs
        """
        graph = {}
        for task in self.tasks:
            dependents = [
                t.id for t in self.tasks 
                if task.id in t.dependencies
            ]
            graph[task.id] = dependents
        return graph
    
    def validate_dependencies(self) -> List[str]:
        """
        Validate that all task dependencies exist in the plan.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        project_ids = {task.id for task in self.tasks}
        
        for task in self.tasks:
            for dep_id in task.dependencies:
                if dep_id not in project_ids:
                    errors.append(
                        f"Task '{task.id}' depends on non-existent task '{dep_id}'"
                    )
                    
            # Check for circular dependencies
            if self._has_circular_dependency(task.id, set()):
                errors.append(f"Task '{task.id}' has circular dependencies")
        
        return errors
    
    def _has_circular_dependency(self, project_id: str, visited: set) -> bool:
        """Check if a task has circular dependencies."""
        if project_id in visited:
            return True
            
        visited.add(project_id)
        task = self.get_task_by_id(project_id)
        
        if task:
            for dep_id in task.dependencies:
                if self._has_circular_dependency(dep_id, visited.copy()):
                    return True
        
        return False
    
    def _update_timestamp(self) -> None:
        """Update the plan's last modified timestamp."""
        self.updated_at = datetime.now()
        self.version += 1


# Compatibility aliases for smooth transition
PlanItem = Task  # Temporary alias, will be removed in v2.0

# Import TaskStep to resolve forward reference before rebuilding
from vibex.core.message import TaskStep

# Rebuild models to resolve forward references
Task.model_rebuild()
Plan.model_rebuild()

__all__ = ['Plan', 'Task', 'TaskStatus', 'FailurePolicy', 'PlanItem']