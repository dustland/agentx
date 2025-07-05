import pytest
from unittest.mock import Mock, AsyncMock, patch
from agentx.core.orchestrator import Orchestrator
from agentx.core.task import Task
from agentx.core.agent import Agent
from agentx.core.message import Message
from agentx.core.plan import Plan, Phase, Task as PlanTask
from agentx.core.config import TeamConfig, AgentConfig, BrainConfig, OrchestrationConfig, PlannerConfig


@pytest.fixture
def mock_task():
    task = Mock(spec=Task)
    task.task_id = "test_task"
    task.plan = None
    task.initial_prompt = "test prompt"
    task.workspace = Mock()
    task.workspace.get_path.return_value = "dummy/path/plan.json"
    return task


@pytest.fixture
def mock_agents():
    return {
        "planner_agent": Mock(spec=Agent),
        "execution_agent": Mock(spec=Agent),
    }


@pytest.fixture
def mock_team_config():
    return TeamConfig(
        name="test_team",
        agents=[
            AgentConfig(name="planner_agent", brain=BrainConfig(model="test_model")),
            AgentConfig(name="execution_agent", brain=BrainConfig(model="test_model")),
        ],
        orchestration=OrchestrationConfig(
            planner=PlannerConfig(agent="planner_agent")
        )
    )


@pytest.fixture
def orchestrator(mock_team_config, mock_agents):
    message_queue = Mock()
    tool_manager = Mock()
    
    # We have to patch the agents into the orchestrator instance
    # because the real agents are created inside TaskExecutor
    orc = Orchestrator(
        team_config=mock_team_config,
        message_queue=message_queue,
        tool_manager=tool_manager,
        agents=mock_agents,
    )
    return orc


@pytest.mark.asyncio
async def test_run_generates_plan_if_none_exists(orchestrator, mock_task, mock_agents):
    # Arrange
    generated_plan = Plan(phases=[Phase(tasks=[PlanTask(description="do work")])])
    
    # Mock the behavior of _generate_plan to return a valid plan
    async def mock_generate_plan(task):
        return generated_plan

    # Patch the internal methods
    with patch.object(orchestrator, '_generate_plan', new=AsyncMock(side_effect=mock_generate_plan)) as mock_gen_plan, \
         patch.object(orchestrator, '_execute_plan', new=AsyncMock()) as mock_exec_plan:
        
        # Act
        async for _ in orchestrator.run(mock_task):
            pass

        # Assert
        mock_gen_plan.assert_called_once_with(mock_task)
        mock_exec_plan.assert_called_once()
        assert mock_task.plan is not None


@pytest.mark.asyncio
async def test_run_executes_existing_plan(orchestrator, mock_task):
    # Arrange
    mock_task.plan = Plan(phases=[Phase(tasks=[PlanTask(description="do work")])])
    
    with patch.object(orchestrator, '_generate_plan', new=AsyncMock()) as mock_gen_plan, \
         patch.object(orchestrator, '_execute_plan', new=AsyncMock()) as mock_exec_plan:

        # Act
        async for _ in orchestrator.run(mock_task):
            pass

        # Assert
        mock_gen_plan.assert_not_called()
        mock_exec_plan.assert_called_once_with(mock_task)



 