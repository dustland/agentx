# Core VibeX components
from .brain import Brain, BrainMessage, BrainResponse
from .message import (
    TaskStep,
    TextPart,
    ToolCallPart,
    ToolResultPart,
    ArtifactPart,
    ImagePart,
    FilePart,
    StepStartPart,
    ReasoningPart,
    ErrorPart,
    Artifact,

    StreamError,
    StreamComplete
)
from .tool import ToolCall, ToolResult
from .project import Project
from .plan import Plan
from .task import Task, TaskStatus, FailurePolicy
from .xagent import XAgent, XAgentResponse

# High-level functions
from .project import start_project, run_project

__all__ = [
    # Brain
    "Brain",
    "BrainMessage",
    "BrainResponse",
    # Messages
    "TaskStep",
    "TextPart",
    "ToolCall",
    "ToolCallPart",
    "ToolResult",
    "ToolResultPart",
    "ArtifactPart",
    "ImagePart",
    "FilePart",
    "StepStartPart",
    "ReasoningPart",
    "ErrorPart",
    "Artifact",

    "StreamError",
    "StreamComplete",
    # Project and Planning
    "Project",
    "Plan",
    "Task",
    "TaskStatus",
    "FailurePolicy",
    # XAgent
    "XAgent",
    "XAgentResponse",
    # High-level functions
    "start_project",
    "run_project"
]

# Note: No model rebuilds needed since ToolCallPart is now self-contained
# and doesn't have forward references to ToolCall
