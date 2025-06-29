from __future__ import annotations
import re
import asyncio
from pathlib import Path
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentx.core.task import Task

from agentx.core.agent import Agent
from agentx.core.brain import Brain
from .config import BrainConfig

class BaseLead(ABC):
    def __init__(self, task: "Task"):
        self.task = task
        self.workspace = Path(self.task.workspace_dir)
        self.plan_path = self.workspace / "artifacts" / "plan.md"

    async def _create_plan(self, planner_agent_name: str):
        """Creates the initial plan for the task using a specified planner agent."""
        if planner_agent_name not in self.task.agents:
            raise ValueError(f"Planner agent '{planner_agent_name}' not found in the team.")
        
        planner = self.task.agents[planner_agent_name]
        
        prompt = f"Create a step-by-step plan to accomplish the following goal: {self.task.initial_prompt}. The plan should be a markdown checklist. Save the plan to a file named '{self.plan_path.name}' in the current directory."
        
        plan_result = await self.task.executor.run_agent(
            agent=planner,
            prompt=prompt
        )
        
        if not self.plan_path.exists():
            raise FileNotFoundError(f"Planner agent '{planner_agent_name}' did not create the plan file at {self.plan_path}. The agent output was: {plan_result}")
        
        print(f"Plan created at {self.plan_path}")

    def get_next_step(self) -> str | None:
        """Reads the plan and returns the next incomplete step."""
        if not self.plan_path.exists():
            return None
        with open(self.plan_path, "r") as f:
            plan_content = f.read()
        
        incomplete_tasks = re.findall(r"-\s*\[\s*\]\s*(.*)", plan_content)
        if not incomplete_tasks:
            return None
        
        return incomplete_tasks[0].strip()

    def _update_plan(self, step: str, result: str):
        """Marks a step as complete and appends the result."""
        with open(self.plan_path, "r+") as f:
            content = f.read()
            pattern = re.compile(r"(-\s*\[\s*\]\s*" + re.escape(step) + r")")
            new_content, count = pattern.subn(f"- [x] {step}", content, 1)

            if count > 0:
                new_content += f"\n\n**Result for '{step}':**\n{result}\n---"
                f.seek(0)
                f.write(new_content)
                f.truncate()
            else:
                print(f"Warning: Could not find step '{step}' to mark as complete in the plan.")

    @abstractmethod
    async def _get_worker_for_step(self, step: str) -> Agent:
        """Abstract method to determine which worker agent should handle the current step."""
        pass

    async def run(self, planner_agent_name: str):
        """Runs the main execution loop."""
        if not self.plan_path.exists():
            await self._create_plan(planner_agent_name)

        while (step := self.get_next_step()):
            print(f"Executing step: {step}")
            
            worker_agent = await self._get_worker_for_step(step)

            result = await self.task.executor.run_agent(
                agent=worker_agent,
                prompt=step
            )
            
            self._update_plan(step, str(result))
            print(f"Step '{step}' completed.")
            await asyncio.sleep(1)

        print("All steps completed. Task finished.")
        self.task.complete_task()


class Lead(BaseLead):
    """
    The default, concrete implementation of the Lead agent.
    It uses an LLM call to dynamically route tasks to the best-suited worker agent.
    """
    async def _get_worker_for_step(self, step: str) -> "Agent":
        """
        Uses a classification model to determine which worker agent should handle the current step.
        """
        agent_names = list(self.task.agents.keys())

        prompt = f"""
        Given the following task description:
        "{step}"

        Which of the following specialist agents is best suited to perform this task?
        {agent_names}

        Respond with only the name of the best agent.
        """

        # Use a fast, cheap model for classification
        routing_config = BrainConfig(
            provider="deepseek",
            model="deepseek/deepseek-chat",
            temperature=0.1,
            max_tokens=100,
            supports_function_calls=False,
            streaming=False
        )
        routing_brain = Brain(routing_config)

        response = await routing_brain.generate_response(
            messages=[{"role": "user", "content": prompt}]
        )

        chosen_agent_name = response.content.strip()

        # Find the agent whose name is contained in the response
        best_agent = None
        for name in agent_names:
            if name.lower() in chosen_agent_name.lower():
                best_agent = self.task.agents[name]
                break

        if best_agent:
            print(f"Routing step to agent: '{best_agent.config.name}'")
            return best_agent
        else:
            print(f"Warning: Could not reliably determine agent for step '{step}'. Defaulting to first agent.")
            return self.task.agents[agent_names[0]] 