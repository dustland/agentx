"""
Message Builder for Streaming

Builds structured messages with parts during streaming,
following the Vercel AI SDK pattern.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from .message import (
    Message, MessagePart, TextPart, ToolCallPart, ToolResultPart,
    ImagePart, StepStartPart, ReasoningPart, ErrorPart
)
from ..utils.id import generate_short_id
from ..utils.logger import get_logger

logger = get_logger(__name__)


class StreamingMessageBuilder:
    """
    Builds a Message with parts during streaming.
    
    This builder accumulates message parts as they stream in,
    maintaining proper structure for frontend visualization.
    """
    
    def __init__(self, message_id: Optional[str] = None, role: str = "assistant"):
        """Initialize a new message builder."""
        self.message_id = message_id or generate_short_id()
        self.role = role
        self.parts: List[MessagePart] = []
        self.current_text = ""
        self.current_part_index = -1
        self.timestamp = datetime.now()
        
        # Track tool calls for matching results
        self.pending_tool_calls: Dict[str, ToolCallPart] = {}
        
        logger.debug(f"Created message builder for {role} message {self.message_id}")
    
    def add_text_delta(self, text: str) -> int:
        """
        Add text to current text part.
        
        Returns:
            Part index where text was added
        """
        self.current_text += text
        return self.current_part_index + 1  # Next index when finalized
    
    def finalize_text_part(self) -> Optional[int]:
        """
        Convert accumulated text to TextPart.
        
        Returns:
            Part index if text was finalized, None if no text
        """
        if self.current_text:
            part = TextPart(text=self.current_text)
            self.parts.append(part)
            self.current_text = ""
            self.current_part_index += 1
            logger.debug(f"Finalized text part at index {self.current_part_index}")
            return self.current_part_index
        return None
    
    def add_tool_call(self, 
                      tool_call_id: str,
                      tool_name: str,
                      args: Dict[str, Any]) -> int:
        """
        Add a tool call part.
        
        Returns:
            Part index of the added tool call
        """
        # Finalize any pending text first
        self.finalize_text_part()
        
        # Create tool call part
        part = ToolCallPart(
            toolCallId=tool_call_id,
            toolName=tool_name,
            args=args
        )
        
        self.parts.append(part)
        self.current_part_index += 1
        
        # Track for result matching
        self.pending_tool_calls[tool_call_id] = part
        
        logger.debug(f"Added tool call {tool_name} at index {self.current_part_index}")
        return self.current_part_index
    
    def add_tool_result(self,
                       tool_call_id: str,
                       tool_name: str,
                       result: Any,
                       is_error: bool = False) -> int:
        """
        Add a tool result part.
        
        Returns:
            Part index of the added tool result
        """
        part = ToolResultPart(
            toolCallId=tool_call_id,
            toolName=tool_name,
            result=result,
            isError=is_error
        )
        
        self.parts.append(part)
        self.current_part_index += 1
        
        # Remove from pending
        self.pending_tool_calls.pop(tool_call_id, None)
        
        logger.debug(f"Added tool result for {tool_name} at index {self.current_part_index}")
        return self.current_part_index
    
    def add_step_start(self, step_id: str, step_name: Optional[str] = None) -> int:
        """Add a step boundary marker."""
        self.finalize_text_part()
        
        part = StepStartPart(
            stepId=step_id,
            stepName=step_name
        )
        
        self.parts.append(part)
        self.current_part_index += 1
        return self.current_part_index
    
    def add_reasoning(self, content: str) -> int:
        """Add agent reasoning/thinking."""
        self.finalize_text_part()
        
        part = ReasoningPart(content=content)
        self.parts.append(part)
        self.current_part_index += 1
        return self.current_part_index
    
    def add_error(self, error: str, error_code: Optional[str] = None) -> int:
        """Add an error part."""
        self.finalize_text_part()
        
        part = ErrorPart(
            error=error,
            errorCode=error_code
        )
        
        self.parts.append(part)
        self.current_part_index += 1
        return self.current_part_index
    
    def add_image(self, image: str, mime_type: Optional[str] = None) -> int:
        """Add an image part."""
        self.finalize_text_part()
        
        part = ImagePart(
            image=image,
            mimeType=mime_type
        )
        
        self.parts.append(part)
        self.current_part_index += 1
        return self.current_part_index
    
    def add_part(self, part: MessagePart) -> int:
        """
        Add a generic MessagePart.
        
        This is useful for adding custom part types that don't have
        dedicated builder methods.
        
        Returns:
            Part index of the added part
        """
        self.finalize_text_part()
        
        self.parts.append(part)
        self.current_part_index += 1
        return self.current_part_index
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current builder state for debugging."""
        return {
            "message_id": self.message_id,
            "role": self.role,
            "parts_count": len(self.parts),
            "current_text_length": len(self.current_text),
            "pending_tool_calls": list(self.pending_tool_calls.keys())
        }
    
    def build(self) -> Message:
        """
        Build the final message.
        
        Returns:
            Complete Message with all parts
        """
        # Finalize any pending text
        self.finalize_text_part()
        
        # Build content field for backward compatibility
        content_parts = []
        
        for part in self.parts:
            if isinstance(part, TextPart):
                content_parts.append(part.text)
            elif isinstance(part, ToolCallPart):
                # Don't include tool calls in content
                pass
            elif isinstance(part, ToolResultPart):
                # Include tool results in a readable format
                if isinstance(part.result, str):
                    content_parts.append(f"\n{part.result}")
                else:
                    # For complex results, just indicate completion
                    status = "failed" if part.isError else "completed"
                    content_parts.append(f"\nTool {part.toolName} {status}.")
            elif isinstance(part, ReasoningPart):
                # Don't include reasoning in main content
                pass
            elif isinstance(part, ErrorPart):
                content_parts.append(f"\nError: {part.error}")
        
        content = "".join(content_parts).strip()
        
        message = Message(
            id=self.message_id,
            role=self.role,
            content=content,
            parts=self.parts,
            timestamp=self.timestamp
        )
        
        logger.info(f"Built message {self.message_id} with {len(self.parts)} parts")
        return message