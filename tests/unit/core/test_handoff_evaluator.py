"""
Tests for the handoff evaluation system.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List

from vibex.core.handoff_evaluator import HandoffEvaluator, HandoffContext
from vibex.core.config import Handoff
from vibex.core.agent import Agent


class TestHandoffEvaluator:
    """Test the HandoffEvaluator class."""

    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing."""
        agents = {
            "writer": Mock(spec=Agent),
            "reviewer": Mock(spec=Agent),
            "editor": Mock(spec=Agent)
        }
        for name, agent in agents.items():
            agent.name = name
        return agents

    @pytest.fixture
    def sample_handoffs(self):
        """Create sample handoff configurations."""
        return [
            Handoff(
                from_agent="writer",
                to_agent="reviewer",
                condition="draft is complete and ready for review",
                priority=1
            ),
            Handoff(
                from_agent="reviewer",
                to_agent="editor",
                condition="review is complete with suggestions",
                priority=1
            ),
            Handoff(
                from_agent="writer",
                to_agent="editor",
                condition="urgent edit needed",
                priority=2  # Higher priority
            )
        ]

    def test_handoff_map_building(self, sample_handoffs, mock_agents):
        """Test that handoff map is built correctly with priority sorting."""
        evaluator = HandoffEvaluator(sample_handoffs, mock_agents)

        # Check that map is built
        assert "writer" in evaluator.handoff_map
        assert "reviewer" in evaluator.handoff_map
        assert "editor" not in evaluator.handoff_map  # No outgoing handoffs

        # Check priority sorting (higher priority first)
        writer_handoffs = evaluator.handoff_map["writer"]
        assert len(writer_handoffs) == 2
        assert writer_handoffs[0].priority == 2  # urgent edit
        assert writer_handoffs[1].priority == 1  # normal review

    @pytest.mark.asyncio
    async def test_evaluate_handoffs_no_match(self, sample_handoffs, mock_agents):
        """Test when no handoff conditions are met."""
        evaluator = HandoffEvaluator(sample_handoffs, mock_agents)

        context = HandoffContext(
            current_agent="writer",
            task_result="Still working on the draft...",
            task_goal="Write article",
            conversation_history=[],
            taskspace_files=[]
        )

        result = await evaluator.evaluate_handoffs(context)
        assert result is None

    @pytest.mark.asyncio
    async def test_evaluate_handoffs_match_complete(self, sample_handoffs, mock_agents):
        """Test when 'complete' condition is met."""
        evaluator = HandoffEvaluator(sample_handoffs, mock_agents)

        context = HandoffContext(
            current_agent="writer",
            task_result="The draft has been completed and saved to draft.md",
            task_goal="Write article",
            conversation_history=[],
            taskspace_files=["draft.md"]
        )

        result = await evaluator.evaluate_handoffs(context)
        # Should match "draft is complete and ready for review"
        assert result == "reviewer"

    @pytest.mark.asyncio
    async def test_evaluate_handoffs_priority_order(self, sample_handoffs, mock_agents):
        """Test that higher priority handoffs are evaluated first."""
        evaluator = HandoffEvaluator(sample_handoffs, mock_agents)

        # Create context that could match both conditions
        context = HandoffContext(
            current_agent="writer",
            task_result="Urgent: Draft completed with critical errors that need immediate editing",
            task_goal="Write article",
            conversation_history=[],
            taskspace_files=["draft.md"]
        )

        # Mock the evaluation to make both conditions true
        with patch.object(evaluator, '_evaluate_condition', new_callable=AsyncMock) as mock_eval:
            mock_eval.return_value = True  # All conditions match

            result = await evaluator.evaluate_handoffs(context)

            # Should return editor (higher priority) not reviewer
            assert result == "editor"

            # Check that it evaluated the urgent condition first
            first_call = mock_eval.call_args_list[0]
            assert first_call[0][0].priority == 2

    @pytest.mark.asyncio
    async def test_evaluate_condition_complete_pattern(self, sample_handoffs, mock_agents):
        """Test condition evaluation for 'complete' patterns."""
        evaluator = HandoffEvaluator(sample_handoffs, mock_agents)
        handoff = sample_handoffs[0]  # "draft is complete and ready for review"

        # Test matching context
        context_match = HandoffContext(
            current_agent="writer",
            task_result="Task completed successfully",
            task_goal="Write article",
            conversation_history=[],
            taskspace_files=[]
        )

        result = await evaluator._evaluate_condition(handoff, context_match)
        assert result is True

        # Test non-matching context
        context_no_match = HandoffContext(
            current_agent="writer",
            task_result="Still in progress",
            task_goal="Write article",
            conversation_history=[],
            taskspace_files=[]
        )

        result = await evaluator._evaluate_condition(handoff, context_no_match)
        assert result is False

    @pytest.mark.asyncio
    async def test_evaluate_condition_error_pattern(self, mock_agents):
        """Test condition evaluation for error/failure patterns."""
        handoff = Handoff(
            from_agent="writer",
            to_agent="reviewer",
            condition="task failed or encountered error",
            priority=1
        )
        evaluator = HandoffEvaluator([handoff], mock_agents)

        # Test error context
        context_error = HandoffContext(
            current_agent="writer",
            task_result="Error: Unable to complete task due to missing data",
            task_goal="Write article",
            conversation_history=[],
            taskspace_files=[]
        )

        result = await evaluator._evaluate_condition(handoff, context_error)
        assert result is True

        # Test failure context
        context_failed = HandoffContext(
            current_agent="writer",
            task_result="Task failed: Invalid input format",
            task_goal="Write article",
            conversation_history=[],
            taskspace_files=[]
        )

        result = await evaluator._evaluate_condition(handoff, context_failed)
        assert result is True

    def test_get_fallback_agent(self, sample_handoffs, mock_agents):
        """Test fallback agent logic."""
        evaluator = HandoffEvaluator(sample_handoffs, mock_agents)

        # Currently returns None - could be extended
        result = evaluator.get_fallback_agent("writer")
        assert result is None

    @pytest.mark.asyncio
    async def test_no_handoffs_configured(self, mock_agents):
        """Test evaluator with no handoffs configured."""
        evaluator = HandoffEvaluator([], mock_agents)

        context = HandoffContext(
            current_agent="writer",
            task_result="Task completed",
            task_goal="Write article",
            conversation_history=[],
            taskspace_files=[]
        )

        result = await evaluator.evaluate_handoffs(context)
        assert result is None
        assert evaluator.handoff_map == {}


class TestHandoffIntegrationWithXAgent:
    """Test handoff integration with XAgent."""

    @pytest.mark.asyncio
    async def test_xagent_handoff_execution(self):
        """Test that XAgent properly executes handoffs after task completion."""
        # This would require a more complete XAgent mock
        # Placeholder for integration test
        pass

    @pytest.mark.asyncio
    async def test_dynamic_plan_modification(self):
        """Test that XAgent adds handoff tasks to the plan dynamically."""
        # This would test the plan modification logic
        # Placeholder for integration test
        pass
