import pytest
from unittest.mock import Mock, AsyncMock, patch
from agentx.core.orchestrator import Orchestrator
from agentx.core.task import Task
from agentx.core.agent import Agent
from agentx.core.message import TaskStep, TextPart, TaskHistory, MessageQueue
from agentx.core.plan import Plan, PlanItem
from agentx.core.config import TeamConfig, AgentConfig, BrainConfig, OrchestratorConfig
from agentx.storage.workspace import WorkspaceStorage
from pathlib import Path
from agentx.core.brain import Brain


@pytest.fixture
def mock_task():
    task = Mock(spec=Task)
    task.task_id = "test_task"
    task.current_plan = None
    task.initial_prompt = "test prompt"

    # Mock workspace
    workspace = Mock(spec=WorkspaceStorage)
    workspace.get_workspace_path.return_value = Path("/tmp/test_workspace")
    task.workspace = workspace

    return task


@pytest.fixture
def mock_agents():
    return {
        "test_agent": Mock(spec=Agent),
        "planner_agent": Mock(spec=Agent),
    }


@pytest.fixture
def mock_team_config():
    return TeamConfig(
        name="test_team",
        agents=[
            AgentConfig(name="test_agent", brain_config=BrainConfig(model="test_model")),
            AgentConfig(name="planner_agent", brain_config=BrainConfig(model="test_model")),
        ],
        orchestrator=OrchestratorConfig(
            brain_config=BrainConfig(model="test_model")
        )
    )


@pytest.fixture
def orchestrator(mock_team_config, mock_agents):
    message_queue = Mock(spec=MessageQueue)
    tool_manager = Mock()

    orc = Orchestrator(
        team_config=mock_team_config,
        message_queue=message_queue,
        tool_manager=tool_manager,
        agents=mock_agents,
    )
    return orc


@pytest.mark.asyncio
async def test_step_generates_plan_if_none_exists(orchestrator, mock_task, mock_agents):
    """Test that orchestrator generates a plan when none exists."""
    # Arrange
    messages = [{"role": "user", "content": "test message"}]
    generated_plan = Plan(
        goal="Test goal",
        tasks=[PlanItem(id="task1", name="Test Task", goal="do work", status="pending")]
    )

    # Mock the _generate_plan method and task.load_plan to return None (no existing plan)
    mock_task.load_plan = AsyncMock(return_value=None)
    mock_task.update_plan = Mock()

    with patch.object(orchestrator, '_generate_plan', new=AsyncMock(return_value=generated_plan)) as mock_gen_plan, \
         patch.object(orchestrator, '_persist_plan', new=AsyncMock()) as mock_persist:

        # Mock agent response
        mock_agents["test_agent"].generate_response = AsyncMock(return_value="Test response")

        # Act
        response = await orchestrator.step(messages, mock_task)

        # Assert
        mock_gen_plan.assert_called_once()
        assert orchestrator.plan == generated_plan
        assert "Test response" in response or "Test Task" in response


@pytest.mark.asyncio
async def test_step_uses_existing_plan(orchestrator, mock_task, mock_agents):
    """Test that orchestrator uses existing plan when available."""
    # Arrange
    messages = [{"role": "user", "content": "test message"}]
    existing_plan = Plan(
        goal="Existing goal",
        tasks=[PlanItem(id="task1", name="Existing Task", goal="do existing work", status="pending")]
    )
    orchestrator.plan = existing_plan

    with patch.object(orchestrator, '_generate_plan', new=AsyncMock()) as mock_gen_plan, \
         patch.object(orchestrator, '_persist_plan', new=AsyncMock()) as mock_persist:

        # Mock agent response
        mock_agents["test_agent"].generate_response = AsyncMock(return_value="Existing task response")

        # Act
        response = await orchestrator.step(messages, mock_task)

        # Assert
        mock_gen_plan.assert_not_called()  # Should not generate new plan
        assert orchestrator.plan == existing_plan


@pytest.mark.asyncio
async def test_step_completes_plan_tasks(orchestrator, mock_task, mock_agents):
    """Test that orchestrator completes plan tasks sequentially."""
    # Arrange
    messages = [{"role": "user", "content": "test message"}]
    plan = Plan(
        goal="Multi-task goal",
        tasks=[
            PlanItem(id="task1", name="First Task", goal="do first work", status="pending"),
            PlanItem(id="task2", name="Second Task", goal="do second work", status="pending", dependencies=["task1"])
        ]
    )
    orchestrator.plan = plan

    with patch.object(orchestrator, '_persist_plan', new=AsyncMock()) as mock_persist:
        # Mock agent response
        mock_agents["test_agent"].generate_response = AsyncMock(return_value="Task completed")

        # Act - First step should execute task1
        response = await orchestrator.step(messages, mock_task)

        # Assert
        assert plan.get_task_by_id("task1").status == "completed"
        assert plan.get_task_by_id("task2").status == "pending"  # Still pending due to dependency
        assert "Task completed" in response


@pytest.mark.asyncio
async def test_step_handles_plan_completion(orchestrator, mock_task, mock_agents):
    """Test that orchestrator handles plan completion correctly."""
    # Arrange
    messages = [{"role": "user", "content": "test message"}]
    plan = Plan(
        goal="Single task goal",
        tasks=[PlanItem(id="task1", name="Only Task", goal="do only work", status="completed")]
    )
    orchestrator.plan = plan

    # Act
    response = await orchestrator.step(messages, mock_task)

    # Assert
    assert "Task completed successfully" in response
    assert "All plan items have been finished" in response


@pytest.mark.asyncio
async def test_step_handles_failed_tasks(orchestrator, mock_task, mock_agents):
    """Test that orchestrator handles task failures correctly."""
    # Arrange
    messages = [{"role": "user", "content": "test message"}]
    plan = Plan(
        goal="Failing task goal",
        tasks=[PlanItem(id="task1", name="Failing Task", goal="will fail", status="pending")]
    )
    orchestrator.plan = plan

    with patch.object(orchestrator, '_persist_plan', new=AsyncMock()) as mock_persist:
        # Mock agent to raise an exception
        mock_agents["test_agent"].generate_response = AsyncMock(side_effect=Exception("Task failed"))

        # Act
        response = await orchestrator.step(messages, mock_task)

        # Assert
        assert plan.get_task_by_id("task1").status == "failed"
        assert "failed" in response.lower()


def test_plan_dependency_management():
    """Test that plan correctly manages task dependencies."""
    # Arrange
    plan = Plan(
        goal="Dependency test",
        tasks=[
            PlanItem(id="task1", name="First", goal="first", status="pending"),
            PlanItem(id="task2", name="Second", goal="second", status="pending", dependencies=["task1"]),
            PlanItem(id="task3", name="Third", goal="third", status="pending", dependencies=["task2"])
        ]
    )

    # Act & Assert
    # Initially, only task1 should be actionable
    next_task = plan.get_next_actionable_task()
    assert next_task.id == "task1"

    # After completing task1, task2 should be actionable
    plan.update_task_status("task1", "completed")
    next_task = plan.get_next_actionable_task()
    assert next_task.id == "task2"

    # After completing task2, task3 should be actionable
    plan.update_task_status("task2", "completed")
    next_task = plan.get_next_actionable_task()
    assert next_task.id == "task3"

    # After completing all tasks, no task should be actionable
    plan.update_task_status("task3", "completed")
    next_task = plan.get_next_actionable_task()
    assert next_task is None
    assert plan.is_complete()


def test_plan_progress_tracking():
    """Test that plan progress tracking works correctly."""
    # Arrange
    plan = Plan(
        goal="Progress test",
        tasks=[
            PlanItem(id="task1", name="First", goal="first", status="completed"),
            PlanItem(id="task2", name="Second", goal="second", status="in_progress"),
            PlanItem(id="task3", name="Third", goal="third", status="pending"),
            PlanItem(id="task4", name="Fourth", goal="fourth", status="failed")
        ]
    )

    # Act
    progress = plan.get_progress_summary()

    # Assert
    assert progress["total"] == 4
    assert progress["completed"] == 1
    assert progress["in_progress"] == 1
    assert progress["pending"] == 1
    assert progress["failed"] == 1
    assert progress["completion_percentage"] == 25.0
    assert plan.has_failed_tasks()
    assert not plan.is_complete()


@pytest.mark.asyncio
async def test_orchestrator_works_without_brain_config():
    """Test that orchestrator works with default brain config when none is provided."""
    # Arrange - team config without brain_config
    team_config = TeamConfig(
        name="test_team_no_brain",
        agents=[
            AgentConfig(name="test_agent", brain_config=BrainConfig(model="test_model"))
        ]
        # Note: No orchestrator.brain_config specified
    )

    message_queue = Mock(spec=MessageQueue)
    tool_manager = Mock()
    mock_agents = {
        "test_agent": Mock(spec=Agent)
    }

    # Act - Should not raise an error
    orchestrator = Orchestrator(
        team_config=team_config,
        message_queue=message_queue,
        tool_manager=tool_manager,
        agents=mock_agents,
    )

    # Assert
    assert orchestrator.brain is not None
    assert isinstance(orchestrator.brain, Brain)
    # Should use default configuration values
    assert orchestrator.brain.config.temperature == 0.3
    assert orchestrator.brain.config.max_tokens == 2000
    assert orchestrator.brain.config.timeout == 120
