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
        initial_goal: str,
        x_agent: Optional['XAgent'] = None,
    ):
        self.project_id = project_id
        self.config = config
        self.history = history
        self.message_queue = message_queue
        self.agents = agents
        self.storage = storage
        self.initial_goal = initial_goal
        self.x_agent = x_agent
        
        self.is_complete: bool = False
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        self.plan: Optional[Plan] = None
        
    def get_agent(self, name: str) -> Agent:
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' not found in project team.")
        return self.agents[name]
    
    def complete(self):
        self.is_complete = True
        logger.info(f"Project {self.project_id} completed")
    
    def get_context(self) -> Dict[str, Any]:
        context = {
            "project_id": self.project_id,
            "status": "completed" if self.is_complete else "in_progress",
            "initial_goal": self.initial_goal,
            "storage_path": str(self.storage.get_project_path()),
            "agents": list(self.agents.keys()),
            "history_length": len(self.history.messages),
            "created_at": self.created_at.isoformat(),
        }
        
        if self.plan:
            context["plan"] = {
                "goal": self.plan.goal,
                "total_tasks": len(self.plan.tasks),
                "progress": self.plan.get_progress_summary(),
            }
            
        return context
    
    async def create_plan(self, plan: Plan) -> None:
        self.plan = plan
        await self._persist_project_state()
        logger.info(f"Created plan for project {self.project_id} with {len(plan.tasks)} tasks")
    
    async def update_plan(self, plan: Plan) -> None:
        self.plan = plan
        self.updated_at = datetime.now()
        await self._persist_project_state()
        logger.info(f"Updated plan for project {self.project_id}")
    
    async def get_next_task(self) -> Optional[Task]:
        if not self.plan:
            return None
        return self.plan.get_next_actionable_task()
    
    async def get_parallel_tasks(self, max_tasks: int = 3) -> List[Task]:
        """Get tasks that can be executed in parallel."""
        if not self.plan:
            return []
        return self.plan.get_all_actionable_tasks(max_tasks)

    async def update_project_status(self, project_id: str, status: TaskStatus) -> bool:
        """Update the status of a task and persist the plan."""
        if not self.plan:
            return False
            
        success = self.plan.update_task_status(project_id, status)
        if success:
            self.updated_at = datetime.now()
            await self._persist_project_state()
            logger.info(f"Updated project {project_id} status to {status}")
            
        return success

    async def assign_task_to_agent(self, task_id: str, agent_name: str) -> bool:
        """Assign a task to a specific agent."""
        if not self.plan:
            return False
            
        task = self.plan.get_task_by_id(task_id)
        if not task:
            return False
            
        if agent_name not in self.agents:
            logger.error(f"Agent '{agent_name}' not found in project team")
            return False
            
        task.agent = agent_name
        self.updated_at = datetime.now()
        await self._persist_project_state()
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
    
    async def _persist_project_state(self) -> None:
        project_data = {
            "project_id": self.project_id,
            "initial_goal": self.initial_goal,
            "status": "completed" if self.is_complete else "in_progress",
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "team_agents": list(self.agents.keys()),
            "plan": self.plan.model_dump() if self.plan else None,
        }
        await self.storage.save_file("project.json", project_data)
    
    async def load_project_state(self) -> bool:
        try:
            project_data = await self.storage.read_file("project.json")
            if project_data:
                import json
                data = json.loads(project_data)
                
                self.created_at = datetime.fromisoformat(data.get("created_at", self.created_at.isoformat()))
                self.updated_at = datetime.fromisoformat(data.get("updated_at", self.updated_at.isoformat()))
                self.is_complete = data.get("status") == "completed"
                
                if data.get("plan"):
                    self.plan = Plan(**data["plan"])
                    
                return True
        except Exception as e:
            logger.error(f"Failed to load project state: {e}")
        return False
    
    async def load_plan(self) -> Optional[Plan]:
        if await self.load_project_state():
            return self.plan
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        summary = {
            "project_id": self.project_id,
            "goal": self.initial_goal,
            "status": "completed" if self.is_complete else "in_progress",
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "team_size": len(self.agents),
        }
        
        if self.plan:
            task_stats = {
                "total": len(self.plan.tasks),
                "completed": sum(1 for t in self.plan.tasks if t.status == "completed"),
                "in_progress": sum(1 for t in self.plan.tasks if t.status == "in_progress"),
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
    workspace_dir: Optional[Path] = None,
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
        base_path=workspace_dir or Path(".vibex/projects"),
        use_git_artifacts=True
    )
    
    message_queue = MessageQueue()
    history = ConversationHistory(project_id=project_id)
    
    tool_manager = ToolManager(
        project_id=project_id,
        workspace_path=str(storage.get_project_path())
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
        workspace_dir=storage.get_project_path(),
        initial_prompt=goal
    )
    
    project = Project(
        project_id=project_id,
        config=team_config.execution,
        history=history,
        message_queue=message_queue,
        agents=agents,
        storage=storage,
        initial_goal=goal,
        x_agent=x_agent
    )
    
    x_agent.project = project
    
    await project._persist_project_state()
    logger.info(f"Created project {project_id} with initial state")
    
    if goal:
        logger.info(f"Creating initial plan for project {project_id}")
        plan_response = await x_agent._generate_plan(goal)
        if plan_response and hasattr(plan_response, 'plan'):
            await project.create_plan(plan_response.plan)
    
    logger.info(f"Started project {project_id} with goal: {goal}")
    return project


async def run_project(
    goal: str,
    config_path: Union[str, Path, TeamConfig],
    project_id: Optional[str] = None,
) -> AsyncGenerator[Message, None]:
    project = await start_project(goal, config_path, project_id)
    
    while not project.is_complete:
        response = await project.x_agent.step()
        
        message = Message.assistant_message(response)
        
        yield message
        
        if project.is_plan_complete() or project.has_failed_tasks():
            project.complete()
            break
    
    logger.info(f"Project {project.project_id} completed")


async def resume_project(
    project_id: str,
    config_path: Union[str, Path, TeamConfig]
) -> Project:
    from vibex.core.xagent import XAgent
    
    workspace_path = Path(f".vibex/projects/{project_id}")
    if not workspace_path.exists():
        raise ValueError(f"Project {project_id} not found")
    
    if isinstance(config_path, (str, Path)):
        team_config = load_team_config(str(config_path))
    else:
        team_config = config_path
    
    storage = ProjectStorageFactory.create_project_storage(
        project_id=project_id,
        base_path=workspace_path.parent.parent,
        use_git_artifacts=True
    )
    
    message_queue = MessageQueue()
    history = ConversationHistory(project_id=project_id)
    
    messages_file = workspace_path / "history" / "messages.jsonl"
    if messages_file.exists():
        import json
        with open(messages_file, 'r') as f:
            for line in f:
                if line.strip():
                    msg_data = json.loads(line)
                    history.add_message(Message(**msg_data))
    
    tool_manager = ToolManager(
        project_id=project_id,
        workspace_path=str(storage.get_project_path())
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
        workspace_dir=storage.get_project_path(),
        initial_prompt=""
    )
    
    initial_goal = ""
    try:
        project_data = await storage.read_file("project.json")
        if project_data:
            data = json.loads(project_data)
            initial_goal = data.get("initial_goal", "")
    except Exception:
        metadata_file = workspace_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                initial_goal = metadata.get("initial_goal", "")
    
    project = Project(
        project_id=project_id,
        config=team_config.execution,
        history=history,
        message_queue=message_queue,
        agents=agents,
        storage=storage,
        initial_goal=initial_goal,
        x_agent=x_agent
    )
    
    x_agent.project = project
    
    await project.load_project_state()
    
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