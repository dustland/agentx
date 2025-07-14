"""
XAgent - The unified conversational interface for AgentX

XAgent merges TaskExecutor and Orchestrator functionality into a single,
user-friendly interface that users can chat with to manage complex multi-agent tasks.

Key Features:
- Rich message handling with attachments and multimedia
- LLM-driven plan adjustment that preserves completed work
- Single point of contact for all user interactions
- Automatic taskspace and tool management

API Design:
- chat(message) - For user conversation, plan adjustments, and Q&A
- step() - For autonomous task execution, moving the plan forward
- start_task() creates a plan but doesn't execute it automatically
"""

from __future__ import annotations
import asyncio
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, AsyncGenerator, Union, List
import json

from agentx.core.agent import Agent
from agentx.core.brain import Brain
from agentx.core.config import TeamConfig, BrainConfig, AgentConfig
from agentx.core.handoff_evaluator import HandoffEvaluator, HandoffContext
from agentx.core.message import (
    MessageQueue, TaskHistory, Message, TaskStep, TextPart,
)
from agentx.core.plan import Plan, PlanItem, TaskStatus
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


class XAgentResponse:
    """Response from XAgent chat interactions."""

    def __init__(
        self,
        text: str,
        artifacts: Optional[List[Any]] = None,
        preserved_steps: Optional[List[str]] = None,
        regenerated_steps: Optional[List[str]] = None,
        plan_changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.text = text
        self.artifacts = artifacts or []
        self.preserved_steps = preserved_steps or []
        self.regenerated_steps = regenerated_steps or []
        self.plan_changes = plan_changes or {}
        self.metadata = metadata or {}


class XAgent(Agent):
    """
    XAgent - The unified conversational interface for AgentX.

    XAgent combines TaskExecutor's execution context management with
    Orchestrator's agent coordination logic into a single, user-friendly
    interface that users can chat with naturally.

    Key capabilities:
    - Rich message handling (text, attachments, multimedia)
    - LLM-driven plan adjustment preserving completed work
    - Automatic taskspace and tool management
    - Conversational task management

    Usage Pattern:
        ```python
        # Start a task (creates plan but doesn't execute)
        x = await start_task("Build a web app", "config/team.yaml")

        # Execute the task autonomously
        while not x.is_complete:
            response = await x.step()  # Autonomous execution
            print(response)

        # Chat for refinements and adjustments
        response = await x.chat("Make it more colorful")  # User conversation
        print(response.text)
        ```
    """

    def __init__(
        self,
        team_config: TeamConfig,
        task_id: Optional[str] = None,
        taskspace_dir: Optional[Path] = None,
        initial_prompt: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        # Generate unique task ID
        self.task_id = task_id or generate_short_id()
        self.user_id = user_id

        # Accept only TeamConfig objects
        if not isinstance(team_config, TeamConfig):
            raise TypeError(f"team_config must be a TeamConfig object, got {type(team_config)}")
        self.team_config = team_config

        # Initialize taskspace storage
        from agentx.storage.factory import StorageFactory
        if taskspace_dir:
            # Use explicit taskspace directory
            self.taskspace = StorageFactory.create_taskspace_storage(taskspace_path=taskspace_dir)
        else:
            # Use user-scoped taskspace: taskspace/{user_id}/{task_id} or taskspace/{task_id}
            self.taskspace = StorageFactory.create_taskspace_storage(
                base_path=Path("./taskspace"),
                task_id=self.task_id,
                user_id=self.user_id
            )
        self._setup_task_logging()

        logger.info(f"Initializing XAgent for task: {self.task_id}")

        # Initialize components
        self.tool_manager = self._initialize_tools()
        self.message_queue = MessageQueue()
        self.specialist_agents = self._initialize_specialist_agents()
        self.history = TaskHistory(task_id=self.task_id)
        
        # Initialize chat history storage
        from ..storage.chat_history import chat_history_manager
        self.chat_storage = chat_history_manager.get_storage(self.taskspace.taskspace_path)

        # Initialize XAgent's own brain for orchestration decisions
        orchestrator_brain_config = self._get_orchestrator_brain_config()

        # Initialize parent Agent class with XAgent configuration
        super().__init__(
            config=self._create_xagent_config(),
            tool_manager=self.tool_manager
        )

        # Override brain with orchestrator-specific configuration
        self.brain = Brain.from_config(orchestrator_brain_config)

        # Task state
        self.plan: Optional[Plan] = None
        self.is_complete: bool = False
        self.conversation_history: List[Message] = []
        self.initial_prompt = initial_prompt
        self._plan_initialized = False
        
        # Parallel execution settings
        self.parallel_execution = True  # Enable parallel execution by default
        self.max_concurrent_tasks = 3  # Default concurrency limit

        # Initialize handoff evaluator if handoffs are configured
        self.handoff_evaluator = None
        if self.team_config.handoffs:
            self.handoff_evaluator = HandoffEvaluator(
                handoffs=self.team_config.handoffs,
                agents=self.specialist_agents
            )

        logger.info("✅ XAgent initialized and ready for conversation")

    def _setup_task_logging(self) -> None:
        """Sets up file-based logging for the task."""
        log_dir = self.taskspace.get_taskspace_path() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir / f"{self.task_id}.log"
        setup_task_file_logging(str(log_file_path))

    def _initialize_tools(self) -> ToolManager:
        """Initializes the ToolManager and registers builtin tools."""
        tool_manager = ToolManager(
            task_id=self.task_id,
            taskspace_path=str(self.taskspace.get_taskspace_path())
        )
        logger.info("ToolManager initialized.")
        return tool_manager

    def _initialize_specialist_agents(self) -> Dict[str, Agent]:
        """Initializes all specialist agents defined in the team configuration."""
        agents: Dict[str, Agent] = {}
        for agent_config in self.team_config.agents:
            agent = Agent(
                config=agent_config,
                tool_manager=self.tool_manager,
            )
            # Pass team memory config to agent if available
            if hasattr(self.team_config, 'memory') and self.team_config.memory:
                agent.team_memory_config = self.team_config.memory
            agents[agent_config.name] = agent
        logger.info(f"Initialized {len(agents)} specialist agents: {list(agents.keys())}")
        return agents

    def _get_orchestrator_brain_config(self) -> BrainConfig:
        """Get brain configuration for orchestration decisions."""
        if (self.team_config.orchestrator and
            self.team_config.orchestrator.brain_config):
            return self.team_config.orchestrator.brain_config

        # Default orchestrator brain config
        return BrainConfig(
            provider="deepseek",
            model="deepseek-chat",
            temperature=0.3,
            max_tokens=8000,
            timeout=120
        )

    def _create_xagent_config(self) -> 'AgentConfig':
        """Create AgentConfig for XAgent itself."""
        from agentx.core.config import AgentConfig
        from pathlib import Path

        # Use the comprehensive XAgent system prompt
        xagent_prompt_path = Path(__file__).parent.parent / "presets" / "agents" / "xagent.md"

        return AgentConfig(
            name="X",
            description="XAgent - The lead orchestrator and strategic planner for AgentX",
            prompt_file=str(xagent_prompt_path),
            tools=[],  # XAgent coordinates but doesn't use tools directly
            enable_memory=True,
            max_consecutive_replies=50
        )

    async def _initialize_with_prompt(self, prompt: str) -> None:
        """Initialize XAgent with an initial prompt and load/create plan."""
        self.initial_prompt = prompt

        # Try to load existing plan
        plan_path = self.taskspace.get_taskspace_path() / "plan.json"
        if plan_path.exists():
            try:
                with open(plan_path, 'r') as f:
                    plan_data = json.load(f)
                self.plan = Plan(**plan_data)
                logger.info("Loaded existing plan from taskspace")
            except Exception as e:
                logger.warning(f"Failed to load existing plan: {e}")

        # Generate new plan if none exists
        if not self.plan:
            self.plan = await self._generate_plan(prompt)
            await self._persist_plan()

    async def _ensure_plan_initialized(self) -> None:
        """Ensure plan is initialized if we have an initial prompt."""
        if not self._plan_initialized and self.initial_prompt:
            await self._initialize_with_prompt(self.initial_prompt)
            self._plan_initialized = True

    async def chat(self, message: Union[str, Message]) -> XAgentResponse:
        """
        Send a conversational message to X and get a response.

        This is the conversational interface that handles:
        - User questions and clarifications
        - Plan adjustments and modifications
        - Rich messages with attachments
        - Preserving completed work while regenerating only necessary steps

        This method is for USER INPUT and conversation, not for autonomous task execution.
        For autonomous task execution, use step() method instead.

        Args:
            message: Either a simple text string or a rich Message with parts

        Returns:
            XAgentResponse with text, artifacts, and execution details
        """
        setup_clean_chat_logging()

        # Convert string to Message if needed
        if isinstance(message, str):
            message = Message.user_message(message)

        # Add to conversation history
        self.conversation_history.append(message)
        self.history.add_message(message)
        
        # Persist message to chat history
        import asyncio
        if hasattr(self, 'chat_storage'):
            asyncio.create_task(self.chat_storage.save_message(self.task_id, message))

        logger.info(f"XAgent received chat message: {message.content[:100]}...")

        try:
            # Ensure plan is initialized if we have an initial prompt
            await self._ensure_plan_initialized()

            # Analyze message impact on current plan
            impact_analysis = await self._analyze_message_impact(message)

            # If message requires plan adjustment
            if impact_analysis.get("requires_plan_adjustment", False):
                return await self._handle_plan_adjustment(message, impact_analysis)

            # If message is Q&A or informational
            elif impact_analysis.get("is_informational", False):
                return await self._handle_informational_query(message)

            # If no plan exists and this is a new task request
            elif not self.plan and impact_analysis.get("is_new_task", False):
                return await self._handle_new_task_request(message)

            # Default: treat as conversational input
            else:
                return await self._handle_conversational_input(message)

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return XAgentResponse(
                text=f"I encountered an error processing your message: {str(e)}",
                metadata={"error": str(e)}
            )



    async def _analyze_message_impact(self, message: Message) -> Dict[str, Any]:
        """
        Use LLM to analyze the impact of a user message on the current plan.

        This determines:
        - Whether the message requires plan adjustments
        - Which tasks might need to be regenerated
        - Whether it's an informational query
        - What artifacts should be preserved
        """
        analysis_prompt = f"""
Analyze this user message in the context of the current execution plan:

USER MESSAGE: {message.content}

CURRENT PLAN STATUS:
{self._get_plan_summary() if self.plan else "No plan exists yet"}

CONVERSATION CONTEXT:
{self._get_conversation_summary()}

Please analyze:
1. Does this message require adjusting the current plan?
2. Is this an informational query (asking about status, sources, methodology)?
3. If plan adjustment is needed, which specific tasks should be regenerated?
4. What completed work should be preserved?

Respond with a JSON object:
{{
  "requires_plan_adjustment": boolean,
  "is_informational": boolean,
  "is_new_task": boolean,
  "affected_tasks": ["list of task IDs that need regeneration"],
  "preserved_tasks": ["list of task IDs to preserve"],
  "adjustment_type": "regenerate|add_tasks|modify_goals|style_change",
  "reasoning": "explanation of the analysis"
}}
"""

        response = await self.brain.generate_response(
            messages=[{"role": "user", "content": analysis_prompt}],
            system_prompt=self.build_system_prompt({"task_id": self.task_id}),
            json_mode=True
        )

        try:
            if response.content is None:
                raise ValueError("Response content is None")
            result: Dict[str, Any] = json.loads(response.content)
            return result
        except (json.JSONDecodeError, ValueError):
            # Fallback to simple heuristics
            return {
                "requires_plan_adjustment": any(word in message.content.lower()
                                               for word in ["regenerate", "redo", "change", "update", "revise"]),
                "is_informational": any(word in message.content.lower()
                                       for word in ["what", "how", "why", "explain", "show"]),
                "is_new_task": not self.plan,
                "affected_tasks": [],
                "preserved_tasks": [],
                "adjustment_type": "regenerate",
                "reasoning": "Fallback analysis due to JSON parsing error"
            }

    async def _handle_plan_adjustment(self, message: Message, impact_analysis: Dict[str, Any]) -> XAgentResponse:
        """Handle messages that require adjusting the current plan."""
        if not self.plan:
            return await self._handle_new_task_request(message)

        preserved_tasks = impact_analysis.get("preserved_tasks", [])
        affected_tasks = impact_analysis.get("affected_tasks", [])

        logger.info(f"Adjusting plan: preserving {len(preserved_tasks)} tasks, regenerating {len(affected_tasks)} tasks")

        # Reset affected tasks to pending status
        for task_id in affected_tasks:
            for task in self.plan.tasks:
                if task.id == task_id:
                    task.status = "pending"
                    logger.info(f"Reset task '{task.name}' to pending for regeneration")

        # Don't auto-execute - let user call step() to execute
        await self._persist_plan()

        return XAgentResponse(
            text=f"I've adjusted the plan based on your request. "
                 f"Preserved {len(preserved_tasks)} completed tasks, "
                 f"reset {len(affected_tasks)} tasks for regeneration. "
                 f"Use step() to continue execution.",
            preserved_steps=[t for t in preserved_tasks],
            regenerated_steps=[t for t in affected_tasks],
            plan_changes=impact_analysis,
            metadata={
                "adjustment_type": impact_analysis.get("adjustment_type"),
                "reasoning": impact_analysis.get("reasoning")
            }
        )

    async def _handle_informational_query(self, message: Message) -> XAgentResponse:
        """Handle informational queries about the task, status, or methodology."""
        context_prompt = f"""
The user is asking an informational question about the current task:

USER QUESTION: {message.content}

CURRENT PLAN STATUS:
{self._get_plan_summary() if self.plan else "No plan exists yet"}

CONVERSATION HISTORY:
{self._get_conversation_summary()}

AVAILABLE ARTIFACTS:
{self._get_artifacts_summary()}

Please provide a helpful, informative response based on the current state of the task.
"""

        response = await self.brain.generate_response(
            messages=[{"role": "user", "content": context_prompt}],
            system_prompt=self.build_system_prompt({"task_id": self.task_id})
        )

        return XAgentResponse(
            text=response.content or "",
            metadata={"query_type": "informational"}
        )

    async def _handle_new_task_request(self, message: Message) -> XAgentResponse:
        """Handle new task requests when no plan exists."""
        # Create a new plan
        self.plan = await self._generate_plan(message.content)
        await self._persist_plan()

        return XAgentResponse(
            text=f"I've created a plan for your task: {self.plan.goal}\n\n"
                 f"The plan includes {len(self.plan.tasks)} tasks. "
                 f"Use step() to execute the plan autonomously, or continue chatting to refine it.",
            metadata={"execution_type": "plan_created"}
        )

    async def _handle_conversational_input(self, message: Message) -> XAgentResponse:
        """Handle general conversational input that doesn't require plan changes."""
        context_prompt = f"""
The user is having a conversation about the current task:

USER MESSAGE: {message.content}

CURRENT PLAN STATUS:
{self._get_plan_summary() if self.plan else "No plan exists yet"}

CONVERSATION HISTORY:
{self._get_conversation_summary()}

Please provide a helpful, conversational response. If the user seems to want to modify the plan,
suggest they be more specific about what changes they want.
"""

        response = await self.brain.generate_response(
            messages=[{"role": "user", "content": context_prompt}],
            system_prompt=self.build_system_prompt({"task_id": self.task_id})
        )

        return XAgentResponse(
            text=response.content or "",
            metadata={"query_type": "conversational"}
        )

    async def _generate_plan(self, goal: str) -> Plan:
        """Generate a new execution plan using the brain."""
        planning_prompt = f"""
Create a strategic execution plan for this goal:

GOAL: {goal}

AVAILABLE SPECIALIST AGENTS: {', '.join(self.specialist_agents.keys())}

Create a plan that breaks down the goal into specific, actionable tasks.
Each task should be assigned to the most appropriate specialist agent.

IMPORTANT: If this task involves creating a document or report:
1. Create separate tasks for writing each major section
2. After all section writing tasks, create a merge task for the writer to combine sections
3. Follow merge task with a review/polish task for the reviewer

Respond with a JSON object following this schema:
{{
  "goal": "string - the main objective",
  "tasks": [
    {{
      "id": "string - unique task identifier",
      "name": "string - task name",
      "goal": "string - specific task objective",
      "agent": "string - agent name from available agents",
      "dependencies": ["array of task IDs this depends on"],
      "status": "pending",
      "on_failure": "proceed"
    }}
  ]
}}
"""

        response = await self.brain.generate_response(
            messages=[{"role": "user", "content": planning_prompt}],
            system_prompt=self.build_system_prompt({"task_id": self.task_id}),
            json_mode=True
        )

        try:
            import json
            if response.content is None:
                raise ValueError("Response content is None")
            plan_data = json.loads(response.content)

            # Extract document outline if present
            document_outline = plan_data.pop("document_outline", None)

            # Create the plan
            plan = Plan(**plan_data)
            logger.info(f"Generated plan with {len(plan.tasks)} tasks")

            # Save document outline if provided
            if document_outline and self.taskspace:
                try:
                    await self.taskspace.store_artifact(
                        name="document_outline.md",
                        content=document_outline,
                        content_type="text/markdown",
                        metadata={"created_by": "XAgent", "purpose": "document_structure"},
                        commit_message="Created document outline for task execution"
                    )
                    logger.info("Saved document outline to taskspace")
                except Exception as e:
                    logger.warning(f"Failed to save document outline: {e}")

            return plan
        except Exception as e:
            logger.error(f"Failed to generate plan: {e}")
            # Create a simple fallback plan
            return Plan(
                goal=goal,
                tasks=[
                    PlanItem(
                        id="task_1",
                        name="Complete the requested task",
                        goal=goal,
                        agent=next(iter(self.specialist_agents.keys())),
                        dependencies=[],
                        status="pending",
                        on_failure="halt"
                    )
                ]
            )

    async def _execute_single_step(self) -> str:
        """Execute a single step of the plan."""
        if not self.plan:
            return "No plan available for execution."

        # Check if plan is already complete
        if self.plan.is_complete():
            self.is_complete = True
            return "🎉 All tasks completed successfully!"

        # Find next actionable task
        next_task = self.plan.get_next_actionable_task()
        if not next_task:
            if self.plan.has_failed_tasks():
                self.is_complete = True
                return "❌ Cannot continue: some tasks have failed"
            else:
                return "⏳ No actionable tasks available (waiting for dependencies)"

        # Execute the task
        try:
            logger.info(f"Executing task: {next_task.name}")
            result = await self._execute_single_task(next_task)

            # Update task status
            next_task.status = "completed"
            await self._persist_plan()

            # Check if this was the last task
            if self.plan.is_complete():
                self.is_complete = True
                return f"✅ {next_task.name}: {result}\n\n🎉 All tasks completed successfully!"
            else:
                return f"✅ {next_task.name}: {result}"

        except Exception as e:
            logger.error(f"Task failed: {next_task.name} - {e}")
            next_task.status = "failed"
            await self._persist_plan()

            if next_task.on_failure == "halt":
                self.is_complete = True
                return f"❌ {next_task.name}: Failed - {e}\n\nTask execution halted."
            else:
                return f"⚠️ {next_task.name}: Failed but continuing - {e}"

    async def _execute_plan_steps(self) -> str:
        """Execute the current plan step by step (for compatibility)."""
        if not self.plan:
            return "No plan available for execution."

        results = []

        while not self.plan.is_complete():
            step_result = await self._execute_single_step()
            results.append(step_result)

            # Break if we hit a halt condition
            if "Task execution halted" in step_result:
                break
            # Break if task is complete
            if self.is_complete:
                break

        return "\n".join(results)

    async def _execute_parallel_step(self, max_concurrent: int = 3) -> str:
        """
        Execute multiple tasks in parallel when possible.
        
        Args:
            max_concurrent: Maximum number of tasks to execute concurrently
            
        Returns:
            Status message about parallel execution
        """
        if not self.plan:
            return "No plan available for execution."

        # Check if plan is already complete
        if self.plan.is_complete():
            self.is_complete = True
            return "🎉 All tasks completed successfully!"

        # Find all actionable tasks for parallel execution
        actionable_tasks = self.plan.get_all_actionable_tasks(max_tasks=max_concurrent)
        
        if not actionable_tasks:
            if self.plan.has_failed_tasks():
                self.is_complete = True
                return "❌ Cannot continue: some tasks have failed"
            else:
                return "⏳ No actionable tasks available (waiting for dependencies)"

        # If only one task, fall back to sequential execution
        if len(actionable_tasks) == 1:
            return await self._execute_single_step()

        # Execute tasks in parallel
        logger.info(f"Executing {len(actionable_tasks)} tasks in parallel")
        
        # Mark all tasks as in_progress to prevent re-execution
        for task in actionable_tasks:
            task.status = "in_progress"
        
        try:
            # Create coroutines for parallel execution
            task_coroutines = []
            for task in actionable_tasks:
                logger.info(f"Starting parallel task: {task.name}")
                task_coroutines.append(self._execute_single_task(task))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*task_coroutines, return_exceptions=True)
            
            # Process results and update task statuses
            completion_messages = []
            failed_tasks = []
            
            for i, (task, result) in enumerate(zip(actionable_tasks, results)):
                if isinstance(result, Exception):
                    # Task failed
                    logger.error(f"Parallel task failed: {task.name} - {result}")
                    task.status = "failed"
                    failed_tasks.append(task)
                    
                    if task.on_failure == "halt":
                        completion_messages.append(f"❌ {task.name}: Failed - {result}")
                        # Mark remaining tasks as failed too
                        for remaining_task in actionable_tasks[i+1:]:
                            remaining_task.status = "failed"
                        break
                    else:
                        completion_messages.append(f"⚠️ {task.name}: Failed but continuing - {result}")
                else:
                    # Task succeeded
                    task.status = "completed"
                    completion_messages.append(f"✅ {task.name}: {result}")
            
            # Persist plan after parallel execution
            await self._persist_plan()
            
            # Check if this completed all tasks
            if self.plan.is_complete():
                self.is_complete = True
                completion_messages.append("🎉 All tasks completed successfully!")
            
            # If we had halt failures, mark as complete
            if failed_tasks and any(task.on_failure == "halt" for task in failed_tasks):
                self.is_complete = True
                completion_messages.append("Task execution halted due to critical failure.")
            
            return "\n".join(completion_messages)
            
        except Exception as e:
            # Rollback task statuses on unexpected failure
            logger.error(f"Parallel execution failed: {e}")
            for task in actionable_tasks:
                task.status = "pending"  # Reset to allow retry
            await self._persist_plan()
            return f"❌ Parallel execution failed: {e}"

    async def _execute_single_task(self, task: PlanItem) -> str:
        """Execute a single task using the appropriate specialist agent."""
        # Get the assigned agent
        if task.agent is None:
            raise ValueError("Task has no assigned agent")
        agent = self.specialist_agents.get(task.agent)
        if not agent:
            raise ValueError(f"Agent '{task.agent}' not found")

        # Task structure contains implicit document outline
        outline_reference = ""

        # Prepare task briefing
        briefing = [
            {
                "role": "system",
                "content": f"""You are being assigned a specific task as part of a larger plan.

TASK: {task.name}
GOAL: {task.goal}

Complete this specific task using your available tools. Save any outputs that other agents might need as files in the taskspace.

Original user request: {self.initial_prompt or "No initial prompt provided"}{outline_reference}
"""
            },
            {
                "role": "user",
                "content": f"Please complete this task: {task.goal}"
            }
        ]

        # Execute with the specialist agent
        response = await agent.generate_response(
            messages=briefing
        )

        # Evaluate if handoff should occur
        if self.handoff_evaluator:
            # Convert conversation history to expected format
            conversation_dicts = []
            for msg in self.conversation_history:
                conversation_dicts.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                })

            if task.agent is None:
                raise ValueError("Task has no assigned agent for handoff")
            context = HandoffContext(
                current_agent=task.agent,
                task_result=response,
                task_goal=task.goal,
                conversation_history=conversation_dicts,
                taskspace_files=[f["name"] for f in await self.taskspace.list_artifacts()]
            )

            next_agent = await self.handoff_evaluator.evaluate_handoffs(context)
            if next_agent and next_agent != task.agent:
                # Create a follow-up task for the handoff
                handoff_task = PlanItem(
                    id=f"handoff_{task.id}_{next_agent}",
                    name=f"Continue work with {next_agent}",
                    goal=f"Continue the work from {task.agent} based on: {task.goal}",
                    agent=next_agent,
                    dependencies=[task.id],
                    status="pending",
                    on_failure="halt"
                )

                # Add to plan dynamically
                if self.plan:
                    self.plan.tasks.append(handoff_task)
                    await self._persist_plan()

                    logger.info(f"Handoff task created: {task.agent} -> {next_agent}")
                    response += f"\n\n🤝 Handing off to {next_agent} for continuation."

        return response

    async def _persist_plan(self) -> None:
        """Persist the current plan to taskspace."""
        if not self.plan:
            return

        plan_path = self.taskspace.get_taskspace_path() / "plan.json"
        try:
            import json
            with open(plan_path, 'w') as f:
                json.dump(self.plan.model_dump(), f, indent=2)
            logger.debug("Plan persisted to taskspace")
        except Exception as e:
            logger.error(f"Failed to persist plan: {e}")

    def _get_plan_summary(self) -> str:
        """Get a summary of the current plan status."""
        if not self.plan:
            return "No plan exists"

        total_tasks = len(self.plan.tasks)
        completed_tasks = len([t for t in self.plan.tasks if t.status == "completed"])
        failed_tasks = len([t for t in self.plan.tasks if t.status == "failed"])

        summary = f"Plan: {self.plan.goal}\n"
        summary += f"Progress: {completed_tasks}/{total_tasks} completed"
        if failed_tasks > 0:
            summary += f", {failed_tasks} failed"

        return summary

    def _get_conversation_summary(self) -> str:
        """Get a summary of recent conversation."""
        if not self.conversation_history:
            return "No previous conversation"

        recent_messages = self.conversation_history[-3:]  # Last 3 messages
        summary = []
        for msg in recent_messages:
            role = msg.role.title()
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            summary.append(f"{role}: {content}")

        return "\n".join(summary)

    def _get_artifacts_summary(self) -> str:
        """Get a summary of available artifacts in taskspace."""
        try:
            artifacts_dir = self.taskspace.get_taskspace_path() / "artifacts"
            if not artifacts_dir.exists():
                return "No artifacts available"

            files = list(artifacts_dir.glob("*"))
            if not files:
                return "No artifacts available"

            return f"Available artifacts: {', '.join([f.name for f in files[:5]])}"
        except Exception:
            return "Unable to check artifacts"

    # Compatibility methods for existing TaskExecutor interface
    async def execute(self, prompt: str, stream: bool = False) -> AsyncGenerator[TaskStep, None]:
        """Compatibility method for TaskExecutor.execute()."""
        response = await self.chat(prompt)

        # Create a TaskStep message
        message = TaskStep(
            agent_name="X",
            parts=[TextPart(text=response.text)]
        )
        self.history.add_step(message)
        
        # Persist step to chat history
        import asyncio
        if hasattr(self, 'chat_storage'):
            asyncio.create_task(self.chat_storage.save_step(self.task_id, message))
        
        yield message

    async def start(self, prompt: str) -> None:
        """Compatibility method for TaskExecutor.start()."""
        await self._initialize_with_prompt(prompt)
    
    def set_parallel_execution(self, enabled: bool = True, max_concurrent: int = 3) -> None:
        """
        Configure parallel execution settings.
        
        Args:
            enabled: Whether to enable parallel execution
            max_concurrent: Maximum number of tasks to execute simultaneously
        """
        self.parallel_execution = enabled
        self.max_concurrent_tasks = max_concurrent
        logger.info(f"Parallel execution {'enabled' if enabled else 'disabled'} (max_concurrent: {max_concurrent})")
    
    def get_parallel_settings(self) -> Dict[str, Any]:
        """Get current parallel execution settings."""
        return {
            "parallel_execution": self.parallel_execution,
            "max_concurrent_tasks": self.max_concurrent_tasks
        }

    async def step(self) -> str:
        """
        Execute one step of autonomous task execution.

        This method is for AUTONOMOUS TASK EXECUTION, not for user conversation.
        It moves the plan forward by executing the next available task.

        For user conversation and plan adjustments, use chat() method instead.

        Returns:
            str: Status message about the step execution
        """
        if self.is_complete:
            return "Task completed"

        # Ensure plan is initialized if we have an initial prompt
        await self._ensure_plan_initialized()

        # If no plan exists, cannot step
        if not self.plan:
            return "No plan available. Use chat() to create a task plan first."

        # Execute based on parallel execution setting
        if self.parallel_execution:
            return await self._execute_parallel_step(self.max_concurrent_tasks)
        else:
            return await self._execute_single_step()

