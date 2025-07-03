"""
Task execution class - the primary interface for AgentX task execution.

Clean API:
    # One-shot execution (Lead-driven)
    await execute_task(prompt, config_path)
    
    # Step-by-step execution (Lead-driven)
    task = start_task(prompt, config_path)
    await task.run()
"""

from typing import Dict, List, Optional, Any, AsyncGenerator
from pathlib import Path
from datetime import datetime
import asyncio
import json
import time
import re

from .agent import Agent
from .orchestrator import Orchestrator
from .message import TaskStep, TextPart, ToolCallPart, ToolResultPart, Artifact
from .tool import ToolCall
from .config import TeamConfig, AgentConfig, BrainConfig
from ..config.team_loader import load_team_config
from ..config.agent_loader import load_agents_config
from ..config.prompt_loader import PromptLoader
from ..utils.logger import get_logger, setup_clean_chat_logging, setup_task_file_logging, set_streaming_mode
from ..utils.id import generate_short_id
from ..tool.manager import ToolManager
from ..builtin_tools.plan import PlanTool

logger = get_logger(__name__)


class Task:
    """
    Pure data container for task state and context.
    No execution logic - just holds the task data.
    """
    
    def __init__(self, team_config: TeamConfig, config_dir: Path, task_id: str = None, workspace_dir: Path = None):
        # Core task identity
        self.task_id = task_id or self._generate_task_id()
        self.team_config = team_config
        self.config_dir = config_dir
        self.workspace_dir = workspace_dir or Path("./workspace") / self.task_id
        
        # Instantiate PlanTool for this task's workspace
        self.plan_tool = PlanTool(workspace_path=str(self.workspace_dir))
        
        # Task execution state
        self.initial_prompt: Optional[str] = None
        self.is_complete: bool = False
        self.is_paused: bool = False
        self.created_at: datetime = datetime.now()
        self.is_resumed: bool = False  # Track if this is a resumed task
        
        # Task data
        self.history: List[TaskStep] = []
        self.artifacts: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        
        # Agent storage (will be populated by TaskExecutor)
        self.agents: Dict[str, Agent] = {}
        
        # Reference to executor for platform services
        self.executor: Optional['TaskExecutor'] = None
        
        # Setup workspace and check for existing state
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self._setup_workspace()
        
        # Load existing state if this is a resumed task
        self._load_existing_state()
        
        logger.info(f"🎯 Task {self.task_id} {'resumed' if self.is_resumed else 'initialized'}")
    
    def _load_existing_state(self):
        """Load existing task state if workspace already contains work."""
        state_file = self.workspace_dir / "artifacts" / "task_state.json"
        plan_file = self.workspace_dir / "artifacts" / "plan.md"
        
        # Check if this is an existing task workspace
        if state_file.exists() or plan_file.exists():
            self.is_resumed = True
            logger.info(f"📂 Detected existing workspace for task {self.task_id}")
            
            # Load state file if it exists
            if state_file.exists():
                try:
                    with open(state_file, 'r') as f:
                        state_data = json.load(f)
                    
                    self.initial_prompt = state_data.get('initial_prompt')
                    self.is_complete = state_data.get('is_complete', False)
                    self.is_paused = state_data.get('is_paused', False)
                    self.created_at = datetime.fromisoformat(state_data.get('created_at', datetime.now().isoformat()))
                    self.metadata = state_data.get('metadata', {})
                    
                    logger.info(f"📋 Loaded existing task state")
                except Exception as e:
                    logger.warning(f"Failed to load task state: {e}")
            
            # If plan exists but task is complete, mark as such
            if plan_file.exists() and self._is_plan_complete():
                self.is_complete = True
                logger.info(f"✅ Task {self.task_id} was already completed")

    def _is_plan_complete(self) -> bool:
        """Check if all steps in the plan are completed."""
        plan_file = self.workspace_dir / "artifacts" / "plan.md"
        if not plan_file.exists():
            return False
        
        try:
            with open(plan_file, 'r') as f:
                content = f.read()
            
            # Check for incomplete tasks
            incomplete_tasks = re.findall(r"-\s*\[\s*\]\s*(.*)", content)
            return len(incomplete_tasks) == 0
        except Exception:
            return False

    def save_state(self):
        """Save current task state for resuming later."""
        state_file = self.workspace_dir / "artifacts" / "task_state.json"
        
        state_data = {
            'task_id': self.task_id,
            'initial_prompt': self.initial_prompt,
            'is_complete': self.is_complete,
            'is_paused': self.is_paused,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
            'saved_at': datetime.now().isoformat()
        }
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            logger.info(f"💾 Task state saved for resuming")
        except Exception as e:
            logger.warning(f"Failed to save task state: {e}")

    def can_resume_with_prompt(self, new_prompt: str) -> bool:
        """Check if the task can be resumed with a different prompt."""
        if not self.is_resumed or not self.initial_prompt:
            return True  # New task or no existing prompt
        
        # Simple similarity check - you could enhance with semantic similarity
        return self.initial_prompt.lower().strip() == new_prompt.lower().strip()

    def get_resume_summary(self) -> str:
        """Get a summary of the existing work for resuming."""
        if not self.is_resumed:
            return "No existing work found."
        
        plan_file = self.workspace_dir / "artifacts" / "plan.md"
        summary = f"📂 Resuming task {self.task_id}\n"
        summary += f"🕐 Originally created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if self.initial_prompt:
            summary += f"📝 Original prompt: {self.initial_prompt[:100]}...\n"
        
        if plan_file.exists():
            try:
                with open(plan_file, 'r') as f:
                    content = f.read()
                
                completed_tasks = re.findall(r"-\s*\[x\]\s*(.*)", content)
                incomplete_tasks = re.findall(r"-\s*\[\s*\]\s*(.*)", content)
                
                summary += f"✅ Completed steps: {len(completed_tasks)}\n"
                summary += f"⏳ Remaining steps: {len(incomplete_tasks)}\n"
                
                if incomplete_tasks:
                    summary += f"🔜 Next step: {incomplete_tasks[0][:50]}...\n"
                
            except Exception as e:
                summary += f"⚠️ Could not read plan: {e}\n"
        
        return summary

    def get_agent(self, name: str):
        """Get agent by name with task context injected."""
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' not found in task")
        
        agent = self.agents[name]
        # Inject task reference into agent for direct access
        agent._task = self
        return agent
    
    def get_context(self) -> Dict[str, Any]:
        """Get complete task context for Lead decisions."""
        return {
            "task_id": self.task_id,
            "initial_prompt": self.initial_prompt,
            "is_complete": self.is_complete,
            "is_paused": self.is_paused,
            "created_at": self.created_at.isoformat(),
            "workspace_dir": str(self.workspace_dir),
            "available_agents": list(self.agents.keys()),
            "history_length": len(self.history),
            "artifacts": list(self.artifacts.keys()),
            "metadata": self.metadata
        }
    
    def add_step(self, step: TaskStep) -> None:
        """Add step to task history."""
        self.history.append(step)
    
    def complete_task(self) -> None:
        """Mark task as complete."""
        self.is_complete = True
        self.save_state()  # Save state when completing
        logger.info(f"✅ Task {self.task_id} completed")
    
    def add_artifact(self, name: str, content: Any, metadata: Dict[str, Any] = None) -> None:
        """Add artifact to task."""
        self.artifacts[name] = {
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now()
        }
        logger.info(f"📄 Task {self.task_id} added artifact '{name}'")
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        return generate_short_id()
    
    def _setup_workspace(self) -> None:
        """Setup task workspace directories."""
        (self.workspace_dir / "artifacts").mkdir(exist_ok=True)
        (self.workspace_dir / "logs").mkdir(exist_ok=True)
        (self.workspace_dir / "temp").mkdir(exist_ok=True)


class TaskExecutor:
    """
    TaskExecutor provides platform services and creates the Lead to manage execution.
    
    Responsibilities:
    - System initialization (storage, memory, search, tools)
    - Platform service provision to Lead and Agents
    - Lead-driven task execution only
    """
    
    def __init__(self, config_path: str, task_id: str = None, workspace_dir: Path = None):
        """Initialize TaskExecutor with config path and setup all systems."""
        # Load team configuration
        self.config_path = Path(config_path)
        self.team_config = load_team_config(str(self.config_path))
        
        self.task = Task(
            team_config=self.team_config,
            config_dir=self.config_path.parent,
            task_id=task_id,
            workspace_dir=workspace_dir
        )
        
        # Inject executor reference for platform services
        self.task.executor = self
        
        # Create task-level tool manager (unified registry + executor)
        self.tool_manager = ToolManager(task_id=self.task.task_id)
        
        # Initialize all systems
        self._initialize_systems()
        
        # Register task-specific tools AFTER systems are initialized
        self._register_tools()
        
        # Create agents with platform service access
        self._create_agents()
        
        # Setup clean logging for better chat experience
        setup_clean_chat_logging()
        
        # Setup workspace and task-specific logging
        self._setup_workspace()
        
        logger.info(f"✅ TaskExecutor initialized for task {self.task.task_id}")

    def _initialize_systems(self):
        """Initialize storage, search, memory systems."""
        # Initialize storage system first (needed for tools)
        self.storage = self._initialize_storage()
        
        # Initialize search system
        self.search = self._initialize_search()
        
        # Initialize memory system
        self.memory = self._initialize_memory()
        
        logger.debug("✅ TaskExecutor systems initialized")

    def _initialize_storage(self):
        """Initialize the storage system for the task."""
        try:
            from ..storage.factory import StorageFactory
            
            # Create workspace storage for the task
            workspace_storage = StorageFactory.create_workspace_storage(
                workspace_path=self.task.workspace_dir,
                use_git_artifacts=True
            )
            
            logger.info(f"Storage system initialized: {self.task.workspace_dir}")
            return workspace_storage
            
        except Exception as e:
            logger.warning(f"Failed to initialize storage system: {e}")
            return None
    
    def _initialize_search(self):
        """Initialize the search system for the task."""
        try:
            from ..search.search_manager import SearchManager
            
            # Get search config from team if available
            # For now, create a basic search manager
            search_manager = SearchManager()
            
            logger.info("Search system initialized")
            return search_manager
            
        except Exception as e:
            logger.warning(f"Failed to initialize search system: {e}")
            return None
    
    def _initialize_memory(self):
        """Initialize the memory system for the task."""
        try:
            from ..memory.factory import create_memory_backend
            
            # Get memory config from team if available
            memory_config = getattr(self.task.team_config, 'memory', None)
            
            if memory_config:
                # Handle simple memory config format (from YAML)
                if isinstance(memory_config, dict) and memory_config.get('enabled', False):
                    # Create default MemoryConfig for simple YAML format
                    from .config import MemoryConfig
                    backend = create_memory_backend(MemoryConfig())
                    logger.info("Memory system initialized with default configuration")
                    return backend
                # Handle full MemoryConfig object
                elif hasattr(memory_config, 'enabled') and memory_config.enabled:
                    backend = create_memory_backend(memory_config)
                    logger.info("Memory system initialized")
                    return backend
                else:
                    logger.debug("Memory system disabled in team config")
                    return None
            else:
                logger.debug("No memory configuration found")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to initialize memory system: {e}")
            return None
    
    def _create_agents(self):
        """Create agent instances following platform service pattern."""
        if not self.team_config or not self.team_config.agents:
            return

        for agent_config in self.team_config.agents:
            # Create agent without direct tool manager access
            agent_instance = Agent(config=agent_config)
            self.task.agents[agent_config.name] = agent_instance
            logger.info(f"✅ Created agent: {agent_config.name}")
        
        logger.info(f"🎯 Created {len(self.task.agents)} agents")

    async def run_agent(self, agent: Agent, prompt: str) -> Any:
        """Platform service method for Lead to run agents with tool access."""
        # Provide tool access through platform service
        agent.tool_manager = self.tool_manager
        
        # Execute agent turn using the correct method
        result = await agent.generate_response(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=agent.build_system_prompt(self.task.get_context())
        )
        
        # Clean up direct tool access (maintain platform boundary)
        agent.tool_manager = None
        
        return result

    async def execute_task(self, prompt: str, planner_agent: str = "planner", stream: bool = False):
        """Execute task to completion using Lead-driven execution only."""
        if stream:
            # Return streaming generator
            return self._stream_execute_task(prompt, planner_agent)
        else:
            # Execute non-streaming
            return await self._execute_task_non_streaming(prompt, planner_agent)

    async def _execute_task_non_streaming(self, prompt: str, planner_agent: str):
        """Execute task without streaming."""
        # Set initial prompt
        self.task.initial_prompt = prompt
        
        # Create Lead instance
        lead_instance = Orchestrator(self.task)
        
        logger.info(f"🚀 Starting Lead-driven execution for task {self.task.task_id}")
        
        # Non-streaming execution
        await lead_instance.run(planner_agent_name=planner_agent)
        return self.task

    async def _stream_execute_task(self, prompt: str, planner_agent: str):
        """Stream task execution progress."""
        # Set initial prompt
        self.task.initial_prompt = prompt
        
        # Create Lead instance
        lead_instance = Orchestrator(self.task)
        
        logger.info(f"🚀 Starting Lead-driven execution for task {self.task.task_id}")
        
        yield {"type": "start", "task_id": self.task.task_id, "lead": Orchestrator.__name__}
        
        # Lead execution (would need to be enhanced for streaming)
        await lead_instance.run(planner_agent_name=planner_agent)
        
        yield {"type": "complete", "task_id": self.task.task_id, "workspace": str(self.task.workspace_dir)}

    # Properties to access task state (clean interface)
    @property
    def is_complete(self) -> bool:
        return self.task.is_complete
    
    @property 
    def is_paused(self) -> bool:
        return self.task.is_paused
    
    # Properties to access initialized systems (platform services)
    @property
    def workspace_storage(self):
        """Access the workspace storage system."""
        return self.storage
    
    @property
    def search_manager(self):
        """Access the search manager."""
        return self.search

    @property
    def memory_backend(self):
        """Access the memory backend."""
        return self.memory

    def _register_tools(self) -> None:
        """Register all available tools with the task's tool manager."""
        # Register builtin tools
        from ..builtin_tools import register_builtin_tools
        register_builtin_tools(
            registry=self.tool_manager.registry,
            workspace_path=str(self.task.workspace_dir),
            memory_system=self.memory
        )
        
        # Register any custom tools from team config
        if hasattr(self.team_config, 'tools') and self.team_config.tools:
            for tool_config in self.team_config.tools:
                # TODO: Implement custom tool loading
                logger.debug(f"Custom tool loading not yet implemented: {tool_config}")
        
        logger.info(f"🔧 Registered {len(self.tool_manager.registry.tools)} tools")

    def register_tool(self, tool) -> None:
        """Register a single tool with the task's tool manager."""
        self.tool_manager.register_tool(tool)

    def _setup_workspace(self) -> None:
        """Setup workspace with task-specific configuration."""
        try:
            # Create workspace structure
            workspace_dir = Path(self.task.workspace_dir)
            workspace_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (workspace_dir / "artifacts").mkdir(exist_ok=True)
            (workspace_dir / "logs").mkdir(exist_ok=True)
            (workspace_dir / "temp").mkdir(exist_ok=True)
            
            # Setup task-specific logging
            self._setup_task_logging()
            
            logger.info(f"📁 Workspace setup complete: {workspace_dir}")
            
        except Exception as e:
            logger.warning(f"Failed to setup workspace: {e}")

    def _setup_task_logging(self) -> None:
        """Setup task-specific logging configuration."""
        try:
            # Create logs directory if it doesn't exist
            logs_dir = Path(self.task.workspace_dir) / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Setup file logging for this task
            log_file_path = logs_dir / "task.log"
            setup_task_file_logging(str(log_file_path))
            
            # Enable streaming mode for clean console output
            set_streaming_mode(True)
            
            logger.info(f"Task logging configured for {self.task.task_id} -> {log_file_path}")
            
        except Exception as e:
            logger.warning(f"Failed to setup task logging: {e}")


# Public API functions (Lead-driven only)
async def execute_task(prompt: str, config_path: str, planner_agent: str = "planner", stream: bool = False, task_id: str = None):
    """
    Execute a task to completion using Lead-driven architecture.
    
    Args:
        prompt: The initial task prompt
        config_path: Path to team configuration file
        planner_agent: Name of the agent to use for planning (default: "planner")
        stream: Whether to stream execution progress
        task_id: Optional task ID for resuming existing work (generated if not provided)
    
    Returns:
        Task object (non-streaming) or AsyncGenerator (streaming)
    """
    executor = TaskExecutor(config_path, task_id=task_id)
    
    # Handle task resuming logic
    if executor.task.is_resumed:
        logger.info(f"🔄 Resuming existing task {executor.task.task_id}")
        print(executor.task.get_resume_summary())
        
        # Check if we can resume with this prompt
        if not executor.task.can_resume_with_prompt(prompt):
            print(f"⚠️ Warning: New prompt differs from original task prompt")
            print(f"Original: {executor.task.initial_prompt[:100]}...")
            print(f"New: {prompt[:100]}...")
            print(f"📝 Continuing with new requirements - task will be extended")
            
            # NEVER reject user requests - allow continuation with new prompt
            if executor.task.is_complete:
                print(f"🔄 Task was completed, but user requests additional work - continuing")
                executor.task.is_complete = False  # Reset completion status
                executor.task.is_paused = False    # Ensure it's not paused
            
            # Update to new prompt for continuation
            executor.task.initial_prompt = prompt
            executor.task.save_state()  # Save updated state
    else:
        # New task - set the initial prompt
        executor.task.initial_prompt = prompt
        executor.task.save_state()  # Save initial state
    
    if stream:
        return executor.execute_task(prompt, planner_agent=planner_agent, stream=True)
    else:
        return await executor.execute_task(prompt, planner_agent=planner_agent, stream=False)

def start_task(prompt: str, config_path: str, planner_agent: str = "planner", task_id: str = None) -> 'TaskExecutor':
    """
    Start a task and return TaskExecutor for manual execution control.
    
    Args:
        prompt: The initial task prompt
        config_path: Path to team configuration file
        planner_agent: Name of the agent to use for planning
        task_id: Optional task ID (generated if not provided)
    
    Returns:
        TaskExecutor instance ready for execution
    """
    executor = TaskExecutor(config_path, task_id=task_id)
    executor.task.initial_prompt = prompt
    return executor