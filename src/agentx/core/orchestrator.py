from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Optional

from agentx.core.agent import Agent
from agentx.core.brain import Brain
from agentx.core.config import TeamConfig
from agentx.core.message import TaskStep, TextPart, MessageQueue, Message
from agentx.core.plan import Plan, PlanItem
# Event logging removed - not currently used
from agentx.tool.manager import ToolManager
from agentx.utils.logger import get_logger
from agentx.storage.workspace import WorkspaceStorage
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
        if self.team_config.orchestrator and self.team_config.orchestrator.brain_config:
            logger.info("Initializing routing brain...")
            return Brain.from_config(self.team_config.orchestrator.brain_config)
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
        # Use the orchestrator's brain for planning
        planner_brain = self.routing_brain or Brain.from_config(self.team_config.orchestrator.get_default_brain_config())
        
        logger.info("Generating plan using orchestrator's brain...")

        # Create a planning prompt
        available_agents = ", ".join(self.agents.keys())
        planning_prompt = f"""
        Create a detailed plan for the following task:
        
        Task: {task.initial_prompt}
        
        Available agents: {available_agents}
        
        Please create a plan with the following structure:
        - goal: Overall goal of the plan
        - tasks: Array of tasks, each with:
          - id: Unique identifier
          - name: Short descriptive name
          - goal: What this task should accomplish
          - agent: Which agent should handle this (optional)
          - status: "pending" (default)
          - dependencies: Array of task IDs this depends on (optional)
        
        Return only a valid JSON object matching this structure.
        """

        try:
            response = await planner_brain.run(planning_prompt)
            
            # Parse the response as JSON
            plan_data = json.loads(response.strip())
            
            # Validate and create the plan
            plan = Plan.model_validate(plan_data)
            self._save_plan(plan, task.workspace)
            logger.info(f"Plan generated and saved for task {task.task_id}")
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plan JSON from brain response: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to generate plan: {e}")
            return None


    async def _execute_plan(self, task: "Task") -> AsyncGenerator[Message, None]:
        while next_task_to_run := self._get_next_task(task.plan):
            next_task_to_run.status = "in_progress"
            
            yield TaskStep(
                agent_name="orchestrator",
                parts=[TextPart(text=f"Starting task: {next_task_to_run.name}")]
            )

            agent_name = next_task_to_run.agent or await self._decide_agent_for_task(next_task_to_run, task)
            agent = self.agents.get(agent_name)

            if not agent:
                error_message = f"Agent '{agent_name}' not found for task '{next_task_to_run.name}'"
                yield TaskStep(
                    agent_name="orchestrator",
                    parts=[TextPart(text=error_message)]
                )
                next_task_to_run.status = "failed"
                continue

            # Build conversation messages for the agent
            messages = [{"role": "user", "content": next_task_to_run.goal}]
            
            # Generate response using agent's interface
            response_content = await agent.generate_response(
                messages=messages,
                orchestrator=self
            )
            
            # Create TaskStep from agent response  
            yield TaskStep(
                agent_name=agent_name,
                parts=[TextPart(text=response_content)]
            )

            next_task_to_run.status = "completed"
            self._save_plan(task.plan, task.workspace)

        yield Message.system_message(content="Plan execution complete.", task_id=task.task_id)


    def _get_next_task(self, plan: Plan) -> Optional[PlanItem]:
        """
        Find the next actionable task in the plan.
        A task is actionable if:
        1. Its status is 'pending'
        2. All of its dependencies have status 'completed'
        """
        for task in plan.tasks:
            if task.status == "pending":
                # Check if all dependencies are completed
                if self._are_dependencies_satisfied(task, plan):
                    return task
        return None
    
    def _are_dependencies_satisfied(self, task: PlanItem, plan: Plan) -> bool:
        """Check if all dependencies for a task are completed."""
        if not task.dependencies:
            return True
        
        # Create a lookup map for task statuses
        task_statuses = {t.id: t.status for t in plan.tasks}
        
        # Check that all dependencies are completed
        for dep_id in task.dependencies:
            if dep_id not in task_statuses:
                logger.warning(f"Task {task.id} depends on unknown task {dep_id}")
                return False
            if task_statuses[dep_id] != "completed":
                return False
        
        return True

    async def _decide_agent_for_task(self, plan_task: PlanItem, task: "Task") -> str:
        if not self.routing_brain:
            # Default to the first agent if no routing brain is available
            return next(iter(self.agents.keys()))
            
        prompt = f"""
        Given the following task:
        Name: {plan_task.name}
        Goal: {plan_task.goal}
        
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

    def _save_plan(self, plan: Plan, workspace: WorkspaceStorage):
        plan_path = workspace.get_workspace_path() / "plan.json"
        try:
            with open(plan_path, "w", encoding="utf-8") as f:
                f.write(plan.model_dump_json(indent=2))
            logger.info(f"Plan progress saved to {plan_path}")
        except Exception as e:
            logger.error(f"Failed to save plan: {e}")
