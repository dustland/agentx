"""
Task execution module.

This module defines TaskExecutor for managing the execution of tasks within a project.
Tasks now contain both descriptive and runtime information, eliminating the need
for a separate TaskRun class.
"""

from __future__ import annotations
from typing import Optional, AsyncGenerator
from vibex.core.message import TaskStep
from vibex.core.task import Task
from vibex.core.agent import Agent
from vibex.utils.logger import get_logger

logger = get_logger(__name__)


class TaskExecutor:
    """
    Manages the execution of individual tasks.
    
    TaskExecutor is responsible for:
    1. Starting task execution
    2. Coordinating with agents
    3. Collecting execution steps
    4. Handling errors
    5. Updating task state
    """
    
    def __init__(self):
        self.current_task: Optional[Task] = None
    
    async def execute(self, task: Task, agent: Agent) -> Task:
        """
        Execute a task with the given agent.
        
        Args:
            task: The task to execute (will be updated with execution state)
            agent: The agent that will execute the task
            
        Returns:
            Task: The same task object, now updated with execution results
        """
        from vibex.utils.id import generate_short_id
        
        # Mark task as started
        run_id = generate_short_id()
        task.mark_started(run_id)
        self.current_task = task
        
        logger.info(f"Starting execution {run_id} for task {task.id} with agent {agent.name}")
        
        try:
            # Prepare agent with task context
            await self._prepare_agent(agent, task)
            
            # Execute task and collect steps
            async for step in self._execute_with_agent(agent, task):
                task.add_step(step)
                
                # Could emit events here for real-time monitoring
                logger.debug(f"Task {task.id} - Step completed by {agent.name}")
            
            # Mark as completed
            task.mark_completed()
            logger.info(f"Task {task.id} (run {run_id}) completed successfully")
            
        except Exception as e:
            # Handle failures
            logger.error(f"Task {task.id} (run {run_id}) failed: {str(e)}")
            task.mark_failed(
                error=str(e),
                details={"exception_type": type(e).__name__}
            )
            raise
            
        finally:
            self.current_task = None
            
        return task
    
    async def _prepare_agent(self, agent: Agent, task: Task) -> None:
        """Prepare agent with task context."""
        # This could involve:
        # - Setting up agent's working directory
        # - Loading relevant context/memory
        # - Configuring tools for the task
        pass
    
    async def _execute_with_agent(self, agent: Agent, task: Task) -> AsyncGenerator[TaskStep, None]:
        """
        Execute task with agent and yield steps.
        
        This is where the actual agent interaction happens.
        The agent performs the task and we collect each step.
        """
        # TODO: This needs to be implemented based on how agents actually work
        # For now, placeholder that shows the pattern
        
        # Send task to agent
        prompt = f"""Please complete the following task:
        Task: {task.action}
        """
        
        # In real implementation, this would interact with agent's brain
        # and collect steps as they happen
        yield TaskStep(
            agent_name=agent.name,
            parts=[]  # Would contain actual tool calls and results
        )
    
    def get_current_task(self) -> Optional[Task]:
        """Get the currently executing task, if any."""
        return self.current_task