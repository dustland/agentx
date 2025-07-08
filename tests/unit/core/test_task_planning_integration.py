"""
Tests for Task class planning integration.

These tests verify that the Task class properly integrates with the planning system,
including plan creation, persistence, loading, and context integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from agentx.core.task import Task
from agentx.core.plan import Plan, PlanItem
from agentx.core.config import TaskConfig
from agentx.core.message import TaskHistory, MessageQueue
from agentx.core.orchestrator import Orchestrator
from agentx.storage.workspace import WorkspaceStorage


@pytest.fixture
def mock_workspace():
    """Mock workspace for testing."""
    workspace = Mock(spec=WorkspaceStorage)
    workspace.store_plan = AsyncMock()
    workspace.get_plan = AsyncMock()
    return workspace


@pytest.fixture
def sample_plan():
    """Sample plan for testing."""
    return Plan(
        goal="Test planning integration",
        tasks=[
            PlanItem(
                id="task1",
                name="First Task",
                goal="Complete the first task",
                status="pending"
            ),
            PlanItem(
                id="task2",
                name="Second Task",
                goal="Complete the second task",
                status="pending",
                dependencies=["task1"]
            )
        ]
    )


@pytest.fixture
def task_instance(mock_workspace):
    """Create a Task instance for testing."""
    return Task(
        task_id="test_task",
        config=TaskConfig(),
        history=TaskHistory(task_id="test_task"),
        message_queue=MessageQueue(),
        agents={},
        workspace=mock_workspace,
        orchestrator=Mock(spec=Orchestrator),
        initial_prompt="Test prompt"
    )


def test_task_initialization_with_planning(task_instance):
    """Test that Task initializes with planning support."""
    # Assert
    assert task_instance.current_plan is None
    assert hasattr(task_instance, 'create_plan')
    assert hasattr(task_instance, 'update_plan')
    assert hasattr(task_instance, 'get_plan')
    assert hasattr(task_instance, 'load_plan')


def test_create_plan(task_instance, sample_plan):
    """Test creating a plan through the Task class."""
    # Act
    task_instance.create_plan(sample_plan)

    # Assert
    assert task_instance.current_plan == sample_plan
    assert task_instance.get_plan() == sample_plan


def test_update_plan(task_instance, sample_plan):
    """Test updating an existing plan."""
    # Arrange
    task_instance.current_plan = sample_plan

    # Create updated plan
    updated_plan = Plan(
        goal="Updated goal",
        tasks=[
            PlanItem(id="new_task", name="New Task", goal="New task goal", status="pending")
        ]
    )

    # Act
    task_instance.update_plan(updated_plan)

    # Assert
    assert task_instance.current_plan == updated_plan
    assert task_instance.get_plan() == updated_plan


def test_get_plan_returns_none_when_no_plan(task_instance):
    """Test that get_plan returns None when no plan exists."""
    # Act & Assert
    assert task_instance.get_plan() is None


@pytest.mark.asyncio
async def test_plan_persistence(task_instance, sample_plan, mock_workspace):
    """Test that plans are persisted to the workspace."""
    # Arrange
    mock_workspace.store_plan.return_value = None

    # Act
    await task_instance._persist_plan()

    # Assert - since no plan is set, store_plan should not be called
    mock_workspace.store_plan.assert_not_called()

    # Set a plan and test persistence
    task_instance.current_plan = sample_plan
    await task_instance._persist_plan()

    # Assert - store_plan should be called with plan data
    mock_workspace.store_plan.assert_called_once_with(sample_plan.model_dump())


@pytest.mark.asyncio
async def test_plan_loading_success(task_instance, sample_plan, mock_workspace):
    """Test successful plan loading from workspace."""
    # Arrange
    plan_data = sample_plan.model_dump()
    mock_workspace.get_plan.return_value = plan_data

    # Act
    loaded_plan = await task_instance.load_plan()

    # Assert
    assert loaded_plan is not None
    assert loaded_plan.goal == sample_plan.goal
    assert len(loaded_plan.tasks) == len(sample_plan.tasks)
    assert task_instance.current_plan == loaded_plan
    mock_workspace.get_plan.assert_called_once_with()


@pytest.mark.asyncio
async def test_plan_loading_file_not_exists(task_instance, mock_workspace):
    """Test plan loading when plan doesn't exist in workspace."""
    # Arrange
    mock_workspace.get_plan.return_value = None

    # Act
    loaded_plan = await task_instance.load_plan()

    # Assert
    assert loaded_plan is None
    assert task_instance.current_plan is None
    mock_workspace.get_plan.assert_called_once_with()


@pytest.mark.asyncio
async def test_plan_loading_with_error(task_instance, mock_workspace):
    """Test plan loading with workspace error."""
    # Arrange
    mock_workspace.get_plan.side_effect = Exception("Workspace error")

    # Act
    loaded_plan = await task_instance.load_plan()

    # Assert
    assert loaded_plan is None
    assert task_instance.current_plan is None


def test_get_context_without_plan(task_instance):
    """Test get_context when no plan exists."""
    # Act
    context = task_instance.get_context()

    # Assert
    assert "plan" not in context
    assert context["task_id"] == "test_task"
    assert context["status"] == "in_progress"
    assert context["initial_prompt"] == "Test prompt"


def test_get_context_with_plan(task_instance, sample_plan):
    """Test get_context includes plan information when plan exists."""
    # Arrange
    task_instance.current_plan = sample_plan

    # Act
    context = task_instance.get_context()

    # Assert
    assert "plan" in context
    plan_context = context["plan"]
    assert plan_context["goal"] == sample_plan.goal
    assert plan_context["total_tasks"] == len(sample_plan.tasks)
    assert "progress" in plan_context
    assert plan_context["is_complete"] == sample_plan.is_complete()


def test_get_context_with_completed_plan(task_instance, sample_plan):
    """Test get_context with a completed plan."""
    # Arrange
    # Mark all tasks as completed
    for task in sample_plan.tasks:
        task.status = "completed"
    task_instance.current_plan = sample_plan

    # Act
    context = task_instance.get_context()

    # Assert
    plan_context = context["plan"]
    assert plan_context["is_complete"] is True
    assert plan_context["progress"]["completion_percentage"] == 100.0
    assert plan_context["progress"]["completed"] == 2


@pytest.mark.asyncio
async def test_plan_persistence_error_handling(task_instance, sample_plan, mock_workspace):
    """Test that plan persistence errors are handled gracefully."""
    # Arrange
    task_instance.current_plan = sample_plan
    mock_workspace.store_plan.side_effect = Exception("Storage error")

    # Act - should not raise exception
    await task_instance._persist_plan()

    # Assert
    # Plan should still be set even if persistence fails
    assert task_instance.current_plan == sample_plan
    mock_workspace.store_plan.assert_called_once_with(sample_plan.model_dump())


def test_task_completion_with_plan(task_instance, sample_plan):
    """Test task completion status with plan integration."""
    # Arrange
    task_instance.current_plan = sample_plan

    # Initially not complete
    assert not task_instance.is_complete

    # Complete the task
    task_instance.complete()

    # Assert
    assert task_instance.is_complete
