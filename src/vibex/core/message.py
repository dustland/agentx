from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Literal, TYPE_CHECKING
from ..utils.id import generate_short_id
from vibex.utils.logger import get_logger

# This file defines the core data structures for the VibeX framework,
# as specified in design document 03-data-and-events.md.

# --- Core Data Structures ---

# Note: ToolCall and ToolResult are defined in core.tool, not here. This separation is intentional:
# - ToolCall/ToolResult = tool execution models (core.tool)
# - ToolCallPart/ToolResultPart = conversation representations (here in message.py)
# The conversation parts are self-contained and don't depend on tool execution models

class Artifact(BaseModel):
    """Artifact reference with versioning and metadata."""
    uri: str  # e.g., "file://artifacts/main.py"
    mime_type: str
    size_bytes: Optional[int] = None
    description: Optional[str] = None
    version: Optional[str] = None  # For artifact versioning
    checksum: Optional[str] = None  # For integrity verification
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Extensible metadata
    created_by: Optional[str] = None  # Agent or tool that created it
    tags: List[str] = Field(default_factory=list)  # For categorization and search

# --- TaskStep and its Parts ---

# Message Parts - Following Vercel AI SDK structure
class MessagePart(BaseModel):
    """Base class for message parts."""
    type: str
    
    class Config:
        # Ensure all fields are included in serialization
        extra = "forbid"

class TextPart(MessagePart):
    """Text content part."""
    type: Literal["text"] = "text"
    text: str

class ToolCallPart(MessagePart):
    """Tool call part - represents a tool invocation."""
    type: Literal["tool-call"] = "tool-call"
    toolCallId: str
    toolName: str
    args: Dict[str, Any]
    
    class Config:
        populate_by_name = True

class ToolResultPart(MessagePart):
    """Tool result part - represents the result of a tool execution."""
    type: Literal["tool-result"] = "tool-result"
    toolCallId: str
    toolName: str
    result: Any
    isError: bool = False
    
    class Config:
        populate_by_name = True

class ArtifactPart(MessagePart):
    """Artifact reference part."""
    type: Literal["artifact"] = "artifact"
    artifact: Artifact

class ImagePart(MessagePart):
    """Image content part."""
    type: Literal["image"] = "image"
    image: Union[str, bytes]  # URL, base64, or binary data
    mimeType: Optional[str] = None
    
    class Config:
        populate_by_name = True

class FilePart(MessagePart):
    """File content part."""
    type: Literal["file"] = "file"
    data: Union[str, bytes]  # URL, base64, or binary data
    mimeType: str
    
    class Config:
        populate_by_name = True

# Extended parts for agent-specific features
class StepStartPart(MessagePart):
    """Step boundary marker for multi-step operations."""
    type: Literal["step-start"] = "step-start"
    stepId: str
    stepName: Optional[str] = None
    
    class Config:
        populate_by_name = True

class ReasoningPart(MessagePart):
    """Agent reasoning/thinking part."""
    type: Literal["reasoning"] = "reasoning"
    content: str

class ErrorPart(MessagePart):
    """Error message part."""
    type: Literal["error"] = "error"
    error: str
    errorCode: Optional[str] = None
    
    class Config:
        populate_by_name = True

# --- Standard Chat Message Format (compatible with Vercel AI SDK) ---

class Message(BaseModel):
    """
    Standard chat message format compatible with LLM APIs and Vercel AI SDK.

    This follows the industry standard format with role/content/parts structure.
    """
    id: str = Field(default_factory=generate_short_id)
    role: Literal["system", "user", "assistant", "tool"] = "user"
    content: str = ""  # Backward compatibility - text content
    parts: List[Union[
        TextPart, 
        ToolCallPart, 
        ToolResultPart, 
        ArtifactPart, 
        ImagePart, 
        FilePart, 
        StepStartPart, 
        ReasoningPart, 
        ErrorPart
    ]] = Field(default_factory=list)  # Modern structured content
    timestamp: datetime = Field(default_factory=datetime.now)

    @classmethod
    def user_message(cls, content: str, parts: Optional[List[MessagePart]] = None) -> "Message":
        """Create a user message."""
        if parts is None:
            parts = [TextPart(text=content)] if content else []
        return cls(
            role="user",
            content=content,
            parts=parts
        )

    @classmethod
    def assistant_message(cls, content: str, parts: Optional[List[MessagePart]] = None) -> "Message":
        """Create an assistant message."""
        if parts is None:
            parts = [TextPart(text=content)] if content else []
        return cls(
            role="assistant",
            content=content,
            parts=parts
        )

    @classmethod
    def system_message(cls, content: str, parts: Optional[List[MessagePart]] = None) -> "Message":
        """Create a system message."""
        if parts is None:
            parts = [TextPart(text=content)] if content else []
        return cls(
            role="system",
            content=content,
            parts=parts
        )
    
    @classmethod
    def tool_message(cls, tool_results: List[ToolResultPart]) -> "Message":
        """Create a tool message."""
        # Combine results into content for backward compatibility
        content = "\n".join([str(r.result) for r in tool_results])
        return cls(
            role="tool",
            content=content,
            parts=tool_results
        )

class UserMessage(Message):
    """User message - alias for Message with role='user'."""
    role: Literal["user"] = "user"

class TaskStep(BaseModel):
    """
    Represents a single execution step taken by an agent within a task.
    
    A TaskStep contains the actions performed by an agent, including tool calls,
    their results, and any other content generated during task execution.
    """
    id: str = Field(default_factory=generate_short_id)
    agent_name: str = Field(description="Name of the agent that performed this step")
    parts: List[MessagePart] = Field(default_factory=list, description="Content parts of this step")
    timestamp: datetime = Field(default_factory=datetime.now)
    task_id: Optional[str] = Field(None, description="ID of the task this step belongs to")
    
    def to_message(self) -> Message:
        """Convert TaskStep to a Message for unified chat history."""
        # Combine all text parts for content
        text_parts = [part.text for part in self.parts if isinstance(part, TextPart)]
        content = " ".join(text_parts) if text_parts else ""
        
        return Message(
            id=self.id,
            role="assistant",
            content=content,
            parts=self.parts,
            timestamp=self.timestamp
        )

class MessageQueue(BaseModel):
    """Queue for managing message flow in tasks."""
    messages: List[Message] = Field(default_factory=list)
    max_size: int = 1000

    def add(self, message: Message) -> None:
        """Add a message to the queue."""
        self.messages.append(message)
        if len(self.messages) > self.max_size:
            self.messages.pop(0)  # Remove oldest message

    def get_all(self) -> List[Message]:
        """Get all messages in the queue."""
        return self.messages.copy()

    def clear(self) -> None:
        """Clear all messages from the queue."""
        self.messages.clear()

class ConversationHistory(BaseModel):
    """Project conversation history with messages and metadata."""
    project_id: str
    messages: List[Message] = Field(default_factory=list)
    steps: List[TaskStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def add_message(self, message: Message) -> None:
        """Add a message to the history."""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def add_step(self, step: TaskStep) -> None:
        """Add a task step to the history."""
        self.steps.append(step)
        self.updated_at = datetime.now()

# --- Streaming Models ---



class StreamError(BaseModel):
    """
    Error in message streaming.
    """
    type: Literal["stream_error"] = "stream_error"
    step_id: str
    agent_name: str
    error_message: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StreamComplete(BaseModel):
    """
    Message streaming completion marker.
    """
    type: Literal["stream_complete"] = "stream_complete"
    step_id: str
    agent_name: str
    total_tokens: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
