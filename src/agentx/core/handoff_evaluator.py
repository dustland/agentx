"""
Handoff evaluation system for XAgent orchestration.

This module provides intelligent handoff evaluation without requiring agents
to explicitly call handoff tools. XAgent evaluates conditions and makes
routing decisions centrally.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

from agentx.core.config import Handoff
from agentx.core.agent import Agent

logger = logging.getLogger(__name__)


class HandoffContext(BaseModel):
    """Context for evaluating handoff conditions."""
    current_agent: str
    task_result: str
    task_goal: str
    conversation_history: List[Dict[str, Any]]
    workspace_files: List[str]


class HandoffEvaluator:
    """Evaluates handoff conditions and determines next agent."""

    def __init__(self, handoffs: List[Handoff], agents: Dict[str, Agent]):
        self.handoffs = handoffs
        self.agents = agents
        self._build_handoff_map()

    def _build_handoff_map(self):
        """Build a map of agent -> possible handoffs for quick lookup."""
        self.handoff_map = {}
        for handoff in self.handoffs:
            if handoff.from_agent not in self.handoff_map:
                self.handoff_map[handoff.from_agent] = []
            self.handoff_map[handoff.from_agent].append(handoff)

        # Sort by priority
        for agent_handoffs in self.handoff_map.values():
            agent_handoffs.sort(key=lambda h: h.priority, reverse=True)

    async def evaluate_handoffs(self, context: HandoffContext) -> Optional[str]:
        """
        Evaluate if a handoff should occur based on current context.
        Returns the target agent name if handoff should occur, None otherwise.
        """
        # Get possible handoffs for current agent
        possible_handoffs = self.handoff_map.get(context.current_agent, [])

        if not possible_handoffs:
            return None

        # Evaluate each handoff condition
        for handoff in possible_handoffs:
            if await self._evaluate_condition(handoff, context):
                logger.info(
                    f"Handoff triggered: {handoff.from_agent} -> {handoff.to_agent} "
                    f"(condition: {handoff.condition})"
                )
                return handoff.to_agent

        return None

    async def _evaluate_condition(self, handoff: Handoff, context: HandoffContext) -> bool:
        """
        Evaluate a single handoff condition using LLM.

        This uses the orchestrator's brain to evaluate if the natural language
        condition is met based on the current context.
        """
        # Build evaluation prompt
        evaluation_prompt = f"""
You are evaluating whether a handoff condition has been met.

HANDOFF RULE:
- From: {handoff.from_agent}
- To: {handoff.to_agent}
- Condition: {handoff.condition}

CURRENT CONTEXT:
- Current Agent: {context.current_agent}
- Task Goal: {context.task_goal}
- Task Result Summary: {context.task_result[:500]}...
- Workspace Files: {', '.join(context.workspace_files)}

Based on the task result and context, has the condition "{handoff.condition}" been met?

Respond with only "YES" or "NO".
"""

        # Note: This would use the XAgent's brain for evaluation
        # For now, we'll return a simplified check
        # In practice, this would call: self.brain.generate_response(...)

        # Simplified condition checking for common patterns
        condition_lower = handoff.condition.lower()
        result_lower = context.task_result.lower()

        # Check for exact pattern matches
        if "work is ready for" in condition_lower:
            # Extract the target agent from condition
            parts = condition_lower.split("ready for")
            if len(parts) > 1:
                target = parts[1].strip()
                # Check if the result mentions readiness for target
                if (f"ready for {target}" in result_lower or
                    f"ready to be {target}" in result_lower or
                    f"needs {target}" in result_lower or
                    f"now {target} can" in result_lower or
                    ("file" in result_lower and "created" in result_lower) or
                    ("completed" in result_lower and target in result_lower)):
                    return True

        # Check if the condition text appears in the result
        # This is a simple substring match for the demo
        if condition_lower in result_lower:
            return True

        # Check for common condition patterns
        if "complete" in condition_lower and "ready for" in condition_lower:
            # Check if "ready for" appears with the target agent name
            target_agent = handoff.to_agent.lower()
            if f"ready for {target_agent}" in result_lower:
                return True
            return "completed" in result_lower or "finished" in result_lower

        if "failed" in condition_lower or "error" in condition_lower:
            return "error" in result_lower or "failed" in result_lower

        # Default to false if we can't evaluate
        return False

    def get_fallback_agent(self, current_agent: str) -> Optional[str]:
        """Get a fallback agent if no conditions are met but work continues."""
        # Could implement round-robin or other strategies
        return None
