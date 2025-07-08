from __future__ import annotations
import json
from typing import TYPE_CHECKING, Dict, Optional

from agentx.core.agent import Agent
from agentx.core.brain import Brain
from agentx.core.config import TeamConfig
from agentx.core.message import MessageQueue
from agentx.core.plan import Plan, PlanItem
from agentx.tool.manager import ToolManager
from agentx.utils.logger import get_logger

if TYPE_CHECKING:
    from agentx.core.task import Task

logger = get_logger(__name__)


class Orchestrator:
    """
    The central coordinator of the system. It manages task state, creates execution plans,
    and routes work to specialist agents. It makes strategic decisions about workflow
    while delegating tactical execution to agents.
    """

    def __init__(
        self,
        team_config: TeamConfig,
        message_queue: MessageQueue,
        tool_manager: ToolManager,
        agents: Dict[str, Agent],
    ):
        self.team_config = team_config
        self.message_queue = message_queue
        self.tool_manager = tool_manager
        self.agents = agents
        self.brain: Brain = self._initialize_brain()
        self.plan: Optional[Plan] = None

    def _initialize_brain(self) -> Brain:
        """Initialize brain with provided config or default configuration."""
        # Use provided brain_config if available
        if self.team_config.orchestrator and self.team_config.orchestrator.brain_config:
            logger.info("Initializing orchestrator brain with provided configuration...")
            return Brain.from_config(self.team_config.orchestrator.brain_config)

        # Fall back to default brain config
        logger.info("Initializing orchestrator brain with default configuration...")
        if self.team_config.orchestrator:
            default_config = self.team_config.orchestrator.get_default_brain_config()
        else:
            # Create minimal default config if no orchestrator config at all
            from agentx.core.config import BrainConfig
            default_config = BrainConfig(
                provider="deepseek",
                model="deepseek-chat",
                temperature=0.3,
                max_tokens=2000,
                timeout=120
            )
        return Brain.from_config(default_config)



    async def step(self, messages: list[dict], task: "Task") -> str:
        """
        Execute one step of the plan-driven orchestration loop.

        This implements the 8-step loop described in the design docs:
        1. Initialize and Generate Plan (If Needed)
        2. Identify Next Actionable Task
        3. Select Agent (and Route If Needed)
        4. Prepare Task Briefing
        5. Dispatch and Monitor
        6. Process Completion Signal
        7. Persist State
        8. Continue or Terminate
        """
        # Step 1: Initialize and Generate Plan (If Needed)
        if not self.plan:
            await self._initialize_plan(messages, task)

        # Step 8: Check if plan is complete
        if self.plan.is_complete():
            logger.info("All tasks in plan completed")
            return "Task completed successfully. All plan items have been finished."

        # Step 2: Identify Next Actionable Task
        next_task = self.plan.get_next_actionable_task()
        if not next_task:
            if self.plan.has_failed_tasks():
                return "Task execution halted due to failed tasks."
            else:
                return "No actionable tasks available. Waiting for dependencies to complete."

        # Step 3: Select Agent (and Route If Needed)
        agent_name = await self._select_agent_for_task(next_task)
        agent = self.agents[agent_name]

        # Step 4: Prepare Task Briefing
        task_briefing = self._prepare_task_briefing(next_task, messages, task)

        # Step 5: Dispatch and Monitor
        logger.info(f"Dispatching task '{next_task.name}' to agent '{agent_name}'")
        self.plan.update_task_status(next_task.id, "in_progress")

        try:
            # Execute the specific micro-task
            response = await agent.generate_response(
                messages=task_briefing,
                orchestrator=self
            )

            # Step 6: Process Completion Signal - CHECK ACTUAL SUCCESS/FAILURE
            task_success = await self._evaluate_task_success(response, next_task)

            if task_success:
                self.plan.update_task_status(next_task.id, "completed")
                logger.info(f"Task '{next_task.name}' completed successfully")
                await self._persist_plan(task)
                return f"Completed task: {next_task.name}\n\n{response}"
            else:
                # Task failed - apply failure policy
                logger.error(f"Task '{next_task.name}' failed - agent response indicates failure")
                self.plan.update_task_status(next_task.id, "failed")

                # Apply failure policy
                if next_task.on_failure == "halt":
                    return f"Task execution halted due to failure in '{next_task.name}': Agent could not complete the task successfully"
                elif next_task.on_failure == "escalate_to_user":
                    return f"Task '{next_task.name}' failed and requires user intervention: Agent could not complete the task successfully"
                else:  # proceed
                    return f"Task '{next_task.name}' failed but continuing with next tasks: Agent could not complete the task successfully"

        except Exception as e:
            # Step 6: Process Failure Signal
            logger.error(f"Task '{next_task.name}' failed: {e}")
            self.plan.update_task_status(next_task.id, "failed")

            # Apply failure policy
            if next_task.on_failure == "halt":
                return f"Task execution halted due to failure in '{next_task.name}': {e}"
            elif next_task.on_failure == "escalate_to_user":
                return f"Task '{next_task.name}' failed and requires user intervention: {e}"
            else:  # proceed
                return f"Task '{next_task.name}' failed but continuing with next tasks: {e}"

    async def _initialize_plan(self, messages: list[dict], task: "Task") -> None:
        """Initialize and generate plan if needed (Step 1)."""
        # Try to load existing plan through Task
        existing_plan = await task.load_plan()
        if existing_plan:
            self.plan = existing_plan
            return

        # Generate new plan using Brain
        logger.info("Generating new plan...")
        self.plan = await self._generate_plan(messages, task)
        # Use Task's plan management and persist the plan
        task.update_plan(self.plan)
        await task._persist_plan()

    async def _generate_plan(self, messages: list[dict], task: "Task") -> Plan:
        """Generate a plan using the Brain."""
        plan_prompt = f"""
Create a detailed execution plan to achieve this goal: {task.initial_prompt}

Available agents: {', '.join(self.agents.keys())}

Break down the goal into specific, actionable tasks. Each task should:
- Have a clear, measurable goal
- Be assignable to one of the available agents
- Have clear dependencies if needed

Respond with a JSON structure like this:
{{
    "goal": "The main objective",
    "tasks": [
        {{
            "id": "task_1",
            "name": "Short task name",
            "goal": "Specific, measurable goal for this task",
            "agent": "agent_name or null for auto-routing",
            "dependencies": [],
            "status": "pending"
        }}
    ]
}}
"""

        response = await self.brain.generate_response(
            messages=[{"role": "user", "content": plan_prompt}],
            json_mode=True
        )

        # Parse the JSON response
        if not response.content:
            raise ValueError("Empty response from Brain during plan generation")

        try:
            plan_data = json.loads(response.content)
            return Plan(**plan_data)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to parse plan from Brain response: {e}")

    async def _select_agent_for_task(self, task_item: PlanItem) -> str:
        """Select agent for a specific task (Step 3)."""
        # If task has specific agent assigned, use it
        if task_item.agent and task_item.agent in self.agents:
            return task_item.agent

        # For single-agent teams, use that agent
        if len(self.agents) == 1:
            return next(iter(self.agents.keys()))

        # Use brain for multi-agent teams
        return await self._route_task(task_item)

    async def _route_task(self, task_item: PlanItem) -> str:
        """Use brain to select best agent for a task."""
        agent_list = ", ".join(self.agents.keys())
        routing_prompt = f"""
Given this specific task and the available agents, which agent is best suited?

Task: {task_item.name}
Goal: {task_item.goal}

Available agents: {agent_list}

Respond with only the agent name.
"""

        response = await self.brain.generate_response(
            messages=[{"role": "user", "content": routing_prompt}]
        )

        agent_name = response.content.strip()
        if agent_name in self.agents:
            return agent_name

        # Brain gave invalid response - this is an error that should be fixed
        available_agents = list(self.agents.keys())
        raise ValueError(f"Brain returned invalid agent '{agent_name}'. Available agents: {available_agents}")

    def _prepare_task_briefing(self, task_item: PlanItem, messages: list[dict], task: "Task") -> list[dict]:
        """Prepare isolated task briefing for the agent (Step 4)."""
        # Create a focused briefing for this specific micro-task
        briefing = [
            {
                "role": "system",
                "content": f"""You are being assigned a specific micro-task as part of a larger plan.

TASK: {task_item.name}
GOAL: {task_item.goal}

Your job is to complete this specific task. You have access to tools and the workspace.
Focus only on this task - do not try to complete the entire project.

Original user request: {task.initial_prompt}
"""
            }
        ]

        # Add the latest user message for context
        if messages:
            briefing.append({
                "role": "user",
                "content": f"Please complete this task: {task_item.goal}"
            })

        return briefing

    async def _persist_plan(self, task: "Task") -> None:
        """Persist the plan via Task's plan management (Step 7)."""
        if not self.plan:
            return

        # Delegate to Task's plan management instead of direct file operations
        task.update_plan(self.plan)

    async def _evaluate_task_success(self, response: str, task_item: PlanItem) -> bool:
        """Evaluate if a task was actually completed successfully by analyzing the response."""
        # Look for failure indicators in the response
        failure_indicators = [
            "connection refused",
            "max retries exceeded",
            "failed to establish",
            "tool failed",
            "error occurred",
            "could not",
            "unable to",
            "no results found",
            "search failed",
            "api error"
        ]

        response_lower = response.lower()

        # Check for explicit failure indicators
        for indicator in failure_indicators:
            if indicator in response_lower:
                logger.warning(f"Task failure detected: '{indicator}' found in response")
                return False

        # For research tasks, check if actual content was generated
        if "research" in task_item.name.lower():
            if len(response.strip()) < 100:  # Very short response likely indicates failure
                logger.warning(f"Research task appears to have failed: response too short ({len(response)} chars)")
                return False

            # Check if response contains only generic/placeholder content
            generic_phrases = [
                "explore the latest",
                "discover the",
                "learn how",
                "understand the modern",
                "it seems there was an issue"
            ]

            for phrase in generic_phrases:
                if phrase in response_lower:
                    logger.warning(f"Research task appears to have failed: generic content detected")
                    return False

        # If no failure indicators found, assume success
        return True
