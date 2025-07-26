"""
XAgent Service Layer

Manages XAgent instances and provides the service interface for the REST API.
XAgent is the primary interface - each instance represents exactly one project.
"""

from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

from vibex.core.xagent import XAgent
from vibex.utils.logger import get_logger
from vibex.core.exceptions import AgentNotFoundError

logger = get_logger(__name__)

# In-memory storage for active XAgent instances.
# In a production environment, this would be replaced with a persistent store.
active_xagents: Dict[str, XAgent] = {}


class XAgentService:
    """
    Service for managing XAgent instances.
    
    XAgent is the primary interface to VibeX. Each XAgent instance represents
    exactly one project and uses the project's ID as its identifier.
    """

    async def create(
        self,
        user_id: Optional[str] = None,
        goal: str = "",
        config_path: str = "",
        context: Optional[dict] = None,
    ) -> XAgent:
        """
        Creates a new XAgent instance.
        
        Returns the actual XAgent instance, not a DTO wrapper.
        The XAgent manages its own project internally.
        """
        logger.info(f"Creating XAgent{f' for user {user_id}' if user_id else ''} with goal: {goal}")
        
        try:
            # Use start_project function to create XAgent properly
            from vibex.core.project import start_project
            
            project = await start_project(
                goal=goal,
                config_path=config_path,
            )
            
            # Get the XAgent from the project
            xagent = project.x_agent
            
            # Store the active XAgent instance
            active_xagents[xagent.project_id] = xagent
            
            logger.info(f"XAgent {xagent.project_id} created successfully.")
            return xagent
            
        except Exception as e:
            logger.error(f"Failed to create XAgent: {e}", exc_info=True)
            raise

    async def get(self, agent_id: str) -> XAgent:
        """
        Get an XAgent instance by ID.
        
        Returns the actual XAgent instance for direct interaction.
        Uses lazy loading - if not in memory, tries to load from filesystem.
        """
        # Check if already loaded in memory
        if agent_id in active_xagents:
            return active_xagents[agent_id]
        
        # Try to load from filesystem (lazy loading)
        try:
            from pathlib import Path
            from vibex.core.project import resume_project
            
            # Check if project exists on filesystem
            project_path = Path(f".vibex/projects/{agent_id}")
            if not project_path.exists():
                raise AgentNotFoundError(f"XAgent {agent_id} not found")
            
            # Load project and get XAgent
            # Use a default config path - in production you'd want to store this
            config_path = "examples/simple_chat/config/team.yaml"
            project = await resume_project(agent_id, config_path)
            xagent = project.x_agent
            
            # Cache it for future requests
            active_xagents[agent_id] = xagent
            
            logger.info(f"Lazy loaded XAgent {agent_id} from filesystem")
            return xagent
            
        except Exception as e:
            logger.error(f"Failed to lazy load XAgent {agent_id}: {e}")
            raise AgentNotFoundError(f"XAgent {agent_id} not found")

    async def list_for_user(self, user_id: Optional[str] = None) -> list[XAgent]:
        """
        Get all XAgent instances for a specific user.
        Note: This is a simplified in-memory implementation.
        """
        # In a real implementation, you would query a database here
        # For now, return all active XAgents (user filtering not implemented)
        return list(active_xagents.values())

    async def delete(self, agent_id: str) -> bool:
        """
        Delete an XAgent instance.
        """
        if agent_id in active_xagents:
            del active_xagents[agent_id]
            logger.info(f"XAgent {agent_id} deleted")
            return True
        return False

    def exists(self, agent_id: str) -> bool:
        """
        Check if an XAgent instance exists.
        """
        return agent_id in active_xagents


# Dependency injection
_xagent_service_instance = None

def get_xagent_service() -> XAgentService:
    global _xagent_service_instance
    if _xagent_service_instance is None:
        _xagent_service_instance = XAgentService()
    return _xagent_service_instance