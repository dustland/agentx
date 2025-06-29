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

from .agent import Agent
from .lead import Lead
from .message import TaskStep, TextPart, ToolCallPart, ToolResultPart, Artifact
from .tool import ToolCall
from .config import TeamConfig, AgentConfig, BrainConfig
from ..config.team_loader import load_team_config
from ..config.agent_loader import load_agents_config
from ..config.prompt_loader import PromptLoader
from ..utils.logger import get_logger, setup_clean_chat_logging
from ..utils.id import generate_short_id
from ..tool.manager import ToolManager

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
        
        # Task execution state
        self.initial_prompt: Optional[str] = None
        self.is_complete: bool = False
        self.is_paused: bool = False
        self.created_at: datetime = datetime.now()
        
        # Task data
        self.history: List[TaskStep] = []
        self.artifacts: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        
        # Agent storage (will be populated by TaskExecutor)
        self.agents: Dict[str, Agent] = {}
        
        # Reference to executor for platform services
        self.executor: Optional['TaskExecutor'] = None
        
        # Setup workspace
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self._setup_workspace()
        
        logger.info(f"🎯 Task {self.task_id} initialized")
    
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
        
        # Always create Lead (no conditional logic)
        self.lead_class = self.team_config.lead or Lead  # Default to framework Lead
        
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
        lead_instance = self.lead_class(self.task)
        
        logger.info(f"🚀 Starting Lead-driven execution for task {self.task.task_id}")
        
        # Non-streaming execution
        await lead_instance.run(planner_agent_name=planner_agent)
        return self.task

    async def _stream_execute_task(self, prompt: str, planner_agent: str):
        """Stream task execution progress."""
        # Set initial prompt
        self.task.initial_prompt = prompt
        
        # Create Lead instance
        lead_instance = self.lead_class(self.task)
        
        logger.info(f"🚀 Starting Lead-driven execution for task {self.task.task_id}")
        
        yield {"type": "start", "task_id": self.task.task_id, "lead": self.lead_class.__name__}
        
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
        from ..builtin_tools.registry import register_builtin_tools
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
            
            # Note: Due to framework logging architecture issues, 
            # task logs currently only go to console
            # See memory about logging system bugs
            
            logger.debug(f"Task logging configured for {self.task.task_id}")
            
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
        task_id: Optional task ID (generated if not provided)
    
    Returns:
        Task object (non-streaming) or AsyncGenerator (streaming)
    """
    executor = TaskExecutor(config_path, task_id=task_id)
    
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