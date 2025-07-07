from __future__ import annotations
import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Optional

from agentx.core.agent import Agent
from agentx.core.brain import Brain
from agentx.core.config import TeamConfig
from agentx.core.message import TaskStep, TextPart, MessageQueue, Message
from agentx.core.plan import Plan, PlanItem, TaskStatus
from agentx.tool.manager import ToolManager
from agentx.utils.logger import get_logger
from agentx.utils.id import generate_short_id

if TYPE_CHECKING:
    from agentx.core.task import Task

logger = get_logger(__name__)


class Orchestrator:
    """
    The central process manager of the system. It executes the Plan with unwavering precision,
    operating as a state machine that moves the system from one task to the next according to
    the instructions in the Plan.
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
        self.routing_brain: Optional[Brain] = self._initialize_routing_brain()
        self.current_plan: Optional[Plan] = None

    def _initialize_routing_brain(self) -> Optional[Brain]:
        if self.team_config.orchestrator and self.team_config.orchestrator.brain_config:
            logger.info("Initializing routing brain...")
            return Brain.from_config(self.team_config.orchestrator.brain_config)
        logger.info("No routing brain configured. Using heuristic routing.")
        return None

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
        if not self.current_plan:
            await self._initialize_plan(messages, task)
        
        # Step 8: Check if plan is complete
        if self.current_plan.is_complete():
            logger.info("All tasks in plan completed")
            return "Task completed successfully. All plan items have been finished."
        
        # Step 2: Identify Next Actionable Task
        next_task = self.current_plan.get_next_actionable_task()
        if not next_task:
            if self.current_plan.has_failed_tasks():
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
        self.current_plan.update_task_status(next_task.id, "in_progress")
        
        try:
            # Execute the specific micro-task
            response = await agent.generate_response(
                messages=task_briefing,
                orchestrator=self
            )
            
            # Step 6: Process Completion Signal (assume success for now)
            self.current_plan.update_task_status(next_task.id, "completed")
            logger.info(f"Task '{next_task.name}' completed successfully")
            
            # Step 7: Persist State
            await self._persist_plan(task)
            
            return f"Completed task: {next_task.name}\n\n{response}"
            
        except Exception as e:
            # Step 6: Process Failure Signal
            logger.error(f"Task '{next_task.name}' failed: {e}")
            self.current_plan.update_task_status(next_task.id, "failed")
            
            # Apply failure policy
            if next_task.on_failure == "halt":
                return f"Task execution halted due to failure in '{next_task.name}': {e}"
            elif next_task.on_failure == "escalate_to_user":
                return f"Task '{next_task.name}' failed and requires user intervention: {e}"
            else:  # proceed
                return f"Task '{next_task.name}' failed but continuing with next tasks: {e}"

    async def _initialize_plan(self, messages: list[dict], task: "Task") -> None:
        """Initialize and generate plan if needed (Step 1)."""
        plan_file = task.workspace.get_workspace_path() / "plan.json"
        
        # Try to load existing plan
        if plan_file.exists():
            try:
                plan_data = json.loads(plan_file.read_text())
                self.current_plan = Plan(**plan_data)
                logger.info("Loaded existing plan from plan.json")
                return
            except Exception as e:
                logger.warning(f"Failed to load existing plan: {e}")
        
        # Generate new plan
        logger.info("Generating new plan...")
        self.current_plan = await self._generate_plan(messages, task)
        await self._persist_plan(task)

    async def _generate_plan(self, messages: list[dict], task: "Task") -> Plan:
        """Generate a plan using the Brain."""
        if not self.routing_brain:
            # Fallback: create a simple single-task plan
            return Plan(
                goal=task.initial_prompt,
                tasks=[
                    PlanItem(
                        id="main_task",
                        name="Complete main task",
                        goal=task.initial_prompt,
                        agent=None,  # Will be routed automatically
                        dependencies=[],
                        status="pending"
                    )
                ]
            )
        
        # Use Brain to generate structured plan
        plan_prompt = f"""
        Create a detailed plan to achieve this goal: {task.initial_prompt}
        
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
        
        try:
            response = await self.routing_brain.generate_response(
                messages=[{"role": "user", "content": plan_prompt}],
                json_mode=True
            )
            
            # Parse the JSON response
            if not response.content:
                raise ValueError("Empty response from Brain")
                
            plan_data = json.loads(response.content)
            return Plan(**plan_data)
            
        except Exception as e:
            logger.error(f"Failed to generate plan with Brain: {e}")
            # Fallback to simple plan
            return Plan(
                goal=task.initial_prompt,
                tasks=[
                    PlanItem(
                        id="main_task",
                        name="Complete main task",
                        goal=task.initial_prompt,
                        agent=None,
                        dependencies=[],
                        status="pending"
                    )
                ]
            )

    async def _select_agent_for_task(self, task_item: PlanItem) -> str:
        """Select agent for a specific task (Step 3)."""
        # If task has specific agent assigned, use it
        if task_item.agent and task_item.agent in self.agents:
            return task_item.agent
        
        # For single-agent teams, use that agent
        if len(self.agents) == 1:
            return next(iter(self.agents.keys()))
        
        # Use routing brain for multi-agent teams
        if self.routing_brain:
            return await self._route_task_with_brain(task_item)
        
        # Fallback: use first agent
        return next(iter(self.agents.keys()))

    async def _route_task_with_brain(self, task_item: PlanItem) -> str:
        """Use routing brain to select best agent for a task."""
        agent_list = ", ".join(self.agents.keys())
        routing_prompt = f"""
        Given this specific task and the available agents, which agent is best suited?
        
        Task: {task_item.name}
        Goal: {task_item.goal}
        
        Available agents: {agent_list}
        
        Respond with only the agent name.
        """
        
        try:
            response = await self.routing_brain.generate_response(
                messages=[{"role": "user", "content": routing_prompt}]
            )
            
            agent_name = response.content.strip()
            if agent_name in self.agents:
                return agent_name
        except Exception as e:
            logger.error(f"Failed to route task with brain: {e}")
        
        # Fallback to first agent
        return next(iter(self.agents.keys()))

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
            latest_message = messages[-1]
            briefing.append({
                "role": "user", 
                "content": f"Please complete this task: {task_item.goal}"
            })
        
        return briefing

    async def _persist_plan(self, task: "Task") -> None:
        """Persist the current plan to plan.json (Step 7)."""
        if not self.current_plan:
            return
            
        plan_file = task.workspace.get_workspace_path() / "plan.json"
        try:
            plan_data = self.current_plan.model_dump()
            plan_file.write_text(json.dumps(plan_data, indent=2))
            logger.debug("Plan persisted to plan.json")
        except Exception as e:
            logger.error(f"Failed to persist plan: {e}")
