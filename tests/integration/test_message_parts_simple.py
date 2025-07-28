"""Simple integration test for message parts without full XAgent setup."""
import pytest
import json
from typing import List, Dict, Any

from vibex.core.message import (
    Message, TextPart, ToolCallPart, ToolResultPart,
    ReasoningPart, ErrorPart, StepStartPart, ImagePart, FilePart
)
from vibex.core.message_builder import StreamingMessageBuilder


@pytest.mark.integration
class TestMessagePartsSimple:
    """Simple integration tests for message parts."""
    
    def test_message_builder_basic(self):
        """Test basic message building with parts."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Add text
        builder.add_text_delta("Hello ")
        builder.add_text_delta("world!")
        
        # Build message
        message = builder.build()
        
        assert message.role == "assistant"
        assert message.content == "Hello world!"
        assert len(message.parts) == 1
        assert message.parts[0].type == "text"
        assert message.parts[0].text == "Hello world!"
    
    def test_message_builder_with_tool_call(self):
        """Test message building with tool call and result."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Add initial text
        builder.add_text_delta("Let me calculate that for you.\n")
        builder.finalize_text_part()
        
        # Add tool call
        tool_call_id = "tc_calc_123"
        part_idx = builder.add_tool_call(
            tool_call_id=tool_call_id,
            tool_name="calculator",
            args={"expression": "2 + 2"}
        )
        assert part_idx == 1
        
        # Add tool result
        part_idx = builder.add_tool_result(
            tool_call_id=tool_call_id,
            tool_name="calculator",
            result={"answer": 4},
            is_error=False
        )
        assert part_idx == 2
        
        # Add final text
        builder.add_text_delta("The answer is 4.")
        
        # Build message
        message = builder.build()
        
        assert len(message.parts) == 4
        assert message.parts[0].type == "text"
        assert message.parts[0].text == "Let me calculate that for you.\n"
        assert message.parts[1].type == "tool-call"
        assert message.parts[1].toolName == "calculator"
        assert message.parts[2].type == "tool-result"
        assert message.parts[2].result["answer"] == 4
        assert message.parts[3].type == "text"
        assert message.parts[3].text == "The answer is 4."
        
        # Check combined content (includes tool result status)
        assert message.content == "Let me calculate that for you.\n\nTool calculator completed.The answer is 4."
    
    def test_message_parts_serialization(self):
        """Test that message parts serialize correctly."""
        # Create message with various parts
        message = Message(
            role="assistant",
            content="Combined text content",
            parts=[
                TextPart(text="Hello"),
                ToolCallPart(
                    toolCallId="tc_123",
                    toolName="search",
                    args={"query": "test"}
                ),
                ToolResultPart(
                    toolCallId="tc_123",
                    toolName="search",
                    result={"results": ["item1", "item2"]},
                    isError=False
                ),
                ReasoningPart(content="Internal thoughts"),
                ErrorPart(error="Something failed", errorCode="ERR_001")
            ]
        )
        
        # Serialize to JSON (using model_dump_json for Pydantic v2)
        json_str = message.model_dump_json()
        data = json.loads(json_str)
        
        # Verify structure
        assert data["role"] == "assistant"
        assert len(data["parts"]) == 5
        
        # Verify each part
        assert data["parts"][0]["type"] == "text"
        assert data["parts"][1]["type"] == "tool-call"
        assert data["parts"][2]["type"] == "tool-result"
        assert data["parts"][3]["type"] == "reasoning"
        assert data["parts"][4]["type"] == "error"
    
    def test_part_field_naming(self):
        """Verify all parts use camelCase field names for frontend compatibility."""
        # Test each part type
        parts = [
            ToolCallPart(toolCallId="tc_1", toolName="test", args={}),
            ToolResultPart(toolCallId="tc_1", toolName="test", result={}, isError=False),
            ImagePart(image="data", mimeType="image/png"),
            StepStartPart(stepId="step_1", stepName="Test Step"),
            ErrorPart(error="Test error", errorCode="TEST_001")
        ]
        
        for part in parts:
            # Convert to dict and check field names (using model_dump for Pydantic v2)
            part_dict = part.model_dump()
            
            # These should all be camelCase
            if part.type == "tool-call":
                assert "toolCallId" in part_dict
                assert "toolName" in part_dict
                assert "tool_call_id" not in part_dict  # Should not have snake_case
            elif part.type == "tool-result":
                assert "toolCallId" in part_dict
                assert "toolName" in part_dict
                assert "isError" in part_dict
                assert "is_error" not in part_dict
            elif part.type == "image":
                assert "mimeType" in part_dict
                assert "mime_type" not in part_dict
            elif part.type == "step-start":
                assert "stepId" in part_dict
                assert "stepName" in part_dict
                assert "step_id" not in part_dict
            elif part.type == "error":
                assert "errorCode" in part_dict
                assert "error_code" not in part_dict
    
    def test_error_handling_in_message(self):
        """Test error parts in messages."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Add normal flow
        builder.add_text_delta("Processing...\n")
        builder.finalize_text_part()
        
        # Add tool call
        tool_call_id = "tc_fail"
        builder.add_tool_call(tool_call_id, "risky_tool", {"action": "dangerous"})
        
        # Add error result
        builder.add_tool_result(
            tool_call_id=tool_call_id,
            tool_name="risky_tool",
            result="Permission denied",
            is_error=True
        )
        
        # Add error part
        builder.add_part(ErrorPart(
            error="Tool execution failed",
            errorCode="PERMISSION_DENIED"
        ))
        
        # Add recovery text
        builder.add_text_delta("Let me try a different approach.")
        
        message = builder.build()
        
        # Verify error handling
        assert len(message.parts) == 5
        
        # Check tool result has error flag
        tool_result = next(p for p in message.parts if p.type == "tool-result")
        assert tool_result.isError == True
        
        # Check error part
        error_part = next(p for p in message.parts if p.type == "error")
        assert error_part.errorCode == "PERMISSION_DENIED"
    
    def test_multimodal_parts(self):
        """Test image and file parts."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Add text
        builder.add_text_delta("Here's the analysis:\n")
        builder.finalize_text_part()
        
        # Add image
        builder.add_part(ImagePart(
            image="data:image/png;base64,iVBORw0...",
            mimeType="image/png"
        ))
        
        # Add file
        builder.add_part(FilePart(
            data="file content",
            mimeType="text/plain"
        ))
        
        # Add final text
        builder.add_text_delta("Analysis complete.")
        
        message = builder.build()
        
        assert len(message.parts) == 4
        assert message.parts[1].type == "image"
        assert message.parts[2].type == "file"
    
    def test_reasoning_and_step_parts(self):
        """Test reasoning and step boundary parts."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Add step start
        builder.add_part(StepStartPart(
            stepId="step_1",
            stepName="Data Analysis"
        ))
        
        # Add reasoning
        builder.add_part(ReasoningPart(
            content="I need to analyze the data structure first..."
        ))
        
        # Add text
        builder.add_text_delta("Starting analysis...")
        
        message = builder.build()
        
        assert len(message.parts) == 3
        assert message.parts[0].type == "step-start"
        assert message.parts[1].type == "reasoning"
        assert message.parts[2].type == "text"
    
    def test_message_id_generation(self):
        """Test that messages get unique IDs."""
        msg1 = Message(role="user", content="Test 1")
        msg2 = Message(role="user", content="Test 2")
        
        assert msg1.id != msg2.id
        assert msg1.id.startswith("msg_") or len(msg1.id) > 0
        assert msg2.id.startswith("msg_") or len(msg2.id) > 0
    
    def test_empty_message_handling(self):
        """Test handling of empty messages."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Build empty message
        message = builder.build()
        
        assert message.role == "assistant"
        assert message.content == ""
        assert len(message.parts) == 0
    
    def test_text_accumulation(self):
        """Test that text accumulates correctly."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Add multiple text chunks
        chunks = ["The", " ", "quick", " ", "brown", " ", "fox"]
        for chunk in chunks:
            builder.add_text_delta(chunk)
        
        # Don't finalize, just build
        message = builder.build()
        
        assert len(message.parts) == 1
        assert message.parts[0].text == "The quick brown fox"
        assert message.content == "The quick brown fox"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])