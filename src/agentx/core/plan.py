from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import uuid

# Literal types for status fields to enforce controlled vocabularies
TaskStatus = Literal["pending", "in_progress", "completed", "failed", "blocked"]
PhaseStatus = Literal["pending", "in_progress", "completed"]
OverallStatus = Literal["not_started", "in_progress", "completed", "failed"]

class PlanMetadata(BaseModel):
    """Metadata associated with the plan."""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    load_error: Optional[str] = None

class Progress(BaseModel):
    """Progress tracking for the entire plan."""
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    percentage_complete: float = 0.0

class Task(BaseModel):
    """A single, discrete unit of work within a phase."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    status: TaskStatus = "pending"
    assigned_to: Optional[str] = None
    deliverable: Optional[str] = None
    success_criteria: List[Dict[str, Any]] = Field(default_factory=list) # To be refined with a formal ValidationRule model
    notes: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())

class Phase(BaseModel):
    """A collection of related tasks that represent a major stage of the project."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    status: PhaseStatus = "pending"
    tasks: List[Task] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Plan(BaseModel):
    """The authoritative, structured guide for a multi-agent task."""
    metadata: PlanMetadata = Field(default_factory=PlanMetadata)
    plan_name: Optional[str] = "Unnamed Plan"
    phases: List[Phase] = Field(default_factory=list)
    overall_status: OverallStatus = "not_started"
    progress: Progress = Field(default_factory=Progress)

    def update_progress(self):
        """Recalculates the overall progress statistics based on task statuses."""
        total_tasks = 0
        completed_tasks = 0
        in_progress_tasks = 0
        failed_tasks = 0

        for phase in self.phases:
            phase_tasks_total = len(phase.tasks)
            phase_tasks_completed = 0
            for task in phase.tasks:
                total_tasks += 1
                if task.status == "completed":
                    completed_tasks += 1
                    phase_tasks_completed += 1
                elif task.status == "in_progress":
                    in_progress_tasks += 1
                elif task.status == "failed":
                    failed_tasks += 1
            
            # Update phase status based on its tasks
            if phase_tasks_total > 0 and phase_tasks_completed == phase_tasks_total:
                phase.status = "completed"
            elif any(t.status in ["in_progress", "completed"] for t in phase.tasks):
                phase.status = "in_progress"
            else:
                phase.status = "pending"


        percentage_complete = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

        self.progress = Progress(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            percentage_complete=round(percentage_complete, 1)
        )

        # Update overall plan status
        if failed_tasks > 0:
            self.overall_status = "failed"
        elif total_tasks > 0 and completed_tasks == total_tasks:
            self.overall_status = "completed"
        elif in_progress_tasks > 0 or completed_tasks > 0:
            self.overall_status = "in_progress"
        else:
            self.overall_status = "not_started"
        
        self.metadata.last_updated = datetime.now().isoformat() 