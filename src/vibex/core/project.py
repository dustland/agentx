"""
Project module - the top-level container for VibeX work.

A Project represents a complete body of work that may involve multiple tasks,
agents, and execution steps. Each project is managed by an XAgent that serves
as its conversational representative.

Key concepts:
- Project: The overall work container (e.g., "Build a web app")
- Task: Individual execution units within a project (e.g., "Create backend API")
- TaskStep: Specific actions within a task (e.g., "Write authentication endpoint")

Example:
    # Start a new project
    project = await start_project(
        goal="Build a documentation website",
        config_path="config/team.yaml"
    )
    
    # The project's X agent manages execution
    response = await project.x_agent.chat("Make it mobile-friendly")
"""

from __future__ import annotations
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, List, Union, AsyncGenerator

from vibex.core.agent import Agent
from vibex.core.config import TeamConfig, AgentConfig, ProjectConfig
from vibex.core.message import MessageQueue, ConversationHistory, Message, TextPart
from vibex.core.plan import Plan
from vibex.core.task import Task, TaskStatus
from vibex.storage.project import ProjectStorage
from vibex.storage import ProjectStorageFactory
from vibex.config.team_loader import load_team_config
from vibex.tool.manager import ToolManager
from vibex.utils.id import generate_short_id
from vibex.utils.logger import get_logger
from vibex.utils.paths import get_project_root, get_project_path

if TYPE_CHECKING:
    from vibex.core.xagent import XAgent

logger = get_logger(__name__)


class Project:
    def __init__(
        self,
        project_id: str,
        config: ProjectConfig,
        history: ConversationHistory,
        message_queue: MessageQueue,
        agents: Dict[str, Agent],
        storage: ProjectStorage,
        goal: str,
        name: Optional[str] = None,
        x_agent: Optional['XAgent'] = None,
    ):
        self.project_id = project_id
        self.config = config
        self.history = history
        self.message_queue = message_queue
        self.agents = agents
        self.storage = storage
        self.goal = goal
        self.name = name or f"Project {project_id}"
        self.x_agent = x_agent
        
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        self.plan: Optional[Plan] = None
        
    def get_agent(self, name: str) -> Agent:
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' not found in project team.")
        return self.agents[name]
    
    def complete(self):
        """Mark project as complete - this is now derived from task status."""
        logger.info(f"Project {self.project_id} completed")
    
    def get_context(self) -> Dict[str, Any]:
        context = {
            "project_id": self.project_id,
            "goal": self.goal,
            "storage_path": str(self.storage.get_project_path()),
            "agents": list(self.agents.keys()),
            "history_length": len(self.history.messages),
            "created_at": self.created_at.isoformat(),
        }
        
        if self.plan:
            context["plan"] = {
                "goal": self.goal,
                "total_tasks": len(self.plan.tasks),
                "progress": self.plan.get_progress_summary(),
            }
            
        return context
    
    async def create_plan(self, plan: Plan) -> None:
        self.plan = plan
        await self._persist_state()
        logger.info(f"Created plan for project {self.project_id} with {len(plan.tasks)} tasks")
    
    async def update_plan(self, plan: Plan) -> None:
        self.plan = plan
        self.updated_at = datetime.now()
        await self._persist_state()
        logger.info(f"Updated plan for project {self.project_id}")
    
    async def set_name(self, name: str) -> None:
        """Set a custom name for this project."""
        self.name = name
        self.updated_at = datetime.now()
        await self._persist_state()
        logger.info(f"Updated project {self.project_id} name to: {name}")
    
    async def get_next_task(self) -> Optional[Task]:
        if not self.plan:
            return None
        return self.plan.get_next_actionable_task()
    
    async def get_parallel_tasks(self, max_tasks: int = 3) -> List[Task]:
        """Get tasks that can be executed in parallel."""
        if not self.plan:
            return []
        return self.plan.get_all_actionable_tasks(max_tasks)

    async def update_status(self, project_id: str, status: TaskStatus) -> bool:
        """Update the status of a task and persist the plan."""
        if not self.plan:
            return False
            
        success = self.plan.update_task_status(project_id, status)
        if success:
            self.updated_at = datetime.now()
            await self._persist_state()
            logger.info(f"Updated project {project_id} status to {status}")
            
        return success

    async def assign_task(self, task_id: str, agent_name: str) -> bool:
        """Assign a task to a specific agent."""
        if not self.plan:
            return False
            
        task = self.plan.get_task_by_id(task_id)
        if not task:
            return False
            
        if agent_name not in self.agents:
            logger.error(f"Agent '{agent_name}' not found in project team")
            return False
            
        task.assigned_to = agent_name
        self.updated_at = datetime.now()
        await self._persist_state()
        logger.info(f"Assigned task {task_id} to agent {agent_name}")
        return True
    
    def is_plan_complete(self) -> bool:
        """Check if all tasks in the plan are completed."""
        if not self.plan:
            return False
        return self.plan.is_complete()
    
    def has_failed_tasks(self) -> bool:
        if not self.plan:
            return False
        return self.plan.has_failed_tasks()
    
    async def _persist_state(self) -> None:
        project_data = {
            "project_id": self.project_id,
            "name": self.name,
            "goal": self.goal,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "team_agents": list(self.agents.keys()),
            "plan": self.plan.model_dump() if self.plan else None,
        }
        await self.storage.save_file("project.json", project_data)
    
    async def load_state(self) -> bool:
        try:
            project_data = await self.storage.read_file("project.json")
            if project_data:
                import json
                data = json.loads(project_data)
                
                self.created_at = datetime.fromisoformat(data.get("created_at", self.created_at.isoformat()))
                self.updated_at = datetime.fromisoformat(data.get("updated_at", self.updated_at.isoformat()))
                self.name = data.get("name", self.name)  # Load name if available
                
                if data.get("plan"):
                    self.plan = Plan(**data["plan"])
                    
                return True
        except Exception as e:
            logger.error(f"Failed to load project state: {e}")
        return False
    
    async def load_plan(self) -> Optional[Plan]:
        if await self.load_state():
            return self.plan
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        summary = {
            "project_id": self.project_id,
            "name": self.name,
            "goal": self.goal,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "team_size": len(self.agents),
        }
        
        if self.plan:
            task_stats = {
                "total": len(self.plan.tasks),
                "completed": sum(1 for t in self.plan.tasks if t.status == "completed"),
                "running": sum(1 for t in self.plan.tasks if t.status == "running"),
                "pending": sum(1 for t in self.plan.tasks if t.status == "pending"),
                "failed": sum(1 for t in self.plan.tasks if t.status == "failed"),
            }
            summary["tasks"] = task_stats
            summary["progress_percentage"] = (
                (task_stats["completed"] / task_stats["total"] * 100)
                if task_stats["total"] > 0 else 0
            )
            
        return summary


async def start_project(
    goal: str,
    config_path: Union[str, Path, TeamConfig],
    project_id: Optional[str] = None,
    project_root: Optional[Path] = None,
    name: Optional[str] = None,
) -> Project:
    from vibex.core.xagent import XAgent
    
    if project_id is None:
        project_id = generate_short_id()
    
    if isinstance(config_path, (str, Path)):
        team_config = load_team_config(str(config_path))
    else:
        team_config = config_path
    
    storage = ProjectStorageFactory.create_project_storage(
        project_id=project_id,
        project_root=project_root or get_project_root(),
        use_git_artifacts=True
    )
    
    message_queue = MessageQueue()
    history = ConversationHistory(project_id=project_id)
    
    tool_manager = ToolManager(
        project_id=project_id,
        project_path=str(storage.get_project_path())
    )
    
    agents = {}
    for agent_config in team_config.agents:
        agent = Agent(
            config=agent_config,
            tool_manager=tool_manager,
        )
        if hasattr(team_config, 'memory') and team_config.memory:
            agent.team_memory_config = team_config.memory
        agents[agent_config.name] = agent
    
    x_agent = XAgent(
        team_config=team_config,
        project_id=project_id,
        project_path=storage.get_project_path(),
        initial_prompt=goal
    )
    
    project = Project(
        project_id=project_id,
        config=team_config.execution,
        history=history,
        message_queue=message_queue,
        agents=agents,
        storage=storage,
        goal=goal,
        name=name,
        x_agent=x_agent
    )
    
    x_agent.project = project
    
    await project._persist_state()
    logger.info(f"Created project {project_id} with initial state")
    
    if goal:
        logger.info(f"Creating initial plan for project {project_id}")
        plan = await x_agent._generate_plan(goal)
        if plan:
            await project.create_plan(plan)
            # Sync plan to XAgent
            x_agent.plan = plan
            x_agent._plan_initialized = True
    
    logger.info(f"Started project {project_id} with goal: {goal}")
    return project


async def run_project(
    goal: str,
    config_path: Union[str, Path, TeamConfig],
    project_id: Optional[str] = None,
) -> AsyncGenerator[Message, None]:
    project = await start_project(goal, config_path, project_id)
    
    while not project.is_plan_complete():
        response = await project.x_agent.step()
        
        message = Message.assistant_message(response)
        
        yield message
        
        if project.has_failed_tasks():
            break
    
    logger.info(f"Project {project.project_id} completed")


async def resume_project(
    project_id: str,
    config_path: Union[str, Path, TeamConfig]
) -> Project:
    from vibex.core.xagent import XAgent
    
    project_path = get_project_path(project_id)
    if not project_path.exists():
        raise ValueError(f"Project {project_id} not found")
    
    if isinstance(config_path, (str, Path)):
        team_config = load_team_config(str(config_path))
    else:
        team_config = config_path
    
    storage = ProjectStorageFactory.create_project_storage(
        project_id=project_id,
        project_root=get_project_root(),
        use_git_artifacts=True
    )
    
    message_queue = MessageQueue()
    history = ConversationHistory(project_id=project_id)
    
    messages_file = project_path / "history" / "messages.jsonl"
    if messages_file.exists():
        import json
        with open(messages_file, 'r') as f:
            for line in f:
                if line.strip():
                    msg_data = json.loads(line)
                    history.add_message(Message(**msg_data))
    
    tool_manager = ToolManager(
        project_id=project_id,
        project_path=str(storage.get_project_path())
    )
    
    agents = {}
    for agent_config in team_config.agents:
        agent = Agent(
            config=agent_config,
            tool_manager=tool_manager,
        )
        if hasattr(team_config, 'memory') and team_config.memory:
            agent.team_memory_config = team_config.memory
        agents[agent_config.name] = agent
    
    x_agent = XAgent(
        team_config=team_config,
        project_id=project_id,
        project_path=storage.get_project_path(),
        initial_prompt=""
    )
    
    goal = ""
    name = None
    try:
        project_data = await storage.read_file("project.json")
        if project_data:
            data = json.loads(project_data)
            goal = data.get("goal", "")
            name = data.get("name")
    except Exception:
        metadata_file = project_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                goal = metadata.get("goal", "")
                name = metadata.get("name")
    
    project = Project(
        project_id=project_id,
        config=team_config.execution,
        history=history,
        message_queue=message_queue,
        agents=agents,
        storage=storage,
        goal=goal,
        name=name,
        x_agent=x_agent
    )
    
    x_agent.project = project
    
    await project.load_state()
    
    logger.info(f"Resumed project {project_id}")
    return project

__all__ = [
    'Project',
    'start_project',
    'run_project',
    'resume_project'
]

async def main():
    """Main function for testing."""
    # Example usage
    project = await start_project(
        goal="Create a report on the latest AI trends.",
        config_path="examples/simple_team/config/team.yaml",
    )
    print(f"Project started with ID: {project.project_id}")

    # Run a few steps
    for i in range(3):
        print(f"\n--- Step {i+1} ---")
        result = await project.x_agent.step()
        print(result)

    # Get task status
    summary = project.get_summary()
    if 'tasks' in summary:
        print(f"Tasks: {summary['tasks']}")

    # Resume the project
    resumed_project = await resume_project(
        project.project_id, "examples/simple_team/config/team.yaml"
    )
    print(f"\nResumed project with ID: {resumed_project.project_id}")
    result = await resumed_project.x_agent.step("Summarize the report.")
    print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())