import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
from agentx.core.task import TaskExecutor
from agentx.core.config import TeamConfig, AgentConfig, BrainConfig, OrchestrationConfig, TaskConfig as CoreTaskConfig
from agentx.core.message import Message


@pytest.fixture
def mock_team_config():
    """Provides a mock TeamConfig for testing."""
    return TeamConfig(
        name="test_team",
        agents=[
            AgentConfig(name="test_agent", brain=BrainConfig(model="test_model"))
        ],
        orchestration=OrchestrationConfig(),
        task=CoreTaskConfig(),
    )


@patch('agentx.core.task.Orchestrator')
@patch('agentx.core.task.Workspace')
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
async def test_start_task_invokes_orchestrator(mock_set_streaming, mock_setup_logging, mock_orchestrator, mock_team_config):
    """
    Tests that calling start() on the executor correctly initiates the
    orchestrator's run method and streams back messages.
    """
    # Arrange
    async def mock_orchestrator_run(*args, **kwargs):
        yield Message.system_message(content="Orchestrator run started")
        yield Message.system_message(content="Orchestrator run finished")

    mock_orchestrator.return_value.run = AsyncMock(side_effect=mock_orchestrator_run)
    
    executor = TaskExecutor(team_config=mock_team_config)
    
    # Act
    prompt = "This is a test prompt"
    messages = [msg async for msg in executor.start(prompt=prompt, stream=True)]

    # Assert
    mock_setup_logging.assert_called_once()
    mock_set_streaming.assert_called_once_with(True)
    
    assert executor.task is not None
    assert executor.task.initial_prompt == prompt
    
    mock_orchestrator.return_value.run.assert_called_once()
    
    assert len(messages) == 2
    assert messages[0].content == "Orchestrator run started"
    assert messages[1].content == "Orchestrator run finished"
    assert executor.task.is_complete is True 