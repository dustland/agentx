"""
Tests for XAgent - the unified conversational interface.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from vibex.core.plan import Plan
from vibex.core.task import Task
from vibex.core.task import Task
from vibex.core.xagent import XAgent, XAgentResponse
from vibex.core.config import TeamConfig, AgentConfig, BrainConfig
from vibex.core.message import Message, TextPart


@pytest.fixture
def mock_team_config():
    """Create a mock team configuration."""
    return TeamConfig(
        name="test_team",
        description="Test team configuration",
        agents=[
            AgentConfig(
                name="test_agent",
                description="Test agent for unit tests",
                tools=["test_tool"],
                brain_config=BrainConfig(provider="test", model="test-model")
            )
        ]
    )


@pytest.fixture
def mock_project_storage_path(tmp_path):
    """Create a temporary project storage path."""
    return tmp_path / "test_project"


def create_test_xagent(team_config, project_path):
    """Helper to create XAgent with mocked project."""
    x = XAgent(team_config=team_config, project_path=project_path)
    
    # Mock the project attribute that would normally be set by start_project
    from unittest.mock import Mock, AsyncMock
    x.project = Mock()
    x.project.goal = "Test goal"
    x.project.name = "Test Project"
    x.project.plan = None
    
    # Mock async methods
    x.project.load_state = AsyncMock()
    x.project._persist_state = AsyncMock()
    
    # XAgent also has its own name property
    x._name = "X"
    
    return x


class TestXAgent:
    """Test XAgent functionality."""

    @patch('vibex.storage.factory.ProjectStorageFactory')
    @patch('vibex.core.xagent.setup_task_file_logging')
    @patch('vibex.tool.manager.ToolManager._register_builtin_tools')
    def test_xagent_initialization(self, mock_register_tools, mock_setup_logging, mock_project_storage_factory, mock_team_config, mock_project_storage_path):
        """Test XAgent initializes correctly."""
        # Arrange
        mock_project_storage = Mock()
        mock_project_storage.get_project_path.return_value = mock_project_storage_path
        mock_project_storage_factory.create_project_storage.return_value = mock_project_storage

        # Act
        x = create_test_xagent(mock_team_config, mock_project_storage_path)

        # Assert
        assert x.project_id is not None
        assert x.team_config == mock_team_config
        assert x.project_storage is not None
        assert x.project_storage.get_project_path() == mock_project_storage_path
        assert "test_agent" in x.specialist_agents
        assert x.name == "Test Project"  # Name comes from project when project exists
        assert not x.is_complete()
        mock_setup_logging.assert_called_once()
        mock_register_tools.assert_called_once()

    @patch('vibex.storage.factory.ProjectStorageFactory')
    @patch('vibex.core.xagent.setup_task_file_logging')
    @patch('vibex.tool.manager.ToolManager._register_builtin_tools')
    @pytest.mark.asyncio
    async def test_chat_with_simple_text(self, mock_register_tools, mock_setup_logging, mock_project_storage_factory, mock_team_config, mock_project_storage_path):
        """Test chat with simple text message creates plan but doesn't execute automatically."""
        # Arrange
        mock_project_storage = Mock()
        mock_project_storage.get_project_path.return_value = mock_project_storage_path
        mock_project_storage_factory.create_project_storage.return_value = mock_project_storage

        x = create_test_xagent(mock_team_config, mock_project_storage_path)

        # Mock the brain's response
        with patch.object(x.brain, 'generate_response') as mock_generate:
            mock_generate.return_value = Mock(content='{"requires_plan_adjustment": false, "is_informational": false, "is_new_task": true}')

            # Mock plan generation with AsyncMock
            with patch.object(x, '_generate_plan', new_callable=AsyncMock) as mock_plan_gen:
                mock_plan = Plan(
                    tasks=[
                        Task(
                            id="task_1",
                            action="Test task",
                            agent="test_agent",
                            dependencies=[],
                            status="pending"
                        )
                    ]
                )
                mock_plan_gen.return_value = mock_plan
                
                # Mock _persist_plan to avoid attribute errors
                with patch.object(x, '_persist_plan', new_callable=AsyncMock) as mock_persist:
                    # Act
                    response = await x.chat("Hello, create a test report")

                    # Assert
                    assert isinstance(response, XAgentResponse)
                    # Verify that plan was created but not executed
                    assert "I've created a plan for your task" in response.text
                    assert "Use step() to execute the plan autonomously" in response.text
                    assert len(x.conversation_history) == 2  # User message + assistant response
                    assert x.conversation_history[0].content == "Hello, create a test report"
                    assert x.conversation_history[1].role == "assistant"
                    # Verify plan was set
                    assert x.plan is not None

    @patch('vibex.storage.factory.ProjectStorageFactory')
    @patch('vibex.core.xagent.setup_task_file_logging')
    @patch('vibex.tool.manager.ToolManager._register_builtin_tools')
    @pytest.mark.asyncio
    async def test_chat_with_message_object(self, mock_register_tools, mock_setup_logging, mock_project_storage_factory, mock_team_config, mock_project_storage_path):
        """Test chat with Message object."""
        # Arrange
        mock_project_storage = Mock()
        mock_project_storage.get_project_path.return_value = mock_project_storage_path
        mock_project_storage_factory.create_project_storage.return_value = mock_project_storage

        x = create_test_xagent(mock_team_config, mock_project_storage_path)

        message = Message.user_message("Test with message object")

        # Mock the brain's response for informational query
        with patch.object(x.brain, 'generate_response') as mock_generate:
            mock_generate.side_effect = [
                Mock(content='{"requires_plan_adjustment": false, "is_informational": true, "is_new_task": false}'),
                Mock(content="This is an informational response about the current task status.")
            ]

            # Act
            response = await x.chat(message)

            # Assert
            assert isinstance(response, XAgentResponse)
            assert isinstance(response, XAgentResponse)
            assert response.text  # Just check we got a response
            assert response.metadata.get("query_type") == "informational"

    @patch('vibex.storage.factory.ProjectStorageFactory')
    @patch('vibex.core.xagent.setup_task_file_logging')
    @patch('vibex.tool.manager.ToolManager._register_builtin_tools')
    @pytest.mark.asyncio
    async def test_plan_adjustment_preserves_work(self, mock_register_tools, mock_setup_logging, mock_project_storage_factory, mock_team_config, mock_project_storage_path):
        """Test that plan adjustment preserves completed work."""
        # Arrange
        mock_project_storage = Mock()
        mock_project_storage.get_project_path.return_value = mock_project_storage_path
        mock_project_storage_factory.create_project_storage.return_value = mock_project_storage

        x = create_test_xagent(mock_team_config, mock_project_storage_path)

        # Set up existing plan with completed tasks
        x.plan = Plan(
            tasks=[
                Task(
                    id="task_1",
                    action="Research and gather information",
                    agent="test_agent",
                    dependencies=[],
                    status="completed"
                ),
                Task(
                    id="task_2",
                    action="Write report based on research",
                    agent="test_agent",
                    dependencies=["task_1"],
                    status="completed"
                )
            ]
        )

        # Mock brain response for plan adjustment
        with patch.object(x.brain, 'generate_response') as mock_generate:
            mock_generate.return_value = Mock(content='''{
                "requires_plan_adjustment": true,
                "is_informational": false,
                "affected_tasks": ["task_2"],
                "preserved_tasks": ["task_1"],
                "adjustment_type": "regenerate",
                "reasoning": "User wants to change report style"
            }''')

            # Mock plan execution
            with patch.object(x, '_execute_plan_steps') as mock_execute:
                mock_execute.return_value = "Report regenerated with new style"

                # Act
                response = await x.chat("Regenerate the report with more visual appeal")

                # Assert
                assert isinstance(response, XAgentResponse)
                assert len(response.preserved_steps) == 1
                assert "task_1" in response.preserved_steps
                assert len(response.regenerated_steps) == 1
                assert "task_2" in response.regenerated_steps
                assert response.plan_changes.get("adjustment_type") == "regenerate"

    @patch('vibex.storage.factory.ProjectStorageFactory')
    @patch('vibex.core.xagent.setup_task_file_logging')
    @patch('vibex.tool.manager.ToolManager._register_builtin_tools')
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_register_tools, mock_setup_logging, mock_project_storage_factory, mock_team_config, mock_project_storage_path):
        """Test error handling in chat method."""
        # Arrange
        mock_project_storage = Mock()
        mock_project_storage.get_project_path.return_value = mock_project_storage_path
        mock_project_storage_factory.create_project_storage.return_value = mock_project_storage

        x = create_test_xagent(mock_team_config, mock_project_storage_path)

        # Mock brain to raise an exception
        with patch.object(x.brain, 'generate_response') as mock_generate:
            mock_generate.side_effect = Exception("Test error")

            # Act
            response = await x.chat("This should cause an error")

            # Assert
            assert isinstance(response, XAgentResponse)
            assert "error processing your message" in response.text.lower()
            assert "Test error" in response.metadata.get("error", "")

    @patch('vibex.storage.factory.ProjectStorageFactory')
    @patch('vibex.core.xagent.setup_task_file_logging')
    @patch('vibex.tool.manager.ToolManager._register_builtin_tools')
    def test_plan_summary_generation(self, mock_register_tools, mock_setup_logging, mock_project_storage_factory, mock_team_config, mock_project_storage_path):
        """Test plan summary generation."""
        # Arrange
        mock_project_storage = Mock()
        mock_project_storage.get_project_path.return_value = mock_project_storage_path
        mock_project_storage_factory.create_project_storage.return_value = mock_project_storage

        x = create_test_xagent(mock_team_config, mock_project_storage_path)

        # Set up plan with mixed statuses
        x.plan = Plan(
            tasks=[
                Task(id="task_1", action="Perform task 1", agent="test_agent", status="completed"),
                Task(id="task_2", action="Perform task 2", agent="test_agent", status="in_progress"),
                Task(id="task_3", action="Perform task 3", agent="test_agent", status="pending")
            ]
        )

        # Act
        summary = x._get_plan_summary()

        # Assert
        assert "Plan: Test goal" in summary
        assert "1/3 completed" in summary

    @patch('vibex.storage.factory.ProjectStorageFactory')
    @patch('vibex.core.xagent.setup_task_file_logging')
    @patch('vibex.tool.manager.ToolManager._register_builtin_tools')
    def test_conversation_summary_generation(self, mock_register_tools, mock_setup_logging, mock_project_storage_factory, mock_team_config, mock_project_storage_path):
        """Test conversation summary generation."""
        # Arrange
        mock_project_storage = Mock()
        mock_project_storage.get_project_path.return_value = mock_project_storage_path
        mock_project_storage_factory.create_project_storage.return_value = mock_project_storage

        x = create_test_xagent(mock_team_config, mock_project_storage_path)

        # Add some conversation history
        x.conversation_history = [
            Message.user_message("Hello"),
            Message.assistant_message("Hi there!"),
            Message.user_message("Can you help me?"),
            Message.assistant_message("Of course!")
        ]

        # Act
        summary = x._get_conversation_summary()

        # Assert
        assert "assistant:" in summary.lower()
        assert "user:" in summary.lower()
        assert "hi there!" in summary.lower()

    @patch('vibex.storage.factory.ProjectStorageFactory')
    @patch('vibex.core.xagent.setup_task_file_logging')
    @patch('vibex.tool.manager.ToolManager._register_builtin_tools')
    @pytest.mark.asyncio
    async def test_compatibility_methods(self, mock_register_tools, mock_setup_logging, mock_project_storage_factory, mock_team_config, mock_project_storage_path):
        """Test XAgent methods."""
        # Arrange
        mock_project_storage = Mock()
        mock_project_storage.get_project_path.return_value = mock_project_storage_path
        mock_project_storage_factory.create_project_storage.return_value = mock_project_storage

        x = create_test_xagent(mock_team_config, mock_project_storage_path)

        # Test is_complete property
        assert not x.is_complete()

        # Test project_storage access
        project_path = x.project_storage.get_project_path()
        assert project_path == mock_project_storage_path

        # Test task_id is set
        assert x.project_id is not None


class TestXAgentResponse:
    """Test XAgentResponse class."""

    def test_xagent_response_initialization(self):
        """Test XAgentResponse initializes with defaults."""
        response = XAgentResponse(text="Test response")

        assert response.text == "Test response"
        assert response.artifacts == []
        assert response.preserved_steps == []
        assert response.regenerated_steps == []
        assert response.plan_changes == {}
        assert response.metadata == {}

    def test_xagent_response_with_all_fields(self):
        """Test XAgentResponse with all fields provided."""
        response = XAgentResponse(
            text="Complete response",
            artifacts=["file1.txt", "file2.pdf"],
            preserved_steps=["task_1", "task_2"],
            regenerated_steps=["task_3"],
            plan_changes={"type": "regenerate"},
            metadata={"execution_time": 1.5}
        )

        assert response.text == "Complete response"
        assert len(response.artifacts) == 2
        assert len(response.preserved_steps) == 2
        assert len(response.regenerated_steps) == 1
        assert response.plan_changes["type"] == "regenerate"
        assert response.metadata["execution_time"] == 1.5
