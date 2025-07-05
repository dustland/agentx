"""
Task execution class - the primary interface for AgentX task execution.

Clean API:
    # One-shot execution (Lead-driven)
    await execute_task(prompt, config_path)
    
    # Step-by-step execution (Lead-driven)
    task = start_task(prompt, config_path)
    await task.run()
"""

from __future__ import annotations
import asyncio
from datetime import datetime
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, AsyncGenerator

from agentx.core.agent import Agent
from agentx.core.config import TeamConfig, TaskConfig
from agentx.core.message import MessageQueue, TaskHistory, Message, UserMessage
from agentx.core.orchestrator import Orchestrator
from agentx.core.plan import Plan
from agentx.event.bus import log_event
from agentx.storage.workspace import Workspace
from agentx.tool.manager import ToolManager
from agentx.utils.id import generate_short_id
from agentx.utils.logger import (
    get_logger,
    setup_clean_chat_logging,
    setup_task_file_logging,
    set_streaming_mode,
)

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
        workspace: Workspace,
        orchestrator: Orchestrator,
        initial_prompt: str,
    ):
        self.task_id = task_id
        self.config = config
        self.history = history
        self.message_queue = message_queue
        self.agents = agents
        self.workspace = workspace
        self.orchestrator = orchestrator
        self.initial_prompt = initial_prompt

        self.plan: Optional[Plan] = self._load_plan()
        self.is_complete: bool = False
        self.created_at: datetime = datetime.now()

    def _load_plan(self) -> Optional[Plan]:
        """Loads the plan from the workspace if it exists."""
        plan_path = self.workspace.get_path("plan.json")
        if plan_path.exists():
            try:
                with open(plan_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                plan = Plan.model_validate(data)
                logger.info(f"Successfully loaded existing plan for task {self.task_id}")
                return plan
            except Exception as e:
                logger.error(f"Failed to load or validate plan for task {self.task_id}: {e}")
                return None
        return None

    def get_agent(self, name: str) -> Agent:
        """Retrieves an agent by name."""
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' not found in task.")
        return self.agents[name]

    def complete(self):
        """Marks the task as complete."""
        self.is_complete = True
        log_event("task_completed", {"task_id": self.task_id})

    def get_context(self) -> Dict[str, Any]:
        """Returns a dictionary with the task's context."""
        return {
            "task_id": self.task_id,
            "status": "completed" if self.is_complete else "in_progress",
            "initial_prompt": self.initial_prompt,
            "workspace": str(self.workspace.get_dir()),
            "plan_exists": self.plan is not None,
            "agents": list(self.agents.keys()),
            "history_length": len(self.history.get_messages()),
        }


class TaskExecutor:
    """
    The main engine for executing a task. It coordinates the agents, tools,
    and orchestrator to fulfill the user's request.
    """

    def __init__(
        self,
        team_config: TeamConfig,
        task_id: Optional[str] = None,
        workspace_dir: Optional[Path] = None,
    ):
        self.task_id = task_id or generate_short_id()
        self.team_config = team_config
        self.workspace = Workspace(
            workspace_dir or (Path("./workspace") / self.task_id)
        )
        self._setup_task_logging()

        logger.info(f"Initializing TaskExecutor for task: {self.task_id}")

        self.tool_manager = self._initialize_tools()
        self.message_queue = MessageQueue()
        self.agents = self._initialize_agents()
        self.history = TaskHistory(self.task_id)
        self.orchestrator = Orchestrator(
            team_config=self.team_config,
            message_queue=self.message_queue,
            tool_manager=self.tool_manager,
            agents=self.agents,
        )

        self.task: Optional[Task] = None
        logger.info("✅ TaskExecutor initialized")

    def _setup_task_logging(self):
        """Sets up file-based logging for the task."""
        log_dir = self.workspace.get_path("logs", create=True)
        setup_task_file_logging(self.task_id, log_dir)

    def _initialize_tools(self) -> ToolManager:
        """Initializes the ToolManager and registers builtin tools."""
        tool_manager = ToolManager()
        logger.info("ToolManager initialized.")
        return tool_manager

    def _initialize_agents(self) -> Dict[str, Agent]:
        """Initializes all agents defined in the team configuration."""
        agents: Dict[str, Agent] = {}
        for agent_config in self.team_config.agents:
            agents[agent_config.name] = Agent.from_config(
                config=agent_config,
                tool_manager=self.tool_manager,
                message_queue=self.message_queue,
            )
        logger.info(f"Initialized {len(agents)} agents: {list(agents.keys())}")
        return agents

    async def start(
        self,
        prompt: str,
        stream: bool = False,
    ) -> AsyncGenerator[Message, None]:
        """
        Starts the task execution and streams back events.
        """
        setup_clean_chat_logging()
        set_streaming_mode(stream)

        self.task = Task(
            task_id=self.task_id,
            config=self.team_config.task,
            history=self.history,
            message_queue=self.message_queue,
            agents=self.agents,
            workspace=self.workspace,
            orchestrator=self.orchestrator,
            initial_prompt=prompt,
        )

        log_event(
            "task_started",
            {"task_id": self.task_id, "prompt": prompt, "stream": stream},
        )

        initial_message = UserMessage(content=prompt)
        self.history.add_message(initial_message)
        await self.message_queue.publish(initial_message)

        async for message in self.orchestrator.run(task=self.task):
            self.history.add_message(message)
            yield message

        self.task.complete()
        log_event("task_finished", {"task_id": self.task_id})


async def execute_task(
    prompt: str,
    config_path: str,
    stream: bool = False,
) -> AsyncGenerator[Message, None]:
    """
    High-level function to execute a task from a prompt and config file.
    """
    from agentx.config.team_loader import load_team_config

    team_config = load_team_config(config_path)
    executor = TaskExecutor(team_config=team_config)

    async for message in executor.start(prompt=prompt, stream=stream):
        yield message