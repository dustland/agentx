"""
Server Models

Data models for the VibeX REST API.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Get current UTC datetime - replaces deprecated datetime.now()"""
    return datetime.now(timezone.utc)


class TaskStatus(str, Enum):
    """Task status enumeration - aligns with XAgent task statuses"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"  # Additional status for error state


class CreateXAgentRequest(BaseModel):
    """Request to create and run an XAgent instance"""
    config_path: str = Field(description="Path to the team configuration file")
    goal: Optional[str] = Field(default="", description="Goal or mission for the XAgent to achieve")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the XAgent")
    user_id: Optional[str] = Field(default=None, description="User ID for multi-tenant isolation")


class XAgentResponse(BaseModel):
    """Response from XAgent operations"""
    agent_id: str = Field(description="The XAgent's unique identifier")
    status: TaskStatus
    goal: Optional[str] = Field(default=None, description="The XAgent's goal")
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    completed_at: Optional[datetime] = None
    user_id: Optional[str] = None
    config_path: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    plan: Optional[Dict[str, Any]] = None


class TaskRunInfo(BaseModel):
    """Detailed information about a task run"""
    agent_id: str
    status: TaskStatus
    config_path: str
    goal: str
    context: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    user_id: Optional[str] = None
    plan: Optional[Dict[str, Any]] = None


class XAgentListResponse(BaseModel):
    """Response for listing XAgents"""
    runs: List[XAgentResponse]


class MemoryRequest(BaseModel):
    """Request for memory operations"""
    agent_id: str
    content: Optional[str] = Field(default=None, description="Content to add to memory")
    query: Optional[str] = Field(default=None, description="Query to search memory")


class MemoryResponse(BaseModel):
    """Response from memory operations"""
    agent_id: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=utc_now)
    version: str = "0.4.0"
    active_agents: int = 0
    service_name: str = "VibeX API"
    service_type: str = "vibex-agent-orchestration"
    api_endpoints: List[str] = Field(default_factory=lambda: [
        "/agents", "/agents/{agent_id}", "/agents/{agent_id}/memory", "/health", "/monitor"
    ])
