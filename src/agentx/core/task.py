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
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, AsyncGenerator, Union

from agentx.core.agent import Agent
from agentx.core.config import TeamConfig, TaskConfig
from agentx.core.message import MessageQueue, TaskHistory, Message, UserMessage, TaskStep, TextPart
from agentx.core.orchestrator import Orchestrator
from agentx.core.plan import Plan, PlanItem
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
        self._persist_plan()
        logger.info(f"Created plan for task {self.task_id} with {len(plan.tasks)} tasks")

    def update_plan(self, plan: Plan) -> None:
        """Updates the current plan."""
        self.current_plan = plan
        self._persist_plan()
        logger.info(f"Updated plan for task {self.task_id}")

    def get_plan(self) -> Optional[Plan]:
        """Returns the current plan."""
        return self.current_plan

    def _persist_plan(self) -> None:
        """Persists the current plan to the task history and workspace."""
        if not self.current_plan:
            return

        # Save plan to workspace
        plan_file = self.workspace.get_workspace_path() / "plan.json"
        try:
            plan_data = self.current_plan.model_dump()
            plan_file.write_text(json.dumps(plan_data, indent=2))
            logger.debug(f"Plan persisted to {plan_file}")
        except Exception as e:
            logger.error(f"Failed to persist plan: {e}")

    def load_plan(self) -> Optional[Plan]:
        """Loads a plan from the workspace if it exists."""
        plan_file = self.workspace.get_workspace_path() / "plan.json"

        if not plan_file.exists():
            return None

        try:
            plan_data = json.loads(plan_file.read_text())
            self.current_plan = Plan(**plan_data)
            logger.info(f"Loaded existing plan from {plan_file}")
            return self.current_plan
        except Exception as e:
            logger.error(f"Failed to load plan: {e}")
            return None


class TaskExecutor:
    """
    The main engine for executing a task. It coordinates the agents, tools,
    and orchestrator to fulfill the user's request.

    Two execution modes:
    1. Fire-and-forget: execute() runs task to completion autonomously
    2. Step-by-step: start() + step() for conversational interaction
    """

    def __init__(
        self,
        team_config: Union[TeamConfig, str],
        task_id: Optional[str] = None,
        workspace_dir: Optional[Path] = None,
    ):
        self.task_id = task_id or generate_short_id()

        # Handle both TeamConfig objects and config file paths
        if isinstance(team_config, str):
            self.team_config = load_team_config(team_config)
        else:
            self.team_config = team_config
        self.workspace = WorkspaceStorage(
            workspace_path=workspace_dir or (Path("./workspace") / self.task_id)
        )
        self._setup_task_logging()

        logger.info(f"Initializing TaskExecutor for task: {self.task_id}")

        self.tool_manager = self._initialize_tools()
        self.message_queue = MessageQueue()
        self.agents = self._initialize_agents()
        self.history = TaskHistory(task_id=self.task_id)
        self.orchestrator = Orchestrator(
            team_config=self.team_config,
            message_queue=self.message_queue,
            tool_manager=self.tool_manager,
            agents=self.agents,
        )

        self.task: Optional[Task] = None
        self._conversation_history: list[dict] = []
        self._current_agent: Optional[str] = None
        self._consecutive_no_tool_responses = 0  # Track responses without tool calls
        logger.info("✅ TaskExecutor initialized")

    def _setup_task_logging(self):
        """Sets up file-based logging for the task."""
        log_dir = self.workspace.get_workspace_path() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir / f"{self.task_id}.log"
        setup_task_file_logging(str(log_file_path))

    def _initialize_tools(self) -> ToolManager:
        """Initializes the ToolManager and registers builtin tools."""
        tool_manager = ToolManager(
            task_id=self.task_id,
            workspace_path=str(self.workspace.get_workspace_path())
        )
        logger.info("ToolManager initialized.")
        return tool_manager

    def _initialize_agents(self) -> Dict[str, Agent]:
        """Initializes all agents defined in the team configuration."""
        agents: Dict[str, Agent] = {}
        for agent_config in self.team_config.agents:
            agents[agent_config.name] = Agent(
                config=agent_config,
                tool_manager=self.tool_manager,
            )
        logger.info(f"Initialized {len(agents)} agents: {list(agents.keys())}")
        return agents

    async def execute(
        self,
        prompt: str,
        stream: bool = False,
    ) -> AsyncGenerator[Message, None]:
        """
        Fire-and-forget execution - runs task to completion autonomously.
        This is the method called by execute_task() for autonomous execution.
        """
        setup_clean_chat_logging()
        set_streaming_mode(stream)

        self.task = Task(
            task_id=self.task_id,
            config=self.team_config.execution,
            history=self.history,
            message_queue=self.message_queue,
            agents=self.agents,
            workspace=self.workspace,
            orchestrator=self.orchestrator,
            initial_prompt=prompt,
        )

        # Load existing plan if available
        self.task.load_plan()

        logger.info(f"Task {self.task_id} executing autonomously with prompt: {prompt[:50]}...")

        # Use simple step-based execution
        self._conversation_history = [{"role": "user", "content": prompt}]

        # Generate response using orchestrator's step method
        response = await self.orchestrator.step(self._conversation_history, self.task)

        # Create a TaskStep message
        message = TaskStep(
            agent_name=next(iter(self.agents.keys())),
            parts=[TextPart(text=response)]
        )
        self.history.add_message(message)
        yield message

        self.task.complete()
        logger.info(f"Task {self.task_id} finished")

    async def start(self, prompt: str) -> None:
        """
        Initialize the conversation with the given prompt.
        This sets up the task but doesn't execute any agent responses yet.
        """
        setup_clean_chat_logging()

        self.task = Task(
            task_id=self.task_id,
            config=self.team_config.execution,
            history=self.history,
            message_queue=self.message_queue,
            agents=self.agents,
            workspace=self.workspace,
            orchestrator=self.orchestrator,
            initial_prompt=prompt,
        )

        # Load existing plan if available
        self.task.load_plan()

        # Add the initial user message to conversation history
        self._conversation_history = [{"role": "user", "content": prompt}]

        logger.info(f"Task {self.task_id} conversation started with prompt: {prompt[:50]}...")

    async def step(self) -> str:
        """
        Execute one conversation step - get a response from the current agent.
        Returns the agent's response as a string.
        """
        if not self.task:
            raise RuntimeError("Task not started. Call start() first.")

        if self.task.is_complete:
            return ""

        # Use orchestrator's step method to get response
        response = await self.orchestrator.step(self._conversation_history, self.task)

        # Add agent response to conversation history
        self._conversation_history.append({"role": "assistant", "content": response})

        # Check if orchestrator indicates task is complete
        if self._is_completion_response(response):
            self.task.complete()

        return response

    def _is_completion_response(self, response: str) -> bool:
        """Check if the response indicates task completion (language-independent)."""
        # Check for specific completion indicators from the orchestrator
        completion_phrases = [
            "Task completed successfully",
            "All plan items have been finished",
            "Task execution halted"
        ]

        return any(phrase in response for phrase in completion_phrases)

    @property
    def is_complete(self) -> bool:
        """Check if the task is complete."""
        return self.task.is_complete if self.task else False

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history."""
        self._conversation_history.append({"role": "user", "content": content})
        # Reset completion status for continued conversation
        if self.task:
            self.task.is_complete = False


async def execute_task(
    prompt: str,
    config_path: str,
    stream: bool = False,
) -> AsyncGenerator[Message, None]:
    """
    High-level function to execute a task from a prompt and config file.
    This function runs the task to completion autonomously.
    """
    from agentx.config.team_loader import load_team_config

    team_config = load_team_config(config_path)
    executor = TaskExecutor(team_config=team_config)

    async for message in executor.execute(prompt=prompt, stream=stream):
        yield message


def start_task(
    prompt: str,
    config_path: str,
    task_id: Optional[str] = None,
    workspace_dir: Optional[Path] = None,
) -> TaskExecutor:
    """
    High-level function to start a task and return the TaskExecutor for step-by-step execution.

    This function is ideal for interactive scenarios where you want to:
    - Execute conversations step by step
    - Build interactive chat interfaces
    - Have manual control over the conversation flow

    Args:
        prompt: The initial task prompt
        config_path: Path to the team configuration file
        task_id: Optional custom task ID
        workspace_dir: Optional custom workspace directory

    Returns:
        TaskExecutor: The initialized executor ready for step-by-step execution

    Example:
        ```python
        # Start a conversational task
        executor = start_task(
            prompt="Hello, how are you?",
            config_path="config/team.yaml"
        )

        # Initialize the conversation
        await executor.start(prompt)

        # Get agent response
        response = await executor.step()
        print(f"Agent: {response}")

        # Continue conversation
        executor.add_user_message("Tell me a joke")
        response = await executor.step()
        print(f"Agent: {response}")
        ```
    """
    from agentx.config.team_loader import load_team_config

    team_config = load_team_config(config_path)
    executor = TaskExecutor(
        team_config=team_config,
        task_id=task_id,
        workspace_dir=workspace_dir
    )

    return executor
