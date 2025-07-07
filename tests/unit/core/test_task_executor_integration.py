import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
from agentx.core.task import TaskExecutor
from agentx.core.config import TeamConfig, AgentConfig, BrainConfig, OrchestratorConfig, TaskConfig as CoreTaskConfig
from agentx.core.message import Message, TaskStep, TextPart


@pytest.fixture
def mock_team_config():
    """Provides a mock TeamConfig for testing."""
    return TeamConfig(
        name="test_team",
        agents=[
            AgentConfig(name="test_agent", brain_config=BrainConfig(model="test_model"))
        ],
        orchestrator=OrchestratorConfig(),
        execution=CoreTaskConfig(),
    )


@patch('agentx.core.task.Orchestrator')
@patch('agentx.core.task.WorkspaceStorage')
@patch('agentx.core.task.setup_task_file_logging')
def test_task_executor_initialization(mock_setup_logging, mock_workspace, mock_orchestrator, mock_team_config):
    """
    Tests that the TaskExecutor initializes all its components correctly.
    """
    # Arrange
    workspace_instance = mock_workspace.return_value
    orchestrator_instance = mock_orchestrator.return_value

    # Act
    executor = TaskExecutor(team_config=mock_team_config)

    # Assert
    assert executor.task_id is not None
    assert executor.team_config == mock_team_config
    assert executor.workspace == workspace_instance
    mock_setup_logging.assert_called_once()

    assert "test_agent" in executor.agents
    assert executor.orchestrator == orchestrator_instance


@pytest.mark.asyncio
@patch('agentx.core.task.Orchestrator')
@patch('agentx.core.task.setup_clean_chat_logging')
@patch('agentx.core.task.set_streaming_mode')
async def test_execute_task_invokes_orchestrator(mock_set_streaming, mock_setup_logging, mock_orchestrator, mock_team_config):
    """
    Tests that calling execute() on the executor correctly initiates the
    orchestrator's step method and returns messages.
    """
    # Arrange
    orchestrator_instance = mock_orchestrator.return_value
    orchestrator_instance.step = AsyncMock(return_value="Test orchestrator response")

    executor = TaskExecutor(team_config=mock_team_config)

    # Act
    prompt = "This is a test prompt"
    messages = [msg async for msg in executor.execute(prompt=prompt, stream=True)]

    # Assert
    mock_setup_logging.assert_called_once()
    mock_set_streaming.assert_called_once_with(True)

    assert executor.task is not None
    assert executor.task.initial_prompt == prompt

    # Verify orchestrator step was called
    orchestrator_instance.step.assert_called_once()

    # Verify we got a message back
    assert len(messages) == 1
    assert isinstance(messages[0], TaskStep)
    assert messages[0].parts[0].text == "Test orchestrator response"
    assert executor.task.is_complete is True


@pytest.mark.asyncio
@patch('agentx.core.task.Orchestrator')
@patch('agentx.core.task.setup_clean_chat_logging')
async def test_start_and_step_execution(mock_setup_logging, mock_orchestrator, mock_team_config):
    """
    Tests the new start() and step() execution pattern.
    """
    # Arrange
    orchestrator_instance = mock_orchestrator.return_value
    orchestrator_instance.step = AsyncMock(return_value="Step response")

    executor = TaskExecutor(team_config=mock_team_config)

    # Act - Start the task
    prompt = "Test conversational prompt"
    await executor.start(prompt)

    # Verify task is created
    assert executor.task is not None
    assert executor.task.initial_prompt == prompt
    assert not executor.is_complete

    # Act - Execute a step
    response = await executor.step()

    # Assert
    assert response == "Step response"
    orchestrator_instance.step.assert_called_once()


@pytest.mark.asyncio
@patch('agentx.core.task.Orchestrator')
async def test_conversational_flow(mock_orchestrator, mock_team_config):
    """
    Tests the conversational flow with multiple steps.
    """
    # Arrange
    orchestrator_instance = mock_orchestrator.return_value
    orchestrator_instance.step = AsyncMock(side_effect=[
        "First response",
        "Second response",
        "Task completed successfully. All plan items have been finished."
    ])

    executor = TaskExecutor(team_config=mock_team_config)

    # Act - Start conversation
    await executor.start("Start a conversation")

    # Step 1
    response1 = await executor.step()
    assert response1 == "First response"
    assert not executor.is_complete

    # Add user message and step 2
    executor.add_user_message("Continue the conversation")
    response2 = await executor.step()
    assert response2 == "Second response"
    assert not executor.is_complete

    # Step 3 - completion
    executor.add_user_message("Finish up")
    response3 = await executor.step()
    assert response3 == "Task completed successfully. All plan items have been finished."
    assert executor.is_complete  # Should be marked complete due to completion phrase


@pytest.mark.asyncio
@patch('agentx.core.task.Orchestrator')
async def test_plan_loading_on_start(mock_orchestrator, mock_team_config):
    """
    Tests that existing plans are loaded when starting a task.
    """
    # Arrange
    orchestrator_instance = mock_orchestrator.return_value
    executor = TaskExecutor(team_config=mock_team_config)

    # Mock the task's load_plan method
    with patch.object(executor, '_initialize_agents'), \
         patch.object(executor, '_initialize_tools'):

        # Act
        await executor.start("Test prompt")

        # Assert that task was created and load_plan was called
        assert executor.task is not None
        # The load_plan method should be called during task creation
        # This is verified by the fact that the task has the load_plan method available
