"""
Integration tests for parallel task execution.

This test verifies that the parallel execution system correctly identifies
and executes multiple independent tasks simultaneously.
"""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch

from agentx.core.plan import Plan, PlanItem
from agentx.core.xagent import XAgent
from agentx.core.config import TeamConfig, AgentConfig, BrainConfig
from agentx.storage.workspace import WorkspaceStorage


class TestParallelExecution:
    """Test parallel task execution functionality."""

    @pytest.fixture
    async def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        workspace = WorkspaceStorage(
            task_id="test_parallel_execution",
            workspace_path=str(temp_dir)
        )
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_team_config(self):
        """Create a mock team configuration for testing."""
        return TeamConfig(
            name="test_team",
            description="Test team for parallel execution",
            agents=[
                AgentConfig(
                    name="researcher",
                    role="specialist", 
                    prompt_file="researcher.md",
                    description="Research specialist",
                    brain_config=BrainConfig(
                        provider="deepseek",
                        model="deepseek/deepseek-chat"
                    ),
                    tools=["research_topic"]
                ),
                AgentConfig(
                    name="writer",
                    role="specialist",
                    prompt_file="writer.md", 
                    description="Writing specialist",
                    brain_config=BrainConfig(
                        provider="deepseek",
                        model="deepseek/deepseek-chat"
                    ),
                    tools=["write_file"]
                )
            ]
        )

    @pytest.mark.asyncio
    async def test_get_all_actionable_tasks(self):
        """Test Plan.get_all_actionable_tasks method."""
        plan = Plan(
            goal="Test parallel execution",
            tasks=[
                PlanItem(
                    id="task1",
                    name="Research Flask",
                    goal="Research Flask framework",
                    agent="researcher",
                    dependencies=[],
                    status="pending"
                ),
                PlanItem(
                    id="task2", 
                    name="Research FastAPI",
                    goal="Research FastAPI framework",
                    agent="researcher",
                    dependencies=[],
                    status="pending"
                ),
                PlanItem(
                    id="task3",
                    name="Write introduction",
                    goal="Write document introduction", 
                    agent="writer",
                    dependencies=["task1", "task2"],  # Depends on research tasks
                    status="pending"
                ),
                PlanItem(
                    id="task4",
                    name="Research Django",
                    goal="Research Django framework",
                    agent="researcher", 
                    dependencies=[],
                    status="pending"
                )
            ]
        )

        # Test: All independent tasks should be actionable
        actionable_tasks = plan.get_all_actionable_tasks()
        actionable_ids = [task.id for task in actionable_tasks]
        
        # task1, task2, and task4 should be actionable (no dependencies)
        # task3 should NOT be actionable (depends on task1 and task2)
        assert "task1" in actionable_ids
        assert "task2" in actionable_ids  
        assert "task4" in actionable_ids
        assert "task3" not in actionable_ids
        assert len(actionable_tasks) == 3

        # Test: Limit max tasks
        limited_tasks = plan.get_all_actionable_tasks(max_tasks=2)
        assert len(limited_tasks) == 2

        # Test: After completing dependencies
        plan.get_task_by_id("task1").status = "completed"
        plan.get_task_by_id("task2").status = "completed"
        
        actionable_tasks = plan.get_all_actionable_tasks()
        actionable_ids = [task.id for task in actionable_tasks]
        
        # Now task3 should be actionable, plus task4
        assert "task3" in actionable_ids
        assert "task4" in actionable_ids
        assert len(actionable_tasks) == 2

    @pytest.mark.asyncio
    async def test_parallel_execution_logic(self, temp_workspace, mock_team_config):
        """Test the parallel execution logic without actual LLM calls."""
        
        # Create XAgent with mocked components
        with patch('agentx.core.xagent.load_team_config', return_value=mock_team_config):
            with patch('agentx.core.agent.Agent') as MockAgent:
                # Setup mock agents
                mock_researcher = AsyncMock()
                mock_writer = AsyncMock()
                
                mock_researcher.generate_response = AsyncMock(return_value=AsyncMock(content="Research completed"))
                mock_writer.generate_response = AsyncMock(return_value=AsyncMock(content="Writing completed"))
                
                MockAgent.side_effect = [mock_researcher, mock_writer]
                
                # Initialize XAgent
                xagent = XAgent(
                    task_id="test_parallel",
                    workspace=temp_workspace,
                    team_config=mock_team_config
                )
                
                # Create a plan with parallel tasks
                xagent.current_plan = Plan(
                    goal="Test parallel research",
                    tasks=[
                        PlanItem(
                            id="research_flask",
                            name="Research Flask",
                            goal="Research Flask framework",
                            agent="researcher",
                            dependencies=[],
                            status="pending"
                        ),
                        PlanItem(
                            id="research_fastapi", 
                            name="Research FastAPI",
                            goal="Research FastAPI framework",
                            agent="researcher",
                            dependencies=[],
                            status="pending"
                        ),
                        PlanItem(
                            id="research_django",
                            name="Research Django", 
                            goal="Research Django framework",
                            agent="researcher",
                            dependencies=[],
                            status="pending"
                        )
                    ]
                )
                
                # Set up specialist agents mock
                xagent.specialist_agents = {
                    "researcher": mock_researcher,
                    "writer": mock_writer
                }
                
                # Mock the _persist_plan method
                xagent._persist_plan = AsyncMock()
                
                # Test parallel execution
                result = await xagent.step_parallel(max_concurrent=3)
                
                # Verify results
                assert "✅" in result  # Should have success messages
                assert "Research Flask" in result
                assert "Research FastAPI" in result  
                assert "Research Django" in result
                
                # Verify all tasks were marked as completed
                for task in xagent.current_plan.tasks:
                    assert task.status == "completed"
                
                # Verify agents were called
                assert mock_researcher.generate_response.call_count == 3

    @pytest.mark.asyncio
    async def test_fallback_to_sequential(self, temp_workspace, mock_team_config):
        """Test that parallel execution falls back to sequential when only one task available."""
        
        with patch('agentx.core.xagent.load_team_config', return_value=mock_team_config):
            with patch('agentx.core.agent.Agent') as MockAgent:
                mock_researcher = AsyncMock()
                mock_researcher.generate_response = AsyncMock(return_value=AsyncMock(content="Research completed"))
                MockAgent.return_value = mock_researcher
                
                xagent = XAgent(
                    task_id="test_sequential_fallback",
                    workspace=temp_workspace,
                    team_config=mock_team_config
                )
                
                # Create a plan with only one actionable task
                xagent.current_plan = Plan(
                    goal="Test sequential fallback",
                    tasks=[
                        PlanItem(
                            id="single_task",
                            name="Single research task",
                            goal="Research one topic",
                            agent="researcher",
                            dependencies=[],
                            status="pending"
                        )
                    ]
                )
                
                xagent.specialist_agents = {"researcher": mock_researcher}
                xagent._persist_plan = AsyncMock()
                
                # Mock _execute_single_step to verify it's called
                xagent._execute_single_step = AsyncMock(return_value="Sequential execution completed")
                
                result = await xagent.step_parallel(max_concurrent=3)
                
                # Should fall back to sequential execution
                assert result == "Sequential execution completed"
                xagent._execute_single_step.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling_in_parallel(self, temp_workspace, mock_team_config):
        """Test error handling during parallel execution."""
        
        with patch('agentx.core.xagent.load_team_config', return_value=mock_team_config):
            with patch('agentx.core.agent.Agent') as MockAgent:
                # Setup one successful and one failing agent
                mock_researcher = AsyncMock()
                
                # First call succeeds, second call fails
                mock_researcher.generate_response = AsyncMock(
                    side_effect=[
                        AsyncMock(content="Research completed"),
                        Exception("API error")
                    ]
                )
                
                MockAgent.return_value = mock_researcher
                
                xagent = XAgent(
                    task_id="test_error_handling", 
                    workspace=temp_workspace,
                    team_config=mock_team_config
                )
                
                # Create plan with tasks that have different failure policies
                xagent.current_plan = Plan(
                    goal="Test error handling",
                    tasks=[
                        PlanItem(
                            id="task_success",
                            name="Successful task",
                            goal="This should succeed",
                            agent="researcher",
                            dependencies=[],
                            status="pending",
                            on_failure="proceed"
                        ),
                        PlanItem(
                            id="task_failure",
                            name="Failing task", 
                            goal="This should fail",
                            agent="researcher",
                            dependencies=[],
                            status="pending",
                            on_failure="proceed"
                        )
                    ]
                )
                
                xagent.specialist_agents = {"researcher": mock_researcher}
                xagent._persist_plan = AsyncMock()
                
                result = await xagent.step_parallel(max_concurrent=2)
                
                # Should have both success and failure messages
                assert "✅ Successful task" in result
                assert "⚠️ Failing task" in result
                assert "API error" in result
                
                # Check final task statuses
                successful_task = xagent.current_plan.get_task_by_id("task_success")
                failed_task = xagent.current_plan.get_task_by_id("task_failure")
                
                assert successful_task.status == "completed"
                assert failed_task.status == "failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])