"""
Tests for XAgent - the unified conversational interface.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from agentx.core.xagent import XAgent, XAgentResponse
from agentx.core.config import TeamConfig, AgentConfig, BrainConfig
from agentx.core.message import Message, TextPart
from agentx.core.plan import Plan, PlanItem


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
def mock_workspace_path(tmp_path):
    """Create a temporary workspace path."""
    return tmp_path / "test_workspace"


class TestXAgent:
    """Test XAgent functionality."""

    @patch('agentx.storage.factory.StorageFactory')
    @patch('agentx.core.xagent.setup_task_file_logging')
    @patch('agentx.tool.manager.ToolManager._register_builtin_tools')
    def test_xagent_initialization(self, mock_register_tools, mock_setup_logging, mock_storage_factory, mock_team_config, mock_workspace_path):
        """Test XAgent initializes correctly."""
        # Arrange
        mock_workspace = Mock()
        mock_workspace.get_workspace_path.return_value = mock_workspace_path
        mock_storage_factory.create_workspace_storage.return_value = mock_workspace

        # Act
        x = XAgent(team_config=mock_team_config, workspace_dir=mock_workspace_path)

        # Assert
        assert x.task_id is not None
        assert x.team_config == mock_team_config
        assert x.workspace == mock_workspace
        assert "test_agent" in x.specialist_agents
        assert x.name == "X"
        assert not x.is_complete
        mock_setup_logging.assert_called_once()
        mock_register_tools.assert_called_once()

    @patch('agentx.storage.factory.StorageFactory')
    @patch('agentx.core.xagent.setup_task_file_logging')
    @patch('agentx.tool.manager.ToolManager._register_builtin_tools')
    @pytest.mark.asyncio
    async def test_chat_with_simple_text(self, mock_register_tools, mock_setup_logging, mock_storage_factory, mock_team_config, mock_workspace_path):
        """Test chat with simple text message creates plan but doesn't execute automatically."""
        # Arrange
        mock_workspace = Mock()
        mock_workspace.get_workspace_path.return_value = mock_workspace_path
        mock_storage_factory.create_workspace_storage.return_value = mock_workspace

        x = XAgent(team_config=mock_team_config, workspace_dir=mock_workspace_path)

        # Mock the brain's response
        with patch.object(x.brain, 'generate_response') as mock_generate:
            mock_generate.return_value = Mock(content='{"requires_plan_adjustment": false, "is_informational": false, "is_new_task": true}')

            # Mock plan generation
            with patch.object(x, '_generate_plan') as mock_plan_gen:
                mock_plan = Plan(
                    goal="Test goal",
                    tasks=[
                        PlanItem(
                            id="task_1",
                            name="Test task",
                            goal="Complete test",
                            agent="test_agent",
                            dependencies=[],
                            status="pending"
                        )
                    ]
                )
                mock_plan_gen.return_value = mock_plan

                # Act
                response = await x.chat("Hello, create a test report")

                # Assert
                assert isinstance(response, XAgentResponse)
                # Verify that plan was created but not executed
                assert "I've created a plan for your task: Test goal" in response.text
                assert "Use step() to execute the plan autonomously" in response.text
                assert len(x.conversation_history) == 1
                assert x.conversation_history[0].content == "Hello, create a test report"
                # Verify plan was set
                assert x.current_plan is not None
                assert x.current_plan.goal == "Test goal"

    @patch('agentx.storage.factory.StorageFactory')
    @patch('agentx.core.xagent.setup_task_file_logging')
    @patch('agentx.tool.manager.ToolManager._register_builtin_tools')
    @pytest.mark.asyncio
    async def test_chat_with_message_object(self, mock_register_tools, mock_setup_logging, mock_storage_factory, mock_team_config, mock_workspace_path):
        """Test chat with Message object."""
        # Arrange
        mock_workspace = Mock()
        mock_workspace.get_workspace_path.return_value = mock_workspace_path
        mock_storage_factory.create_workspace_storage.return_value = mock_workspace

        x = XAgent(team_config=mock_team_config, workspace_dir=mock_workspace_path)

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
            assert "informational response" in response.text
            assert response.metadata.get("query_type") == "informational"

    @patch('agentx.storage.factory.StorageFactory')
    @patch('agentx.core.xagent.setup_task_file_logging')
    @patch('agentx.tool.manager.ToolManager._register_builtin_tools')
    @pytest.mark.asyncio
    async def test_plan_adjustment_preserves_work(self, mock_register_tools, mock_setup_logging, mock_storage_factory, mock_team_config, mock_workspace_path):
        """Test that plan adjustment preserves completed work."""
        # Arrange
        mock_workspace = Mock()
        mock_workspace.get_workspace_path.return_value = mock_workspace_path
        mock_storage_factory.create_workspace_storage.return_value = mock_workspace

        x = XAgent(team_config=mock_team_config, workspace_dir=mock_workspace_path)

        # Set up existing plan with completed tasks
        x.current_plan = Plan(
            goal="Test goal",
            tasks=[
                PlanItem(
                    id="task_1",
                    name="Research",
                    goal="Do research",
                    agent="test_agent",
                    dependencies=[],
                    status="completed"
                ),
                PlanItem(
                    id="task_2",
                    name="Write report",
                    goal="Write the report",
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

    @patch('agentx.storage.factory.StorageFactory')
    @patch('agentx.core.xagent.setup_task_file_logging')
    @patch('agentx.tool.manager.ToolManager._register_builtin_tools')
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_register_tools, mock_setup_logging, mock_storage_factory, mock_team_config, mock_workspace_path):
        """Test error handling in chat method."""
        # Arrange
        mock_workspace = Mock()
        mock_workspace.get_workspace_path.return_value = mock_workspace_path
        mock_storage_factory.create_workspace_storage.return_value = mock_workspace

        x = XAgent(team_config=mock_team_config, workspace_dir=mock_workspace_path)

        # Mock brain to raise an exception
        with patch.object(x.brain, 'generate_response') as mock_generate:
            mock_generate.side_effect = Exception("Test error")

            # Act
            response = await x.chat("This should cause an error")

            # Assert
            assert isinstance(response, XAgentResponse)
            assert "error processing your message" in response.text.lower()
            assert "Test error" in response.metadata.get("error", "")

    @patch('agentx.storage.factory.StorageFactory')
    @patch('agentx.core.xagent.setup_task_file_logging')
    @patch('agentx.tool.manager.ToolManager._register_builtin_tools')
    def test_plan_summary_generation(self, mock_register_tools, mock_setup_logging, mock_storage_factory, mock_team_config, mock_workspace_path):
        """Test plan summary generation."""
        # Arrange
        mock_workspace = Mock()
        mock_workspace.get_workspace_path.return_value = mock_workspace_path
        mock_storage_factory.create_workspace_storage.return_value = mock_workspace

        x = XAgent(team_config=mock_team_config, workspace_dir=mock_workspace_path)

        # Set up plan with mixed statuses
        x.current_plan = Plan(
            goal="Test comprehensive plan",
            tasks=[
                PlanItem(id="task_1", name="Task 1", goal="Goal 1", agent="test_agent", status="completed"),
                PlanItem(id="task_2", name="Task 2", goal="Goal 2", agent="test_agent", status="in_progress"),
                PlanItem(id="task_3", name="Task 3", goal="Goal 3", agent="test_agent", status="pending")
            ]
        )

        # Act
        summary = x._get_plan_summary()

        # Assert
        assert "Test comprehensive plan" in summary
        assert "1/3 completed" in summary

    @patch('agentx.storage.factory.StorageFactory')
    @patch('agentx.core.xagent.setup_task_file_logging')
    @patch('agentx.tool.manager.ToolManager._register_builtin_tools')
    def test_conversation_summary_generation(self, mock_register_tools, mock_setup_logging, mock_storage_factory, mock_team_config, mock_workspace_path):
        """Test conversation summary generation."""
        # Arrange
        mock_workspace = Mock()
        mock_workspace.get_workspace_path.return_value = mock_workspace_path
        mock_storage_factory.create_workspace_storage.return_value = mock_workspace

        x = XAgent(team_config=mock_team_config, workspace_dir=mock_workspace_path)

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

    @patch('agentx.storage.factory.StorageFactory')
    @patch('agentx.core.xagent.setup_task_file_logging')
    @patch('agentx.tool.manager.ToolManager._register_builtin_tools')
    @pytest.mark.asyncio
    async def test_compatibility_methods(self, mock_register_tools, mock_setup_logging, mock_storage_factory, mock_team_config, mock_workspace_path):
        """Test XAgent methods."""
        # Arrange
        mock_workspace = Mock()
        mock_workspace.get_workspace_path.return_value = mock_workspace_path
        mock_storage_factory.create_workspace_storage.return_value = mock_workspace

        x = XAgent(team_config=mock_team_config, workspace_dir=mock_workspace_path)

        # Test is_complete property
        assert not x.is_complete

        # Test workspace access
        workspace_path = x.workspace.get_workspace_path()
        assert workspace_path == mock_workspace_path

        # Test task_id is set
        assert x.task_id is not None


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
