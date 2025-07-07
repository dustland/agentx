"""
Tests for Task class planning integration.

These tests verify that the Task class properly integrates with the planning system,
including plan creation, persistence, loading, and context integration.
"""

import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path
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
    workspace_path = Path("/tmp/test_workspace")
    workspace.get_workspace_path.return_value = workspace_path
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
    with patch.object(task_instance, '_persist_plan') as mock_persist:
        task_instance.create_plan(sample_plan)

    # Assert
    assert task_instance.current_plan == sample_plan
    assert task_instance.get_plan() == sample_plan
    mock_persist.assert_called_once()


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
    with patch.object(task_instance, '_persist_plan') as mock_persist:
        task_instance.update_plan(updated_plan)

    # Assert
    assert task_instance.current_plan == updated_plan
    assert task_instance.get_plan() == updated_plan
    mock_persist.assert_called_once()


def test_get_plan_returns_none_when_no_plan(task_instance):
    """Test that get_plan returns None when no plan exists."""
    # Act & Assert
    assert task_instance.get_plan() is None


def test_plan_persistence(task_instance, sample_plan, mock_workspace):
    """Test that plans are persisted to the workspace."""
    # Arrange
    plan_file_path = Path("/tmp/test_workspace/plan.json")

    # Mock file operations
    with patch('json.dumps') as mock_json_dumps, \
         patch.object(plan_file_path, 'write_text') as mock_write_text, \
         patch.object(plan_file_path, 'parent') as mock_parent:

        mock_json_dumps.return_value = '{"test": "json"}'

        # Act
        task_instance.create_plan(sample_plan)

        # Assert
        mock_json_dumps.assert_called_once()
        # Verify plan data was serialized
        call_args = mock_json_dumps.call_args[0][0]
        assert call_args == sample_plan.model_dump()


def test_plan_loading_success(task_instance, sample_plan, mock_workspace):
    """Test successful plan loading from workspace."""
    # Arrange
    plan_file_path = Path("/tmp/test_workspace/plan.json")
    plan_data = sample_plan.model_dump()

    with patch.object(plan_file_path, 'exists', return_value=True), \
         patch.object(plan_file_path, 'read_text', return_value=json.dumps(plan_data)):

        # Act
        loaded_plan = task_instance.load_plan()

        # Assert
        assert loaded_plan is not None
        assert loaded_plan.goal == sample_plan.goal
        assert len(loaded_plan.tasks) == len(sample_plan.tasks)
        assert task_instance.current_plan == loaded_plan


def test_plan_loading_file_not_exists(task_instance, mock_workspace):
    """Test plan loading when file doesn't exist."""
    # Arrange
    plan_file_path = Path("/tmp/test_workspace/plan.json")

    with patch.object(plan_file_path, 'exists', return_value=False):

        # Act
        loaded_plan = task_instance.load_plan()

        # Assert
        assert loaded_plan is None
        assert task_instance.current_plan is None


def test_plan_loading_invalid_json(task_instance, mock_workspace):
    """Test plan loading with invalid JSON."""
    # Arrange
    plan_file_path = Path("/tmp/test_workspace/plan.json")

    with patch.object(plan_file_path, 'exists', return_value=True), \
         patch.object(plan_file_path, 'read_text', return_value="invalid json"):

        # Act
        loaded_plan = task_instance.load_plan()

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


def test_plan_persistence_error_handling(task_instance, sample_plan, mock_workspace):
    """Test that plan persistence errors are handled gracefully."""
    # Arrange
    plan_file_path = Path("/tmp/test_workspace/plan.json")

    with patch.object(plan_file_path, 'write_text', side_effect=Exception("Write error")), \
         patch('agentx.core.task.logger') as mock_logger:

        # Act
        task_instance.create_plan(sample_plan)

        # Assert
        # Plan should still be set even if persistence fails
        assert task_instance.current_plan == sample_plan

        # Error should be logged
        mock_logger.error.assert_called_once()
        assert "Failed to persist plan" in str(mock_logger.error.call_args)


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
