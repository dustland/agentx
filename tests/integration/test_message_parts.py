import pytest
import asyncio
from typing import List, Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

from vibex.core.message import (
    Message, TextPart, ToolCallPart, ToolResultPart,
    ImagePart, FilePart, StepStartPart, ReasoningPart, ErrorPart
)
from vibex.core.message_builder import StreamingMessageBuilder
from vibex.core.xagent import XAgent
from vibex.core.tool import ToolCall, ToolResult
from vibex.tools import ToolRegistry
from vibex.agents import Agent
from vibex.utils.id import generate_short_id


class MockTool:
    """Mock tool for testing."""
    name = "test_tool"
    description = "A test tool"
    
    async def execute(self, **kwargs):
        return {"result": "Test result", "input": kwargs}


class MessageCapturingAgent(Agent):
    """Agent that captures all message parts during execution."""
    
    def __init__(self, name: str = "test_agent"):
        super().__init__(name=name)
        self.captured_parts: List[Dict[str, Any]] = []
        self.captured_messages: List[Message] = []
        self.captured_sse_events: List[Dict[str, Any]] = []
    
    async def run(self, task_context: Dict[str, Any], send_update):
        """Simulate agent execution with various message parts."""
        # Capture the send_update function to record SSE events
        original_send_update = send_update
        
        async def capturing_send_update(event_type: str, data: Any):
            self.captured_sse_events.append({
                "event": event_type,
                "data": data
            })
            await original_send_update(event_type, data)
        
        # Start with text
        builder = StreamingMessageBuilder(role="assistant")
        builder.add_text_delta("Let me help you with that. ")
        builder.add_text_delta("I'll use a tool to get the information.\n")
        
        # Add reasoning (internal monologue)
        builder.finalize_text_part()
        builder.add_part(ReasoningPart(content="I should use the test_tool to process this request."))
        
        # Add tool call
        tool_call_id = f"tc_{generate_short_id()}"
        builder.add_tool_call(
            tool_call_id=tool_call_id,
            tool_name="test_tool",
            args={"input": "test data", "count": 42}
        )
        
        # Simulate tool execution and add result
        builder.add_tool_result(
            tool_call_id=tool_call_id,
            tool_name="test_tool",
            result={"status": "success", "data": "Processed successfully"},
            is_error=False
        )
        
        # Add final text
        builder.add_text_delta("\nThe tool execution was successful. ")
        builder.add_text_delta("Here's what I found: the data was processed successfully.")
        
        # Build and capture the message
        message = builder.build()
        self.captured_messages.append(message)
        
        # Capture all parts
        for part in message.parts:
            self.captured_parts.append({
                "type": part.type,
                "data": part.dict()
            })
        
        # Return the message content
        return message.content


class TestMessagePartsIntegration:
    """Integration tests for message parts generation and transmission."""
    
    @pytest.mark.asyncio
    async def test_message_parts_generation(self):
        """Test that message parts are correctly generated during agent execution."""
        # Create agent
        agent = MessageCapturingAgent()
        
        # Run agent
        result = await agent.run(
            task_context={"input": "Test input"},
            send_update=AsyncMock()
        )
        
        # Verify message was created
        assert len(agent.captured_messages) == 1
        message = agent.captured_messages[0]
        
        # Verify message structure
        assert message.role == "assistant"
        assert len(message.parts) > 0
        
        # Verify part types and order
        part_types = [part.type for part in message.parts]
        expected_types = ["text", "reasoning", "tool-call", "tool-result", "text"]
        assert part_types == expected_types
        
        # Verify text parts
        text_parts = [p for p in message.parts if isinstance(p, TextPart)]
        assert len(text_parts) == 2
        assert "Let me help you with that" in text_parts[0].text
        assert "successful" in text_parts[1].text
        
        # Verify reasoning part
        reasoning_parts = [p for p in message.parts if isinstance(p, ReasoningPart)]
        assert len(reasoning_parts) == 1
        assert "test_tool" in reasoning_parts[0].content
        
        # Verify tool call part
        tool_calls = [p for p in message.parts if isinstance(p, ToolCallPart)]
        assert len(tool_calls) == 1
        tool_call = tool_calls[0]
        assert tool_call.toolName == "test_tool"
        assert tool_call.args["input"] == "test data"
        assert tool_call.args["count"] == 42
        
        # Verify tool result part
        tool_results = [p for p in message.parts if isinstance(p, ToolResultPart)]
        assert len(tool_results) == 1
        tool_result = tool_results[0]
        assert tool_result.toolName == "test_tool"
        assert tool_result.toolCallId == tool_call.toolCallId
        assert tool_result.result["status"] == "success"
        assert not tool_result.isError
    
    @pytest.mark.asyncio
    async def test_xagent_message_parts_streaming(self):
        """Test XAgent integration with message parts streaming."""
        # Mock brain that returns structured response
        mock_brain = AsyncMock()
        mock_brain.think = AsyncMock()
        
        # Create a mock async generator for streaming
        async def mock_stream():
            # Yield text chunks
            yield {"type": "text", "text": "I'll analyze "}
            yield {"type": "text", "text": "this for you.\n"}
            
            # Yield tool call
            yield {
                "type": "tool_call",
                "tool_call": {
                    "id": "tc_123",
                    "name": "analyze_data",
                    "arguments": json.dumps({"data": "test"})
                }
            }
            
            # Yield tool result (simulated)
            yield {
                "type": "tool_result",
                "tool_call_id": "tc_123",
                "tool_name": "analyze_data",
                "result": {"analysis": "complete"},
                "is_error": False
            }
            
            # Yield final text
            yield {"type": "text", "text": "Analysis complete!"}
        
        mock_brain.think.return_value.__aiter__.return_value = mock_stream()
        
        # Create XAgent with mocked components
        xagent = XAgent(
            xagent_id="test_xagent",
            project_id="test_project",
            goal="Test goal",
            plan={"steps": ["Test step"]},
            config={"model": "test-model"},
            brain=mock_brain
        )
        
        # Mock tool registry
        mock_tool_registry = Mock(spec=ToolRegistry)
        mock_tool = MockTool()
        mock_tool_registry.get_tool.return_value = mock_tool
        mock_tool_registry.get_all_tools.return_value = [mock_tool]
        
        # Capture SSE events
        captured_events = []
        
        async def capture_sse(event_type: str, data: Any):
            captured_events.append({"event": event_type, "data": data})
        
        # Mock the streaming response
        with patch.object(xagent, 'tool_registry', mock_tool_registry):
            with patch.object(xagent, '_execute_tool_calls', new_callable=AsyncMock) as mock_execute:
                # Mock tool execution to return proper result
                mock_execute.return_value = [
                    ToolResult(
                        tool_call_id="tc_123",
                        tool_name="analyze_data",
                        result={"analysis": "complete"},
                        is_error=False
                    )
                ]
                
                # Stream the response
                message = Message.user_message("Test input")
                result = await xagent._stream_full_response(message, capture_sse)
        
        # Verify SSE events were sent
        event_types = [e["event"] for e in captured_events]
        assert "message_start" in event_types
        assert "part_delta" in event_types
        assert "part_complete" in event_types
        assert "message_complete" in event_types
        
        # Verify message_start event
        message_start = next(e for e in captured_events if e["event"] == "message_start")
        assert message_start["data"]["role"] == "assistant"
        assert "message_id" in message_start["data"]
        
        # Verify part_complete events
        part_completes = [e for e in captured_events if e["event"] == "part_complete"]
        part_types = [e["data"]["part"]["type"] for e in part_completes]
        assert "text" in part_types
        assert "tool-call" in part_types
        assert "tool-result" in part_types
        
        # Verify message_complete event
        message_complete = next(e for e in captured_events if e["event"] == "message_complete")
        final_message = message_complete["data"]["message"]
        assert final_message["role"] == "assistant"
        assert len(final_message["parts"]) >= 3  # At least text, tool-call, tool-result
        assert final_message["content"] != ""  # Combined text content
    
    @pytest.mark.asyncio
    async def test_message_builder_part_ordering(self):
        """Test that StreamingMessageBuilder maintains correct part ordering."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Add various parts in a specific order
        builder.add_text_delta("Starting...\n")
        builder.finalize_text_part()
        
        part1_idx = builder.add_part(StepStartPart(stepId="step_1", stepName="Initialize"))
        assert part1_idx == 1
        
        builder.add_text_delta("Executing tool...\n")
        builder.finalize_text_part()
        
        part2_idx = builder.add_tool_call("tc_1", "calculator", {"expression": "2+2"})
        assert part2_idx == 3
        
        part3_idx = builder.add_tool_result("tc_1", "calculator", {"result": 4}, False)
        assert part3_idx == 4
        
        builder.add_text_delta("Result: 4")
        
        # Build message
        message = builder.build()
        
        # Verify parts order and content
        assert len(message.parts) == 5
        assert message.parts[0].type == "text"
        assert message.parts[0].text == "Starting...\n"
        assert message.parts[1].type == "step-start"
        assert message.parts[2].type == "text"
        assert message.parts[2].text == "Executing tool...\n"
        assert message.parts[3].type == "tool-call"
        assert message.parts[4].type == "tool-result"
        
        # Verify content is combined correctly
        assert message.content == "Starting...\nExecuting tool...\nResult: 4"
    
    @pytest.mark.asyncio
    async def test_error_handling_in_parts(self):
        """Test that errors are properly captured as ErrorPart."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Add normal flow
        builder.add_text_delta("Processing your request...\n")
        builder.finalize_text_part()
        
        # Add tool call that will fail
        tool_call_id = "tc_error_test"
        builder.add_tool_call(tool_call_id, "failing_tool", {"will": "fail"})
        
        # Add error result
        builder.add_tool_result(
            tool_call_id=tool_call_id,
            tool_name="failing_tool",
            result="Tool execution failed: Connection timeout",
            is_error=True
        )
        
        # Add error part
        builder.add_part(ErrorPart(
            error="Failed to complete the operation",
            errorCode="TOOL_EXECUTION_ERROR"
        ))
        
        # Add recovery text
        builder.add_text_delta("I encountered an error but will try an alternative approach.")
        
        message = builder.build()
        
        # Verify error handling
        assert len(message.parts) == 5
        
        # Check tool result part has error flag
        tool_result = next(p for p in message.parts if p.type == "tool-result")
        assert tool_result.isError == True
        
        # Check error part
        error_part = next(p for p in message.parts if p.type == "error")
        assert error_part.errorCode == "TOOL_EXECUTION_ERROR"
        assert "Failed to complete" in error_part.error
    
    @pytest.mark.asyncio
    async def test_multimodal_parts(self):
        """Test handling of image and file parts."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Add text
        builder.add_text_delta("Here's the image analysis:\n")
        builder.finalize_text_part()
        
        # Add image part
        builder.add_part(ImagePart(
            image="data:image/png;base64,iVBORw0KGgoAAAANS...",
            mimeType="image/png"
        ))
        
        # Add file part
        builder.add_part(FilePart(
            data="file content here",
            mimeType="text/plain"
        ))
        
        # Add analysis text
        builder.add_text_delta("The image shows a test pattern.")
        
        message = builder.build()
        
        # Verify multimodal parts
        assert len(message.parts) == 4
        
        image_part = next(p for p in message.parts if p.type == "image")
        assert image_part.mimeType == "image/png"
        
        file_part = next(p for p in message.parts if p.type == "file")
        assert file_part.mimeType == "text/plain"
    
    def test_message_part_serialization(self):
        """Test that all message parts serialize correctly to JSON."""
        # Create various parts
        parts = [
            TextPart(text="Hello world"),
            ToolCallPart(
                toolCallId="tc_123",
                toolName="search",
                args={"query": "test", "limit": 10}
            ),
            ToolResultPart(
                toolCallId="tc_123",
                toolName="search",
                result={"results": ["item1", "item2"]},
                isError=False
            ),
            ReasoningPart(content="Internal thought process"),
            ErrorPart(error="Something went wrong", errorCode="ERR_001"),
            ImagePart(image="base64data", mimeType="image/jpeg"),
            FilePart(data="filedata", mimeType="application/pdf"),
            StepStartPart(stepId="step_1", stepName="First Step")
        ]
        
        # Create message with all parts
        message = Message(
            role="assistant",
            content="Combined text content",
            parts=parts
        )
        
        # Serialize to JSON
        json_str = message.json()
        data = json.loads(json_str)
        
        # Verify structure
        assert data["role"] == "assistant"
        assert data["content"] == "Combined text content"
        assert len(data["parts"]) == 8
        
        # Verify each part type
        for i, part_data in enumerate(data["parts"]):
            assert "type" in part_data
            
            if part_data["type"] == "tool-call":
                assert "toolCallId" in part_data
                assert "toolName" in part_data
                assert "args" in part_data
            elif part_data["type"] == "tool-result":
                assert "toolCallId" in part_data
                assert "toolName" in part_data
                assert "result" in part_data
                assert "isError" in part_data
            elif part_data["type"] == "text":
                assert "text" in part_data
            elif part_data["type"] == "reasoning":
                assert "content" in part_data
            elif part_data["type"] == "error":
                assert "error" in part_data
                assert "errorCode" in part_data
        
        # Verify deserialization
        message2 = Message(**data)
        assert message2.role == message.role
        assert len(message2.parts) == len(message.parts)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
