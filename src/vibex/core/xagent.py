"""
XAgent - The project's conversational representative

X is the interface between users and their projects. Each project has an X agent
that acts as its representative. When you need to interact with a project, you
talk to X. XAgent merges TaskExecutor and Orchestrator functionality into a 
single, user-friendly interface.

Key Features:
- Acts as the project's representative for all interactions
- Rich message handling with attachments and multimedia
- LLM-driven plan adjustment that preserves completed work
- Single point of contact for all user interactions
- Automatic workspace and tool management

API Design:
- chat(message) - Talk to X about the project (adjustments, Q&A, etc.)
- step() - Let X autonomously execute the next project step
"""

from __future__ import annotations
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, AsyncGenerator, Union, List
import json

from vibex.core.agent import Agent
from vibex.core.brain import Brain
from vibex.core.config import TeamConfig, BrainConfig, AgentConfig
from vibex.core.handoff_evaluator import HandoffEvaluator, HandoffContext
from vibex.core.message import (
    MessageQueue, ConversationHistory, Message, TaskStep, TextPart,
    ToolCallPart, ToolResultPart, StepStartPart, ReasoningPart
)
from vibex.core.message_builder import StreamingMessageBuilder
from vibex.core.plan import Plan
from vibex.core.task import Task, TaskStatus
from vibex.tool.manager import ToolManager
from vibex.utils.id import generate_short_id
from vibex.utils.logger import (
    get_logger,
    setup_clean_chat_logging,
    setup_task_file_logging,
    set_streaming_mode,
)
from vibex.config.team_loader import load_team_config
from vibex.utils.paths import get_project_root

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
        metadata: Optional[Dict[str, Any]] = None,
        user_message: Optional['Message'] = None,
        assistant_message: Optional['Message'] = None,
        message_id: Optional[str] = None,
        parts: Optional[List[Any]] = None
    ):
        self.text = text
        self.artifacts = artifacts or []
        self.preserved_steps = preserved_steps or []
        self.regenerated_steps = regenerated_steps or []
        self.plan_changes = plan_changes or {}
        self.metadata = metadata or {}
        self.user_message = user_message
        self.assistant_message = assistant_message
        self.message_id = message_id
        self.parts = parts or []


class XAgent(Agent):
    """
    XAgent - The project's conversational representative.

    XAgent (X) acts as the interface between users and their projects. When you
    need to interact with a project, you talk to its X agent. X combines 
    TaskExecutor's execution context management with Orchestrator's agent 
    coordination logic into a single, user-friendly interface.

    Key capabilities:
    - Acts as the project's representative for all interactions
    - Rich message handling (text, attachments, multimedia)
    - LLM-driven plan adjustment preserving completed work
    - Automatic workspace and tool management
    - Conversational project management

    Usage Pattern:
        ```python
        # Start a project
        x = await XAgent.start("Build a web app", "config/team.yaml")

        # Execute the project autonomously
        while not x.is_complete():
            response = await x.step()  # Autonomous execution
            print(response)

        # Chat for refinements and adjustments
        response = await x.chat("Make it more colorful")  # User conversation
        print(response)
        ```
    """

    def __init__(
        self,
        team_config: TeamConfig,
        project_id: Optional[str] = None,
        project_path: Optional[Path] = None,
        initial_prompt: Optional[str] = None,
    ):
        # Generate unique project ID
        self.project_id = project_id or generate_short_id()

        # Accept only TeamConfig objects
        if not isinstance(team_config, TeamConfig):
            raise TypeError(f"team_config must be a TeamConfig object, got {type(team_config)}")
        self.team_config = team_config

        # Initialize project storage storage with appropriate caching
        from vibex.storage import ProjectStorageFactory
        
        # Determine cache provider based on environment
        cache_provider = None
        if os.getenv("ENABLE_REDIS_CACHE", "false").lower() == "true":
            cache_provider = "redis"
        elif os.getenv("ENABLE_MEMORY_CACHE", "false").lower() == "true":
            cache_provider = "memory"
        
        if project_path:
            # Use explicit project path (for resuming existing projects)
            from ..storage.project import ProjectStorage
            from ..storage.backends import LocalFileStorage
            
            project_path = Path(project_path)
            storage = LocalFileStorage(project_path)
            cache_backend = ProjectStorageFactory.get_cache_provider(cache_provider)
            
            # Create ProjectStorage with the provided path
            self.project_storage = ProjectStorage(
                project_path=project_path,
                project_id=self.project_id,
                file_storage=storage,
                use_git_artifacts=True,
                cache_backend=cache_backend
            )
        else:
            # Use standard project storage with default project root
            self.project_storage = ProjectStorageFactory.create_project_storage(
                project_root=get_project_root(),
                project_id=self.project_id,
                cache_provider=cache_provider
            )
        self._setup_task_logging()

        logger.info(f"Initializing XAgent for project: {self.project_id}")

        # Initialize components
        self.tool_manager = self._initialize_tools()
        self.message_queue = MessageQueue()
        self.specialist_agents = self._initialize_specialist_agents()
        self.history = ConversationHistory(project_id=self.project_id)
        
        # Initialize chat history storage
        from ..storage.chat_history import chat_history_manager
        self.chat_storage = chat_history_manager.get_storage(str(self.project_storage.project_path))

        # Initialize XAgent's own brain for orchestration decisions
        orchestrator_brain_config = self._get_orchestrator_brain_config()

        # Initialize parent Agent class with XAgent configuration
        super().__init__(
            config=self._create_xagent_config(),
            tool_manager=self.tool_manager
        )

        # Override brain with orchestrator-specific configuration
        self.brain = Brain.from_config(orchestrator_brain_config)

        # Project state
        self.plan: Optional[Plan] = None

        self.conversation_history: List[Message] = []
        self.initial_prompt = initial_prompt
        self._plan_initialized = False
        
        # Parallel execution settings
        self.parallel_execution = True  # Enable parallel execution by default
        self.max_concurrent_tasks = 3  # Default concurrency limit
        
        # Execution control
        self._execution_interrupted = False  # Flag to interrupt ongoing execution
        
        # Message queue for async processing
        self._message_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._consumer_task: Optional[asyncio.Task] = None
        self._is_processing = False
        
        # Response tracking
        self._response_futures: Dict[str, asyncio.Future] = {}
        
        # Mode tracking for messages
        self._message_modes: Dict[str, str] = {}

        # Initialize handoff evaluator if handoffs are configured
        self.handoff_evaluator = None
        if self.team_config.handoffs:
            self.handoff_evaluator = HandoffEvaluator(
                handoffs=self.team_config.handoffs,
                agents=self.specialist_agents
            )

        logger.info("XAgent initialized and ready for conversation")
        
        # Start the message consumer
        self._start_message_consumer()

    async def cleanup(self) -> None:
        """Clean up resources when XAgent is done."""
        # Set interruption flag
        self._execution_interrupted = True
        
        # Stop the consumer task
        if self._consumer_task and not self._consumer_task.done():
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped message consumer")
        
        # Cancel any pending response futures
        for future in self._response_futures.values():
            if not future.done():
                future.cancel()
        self._response_futures.clear()
        
        # Clean up any streaming operations in the brain
        if hasattr(self, 'brain') and hasattr(self.brain, 'cleanup'):
            await self.brain.cleanup()
    
    def _start_message_consumer(self) -> None:
        """Start the async message consumer loop."""
        if not self._consumer_task or self._consumer_task.done():
            self._consumer_task = asyncio.create_task(self._message_consumer_loop())
            logger.info("Started message consumer loop")
    
    async def _message_consumer_loop(self) -> None:
        """Continuously process messages from the queue."""
        logger.info("Message consumer loop started")
        
        while True:
            try:
                # Wait for a message from the queue
                message = await self._message_queue.get()
                logger.info(f"Processing message from queue: {message.content[:100]}...")
                
                # Set processing flag
                self._is_processing = True
                
                try:
                    # Process the message
                    response = await self._process_message(message)
                    
                    # Set the response future if one exists
                    response_future = self._response_futures.pop(message.id, None)
                    if response_future and not response_future.done():
                        response_future.set_result(response)
                        logger.info(f"Response sent for message {message.id}")
                    
                    # Clean up mode tracking
                    self._message_modes.pop(message.id, None)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    
                    # Set error response if future exists
                    response_future = self._response_futures.pop(message.id, None)
                    if response_future and not response_future.done():
                        error_response = XAgentResponse(
                            text=f"Error processing message: {str(e)}",
                            metadata={"error": str(e)}
                        )
                        response_future.set_result(error_response)
                    
                    # Clean up mode tracking
                    self._message_modes.pop(message.id, None)
                    
                finally:
                    self._is_processing = False
                    
            except asyncio.CancelledError:
                logger.info("Message consumer loop cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in message consumer: {e}", exc_info=True)
                await asyncio.sleep(1)  # Brief pause before retrying
    
    def _build_context_messages(self) -> List[Dict[str, Any]]:
        """Build context messages for the LLM including plan state."""
        messages = []
        
        # Add plan context if available
        if self.plan:
            plan_summary = f"Current goal: {self.project.goal if self.project else 'Unknown'}\n"
            plan_summary += f"Total tasks: {len(self.plan.tasks)}\n"
            plan_summary += f"Pending: {sum(1 for t in self.plan.tasks if t.status == 'pending')}\n"
            plan_summary += f"Completed: {sum(1 for t in self.plan.tasks if t.status == 'completed')}\n"
            
            messages.append({
                "role": "system",
                "content": f"Plan context:\n{plan_summary}"
            })
        
        # Add recent conversation history if needed
        # For now, just return the plan context
        return messages
    
    def _setup_task_logging(self) -> None:
        """Sets up file-based logging for the project."""
        log_dir = self.project_storage.get_project_path() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir / "project.log"
        setup_task_file_logging(str(log_file_path))

    def _initialize_tools(self) -> ToolManager:
        """Initializes the ToolManager and registers builtin tools."""
        tool_manager = ToolManager(
            project_id=self.project_id,
            project_path=str(self.project_storage.get_project_path())
        )
        logger.debug("ToolManager initialized.")
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
        from vibex.core.config import AgentConfig
        from pathlib import Path

        # Use the comprehensive XAgent system prompt
        xagent_prompt_path = Path(__file__).parent.parent / "presets" / "agents" / "xagent.md"

        return AgentConfig(
            name="X",
            description="XAgent - The lead orchestrator and strategic planner for VibeX",
            prompt_file=str(xagent_prompt_path),
            tools=[],  # XAgent coordinates but doesn't use tools directly
            enable_memory=True,
            max_consecutive_replies=50
        )

    async def _initialize_with_prompt(self, prompt: str) -> None:
        """Initialize XAgent with an initial prompt and load/create plan."""
        self.initial_prompt = prompt

        # Try to load existing plan from project
        if self.project:
            await self.project.load_state()
            if self.project.plan:
                self.plan = self.project.plan
                logger.info("Loaded existing plan from project")

        # Generate new plan if none exists
        if not self.plan:
            self.plan = await self._generate_plan(prompt)
            await self._persist_plan()

    async def _ensure_plan_initialized(self) -> None:
        """Ensure plan is initialized - either from initial prompt or by loading existing plan."""
        if self._plan_initialized:
            return
            
        # If we have an initial prompt, use it to initialize
        if self.initial_prompt:
            await self._initialize_with_prompt(self.initial_prompt)
            self._plan_initialized = True
        # Otherwise, try to load existing plan from project
        elif not self.plan and self.project:
            await self.project.load_state()
            if self.project.plan:
                self.plan = self.project.plan
                logger.info("Loaded existing plan from project")
                self._plan_initialized = True

    async def chat(self, message: Union[str, Message], mode: str = "agent") -> XAgentResponse:
        """
        Queue a message for processing and wait for response.
        
        This method adds messages to the queue and waits for the consumer
        to process them, ensuring proper message ordering and interruption.
        
        Args:
            message: The message to process
            mode: Execution mode - "agent" (multi-agent with plan) or "chat" (direct response)
            
        Returns:
            XAgentResponse with the processing result
        """
        # Convert string to Message if needed
        if isinstance(message, str):
            message = Message.user_message(message)
            
        # Store mode separately since Message doesn't have metadata
        self._message_modes[message.id] = mode
        
        # Create a future to track the response
        response_future = asyncio.Future()
        self._response_futures[message.id] = response_future
        
        # Add to queue
        await self._message_queue.put(message)
        logger.info(f"Message queued: {message.content[:100]}...")
        
        try:
            # Wait for the response (with timeout)
            response = await asyncio.wait_for(response_future, timeout=300.0)  # 5 minute timeout
            return response
        except asyncio.TimeoutError:
            # Clean up the future and mode tracking
            self._response_futures.pop(message.id, None)
            self._message_modes.pop(message.id, None)
            return XAgentResponse(
                text="Request timed out after 5 minutes",
                metadata={"error": "timeout", "mode": mode}
            )
    
    async def _process_message(self, message: Message) -> XAgentResponse:
        """
        Process a message from the queue.

        This handles the actual message processing logic:
        - User questions and clarifications
        - Plan adjustments and modifications
        - Rich messages with attachments
        - Preserving completed work while regenerating only necessary steps

        Args:
            message: The message to process (from queue)

        Returns:
            XAgentResponse with text, artifacts, and execution details
        """
        setup_clean_chat_logging()
        
        # Get mode from tracking dict
        mode = self._message_modes.get(message.id, "agent")

        # Add to conversation history
        self.conversation_history.append(message)
        self.history.add_message(message)
        
        # Persist message to chat history
        if hasattr(self, 'chat_storage'):
            asyncio.create_task(self.chat_storage.save_message(self.project_id, message))
        
        # If another message arrives while processing, it will be queued
        # The consumer loop will process it after this one completes

        logger.info(f"XAgent received chat message: {message.content[:100]}...")

        response = None
        try:
            # Handle empty message - means "figure out what to do next"
            if not message.content.strip():
                logger.info("Empty message received - X will figure out what to do next")
                logger.info(f"Plan exists: {self.plan is not None}, Tasks: {len(self.plan.tasks) if self.plan else 0}")
                if self.plan:
                    pending_count = sum(1 for t in self.plan.tasks if t.status == "pending")
                    logger.info(f"Pending tasks: {pending_count}")
                # If we have a plan, execute the next pending task
                if self.plan and any(task.status == "pending" for task in self.plan.tasks):
                    # Reset interruption flag before executing
                    self._execution_interrupted = False
                    
                    # Execute all pending tasks, checking for interruptions
                    execution_results = []
                    while self.plan and any(task.status == "pending" for task in self.plan.tasks):
                        # Check if we should stop for a new message
                        if not self._message_queue.empty():
                            logger.info("New message in queue, pausing execution")
                            execution_results.append("⏸️ Execution paused - new message received")
                            break
                            
                        # Execute one step
                        try:
                            step_result = await self.step()
                            execution_results.append(step_result)
                        except asyncio.CancelledError:
                            logger.info("Step execution cancelled")
                            execution_results.append("⏸️ Execution interrupted")
                            break
                        except Exception as e:
                            logger.error(f"Error during step: {e}")
                            execution_results.append(f"Error: {str(e)}")
                            break
                        
                        # Check if execution was interrupted
                        if self._execution_interrupted:
                            break
                            
                        # Break if completed or failed
                        if "completed successfully" in step_result or "Cannot continue" in step_result:
                            break
                    
                    response_text = "\n".join(execution_results) if execution_results else "No tasks executed"
                    response = XAgentResponse(
                        text=response_text,
                        metadata={"empty_message": True}
                    )
                # If no plan or all tasks complete, ask for direction
                else:
                    response = XAgentResponse(
                        text="I'm ready to help! What would you like me to work on? Please provide a specific task or goal.",
                        metadata={"empty_message": True, "has_plan": bool(self.plan)}
                    )
            
            # Handle based on mode
            if mode == "chat":
                # Chat mode - always respond directly without plan
                response = await self._handle_chat_mode(message)
            else:
                # Agent mode - handle message and execute plan
                await self._ensure_plan_initialized()
                
                # Non-empty message with existing plan
                if self.plan:
                    # The message goes to the LLM to interpret and respond
                    # The LLM's response IS the action - no keyword detection
                    response = await self._handle_agent_message(message)
                    
                    # After responding, check if there are pending tasks and no new messages
                    # This allows natural flow: respond first, then continue execution if appropriate
                    if (self.plan and 
                        any(task.status == "pending" for task in self.plan.tasks) and
                        self._message_queue.empty()):
                        
                        logger.info("Continuing execution after message handling")
                        
                        # Reset interruption flag before executing
                        self._execution_interrupted = False
                        
                        # Execute one step at a time, checking for interruptions
                        execution_results = []
                        try:
                            step_result = await self.step()
                            execution_results.append(step_result)
                        except asyncio.CancelledError:
                            logger.info("Initial execution cancelled")
                            execution_results.append("⏸️ Execution interrupted")
                        except Exception as e:
                            logger.error(f"Error during initial step: {e}")
                            execution_results.append(f"Error: {str(e)}")
                        
                        # Only continue if no new messages
                        while (self.plan and 
                               any(task.status == "pending" for task in self.plan.tasks) and
                               self._message_queue.empty() and
                               not self._execution_interrupted):
                            
                            # Break if completed or failed
                            if "completed successfully" in step_result or "Cannot continue" in step_result:
                                break
                            
                            try:
                                # Execute next step with proper cancellation handling
                                step_result = await self.step()
                                execution_results.append(step_result)
                            except asyncio.CancelledError:
                                logger.info("Execution cancelled due to interruption")
                                execution_results.append("⏸️ Execution interrupted")
                                break
                            except Exception as e:
                                logger.error(f"Error during step execution: {e}")
                                execution_results.append(f"Error: {str(e)}")
                                break
                        
                        # Append execution results to the response
                        if execution_results:
                            execution_text = "\n\n" + "\n".join(execution_results)
                            response = XAgentResponse(
                                text=response.text + execution_text,
                                metadata=response.metadata
                            )
                else:
                    # No plan yet - create one based on the message
                    response = await self._handle_new_task_request(message)

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            response = XAgentResponse(
                text=f"I encountered an error processing your message: {str(e)}",
                metadata={"error": str(e)}
            )
        
        # Persist assistant response to chat history
        if response and response.text:
            # Create assistant message with parts if available
            assistant_message = Message.assistant_message(
                response.text, 
                parts=response.parts if hasattr(response, 'parts') and response.parts else None
            )
            # Use consistent message ID if available from streaming
            if hasattr(response, 'message_id') and response.message_id:
                assistant_message.id = response.message_id
            self.conversation_history.append(assistant_message)
            self.history.add_message(assistant_message)
            
            # Persist to storage
            if hasattr(self, 'chat_storage'):
                asyncio.create_task(self.chat_storage.save_message(self.project_id, assistant_message))
            
            # Send complete message with parts via SSE
            try:
                from ..server.streaming import send_message_object
                asyncio.create_task(send_message_object(self.project_id, assistant_message))
            except ImportError:
                pass
            
            # Add messages to response
            response.user_message = message
            response.assistant_message = assistant_message
                
        return response

    async def _stream_full_response(self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None) -> tuple[str, str, List[Any]]:
        """Stream full response using Brain's streaming capabilities.
        
        Returns:
            tuple: (accumulated_text, message_id, parts) where message_id is used for both streaming and final message
        """
        # Create message builder
        builder = StreamingMessageBuilder(role="assistant")
        message_id = builder.message_id
        
        logger.info(f"[STREAMING] Starting streaming response for task {self.project_id} with message_id {message_id}")
        
        try:
            # Import streaming functions (avoid circular import)
            from ..server.streaming import (
                send_tool_call_start, send_tool_call_result,
                send_message_part, event_stream_manager
            )
            
            # Send message start event
            logger.info(f"[STREAMING] Sending message_start event: message_id={message_id}, role=assistant")
            await event_stream_manager.send_event(
                self.project_id,
                "message_start",
                {"message_id": message_id, "role": "assistant"}
            )
            
            # Use the agent's streaming loop
            async for chunk in self.stream_response(
                messages=messages,
                system_prompt=system_prompt
            ):
                # Handle different chunk types from Agent
                if isinstance(chunk, dict):
                    chunk_type = chunk.get("type")
                    
                    if chunk_type == "content":
                        # Handle text content chunks
                        chunk_text = chunk.get("content", "")
                        if chunk_text:  # Only process non-empty chunks
                            builder.add_text_delta(chunk_text)
                            logger.debug(f"[STREAMING] Received text chunk: '{chunk_text[:50]}{'...' if len(chunk_text) > 50 else ''}' (length: {len(chunk_text)})")
                            
                            # Send text delta event
                            try:
                                part_index = len(builder.parts) - 1 if builder.parts else 0
                                logger.debug(f"[STREAMING] Sending part_delta for text: message_id={message_id}, part_index={part_index}, delta_length={len(chunk_text)}")
                                await event_stream_manager.send_event(
                                    self.project_id,
                                    "part_delta",
                                    {
                                        "message_id": message_id,
                                        "part_index": part_index,  # Current text part index
                                        "delta": chunk_text,
                                        "type": "text"
                                    }
                                )

                            except Exception as e:
                                logger.error(f"[STREAMING] Error sending text chunk: {e}")
                    
                    elif chunk_type == "tool_call":
                        # Tool call being executed
                        tool_name = chunk.get("name", "unknown")
                        tool_args = chunk.get("arguments", {})
                        tool_call_id = generate_short_id()
                        
                        logger.info(f"[STREAMING] Tool call started: {tool_name}")
                        
                        # Parse args if string
                        parsed_args = json.loads(tool_args) if isinstance(tool_args, str) else tool_args
                        
                        # Add tool call part and get its index
                        part_index = builder.add_tool_call(
                            tool_call_id=tool_call_id,
                            tool_name=tool_name,
                            args=parsed_args
                        )
                        
                        logger.info(f"[STREAMING] Added tool call part: tool={tool_name}, part_index={part_index}, tool_call_id={tool_call_id}")
                        
                        # Send part complete event for tool call
                        try:
                            tool_call_part = builder.parts[part_index]
                            logger.info(f"[STREAMING] Sending part_complete for tool call: {tool_call_part.model_dump(by_alias=True)}")
                            await event_stream_manager.send_event(
                                self.project_id,
                                "part_complete",
                                {
                                    "message_id": message_id,
                                    "part_index": part_index,
                                    "part": tool_call_part.model_dump(by_alias=True)
                                }
                            )
                            # Legacy event
                            logger.info(f"[STREAMING] Sending legacy tool_call_start event")
                            await send_tool_call_start(
                                project_id=self.project_id,
                                tool_call_id=tool_call_id,
                                tool_name=tool_name,
                                args=parsed_args
                            )
                        except Exception as e:
                            logger.error(f"[STREAMING] Error sending tool call start: {e}")
                    
                    elif chunk_type == "tool_result":
                        # Tool result received
                        tool_name = chunk.get("name", "unknown")
                        success = chunk.get("success", False)
                        result_content = chunk.get("content", "")
                        
                        logger.info(f"[STREAMING] Tool result: {tool_name} - success: {success}")
                        
                        # Find corresponding tool call ID
                        tool_call_id = None
                        for tc_id, tc_part in builder.pending_tool_calls.items():
                            if tc_part.toolName == tool_name:
                                tool_call_id = tc_id
                                break
                        
                        if not tool_call_id:
                            tool_call_id = generate_short_id()
                        
                        # Add tool result part
                        part_index = builder.add_tool_result(
                            tool_call_id=tool_call_id,
                            tool_name=tool_name,
                            result=result_content,
                            is_error=not success
                        )
                        
                        logger.info(f"[STREAMING] Added tool result part: tool={tool_name}, part_index={part_index}, tool_call_id={tool_call_id}, result_length={len(str(result_content))}")
                        
                        # Send part complete event for tool result
                        try:
                            tool_result_part = builder.parts[part_index]
                            logger.info(f"[STREAMING] Sending part_complete for tool result: {tool_result_part.model_dump(by_alias=True)[:200]}...")
                            await event_stream_manager.send_event(
                                self.project_id,
                                "part_complete",
                                {
                                    "message_id": message_id,
                                    "part_index": part_index,
                                    "part": tool_result_part.model_dump(by_alias=True)
                                }
                            )
                            # Legacy event
                            logger.info(f"[STREAMING] Sending legacy tool_call_result event")
                            await send_tool_call_result(
                                project_id=self.project_id,
                                tool_call_id=tool_call_id,
                                tool_name=tool_name,
                                result=result_content,
                                is_error=not success
                            )
                        except Exception as e:
                            logger.error(f"[STREAMING] Error sending tool result: {e}")
                    
                    elif chunk_type == "error":
                        # Handle error chunks
                        error_content = chunk.get("content", "Unknown error")
                        logger.error(f"[STREAMING] Error chunk received: {error_content}")
                        
                        # Add error part
                        part_index = builder.add_error(error_content)
                        
                        try:
                            error_part = builder.parts[part_index]
                            await event_stream_manager.send_event(
                                self.project_id,
                                "part_complete",
                                {
                                    "message_id": message_id,
                                    "part_index": part_index,
                                    "part": error_part.model_dump(by_alias=True)
                                }
                            )
                            # Legacy error event
                            await send_stream_chunk(
                                project_id=self.project_id,
                                chunk="",
                                message_id=message_id,
                                is_final=True,
                                error=error_content
                            )
                        except Exception as e:
                            logger.error(f"[STREAMING] Error sending error chunk: {e}")
                        break
                elif isinstance(chunk, str):
                    # Handle plain string chunks (backward compatibility)
                    builder.add_text_delta(chunk)
            
            # Build final message
            message = builder.build()
            accumulated_text = message.content
            parts = message.parts
            
            # Send message complete event
            try:
                logger.info(f"[STREAMING] Sending message_complete event: message_id={message.id}, parts_count={len(message.parts)}, content_length={len(message.content)}")
                await event_stream_manager.send_event(
                    self.project_id,
                    "message_complete",
                    {
                        "message": message.model_dump(by_alias=True)
                    }
                )
                # Legacy final chunk
                await send_stream_chunk(
                    project_id=self.project_id,
                    chunk="",
                    message_id=message_id,
                    is_final=True
                )
                logger.info(f"[STREAMING] Sent message complete for {message_id} with {len(parts)} parts")
            except Exception as e:
                logger.error(f"[STREAMING] Error sending final events: {e}")
                
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            # Send error chunk via SSE
            try:
                from ..server.streaming import send_stream_chunk
                await send_stream_chunk(
                    project_id=self.project_id,
                    chunk="",
                    message_id=message_id,
                    is_final=True,
                    error=str(e)
                )
            except Exception as send_error:
                logger.error(f"[STREAMING] Error sending error chunk: {send_error}")
            
            # Fallback to non-streaming
            response = await self.brain.generate_response(
                messages=messages,
                system_prompt=system_prompt
            )
            accumulated_text = response.content or ""
        
        return accumulated_text, message_id, parts

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
1. Is this a command to execute/continue the current plan?
2. Does this message require adjusting the current plan?
3. Is this an informational query (asking about status, sources, methodology)?
4. If plan adjustment is needed, which specific tasks should be regenerated?
5. What completed work should be preserved?

Respond with a JSON object:
{{
  "is_execution_command": boolean,
  "requires_plan_adjustment": boolean,
  "is_informational": boolean,
  "is_new_task": boolean,
  "affected_tasks": ["list of task IDs that need regeneration"],
  "preserved_tasks": ["list of task IDs to preserve"],
  "adjustment_type": "regenerate|add_projects|modify_goals|style_change",
  "reasoning": "explanation of the analysis"
}}
"""

        response = await self.brain.generate_response(
            messages=[{"role": "user", "content": analysis_prompt}],
            system_prompt=self.build_system_prompt({"project_id": self.project_id}),
            json_mode=True
        )

        try:
            if response.content is None:
                raise ValueError("Response content is None")
            result: Dict[str, Any] = json.loads(response.content)
            return result
        except (json.JSONDecodeError, ValueError):
            # Fallback to simple heuristics
            message_lower = message.content.lower()
            return {
                "is_execution_command": any(word in message_lower 
                                          for word in ["execute", "continue", "run", "go", "start", "proceed"]),
                "requires_plan_adjustment": any(word in message_lower
                                               for word in ["regenerate", "redo", "change", "update", "revise"]),
                "is_informational": any(word in message_lower
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
                    logger.info(f"Reset task '{task.action}' to pending for regeneration")

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

        # Stream the response
        response_text, message_id = await self._stream_full_response(
            messages=[{"role": "user", "content": context_prompt}],
            system_prompt=self.build_system_prompt({"project_id": self.project_id})
        )

        return XAgentResponse(
            text=response_text,
            metadata={"query_type": "informational"},
            message_id=message_id
        )

    async def _handle_new_task_request(self, message: Message) -> XAgentResponse:
        """Handle new task requests when no plan exists."""
        # Create a new plan
        self.plan = await self._generate_plan(message.content)
        await self._persist_plan()

        return XAgentResponse(
            text=f"I've created a plan for your task: {self.project.goal if self.project else 'Unknown'}\n\n"
                 f"The plan includes {len(self.plan.tasks)} tasks.\n\n"
                 f"To execute the plan, you can:\n"
                 f"- Say 'continue', 'execute', or 'run' to start execution\n"
                 f"- Send an empty message to execute the next step\n"
                 f"- Or continue chatting to refine the plan first",
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

        # Stream the response
        response_text, message_id = await self._stream_full_response(
            messages=[{"role": "user", "content": context_prompt}],
            system_prompt=self.build_system_prompt({"project_id": self.project_id})
        )

        return XAgentResponse(
            text=response_text,
            metadata={"query_type": "conversational"},
            message_id=message_id
        )

    async def _handle_agent_message(self, message: Message) -> XAgentResponse:
        """
        Handle a message in agent mode - let the LLM interpret and respond.
        No keyword detection or rule-based logic.
        """
        messages = self._build_context_messages()
        messages.append({"role": "user", "content": message.content})
        
        # Simple prompt - let the LLM be intelligent
        system_prompt = f"""You are the project's X agent. You're managing the execution of a plan.

Current project goal: {self.project.goal if self.project else 'Unknown'}
Plan status: {len([t for t in self.plan.tasks if t.status == 'pending'])} pending, {len([t for t in self.plan.tasks if t.status == 'completed'])} completed

Respond naturally to the user's message. Be concise and helpful."""
        
        # Get response from brain
        response_text, msg_id, parts = await self._stream_full_response(messages, system_prompt)
        
        return XAgentResponse(
            text=response_text,
            metadata={"message_id": msg_id, "mode": "agent"}
        )
    
    async def _handle_chat_mode(self, message: Message) -> XAgentResponse:
        """Handle messages in chat mode - direct LLM response without plan."""
        # Build context for direct response
        context_prompt = f"""
You are a helpful AI assistant. Respond directly to the user's message without creating or executing plans.

USER MESSAGE: {message.content}

CONVERSATION HISTORY:
{self._get_conversation_summary()}

Please provide a direct, helpful response to the user's message.
"""

        # Stream the response
        response_text, message_id = await self._stream_full_response(
            messages=[{"role": "user", "content": context_prompt}],
            system_prompt=self.build_system_prompt({"project_id": self.project_id})
        )

        return XAgentResponse(
            text=response_text,
            metadata={"mode": "chat", "query_type": "direct_response"},
            message_id=message_id
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
      "action": "string - the action to be performed",
      "assigned_to": "string - agent name from available agents",
      "dependencies": ["array of task IDs this depends on"],
      "status": "pending"
    }}
  ]
}}
"""

        response = await self.brain.generate_response(
            messages=[{"role": "user", "content": planning_prompt}],
            system_prompt=self.build_system_prompt({"project_id": self.project_id}),
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
            if document_outline and self.project_storage:
                try:
                    await self.project_storage.store_artifact(
                        name="document_outline.md",
                        content=document_outline,
                        content_type="text/markdown",
                        metadata={"created_by": "XAgent", "purpose": "document_structure"},
                        commit_message="Created document outline for project execution"
                    )
                    logger.info("Saved document outline to project storage")
                except Exception as e:
                    logger.warning(f"Failed to save document outline: {e}")

            return plan
        except Exception as e:
            logger.error(f"Failed to generate plan: {e}")
            # Create a simple fallback plan
            return Plan(
                goal=goal,
                tasks=[
                    Task(
                        id="task_1",
                        action="Complete the requested task",
                        assigned_to=next(iter(self.specialist_agents.keys())),
                        dependencies=[],
                        status="pending"
                    )
                ]
            )

    async def _execute_single_step(self) -> str:
        """Execute a single step of the plan."""
        if not self.plan:
            return "No plan available for execution."
            
        # Check for interruption
        if self._execution_interrupted:
            logger.info("Execution interrupted by new message")
            return "⏸️ Execution paused - new message received"

        # Check if plan is already complete
        if self.plan.is_complete():
            self.is_complete_flag = True
            return "🎉 All tasks completed successfully!"

        # Find next actionable task
        next_task = self.plan.get_next_actionable_task()
        if not next_task:
            if self.plan.has_failed_tasks():
                self.is_complete_flag = True
                return "Cannot continue: some tasks have failed"
            else:
                return "⏳ No actionable tasks available (waiting for dependencies)"

        # Execute the task
        try:
            logger.info(f"Executing task: {next_task.action}")
            
            # Mark task as in progress and send start event
            next_task.status = "running"
            await self._persist_plan()
            
            # Send task start event
            try:
                from ..server.streaming import send_task_update
                await send_task_update(
                    project_id=self.project_id,
                    status="running",
                    result={"task": next_task.action, "task_id": next_task.id}
                )
            except ImportError:
                # Streaming not available in this context
                pass
            
            result = await self._execute_single_task(next_task)

            # Update task status
            next_task.status = "completed"
            await self._persist_plan()
            
            # Send completion event
            try:
                from ..server.streaming import send_task_update
                await send_task_update(
                    project_id=self.project_id,
                    status="completed",
                    result={"task": next_task.action, "result": result}
                )
            except ImportError:
                # Streaming not available in this context
                pass

            # Check if this was the last task
            if self.plan.is_complete():
                try:
                    from ..server.streaming import send_task_update
                    await send_task_update(
                        project_id=self.project_id,
                        status="completed",
                        result={"message": "All tasks completed successfully!"}
                    )
                except ImportError:
                    pass
                return {
                    "task": next_task.action,
                    "result": result,
                    "status": "completed",
                    "all_tasks_completed": True
                }
            else:
                return {
                    "task": next_task.action,
                    "result": result,
                    "status": "completed"
                }

        except Exception as e:
            logger.error(f"Task failed: {next_task.action} - {e}")
            next_task.status = "failed"
            await self._persist_plan()
            
            # Send failure event
            try:
                from ..server.streaming import send_task_update
                await send_task_update(
                    project_id=self.project_id,
                    status="failed",
                    result={"error": str(e), "task": next_task.action}
                )
            except ImportError:
                # Streaming not available in this context
                pass

            if next_task.on_failure == "halt":
                return f"{next_task.action}: Failed - {e}\n\nTask execution halted."
            else:
                return f"{next_task.action}: Failed but continuing - {e}"

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
            if self.is_complete():
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
            self.is_complete_flag = True
            return "🎉 All tasks completed successfully!"

        # Find all actionable tasks for parallel execution
        actionable_tasks = self.plan.get_all_actionable_tasks(max_tasks=max_concurrent)
        
        if not actionable_tasks:
            if self.plan.has_failed_tasks():
                return "Cannot continue: some tasks have failed"
            else:
                return "⏳ No actionable tasks available (waiting for dependencies)"

        # If only one task, fall back to sequential execution
        if len(actionable_tasks) == 1:
            return await self._execute_single_step()

        # Execute tasks in parallel
        logger.info(f"Executing {len(actionable_tasks)} tasks in parallel")
        
        # Mark all tasks as in_progress to prevent re-execution and send start events
        for task in actionable_tasks:
            task.status = "running"
            
            # Send task start event
            try:
                from ..server.streaming import send_task_update
                await send_task_update(
                    project_id=self.project_id,
                    status="running",
                    result={"task": task.action, "task_id": task.id}
                )
            except ImportError:
                # Streaming not available in this context
                pass
        
        try:
            # Create coroutines for parallel execution
            task_coroutines = []
            for task in actionable_tasks:
                logger.info(f"Starting parallel task: {task.action}")
                task_coroutines.append(self._execute_single_task(task))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*task_coroutines, return_exceptions=True)
            
            # Process results and update task statuses
            completion_messages = []
            failed_tasks = []
            
            for i, (task, result) in enumerate(zip(actionable_tasks, results)):
                if isinstance(result, Exception):
                    # Task failed
                    logger.error(f"Parallel task failed: {task.action} - {result}")
                    task.status = "failed"
                    failed_tasks.append(task)
                    
                    if task.on_failure == "halt":
                        completion_messages.append(f"{task.action}: Failed - {result}")
                        # Mark remaining tasks as failed too
                        for remaining_task in actionable_tasks[i+1:]:
                            remaining_task.status = "failed"
                        break
                    else:
                        completion_messages.append(f"{task.action}: Failed but continuing - {result}")
                else:
                    # Task succeeded
                    task.status = "completed"
                    completion_messages.append(f"{task.action}: {result}")
            
            # Persist plan after parallel execution
            await self._persist_plan()
            
            # Check if this completed all tasks
            if self.plan.is_complete():
                completion_messages.append("🎉 All tasks completed successfully!")
            
            # If we had halt failures, mark as complete
            if failed_tasks and any(task.on_failure == "halt" for task in failed_tasks):
                completion_messages.append("Task execution halted due to critical failure.")
            
            return "\n".join(completion_messages)
            
        except Exception as e:
            # Rollback task statuses on unexpected failure
            logger.error(f"Parallel execution failed: {e}")
            for task in actionable_tasks:
                task.status = "pending"  # Reset to allow retry
            await self._persist_plan()
            return f"Parallel execution failed: {e}"

    async def _execute_single_task(self, task: Task) -> str:
        """Execute a single task using the appropriate specialist agent."""
        # Get the assigned agent
        if task.assigned_to is None:
            raise ValueError("Task has no assigned agent")
        agent = self.specialist_agents.get(task.assigned_to)
        if not agent:
            raise ValueError(f"Agent '{task.assigned_to}' not found")

        # Send task start event
        try:
            from ..server.streaming import send_agent_status, send_message_object
            from vibex.core.message import Message
            await send_agent_status(
                project_id=self.project_id,
                xagent_id=task.assigned_to,
                status="starting",
                progress=0
            )
            
            # Send task briefing as system message
            system_message = Message.system_message(f"Starting task: {task.action}")
            await send_message_object(self.project_id, system_message)
            # Persist the message
            await self.chat_storage.save_message(self.project_id, system_message)
        except ImportError:
            # Streaming not available in this context
            pass

        # Task structure contains implicit document outline
        outline_reference = ""

        # Prepare task briefing
        briefing = [
            {
                "role": "system",
                "content": f"""You are being assigned a specific task as part of a larger plan.

TASK: {task.action}

Complete this specific task using your available tools. Save any outputs that other agents might need as files in the project storage.

Original user request: {self.initial_prompt or "No initial prompt provided"}{outline_reference}
"""
            },
            {
                "role": "user",
                "content": f"Please complete this task: {task.action}"
            }
        ]

        # Check if we should stream the response
        # Enable streaming if we're in a streaming context (e.g., API call)
        stream_mode = hasattr(self, '_stream_mode') and self._stream_mode
        
        # Also check if event_stream_manager is available (indicates we're in API context)
        try:
            from ..server.streaming import event_stream_manager
            if event_stream_manager and self.project_id:
                stream_mode = True
        except ImportError:
            stream_mode = False
        
        if stream_mode:
            # Use streaming for real-time updates
            try:
                from ..server.streaming import event_stream_manager
                from vibex.core.message_builder import StreamingMessageBuilder
                
                logger.info(f"[TASK] Streaming response for task: {task.action}")
                logger.info(f"[TASK] Project ID: {self.project_id}, Agent: {agent.name if hasattr(agent, 'name') else task.assigned_to}")
                
                # Create a message builder for streaming
                builder = StreamingMessageBuilder(role="assistant")
                message_id = builder.message_id
                
                # Send message start event
                await event_stream_manager.send_event(
                    self.project_id,
                    "message_start",
                    {"message_id": message_id, "role": "assistant"}
                )
                
                # Stream the response
                response_parts = []
                async for chunk in agent.stream_response(messages=briefing):
                    response_parts.append(chunk)
                    
                    # Handle different chunk types
                    if isinstance(chunk, dict):
                        chunk_type = chunk.get("type", "content")
                        
                        if chunk_type == "content":
                            # Text content
                            text = chunk.get("content", "")
                            if text:
                                builder.add_text_delta(text)
                                await event_stream_manager.send_event(
                                    self.project_id,
                                    "part_delta",
                                    {
                                        "message_id": message_id,
                                        "part_index": len(builder.parts) - 1 if builder.parts else 0,
                                        "delta": text,
                                        "type": "text"
                                    }
                                )
                        
                        elif chunk_type == "tool_call":
                            # Tool call chunk
                            tool_name = chunk.get("name", "unknown")
                            tool_args = chunk.get("args", {})
                            tool_call_id = chunk.get("tool_call_id", generate_short_id())
                            
                            logger.info(f"[TASK] Tool call during task: {tool_name}")
                            logger.info(f"[TASK] Tool args: {json.dumps(tool_args)[:200]}...")
                            logger.info(f"[TASK] Current parts count: {len(builder.parts)}")
                            
                            part_index = builder.add_tool_call(
                                tool_call_id=tool_call_id,
                                tool_name=tool_name,
                                args=tool_args
                            )
                            
                            logger.info(f"[TASK] Sending tool call part_complete event: part_index={part_index}")
                            await event_stream_manager.send_event(
                                self.project_id,
                                "part_complete",
                                {
                                    "message_id": message_id,
                                    "part_index": part_index,
                                    "part": builder.parts[part_index].model_dump(by_alias=True)
                                }
                            )
                            logger.info(f"[TASK] Tool call part_complete event sent successfully")
                        
                        elif chunk_type == "tool_result":
                            # Tool result chunk
                            tool_name = chunk.get("name", "unknown")
                            result = chunk.get("content", "")
                            success = chunk.get("success", False)
                            
                            # Find tool call ID
                            tool_call_id = None
                            for tc_id, tc_part in builder.pending_tool_calls.items():
                                if tc_part.toolName == tool_name:
                                    tool_call_id = tc_id
                                    break
                            
                            if not tool_call_id:
                                tool_call_id = generate_short_id()
                            
                            part_index = builder.add_tool_result(
                                tool_call_id=tool_call_id,
                                tool_name=tool_name,
                                result=result,
                                is_error=not success
                            )
                            
                            await event_stream_manager.send_event(
                                self.project_id,
                                "part_complete",
                                {
                                    "message_id": message_id,
                                    "part_index": part_index,
                                    "part": builder.parts[part_index].model_dump(by_alias=True)
                                }
                            )
                    
                    elif isinstance(chunk, str):
                        # Plain string chunk
                        response_parts.append(chunk)
                        builder.add_text_delta(chunk)
                
                # Build final message
                message = builder.build()
                response = message.content
                
                # Send message complete event
                logger.info(f"[TASK] Sending message_complete event: message_id={message.id}, parts={len(message.parts)}")
                await event_stream_manager.send_event(
                    self.project_id,
                    "message_complete",
                    {"message": message.model_dump(by_alias=True)}
                )
                logger.info(f"[TASK] Message complete event sent successfully")
                
                # Persist the message
                await self.chat_storage.save_message(self.project_id, message)
                
            except Exception as e:
                logger.error(f"[TASK] Error during streaming: {e}")
                # Fall back to non-streaming
                response = await agent.generate_response(messages=briefing)
        else:
            # Non-streaming execution
            response = await agent.generate_response(messages=briefing)
            
            # Send agent response as message
            try:
                from ..server.streaming import send_message_object
                from vibex.core.message import Message
                agent_message = Message.assistant_message(response)
                await send_message_object(self.project_id, agent_message)
                # Persist the message
                await self.chat_storage.save_message(self.project_id, agent_message)
                
                # Send task completion status
                completion_message = Message.system_message(f"Completed task: {task.action}")
                await send_message_object(self.project_id, completion_message)
                await self.chat_storage.save_message(self.project_id, completion_message)
            except ImportError:
                # Streaming not available in this context
                pass

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

            if task.assigned_to is None:
                raise ValueError("Task has no assigned agent for handoff")
            context = HandoffContext(
                current_agent=task.assigned_to,
                task_result=response,
                task_goal=task.action,
                conversation_history=conversation_dicts,
                taskspace_files=[f["name"] for f in await self.project_storage.list_artifacts()]
            )

            next_agent = await self.handoff_evaluator.evaluate_handoffs(context)
            if next_agent and next_agent != task.assigned_to:
                # Create a follow-up task for the handoff
                handoff_task = Task(
                    id=f"handoff_{task.id}_{next_agent}",
                    action=f"Continue work with {next_agent}",
                    assigned_to=next_agent,
                    dependencies=[task.id],
                    status="pending"
                )

                # Add to plan dynamically
                if self.plan:
                    self.plan.tasks.append(handoff_task)
                    await self._persist_plan()

                    logger.info(f"Handoff task created: {task.assigned_to} -> {next_agent}")
                    response += f"\n\n🤝 Handing off to {next_agent} for continuation."

        return response

    async def _persist_plan(self) -> None:
        """Persist the current plan to project storage via Project class."""
        if not self.plan or not self.project:
            return

        try:
            # Update the project's plan field and persist project state
            self.project.plan = self.plan
            await self.project._persist_state()
            logger.debug("Plan persisted to project.json via Project class")
        except Exception as e:
            logger.error(f"Failed to persist plan: {e}")

    def _get_plan_summary(self) -> str:
        """Get a summary of the current plan status."""
        if not self.plan:
            return "No plan exists"

        total_tasks = len(self.plan.tasks)
        completed_tasks = len([t for t in self.plan.tasks if t.status == "completed"])
        failed_tasks = len([t for t in self.plan.tasks if t.status == "failed"])

        summary = f"Plan: {self.project.goal if self.project else 'Unknown'}\n"
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
        """Get a summary of available artifacts in project storage."""
        try:
            artifacts_dir = self.project_storage.get_project_path() / "artifacts"
            if not artifacts_dir.exists():
                return "No artifacts available"

            files = list(artifacts_dir.glob("*"))
            if not files:
                return "No artifacts available"

            return f"Available artifacts: {', '.join([f.name for f in files[:5]])}"
        except Exception:
            return "Unable to check artifacts"

    # Compatibility methods for existing TaskExecutor interface
    async def execute(self, prompt: str, stream: bool = False) -> AsyncGenerator[Task, None]:
        """Compatibility method for TaskExecutor.execute()."""
        response = await self.chat(prompt)

        # Create a Task message
        message = TaskStep(
            agent_name="X",
            parts=[TextPart(text=response.text)]
        )
        self.history.add_step(message)
        
        # Persist step to chat history
        import asyncio
        if hasattr(self, 'chat_storage'):
            asyncio.create_task(self.chat_storage.save_step(self.project_id, message))
        
        yield message

    def is_complete(self) -> bool:
        """Check if the project is complete."""
        if self.plan:
            return self.plan.is_complete()
        return False

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
    
    async def set_name(self, name: str) -> None:
        """Set a custom name for this XAgent/Project."""
        self._name = name
        if self.project:
            await self.project.set_name(name)
            logger.info(f"Updated project name to: {name}")
        else:
            logger.info(f"Updated XAgent name to: {name}")
    
    @property
    def goal(self) -> str:
        """Get the project goal."""
        if self.project:
            return self.project.goal
        return self.initial_prompt or ""
    
    @property
    def name(self) -> str:
        """Get the project name."""
        if hasattr(self, 'project') and self.project:
            return self.project.name
        return getattr(self, '_name', f"Project {self.project_id}")
    
    @name.setter
    def name(self, value: str) -> None:
        """Set the project name."""
        self._name = value

    async def step(self) -> str:
        """
        Execute one step of autonomous project execution.

        This method is for AUTONOMOUS TASK EXECUTION, not for user conversation.
        It moves the plan forward by executing the next available task.

        For user conversation and plan adjustments, use chat() method instead.

        Returns:
            str: Status message about the step execution
        """
        if self.is_complete():
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