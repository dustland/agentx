"""
Integration tests for XAgent handoff functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import json

from vibex.core.handoff_evaluator import HandoffEvaluator, HandoffContext
from vibex.core.message import Message
from vibex.core.task import Task
from vibex.core.xagent import XAgent
from vibex.core.config import TeamConfig, AgentConfig, Handoff
from vibex.core.plan import Plan


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
                    goal="Writes content",
                    tools=["file_write"]
                ),
                AgentConfig(
                    name="reviewer",
                    goal="Reviews content",
                    tools=["file_read", "file_write"]
                ),
                AgentConfig(
                    name="editor",
                    goal="Edits content",
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
    def mock_taskspace(self, tmp_path):
        """Create a mock project_storage."""
        taskspace_mock = Mock()
        taskspace_mock.get_project_storage_path.return_value = tmp_path
        taskspace_mock.list_files.return_value = ["draft.md", "notes.txt"]
        taskspace_mock.save_task_history = AsyncMock()
        return taskspace_mock

    @pytest.mark.asyncio
    async def test_xagent_initializes_handoff_evaluator(self, team_config_with_handoffs, mock_taskspace):
        """Test that XAgent properly initializes HandoffEvaluator when handoffs are configured."""
        with patch('vibex.core.xagent.Agent'), \
             patch('vibex.core.xagent.ToolManager'), \
             patch('vibex.core.xagent.MessageQueue'), \
             patch('vibex.core.xagent.setup_task_file_logging'), \
             patch('vibex.core.xagent.Brain'):

            # Mock agent creation
            mock_agents = {}
            for agent_config in team_config_with_handoffs.agents:
                mock_agent = Mock()
                mock_agent.name = agent_config.name
                mock_agents[agent_config.name] = mock_agent
                # MockAgent.return_value = mock_agent # This line was removed as per new_code

            xagent = XAgent(
                project_id="test_project",
                team_config=team_config_with_handoffs,
                workspace_dir=mock_taskspace.get_project_storage_path()
            )

            # Verify handoff evaluator was created
            assert xagent.handoff_evaluator is not None
            assert isinstance(xagent.handoff_evaluator, HandoffEvaluator)
            assert len(xagent.handoff_evaluator.handoffs) == 2

    @pytest.mark.asyncio
    async def test_xagent_no_handoff_evaluator_without_handoffs(self, mock_taskspace):
        """Test that XAgent doesn't create HandoffEvaluator when no handoffs configured."""
        team_config_no_handoffs = TeamConfig(
            name="Test Team",
            agents=[
                AgentConfig(name="writer", description="Writer")
            ],
            handoffs=[]  # No handoffs
        )

        with patch('vibex.core.xagent.Agent'), \
             patch('vibex.core.xagent.ToolManager'), \
             patch('vibex.core.xagent.MessageQueue'), \
             patch('vibex.core.xagent.setup_task_file_logging'), \
             patch('vibex.core.xagent.Brain'):

            xagent = XAgent(
                project_id="test_project",
                team_config=team_config_no_handoffs,
                workspace_dir=mock_taskspace.get_project_storage_path()
            )

            # Verify no handoff evaluator was created
            assert xagent.handoff_evaluator is None

    @pytest.mark.asyncio
    async def test_execute_single_task_with_handoff(self, team_config_with_handoffs, mock_taskspace):
        """Test that executing a task evaluates and creates handoffs."""
        with patch('vibex.core.xagent.Agent'), \
             patch('vibex.core.xagent.ToolManager'), \
             patch('vibex.core.xagent.MessageQueue'), \
             patch('vibex.core.xagent.setup_task_file_logging'), \
             patch('vibex.core.xagent.Brain') as MockAgent:

            # Setup mock agents
            mock_writer = AsyncMock()
            mock_writer.name = "writer"
            mock_writer.generate_response = AsyncMock(
                return_value="Draft completed and saved to draft.md"
            )

            MockAgent.side_effect = lambda *args, **kwargs: mock_writer

            xagent = XAgent(
                project_id="test_project",
                team_config=team_config_with_handoffs,
                workspace_dir=mock_taskspace.get_project_storage_path()
            )

            # Override specialist agents to use our mock
            xagent.specialist_agents = {"writer": mock_writer}

            # Create a test plan with a writer task
            test_plan = Plan(
                goal="Write and review article",
                tasks=[
                    Task(
                        id="task_1",
                        name="Write draft",
                        description="Write the initial draft",
                        assigned_to="writer",
                        status="pending"
                    )
                ]
            )
            xagent.plan = test_plan

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
                assert handoff_task.assigned_to == "reviewer"
                assert handoff_task.dependencies == ["task_1"]
                assert "Continue work with reviewer" in handoff_task.name

                # Verify response includes handoff message
                assert "Handing off to reviewer" in result

    @pytest.mark.asyncio
    async def test_execute_single_task_no_handoff(self, team_config_with_handoffs, mock_taskspace):
        """Test task execution when no handoff occurs."""
        with patch('vibex.core.xagent.Agent'), \
             patch('vibex.core.xagent.ToolManager'), \
             patch('vibex.core.xagent.MessageQueue'), \
             patch('vibex.core.xagent.setup_task_file_logging'), \
             patch('vibex.core.xagent.Brain') as MockAgent:

            # Setup mock agent
            mock_writer = AsyncMock()
            mock_writer.name = "writer"
            mock_writer.generate_response = AsyncMock(
                return_value="Still working on the draft..."
            )

            MockAgent.side_effect = lambda *args, **kwargs: mock_writer

            xagent = XAgent(
                project_id="test_project",
                team_config=team_config_with_handoffs,
                workspace_dir=mock_taskspace.get_project_storage_path()
            )

            xagent.specialist_agents = {"writer": mock_writer}

            # Create a test plan
            test_plan = Plan(
                goal="Write article",
                tasks=[
                    Task(
                        id="task_1",
                        name="Write draft",
                        description="Write the initial draft",
                        assigned_to="writer",
                        status="pending"
                    )
                ]
            )
            xagent.plan = test_plan

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
    async def test_handoff_task_dependencies(self, team_config_with_handoffs, mock_taskspace):
        """Test that handoff tasks have proper dependencies."""
        with patch('vibex.core.xagent.Agent'), \
             patch('vibex.core.xagent.ToolManager'), \
             patch('vibex.core.xagent.MessageQueue'), \
             patch('vibex.core.xagent.setup_task_file_logging'), \
             patch('vibex.core.xagent.Brain') as MockAgent:

            mock_writer = AsyncMock()
            mock_writer.name = "writer"
            mock_writer.generate_response = AsyncMock(return_value="Task completed")

            MockAgent.side_effect = lambda *args, **kwargs: mock_writer

            xagent = XAgent(
                project_id="test_project",
                team_config=team_config_with_handoffs,
                workspace_dir=mock_taskspace.get_project_storage_path()
            )

            xagent.specialist_agents = {"writer": mock_writer}

            # Create a plan with existing dependencies
            test_plan = Plan(
                goal="Complex workflow",
                tasks=[
                    Task(
                        id="task_1",
                        name="Research",
                        description="Research topic",
                        assigned_to="writer",
                        status="completed"
                    ),
                    Task(
                        id="task_2",
                        name="Write draft",
                        description="Write based on research",
                        assigned_to="writer",
                        dependencies=["task_1"],
                        status="pending"
                    )
                ]
            )
            xagent.plan = test_plan

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
    async def test_persist_plan_after_handoff(self, team_config_with_handoffs, mock_taskspace, tmp_path):
        """Test that plan is persisted after adding handoff task."""
        with patch('vibex.core.xagent.Agent'), \
             patch('vibex.core.xagent.ToolManager'), \
             patch('vibex.core.xagent.MessageQueue'), \
             patch('vibex.core.xagent.setup_task_file_logging'), \
             patch('vibex.core.xagent.Brain') as MockAgent:

            # Setup project_storage to actually save files
            mock_taskspace.get_project_storage_path.return_value = tmp_path

            mock_writer = AsyncMock()
            mock_writer.name = "writer"
            mock_writer.generate_response = AsyncMock(return_value="Task done")

            MockAgent.side_effect = lambda *args, **kwargs: mock_writer

            xagent = XAgent(
                project_id="test_project",
                team_config=team_config_with_handoffs,
                workspace_dir=mock_taskspace.get_project_storage_path()
            )

            xagent.specialist_agents = {"writer": mock_writer}

            test_plan = Plan(
                goal="Test workflow",
                tasks=[
                    Task(
                        id="task_1",
                        name="Write",
                        description="Write content",
                        assigned_to="writer",
                        status="pending"
                    )
                ]
            )
            xagent.plan = test_plan

            # Mock handoff
            with patch.object(xagent.handoff_evaluator, 'evaluate_handoffs',
                            new_callable=AsyncMock) as mock_evaluate:
                mock_evaluate.return_value = "reviewer"

                # Execute task
                await xagent._execute_single_task(test_plan.tasks[0])

                # Verify plan was saved
                # When workspace_dir is provided, ProjectStorage uses workspace_dir.parent / project_id
                project_storage_path = xagent.project_storage.get_project_path()
                plan_file = project_storage_path / "plan.json"
                assert plan_file.exists()

                # Load and verify saved plan
                with open(plan_file) as f:
                    saved_plan_data = json.load(f)

                assert len(saved_plan_data["tasks"]) == 2
                assert saved_plan_data["tasks"][1]["assigned_to"] == "reviewer"
