"""
Integration tests for XAgent handoff functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import json

from agentx.core.xagent import XAgent
from agentx.core.config import TeamConfig, AgentConfig, Handoff
from agentx.core.plan import Plan, PlanItem
from agentx.core.handoff_evaluator import HandoffEvaluator, HandoffContext


class TestXAgentHandoffs:
    """Test XAgent handoff functionality."""

    @pytest.fixture
    def team_config_with_handoffs(self):
        """Create a team configuration with handoffs."""
        return TeamConfig(
            name="Test Team",
            agents=[
                AgentConfig(
                    name="writer",
                    description="Writes content",
                    tools=["file_write"]
                ),
                AgentConfig(
                    name="reviewer",
                    description="Reviews content",
                    tools=["file_read", "file_write"]
                ),
                AgentConfig(
                    name="editor",
                    description="Edits content",
                    tools=["file_read", "file_write"]
                )
            ],
            handoffs=[
                Handoff(
                    from_agent="writer",
                    to_agent="reviewer",
                    condition="draft is complete and ready for review",
                    priority=1
                ),
                Handoff(
                    from_agent="reviewer",
                    to_agent="editor",
                    condition="review complete with changes needed",
                    priority=1
                )
            ]
        )

    @pytest.fixture
    def mock_workspace(self, tmp_path):
        """Create a mock workspace."""
        workspace_mock = Mock()
        workspace_mock.get_workspace_path.return_value = tmp_path
        workspace_mock.list_files.return_value = ["draft.md", "notes.txt"]
        workspace_mock.save_task_history = AsyncMock()
        return workspace_mock

    @pytest.mark.asyncio
    async def test_xagent_initializes_handoff_evaluator(self, team_config_with_handoffs, mock_workspace):
        """Test that XAgent properly initializes HandoffEvaluator when handoffs are configured."""
        with patch('agentx.core.xagent.Brain'), \
             patch('agentx.core.xagent.ToolManager'), \
             patch('agentx.core.xagent.MessageQueue'), \
             patch('agentx.core.xagent.setup_task_file_logging'), \
             patch('agentx.core.xagent.Agent') as MockAgent:

            # Mock agent creation
            mock_agents = {}
            for agent_config in team_config_with_handoffs.agents:
                mock_agent = Mock()
                mock_agent.name = agent_config.name
                mock_agents[agent_config.name] = mock_agent
                MockAgent.return_value = mock_agent

            xagent = XAgent(
                task_id="test_task",
                team_config=team_config_with_handoffs,
                workspace_dir=mock_workspace.get_workspace_path()
            )

            # Verify handoff evaluator was created
            assert xagent.handoff_evaluator is not None
            assert isinstance(xagent.handoff_evaluator, HandoffEvaluator)
            assert len(xagent.handoff_evaluator.handoffs) == 2

    @pytest.mark.asyncio
    async def test_xagent_no_handoff_evaluator_without_handoffs(self, mock_workspace):
        """Test that XAgent doesn't create HandoffEvaluator when no handoffs configured."""
        team_config_no_handoffs = TeamConfig(
            name="Test Team",
            agents=[
                AgentConfig(name="writer", description="Writer")
            ],
            handoffs=[]  # No handoffs
        )

        with patch('agentx.core.xagent.Brain'), \
             patch('agentx.core.xagent.ToolManager'), \
             patch('agentx.core.xagent.MessageQueue'), \
             patch('agentx.core.xagent.setup_task_file_logging'), \
             patch('agentx.core.xagent.Agent'):

            xagent = XAgent(
                task_id="test_task",
                team_config=team_config_no_handoffs,
                workspace_dir=mock_workspace.get_workspace_path()
            )

            # Verify no handoff evaluator was created
            assert xagent.handoff_evaluator is None

    @pytest.mark.asyncio
    async def test_execute_single_task_with_handoff(self, team_config_with_handoffs, mock_workspace):
        """Test that executing a task evaluates and creates handoffs."""
        with patch('agentx.core.xagent.Brain'), \
             patch('agentx.core.xagent.ToolManager'), \
             patch('agentx.core.xagent.MessageQueue'), \
             patch('agentx.core.xagent.setup_task_file_logging'), \
             patch('agentx.core.xagent.Agent') as MockAgent:

            # Setup mock agents
            mock_writer = AsyncMock()
            mock_writer.name = "writer"
            mock_writer.generate_response = AsyncMock(
                return_value="Draft completed and saved to draft.md"
            )

            MockAgent.side_effect = lambda *args, **kwargs: mock_writer

            xagent = XAgent(
                task_id="test_task",
                team_config=team_config_with_handoffs,
                workspace_dir=mock_workspace.get_workspace_path()
            )

            # Override specialist agents to use our mock
            xagent.specialist_agents = {"writer": mock_writer}

            # Create a test plan with a writer task
            test_plan = Plan(
                goal="Write and review article",
                tasks=[
                    PlanItem(
                        id="task_1",
                        name="Write draft",
                        goal="Write the initial draft",
                        agent="writer",
                        status="pending"
                    )
                ]
            )
            xagent.current_plan = test_plan

            # Mock the handoff evaluator to return "reviewer"
            with patch.object(xagent.handoff_evaluator, 'evaluate_handoffs',
                            new_callable=AsyncMock) as mock_evaluate:
                mock_evaluate.return_value = "reviewer"

                # Execute the task
                result = await xagent._execute_single_task(test_plan.tasks[0])

                # Verify handoff was evaluated
                mock_evaluate.assert_called_once()
                call_args = mock_evaluate.call_args[0][0]
                assert isinstance(call_args, HandoffContext)
                assert call_args.current_agent == "writer"
                assert "Draft completed" in call_args.task_result

                # Verify handoff task was added to plan
                assert len(test_plan.tasks) == 2
                handoff_task = test_plan.tasks[1]
                assert handoff_task.agent == "reviewer"
                assert handoff_task.dependencies == ["task_1"]
                assert "Continue work with reviewer" in handoff_task.name

                # Verify response includes handoff message
                assert "Handing off to reviewer" in result

    @pytest.mark.asyncio
    async def test_execute_single_task_no_handoff(self, team_config_with_handoffs, mock_workspace):
        """Test task execution when no handoff occurs."""
        with patch('agentx.core.xagent.Brain'), \
             patch('agentx.core.xagent.ToolManager'), \
             patch('agentx.core.xagent.MessageQueue'), \
             patch('agentx.core.xagent.setup_task_file_logging'), \
             patch('agentx.core.xagent.Agent') as MockAgent:

            # Setup mock agent
            mock_writer = AsyncMock()
            mock_writer.name = "writer"
            mock_writer.generate_response = AsyncMock(
                return_value="Still working on the draft..."
            )

            MockAgent.side_effect = lambda *args, **kwargs: mock_writer

            xagent = XAgent(
                task_id="test_task",
                team_config=team_config_with_handoffs,
                workspace_dir=mock_workspace.get_workspace_path()
            )

            xagent.specialist_agents = {"writer": mock_writer}

            # Create a test plan
            test_plan = Plan(
                goal="Write article",
                tasks=[
                    PlanItem(
                        id="task_1",
                        name="Write draft",
                        goal="Write the initial draft",
                        agent="writer",
                        status="pending"
                    )
                ]
            )
            xagent.current_plan = test_plan

            # Mock the handoff evaluator to return None (no handoff)
            with patch.object(xagent.handoff_evaluator, 'evaluate_handoffs',
                            new_callable=AsyncMock) as mock_evaluate:
                mock_evaluate.return_value = None

                # Execute the task
                result = await xagent._execute_single_task(test_plan.tasks[0])

                # Verify no handoff task was added
                assert len(test_plan.tasks) == 1

                # Verify no handoff message in response
                assert "Handing off" not in result

    @pytest.mark.asyncio
    async def test_handoff_task_dependencies(self, team_config_with_handoffs, mock_workspace):
        """Test that handoff tasks have proper dependencies."""
        with patch('agentx.core.xagent.Brain'), \
             patch('agentx.core.xagent.ToolManager'), \
             patch('agentx.core.xagent.MessageQueue'), \
             patch('agentx.core.xagent.setup_task_file_logging'), \
             patch('agentx.core.xagent.Agent') as MockAgent:

            mock_writer = AsyncMock()
            mock_writer.name = "writer"
            mock_writer.generate_response = AsyncMock(return_value="Task completed")

            MockAgent.side_effect = lambda *args, **kwargs: mock_writer

            xagent = XAgent(
                task_id="test_task",
                team_config=team_config_with_handoffs,
                workspace_dir=mock_workspace.get_workspace_path()
            )

            xagent.specialist_agents = {"writer": mock_writer}

            # Create a plan with existing dependencies
            test_plan = Plan(
                goal="Complex workflow",
                tasks=[
                    PlanItem(
                        id="task_1",
                        name="Research",
                        goal="Research topic",
                        agent="writer",
                        status="completed"
                    ),
                    PlanItem(
                        id="task_2",
                        name="Write draft",
                        goal="Write based on research",
                        agent="writer",
                        dependencies=["task_1"],
                        status="pending"
                    )
                ]
            )
            xagent.current_plan = test_plan

            # Mock handoff to reviewer
            with patch.object(xagent.handoff_evaluator, 'evaluate_handoffs',
                            new_callable=AsyncMock) as mock_evaluate:
                mock_evaluate.return_value = "reviewer"

                # Execute task_2
                await xagent._execute_single_task(test_plan.tasks[1])

                # Verify handoff task has correct dependencies
                assert len(test_plan.tasks) == 3
                handoff_task = test_plan.tasks[2]
                assert handoff_task.dependencies == ["task_2"]
                assert handoff_task.id == "handoff_task_2_reviewer"

    @pytest.mark.asyncio
    async def test_persist_plan_after_handoff(self, team_config_with_handoffs, mock_workspace, tmp_path):
        """Test that plan is persisted after adding handoff task."""
        with patch('agentx.core.xagent.Brain'), \
             patch('agentx.core.xagent.ToolManager'), \
             patch('agentx.core.xagent.MessageQueue'), \
             patch('agentx.core.xagent.setup_task_file_logging'), \
             patch('agentx.core.xagent.Agent') as MockAgent:

            # Setup workspace to actually save files
            mock_workspace.get_workspace_path.return_value = tmp_path

            mock_writer = AsyncMock()
            mock_writer.name = "writer"
            mock_writer.generate_response = AsyncMock(return_value="Task done")

            MockAgent.side_effect = lambda *args, **kwargs: mock_writer

            xagent = XAgent(
                task_id="test_task",
                team_config=team_config_with_handoffs,
                workspace_dir=mock_workspace.get_workspace_path()
            )

            xagent.specialist_agents = {"writer": mock_writer}

            test_plan = Plan(
                goal="Test workflow",
                tasks=[
                    PlanItem(
                        id="task_1",
                        name="Write",
                        goal="Write content",
                        agent="writer",
                        status="pending"
                    )
                ]
            )
            xagent.current_plan = test_plan

            # Mock handoff
            with patch.object(xagent.handoff_evaluator, 'evaluate_handoffs',
                            new_callable=AsyncMock) as mock_evaluate:
                mock_evaluate.return_value = "reviewer"

                # Execute task
                await xagent._execute_single_task(test_plan.tasks[0])

                # Verify plan was saved
                plan_file = tmp_path / "plan.json"
                assert plan_file.exists()

                # Load and verify saved plan
                with open(plan_file) as f:
                    saved_plan_data = json.load(f)

                assert len(saved_plan_data["tasks"]) == 2
                assert saved_plan_data["tasks"][1]["agent"] == "reviewer"
