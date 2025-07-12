"""
Task execution class - the primary interface for AgentX task execution.

Clean API:
    # One-shot execution (Fire-and-forget)
    await execute_task(prompt, config_path)

    # Step-by-step execution (Conversational)
    executor = start_task(prompt, config_path)
    await executor.start(prompt)
    while not executor.is_complete():
        response = await executor.step()
        print(response)
"""

from __future__ import annotations
import asyncio
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, AsyncGenerator, Union

from agentx.core.agent import Agent
from agentx.core.config import TeamConfig, TaskConfig
from agentx.core.message import MessageQueue, TaskHistory, Message, UserMessage, TaskStep, TextPart
# Orchestrator functionality moved to XAgent
from agentx.core.plan import Plan, PlanItem, TaskStatus
from agentx.storage.workspace import WorkspaceStorage
from agentx.tool.manager import ToolManager
from agentx.utils.id import generate_short_id
from agentx.utils.logger import (
    get_logger,
    setup_clean_chat_logging,
    setup_task_file_logging,
    set_streaming_mode,
)
from agentx.config.team_loader import load_team_config
from agentx.core.xagent import XAgent

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


class Task:
    """
    Represents the state and context of a single task being executed.
    This class is a data container and does not have execution logic.
    """

    def __init__(
        self,
        task_id: str,
        config: TaskConfig,
        history: TaskHistory,
        message_queue: MessageQueue,
        agents: Dict[str, Agent],
        workspace: WorkspaceStorage,
        initial_prompt: str,
    ):
        self.task_id = task_id
        self.config = config
        self.history = history
        self.message_queue = message_queue
        self.agents = agents
        self.workspace = workspace
        self.initial_prompt = initial_prompt

        self.is_complete: bool = False
        self.created_at: datetime = datetime.now()
        self.current_plan: Optional[Plan] = None

    def get_agent(self, name: str) -> Agent:
        """Retrieves an agent by name."""
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' not found in task.")
        return self.agents[name]

    def complete(self):
        """Marks the task as complete."""
        self.is_complete = True
        logger.info(f"Task {self.task_id} completed")

    def get_context(self) -> Dict[str, Any]:
        """Returns a dictionary with the task's context."""
        context = {
            "task_id": self.task_id,
            "status": "completed" if self.is_complete else "in_progress",
            "initial_prompt": self.initial_prompt,
            "workspace": str(self.workspace.get_workspace_path()),
            "agents": list(self.agents.keys()),
            "history_length": len(self.history.messages),
        }

        # Add plan information if available
        if self.current_plan:
            context["plan"] = {
                "goal": self.current_plan.goal,
                "total_tasks": len(self.current_plan.tasks),
                "progress": self.current_plan.get_progress_summary(),
                "is_complete": self.current_plan.is_complete(),
            }

        return context

    def create_plan(self, plan: Plan) -> None:
        """Creates a new plan for the task."""
        self.current_plan = plan
        logger.info(f"Created plan for task {self.task_id} with {len(plan.tasks)} tasks")

    async def update_plan(self, plan: Plan) -> None:
        """Updates the current plan and persists it."""
        self.current_plan = plan
        logger.info(f"Updated plan for task {self.task_id}")
        await self._persist_plan()

    async def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status and automatically persist the plan."""
        if not self.current_plan:
            return False

        success = self.current_plan.update_task_status(task_id, status)
        if success:
            await self._persist_plan()
        return success

    def get_plan(self) -> Optional[Plan]:
        """Returns the current plan."""
        return self.current_plan

    async def _persist_plan(self) -> None:
        """Persists the current plan to plan.json."""
        if not self.current_plan:
            return

        try:
            plan_data = self.current_plan.model_dump()
            await self.workspace.store_plan(plan_data)
            logger.debug(f"Plan persisted to plan.json")
        except Exception as e:
            logger.error(f"Failed to persist plan: {e}")

    async def load_plan(self) -> Optional[Plan]:
        """Loads the plan from plan.json if it exists."""
        try:
            plan_data = await self.workspace.get_plan()
            if plan_data:
                self.current_plan = Plan(**plan_data)
                logger.info(f"Loaded existing plan from plan.json")
                return self.current_plan
            return None
        except Exception as e:
            logger.error(f"Failed to load plan: {e}")
            return None


async def execute_task(
    prompt: str,
    config_path: str,
    stream: bool = False,
) -> AsyncGenerator[Message, None]:
    """
    High-level function to execute a task from a prompt and config file.
    This function runs the task to completion autonomously.
    """
    # Use XAgent for task execution - it handles plan generation internally
    x = XAgent(
        team_config=config_path,
        initial_prompt=prompt
    )

    # Execute the task autonomously
    while not x.is_complete:
        response = await x.step()

        # Create a TaskStep message for compatibility
        message = TaskStep(
            agent_name="X",
            parts=[TextPart(text=response)]
        )
        x.history.add_message(message)
        yield message


async def start_task(
    prompt: str,
    config_path: Union[str, Path, TeamConfig],
    task_id: Optional[str] = None,
    workspace_dir: Optional[Path] = None,
) -> XAgent:
    """
    High-level function to start a task and return an initialized XAgent.

    This function creates an XAgent instance that users can chat with
    to manage complex multi-agent tasks conversationally.

    Args:
        prompt: The initial task prompt
        config_path: Path to the team configuration file
        task_id: Optional custom task ID
        workspace_dir: Optional custom workspace directory

    Returns:
        XAgent: The initialized XAgent ready for conversational interaction

    Example:
        ```python
        # Start a conversational task
        x = await start_task(
            prompt="Create a market research report",
            config_path="config/team.yaml"
        )

        # Chat with X to manage the task
        response = await x.chat("Update the report with more visual appeal")
        print(response.text)

        # Send rich messages with attachments
        response = await x.chat(Message(parts=[
            TextPart("Use this style guide"),
            ArtifactPart(artifact=style_guide)
        ]))
        ```
    """
    from agentx.config.team_loader import load_team_config

    # Load team configuration if path is provided
    if isinstance(config_path, (str, Path)):
        team_config = load_team_config(str(config_path))
    else:
        team_config = config_path

    # Create XAgent with the loaded configuration
    # XAgent handles plan generation internally when initial_prompt is provided
    x = XAgent(
        team_config=team_config,
        task_id=task_id,
        workspace_dir=workspace_dir,
        initial_prompt=prompt
    )

    return x
