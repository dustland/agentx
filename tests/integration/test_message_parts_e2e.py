"""End-to-end integration test demonstrating message parts in action."""
import pytest
import json
from typing import List, Dict, Any

from vibex.core.message import Message, TextPart, ToolCallPart, ToolResultPart
from vibex.core.message_builder import StreamingMessageBuilder


def simulate_sse_streaming(builder: StreamingMessageBuilder) -> List[Dict[str, Any]]:
    """
    Simulate SSE streaming events for a message being built.
    
    Returns list of events that would be sent over SSE.
    """
    events = []
    
    # Message start event
    events.append({
        "event": "message_start",
        "data": {
            "message_id": builder.message_id,
            "role": builder.role
        }
    })
    
    # Simulate text streaming
    text_chunks = [
        "I'll help you analyze",
        " the weather data",
        " for Tokyo.\n"
    ]
    
    for i, chunk in enumerate(text_chunks):
        builder.add_text_delta(chunk)
        events.append({
            "event": "part_delta",
            "data": {
                "message_id": builder.message_id,
                "part_index": 0,
                "type": "text",
                "delta": chunk
            }
        })
    
    # Finalize text and emit part_complete
    builder.finalize_text_part()
    events.append({
        "event": "part_complete",
        "data": {
            "message_id": builder.message_id,
            "part_index": 0,
            "part": builder.parts[0].model_dump()
        }
    })
    
    # Add tool call
    tool_call_id = "tc_weather_tokyo_123"
    part_idx = builder.add_tool_call(
        tool_call_id=tool_call_id,
        tool_name="get_weather",
        args={"location": "Tokyo", "units": "celsius"}
    )
    
    events.append({
        "event": "part_complete",
        "data": {
            "message_id": builder.message_id,
            "part_index": part_idx,
            "part": builder.parts[part_idx].model_dump()
        }
    })
    
    # Simulate tool execution and result
    part_idx = builder.add_tool_result(
        tool_call_id=tool_call_id,
        tool_name="get_weather",
        result={
            "location": "Tokyo",
            "temperature": 22,
            "condition": "Partly cloudy",
            "humidity": 65,
            "wind_speed": 12
        },
        is_error=False
    )
    
    events.append({
        "event": "part_complete",
        "data": {
            "message_id": builder.message_id,
            "part_index": part_idx,
            "part": builder.parts[part_idx].model_dump()
        }
    })
    
    # Stream final response text
    final_chunks = [
        "\nBased on the current data:\n",
        "- Temperature: 22°C\n",
        "- Conditions: Partly cloudy\n",
        "- Humidity: 65%\n",
        "- Wind: 12 km/h\n\n",
        "It's a pleasant day in Tokyo!"
    ]
    
    for chunk in final_chunks:
        builder.add_text_delta(chunk)
        events.append({
            "event": "part_delta",
            "data": {
                "message_id": builder.message_id,
                "part_index": 3,  # Fourth part (0-indexed)
                "type": "text",
                "delta": chunk
            }
        })
    
    # Build final message
    message = builder.build()
    
    # Message complete event
    events.append({
        "event": "message_complete",
        "data": {
            "message": message.model_dump()
        }
    })
    
    return events, message


class TestMessagePartsE2E:
    """End-to-end tests for message parts system."""
    
    def test_weather_assistant_flow(self):
        """Test a complete weather assistant interaction with tool use."""
        # Initialize builder
        builder = StreamingMessageBuilder(
            message_id="msg_weather_test",
            role="assistant"
        )
        
        # Simulate streaming
        events, message = simulate_sse_streaming(builder)
        
        # Verify events were generated
        assert len(events) > 10  # Should have many events
        
        # Check event types
        event_types = [e["event"] for e in events]
        assert "message_start" in event_types
        assert event_types.count("part_delta") >= 8  # Text chunks
        assert event_types.count("part_complete") == 3  # 3 complete parts
        assert "message_complete" in event_types
        
        # Verify final message structure
        assert message.role == "assistant"
        assert len(message.parts) == 4
        
        # Check part types and content
        assert message.parts[0].type == "text"
        assert "analyze the weather data" in message.parts[0].text
        
        assert message.parts[1].type == "tool-call"
        assert message.parts[1].toolName == "get_weather"
        assert message.parts[1].args["location"] == "Tokyo"
        
        assert message.parts[2].type == "tool-result"
        assert message.parts[2].result["temperature"] == 22
        assert not message.parts[2].isError
        
        assert message.parts[3].type == "text"
        assert "22°C" in message.parts[3].text
        assert "pleasant day" in message.parts[3].text
        
        # Verify combined content (for backward compatibility)
        assert "analyze the weather data" in message.content
        assert "Tool get_weather completed." in message.content
        assert "22°C" in message.content
    
    def test_frontend_consumption(self):
        """Test that message parts can be consumed by frontend."""
        # Create a message with various parts
        builder = StreamingMessageBuilder(role="assistant")
        
        # Add different part types
        builder.add_text_delta("Processing your request...\n")
        builder.finalize_text_part()
        
        builder.add_tool_call("tc_1", "search", {"query": "Python tutorials"})
        builder.add_tool_result("tc_1", "search", {"results": ["Tutorial 1", "Tutorial 2"]}, False)
        
        builder.add_text_delta("Found 2 tutorials for you.")
        
        message = builder.build()
        
        # Serialize for frontend
        json_data = message.model_dump()
        
        # Verify structure matches frontend expectations
        assert "id" in json_data
        assert "role" in json_data
        assert "content" in json_data
        assert "parts" in json_data
        
        # Check parts are properly serialized with camelCase
        for part in json_data["parts"]:
            assert "type" in part
            
            if part["type"] == "tool-call":
                assert "toolCallId" in part
                assert "toolName" in part
                assert "args" in part
            elif part["type"] == "tool-result":
                assert "toolCallId" in part
                assert "toolName" in part
                assert "result" in part
                assert "isError" in part
            elif part["type"] == "text":
                assert "text" in part
    
    def test_error_recovery_flow(self):
        """Test message flow with error handling."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Initial attempt
        builder.add_text_delta("Let me fetch that information...\n")
        builder.finalize_text_part()
        
        # Tool call that fails
        builder.add_tool_call("tc_fail", "database_query", {"query": "SELECT * FROM users"})
        
        # Error result
        builder.add_tool_result(
            "tc_fail",
            "database_query",
            "Connection timeout: Unable to connect to database",
            is_error=True
        )
        
        # Recovery
        builder.add_text_delta("\nI encountered a database error. Let me try an alternative approach...\n")
        builder.finalize_text_part()
        
        # Alternative tool
        builder.add_tool_call("tc_cache", "cache_lookup", {"key": "users_list"})
        builder.add_tool_result(
            "tc_cache",
            "cache_lookup",
            {"users": ["Alice", "Bob", "Charlie"]},
            is_error=False
        )
        
        # Final response
        builder.add_text_delta("\nI found 3 users in the cache: Alice, Bob, and Charlie.")
        
        message = builder.build()
        
        # Verify error handling
        assert len(message.parts) == 7  # 3 text parts, 2 tool calls, 2 tool results
        
        # Check error tool result
        error_result = message.parts[2]
        assert error_result.type == "tool-result"
        assert error_result.isError == True
        assert "Connection timeout" in str(error_result.result)
        
        # Check recovery worked
        success_result = message.parts[5]
        assert success_result.type == "tool-result"
        assert success_result.isError == False
        assert len(success_result.result["users"]) == 3
        
        # Check final text
        final_text = message.parts[6]
        assert final_text.type == "text"
        assert "3 users" in final_text.text
        
        # Verify readable content
        assert "database error" in message.content
        assert "Tool cache_lookup completed." in message.content
        assert "3 users" in message.content
    
    def test_streaming_state_management(self):
        """Test that streaming state is properly managed."""
        builder = StreamingMessageBuilder(role="assistant")
        
        # Check initial state
        state = builder.get_current_state()
        assert state["parts_count"] == 0
        assert state["current_text_length"] == 0
        
        # Add some text
        builder.add_text_delta("Hello ")
        state = builder.get_current_state()
        assert state["current_text_length"] == 6
        
        # Add tool call
        builder.add_tool_call("tc_1", "test_tool", {})
        state = builder.get_current_state()
        assert state["parts_count"] == 2  # Text was auto-finalized + tool call
        assert state["current_text_length"] == 0  # Text was finalized
        assert "tc_1" in state["pending_tool_calls"]
        
        # Add tool result
        builder.add_tool_result("tc_1", "test_tool", {"result": "ok"}, False)
        state = builder.get_current_state()
        assert "tc_1" not in state["pending_tool_calls"]  # Resolved


if __name__ == "__main__":
    pytest.main([__file__, "-v"])