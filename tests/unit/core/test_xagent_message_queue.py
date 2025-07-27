"""
Tests for XAgent message queue functionality.

This test suite verifies:
1. Message queuing and ordering
2. Execution interruption when new messages arrive
3. Response tracking with futures
4. Concurrent message handling
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

from vibex.core.xagent import XAgent, XAgentResponse
from vibex.core.config import TeamConfig, AgentConfig, BrainConfig
from vibex.core.message import Message, TextPart
from vibex.core.plan import Plan
from vibex.core.task import Task


@pytest.fixture
def mock_team_config():
    """Create a mock team configuration."""
    return TeamConfig(
        name="test_team",
        description="Test team configuration",
        agents=[
            AgentConfig(
                name="developer",
                description="Test developer agent",
                tools=["test_tool"],
                brain_config=BrainConfig(provider="test", model="test-model")
            )
        ]
    )


@pytest.fixture
def mock_project_path(tmp_path):
    """Create a temporary project path."""
    return tmp_path / "test_project"


def create_test_xagent_with_mocks(team_config, project_path):
    """Create XAgent with all necessary mocks."""
    with patch('vibex.storage.factory.ProjectStorageFactory') as mock_storage_factory, \
         patch('vibex.core.xagent.setup_task_file_logging'), \
         patch('vibex.tool.manager.ToolManager._register_builtin_tools'):
        
        # Mock project storage
        mock_project_storage = Mock()
        mock_project_storage.get_project_path.return_value = project_path
        mock_storage_factory.create_project_storage.return_value = mock_project_storage
        
        # Create XAgent
        x = XAgent(team_config=team_config, project_path=project_path)
        
        # Mock the project
        x.project = Mock()
        x.project.goal = "Test goal"
        x.project.name = "Test Project"
        x.project.plan = None
        x.project.load_state = AsyncMock()
        x.project._persist_state = AsyncMock()
        
        # Mock brain for responses
        x.brain = Mock()
        x.brain.stream_response = AsyncMock()
        
        # Mock helper methods
        x._build_context_messages = Mock(return_value=[])
        x._handle_new_task_request = AsyncMock(return_value=XAgentResponse(text="Creating plan..."))
        
        # Mock chat storage
        x.chat_storage = Mock()
        x.chat_storage.save_message = AsyncMock()
        
        return x


class TestMessageQueue:
    """Test message queue functionality."""
    
    @pytest.mark.asyncio
    async def test_message_queue_ordering(self, mock_team_config, mock_project_path):
        """Test that messages are processed in FIFO order."""
        # Arrange
        x = create_test_xagent_with_mocks(mock_team_config, mock_project_path)
        
        # Track processed messages
        processed_messages = []
        
        # Mock _process_message to track order
        async def mock_process_message(message):
            processed_messages.append(message.content)
            await asyncio.sleep(0.1)  # Simulate processing time
            return XAgentResponse(text=f"Processed: {message.content}")
        
        x._process_message = mock_process_message
        
        # Act - Queue multiple messages rapidly
        futures = []
        for i in range(3):
            msg = Message.user_message(f"Message {i}")
            future = asyncio.create_task(x.chat(msg))
            futures.append(future)
        
        # Wait for all to complete
        responses = await asyncio.gather(*futures)
        
        # Assert - Messages were processed in order
        assert processed_messages == ["Message 0", "Message 1", "Message 2"]
        
        # Clean up
        await x.cleanup()
    
    @pytest.mark.asyncio
    async def test_execution_interruption(self, mock_team_config, mock_project_path):
        """Test that new messages interrupt ongoing execution."""
        # Arrange
        x = create_test_xagent_with_mocks(mock_team_config, mock_project_path)
        
        # Create a plan with tasks
        x.plan = Plan(
            goal="Test plan",
            tasks=[
                Task(id="task1", action="Task 1", assigned_to="developer", status="pending"),
                Task(id="task2", action="Task 2", assigned_to="developer", status="pending"),
                Task(id="task3", action="Task 3", assigned_to="developer", status="pending"),
            ]
        )
        
        # Track execution steps
        execution_steps = []
        
        # Mock step to track execution and add delay
        async def mock_step():
            task = x.plan.get_next_actionable_task()
            if task:
                execution_steps.append(task.action)
                task.status = "completed"
                await asyncio.sleep(0.2)  # Simulate task execution time
                
                # Check for interruption
                if x._execution_interrupted or not x._message_queue.empty():
                    return "⏸️ Execution paused - new message received"
                    
                return f"Completed: {task.action}"
            return "No more tasks"
        
        x.step = mock_step
        
        # Mock brain response for empty message
        x.brain.stream_response.return_value = AsyncMock()
        x.brain.stream_response.return_value.__aiter__.return_value = iter([
            {"type": "text-delta", "content": "Starting execution..."}
        ])
        
        # Act
        # Send empty message to trigger execution
        empty_msg_future = asyncio.create_task(x.chat(""))
        
        # Wait a bit for execution to start
        await asyncio.sleep(0.3)
        
        # Send interrupting message
        interrupt_future = asyncio.create_task(x.chat("Stop and do something else"))
        
        # Wait for both to complete
        responses = await asyncio.gather(empty_msg_future, interrupt_future, return_exceptions=True)
        
        # Assert
        # Execution should have been interrupted
        assert len(execution_steps) < 3  # Not all tasks completed
        assert any("paused" in str(r) for r in responses if not isinstance(r, Exception))
        
        # Clean up
        await x.cleanup()
    
    @pytest.mark.asyncio
    async def test_response_tracking(self, mock_team_config, mock_project_path):
        """Test that responses are correctly tracked and returned."""
        # Arrange
        x = create_test_xagent_with_mocks(mock_team_config, mock_project_path)
        
        # Mock _process_message with different responses
        async def mock_process_message(message):
            await asyncio.sleep(0.1)  # Simulate processing
            return XAgentResponse(
                text=f"Response to: {message.content}",
                metadata={"message_id": message.id}
            )
        
        x._process_message = mock_process_message
        
        # Act - Send multiple messages concurrently
        msg1 = Message.user_message("First message")
        msg2 = Message.user_message("Second message")
        msg3 = Message.user_message("Third message")
        
        # Queue messages concurrently
        future1 = asyncio.create_task(x.chat(msg1))
        future2 = asyncio.create_task(x.chat(msg2))
        future3 = asyncio.create_task(x.chat(msg3))
        
        # Wait for all responses
        response1, response2, response3 = await asyncio.gather(future1, future2, future3)
        
        # Assert - Each message got its correct response
        assert response1.text == "Response to: First message"
        assert response2.text == "Response to: Second message"
        assert response3.text == "Response to: Third message"
        
        # Clean up
        await x.cleanup()
    
    @pytest.mark.asyncio
    async def test_message_timeout(self, mock_team_config, mock_project_path):
        """Test that messages timeout if not processed."""
        # Arrange
        x = create_test_xagent_with_mocks(mock_team_config, mock_project_path)
        
        # Mock _process_message to hang
        async def mock_process_message(message):
            await asyncio.sleep(10)  # Longer than timeout
            return XAgentResponse(text="Should not reach here")
        
        x._process_message = mock_process_message
        
        # Reduce timeout for faster test
        with patch('vibex.core.xagent.asyncio.wait_for', 
                  side_effect=lambda coro, timeout: asyncio.wait_for(coro, timeout=0.5)):
            
            # Act
            response = await x.chat("Test timeout")
            
            # Assert
            assert "timeout" in response.metadata.get("error", "")
            assert "timed out" in response.text.lower()
        
        # Clean up
        await x.cleanup()
    
    @pytest.mark.asyncio
    async def test_empty_message_execution(self, mock_team_config, mock_project_path):
        """Test that empty messages trigger plan execution."""
        # Arrange
        x = create_test_xagent_with_mocks(mock_team_config, mock_project_path)
        
        # Create a plan
        x.plan = Plan(
            goal="Test plan",
            tasks=[
                Task(id="task1", action="Build feature", assigned_to="developer", status="pending"),
            ]
        )
        
        # Mock step execution
        x.step = AsyncMock(return_value="Completed: Build feature")
        
        # Mock brain response
        x.brain.stream_response.return_value = AsyncMock()
        x.brain.stream_response.return_value.__aiter__.return_value = iter([
            {"type": "text-delta", "content": "Executing plan..."}
        ])
        
        # Act - Send empty message
        response = await x.chat("")
        
        # Assert
        # Wait for message to be processed
        await asyncio.sleep(0.5)
        
        # Step should have been called
        assert x.step.called
        
        # Clean up
        await x.cleanup()
    
    @pytest.mark.asyncio
    async def test_non_empty_message_adjustment(self, mock_team_config, mock_project_path):
        """Test that non-empty messages can adjust the plan before execution."""
        # Arrange
        x = create_test_xagent_with_mocks(mock_team_config, mock_project_path)
        
        # Create a plan
        x.plan = Plan(
            goal="Build a web app",
            tasks=[
                Task(id="task1", action="Create backend", assigned_to="developer", status="pending"),
                Task(id="task2", action="Create frontend", assigned_to="developer", status="pending"),
            ]
        )
        
        # Mock brain to respond about plan adjustment
        x.brain.stream_response.return_value = AsyncMock()
        x.brain.stream_response.return_value.__aiter__.return_value = iter([
            {"type": "text-delta", "content": "I'll add authentication to the plan and continue."}
        ])
        
        # Mock step execution
        execution_count = 0
        async def mock_step():
            nonlocal execution_count
            execution_count += 1
            return f"Step {execution_count} completed"
        
        x.step = mock_step
        
        # Act - Send message requesting change
        response = await x.chat("Add user authentication first")
        
        # Assert
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Should have acknowledged the change
        assert "authentication" in response.text.lower()
        
        # Should have executed steps
        assert execution_count > 0
        
        # Clean up
        await x.cleanup()
    
    @pytest.mark.asyncio
    async def test_consumer_loop_error_handling(self, mock_team_config, mock_project_path):
        """Test that consumer loop handles errors gracefully."""
        # Arrange
        x = create_test_xagent_with_mocks(mock_team_config, mock_project_path)
        
        # Mock _process_message to raise error
        async def mock_process_message(message):
            if "error" in message.content:
                raise ValueError("Test error")
            return XAgentResponse(text="Success")
        
        x._process_message = mock_process_message
        
        # Act
        # Send error-causing message
        error_response = await x.chat("Please error")
        
        # Send normal message after error
        normal_response = await x.chat("Normal message")
        
        # Assert
        # Error message should get error response
        assert "error" in error_response.metadata
        assert "Test error" in error_response.text
        
        # Normal message should still work
        assert normal_response.text == "Success"
        
        # Consumer should still be running
        assert x._consumer_task and not x._consumer_task.done()
        
        # Clean up
        await x.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_message_processing(self, mock_team_config, mock_project_path):
        """Test handling of many concurrent messages."""
        # Arrange
        x = create_test_xagent_with_mocks(mock_team_config, mock_project_path)
        
        # Track processing
        processed_count = 0
        processing_lock = asyncio.Lock()
        
        async def mock_process_message(message):
            nonlocal processed_count
            async with processing_lock:
                processed_count += 1
            await asyncio.sleep(0.05)  # Simulate work
            return XAgentResponse(text=f"Processed: {message.content}")
        
        x._process_message = mock_process_message
        
        # Act - Send many messages concurrently
        futures = []
        message_count = 20
        for i in range(message_count):
            future = asyncio.create_task(x.chat(f"Message {i}"))
            futures.append(future)
        
        # Wait for all
        responses = await asyncio.gather(*futures)
        
        # Assert
        # All messages should be processed
        assert processed_count == message_count
        assert len(responses) == message_count
        assert all(r.text.startswith("Processed:") for r in responses)
        
        # Clean up
        await x.cleanup()


class TestMessageQueueIntegration:
    """Integration tests for message queue with real components."""
    
    @pytest.mark.asyncio
    async def test_chat_mode_vs_agent_mode(self, mock_team_config, mock_project_path):
        """Test different behavior in chat vs agent mode."""
        # Arrange
        x = create_test_xagent_with_mocks(mock_team_config, mock_project_path)
        
        # Track which mode was used
        modes_used = []
        
        async def mock_process_message(message):
            mode = x._message_modes.get(message.id, "agent")
            modes_used.append(mode)
            return XAgentResponse(text=f"Mode: {mode}")
        
        x._process_message = mock_process_message
        
        # Act
        # Send in agent mode (default)
        agent_response = await x.chat("Do something", mode="agent")
        
        # Send in chat mode
        chat_response = await x.chat("Just chat", mode="chat")
        
        # Assert
        assert modes_used == ["agent", "chat"]
        assert agent_response.text == "Mode: agent"
        assert chat_response.text == "Mode: chat"
        
        # Clean up
        await x.cleanup()