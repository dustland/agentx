from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Optional

from agentx.core.agent import Agent
from agentx.core.brain import Brain
from agentx.core.config import TeamConfig
from agentx.core.message import Message, MessageQueue, UserMessage
from agentx.core.plan import Plan, Task as PlanTask, ToolCall, ToolResult
from agentx.event.bus import log_event
from agentx.tool.manager import ToolManager
from agentx.utils.logger import get_logger
from agentx.storage.workspace import Workspace
import json

if TYPE_CHECKING:
    from agentx.core.task import Task

logger = get_logger(__name__)


class Orchestrator:
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
        self.routing_brain: Optional[Brain] = self._initialize_routing_brain()

    def _initialize_routing_brain(self) -> Optional[Brain]:
        if self.team_config.orchestration and self.team_config.orchestration.routing_brain:
            logger.info("Initializing routing brain...")
            return Brain.from_config(self.team_config.orchestration.routing_brain)
        logger.info("No routing brain configured. Using heuristic routing.")
        return None

    async def run(self, task: "Task") -> AsyncGenerator[Message, None]:
        if task.plan:
            logger.info(f"Task {task.task_id} has an existing plan. Executing plan.")
            async for message in self._execute_plan(task):
                yield message
        else:
            logger.info(f"Task {task.task_id} has no plan. Generating a new one.")
            new_plan = await self._generate_plan(task)
            if new_plan:
                task.plan = new_plan
                async for message in self._execute_plan(task):
                    yield message
            else:
                yield Message.system_message(
                    content="Failed to generate a plan. Cannot proceed.",
                    task_id=task.task_id,
                )

    async def _generate_plan(self, task: "Task") -> Optional[Plan]:
        planner_config = self.team_config.orchestration.planner
        planner_agent = self.agents.get(planner_config.agent)

        if not planner_agent:
            logger.error(f"Planner agent '{planner_config.agent}' not found.")
            return None

        logger.info(f"Generating plan with agent: {planner_agent.name}")

        response_message = await planner_agent.run(task.initial_prompt)

        # The planner agent is expected to call a tool that creates the plan.
        if not response_message.tool_calls:
            logger.error("Planner agent did not request a tool call to create the plan.")
            return None
        
        # Assume the first tool call is the plan creation
        tool_call = response_message.tool_calls[0]
        
        # This is a placeholder for a more robust tool execution flow
        # In a real scenario, a "CreatePlan" tool would be invoked.
        # For now, we simulate this by parsing the arguments directly.
        try:
            plan_data = tool_call.args
            if isinstance(plan_data, str):
                plan_data = json.loads(plan_data)
            
            plan = Plan.model_validate(plan_data)
            self._save_plan(plan, task.workspace)
            logger.info(f"Plan generated and saved for task {task.task_id}")
            return plan
        except Exception as e:
            logger.error(f"Failed to parse or validate the plan from planner agent: {e}")
            return None


    async def _execute_plan(self, task: "Task") -> AsyncGenerator[Message, None]:
        while next_task_to_run := self._get_next_task(task.plan):
            next_task_to_run.status = "in_progress"
            
            yield Message.system_message(
                content=f"Starting task: {next_task_to_run.description}",
                task_id=task.task_id,
                metadata={"plan_task_id": next_task_to_run.id}
            )

            agent_name = next_task_to_run.agent or await self._decide_agent_for_task(next_task_to_run, task)
            agent = self.agents.get(agent_name)

            if not agent:
                error_message = f"Agent '{agent_name}' not found for task '{next_task_to_run.description}'"
                yield Message.system_message(content=error_message, task_id=task.task_id)
                next_task_to_run.status = "failed"
                continue

            response_message = await agent.run(next_task_to_run.description)
            yield response_message

            next_task_to_run.status = "completed"
            self._save_plan(task.plan, task.workspace)

        yield Message.system_message(content="Plan execution complete.", task_id=task.task_id)


    def _get_next_task(self, plan: Plan) -> Optional[PlanTask]:
        for phase in plan.phases:
            for task in phase.tasks:
                if task.status == "pending":
                    return task
        return None

    async def _decide_agent_for_task(self, plan_task: PlanTask, task: "Task") -> str:
        if not self.routing_brain:
            # Default to the first agent if no routing brain is available
            return next(iter(self.agents.keys()))
            
        prompt = f"""
        Given the following task:
        Description: {plan_task.description}
        
        And the following available agents:
        {list(self.agents.keys())}
        
        Which agent is best suited to perform this task?
        Respond with only the name of the agent.
        """
        response = await self.routing_brain.run(prompt)
        
        agent_name = response.strip()
        if agent_name in self.agents:
            return agent_name
            
        return next(iter(self.agents.keys())) # Fallback

    def _save_plan(self, plan: Plan, workspace: Workspace):
        plan_path = workspace.get_path("plan.json")
        try:
            with open(plan_path, "w", encoding="utf-8") as f:
                f.write(plan.model_dump_json(indent=2))
            logger.info(f"Plan progress saved to {plan_path}")
        except Exception as e:
            logger.error(f"Failed to save plan: {e}")
