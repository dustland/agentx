"""
VibeX - Multi-Agent Conversation Framework

A flexible framework for building AI agent teams with:
- Autonomous agents with private LLM interactions
- Centralized tool execution for security and monitoring
- Built-in storage, memory, and search capabilities
- Team coordination and project management
"""

# Tool creation - for custom tools
from .core.tool import Tool, tool

# No configuration loading needed - users pass config paths to start_project/run_project

# Logging utilities
from .utils.logger import setup_clean_chat_logging, set_log_level, get_logger

# Core classes for advanced usage
from vibex.core.agent import Agent
from .core.xagent import XAgent
from .config.team_loader import load_team_config

__version__ = "0.30.1"

__all__ = [
    # Main API - primary entry points (v2.0)
    "XAgent",
    "start_task",
    
    # Tool creation - for custom tools
    "Tool",
    "tool",

    # Logging utilities
    "setup_clean_chat_logging",
    "set_log_level",
    "get_logger",

    # Core classes
    "Agent",
]

# Load environment variables automatically on import
try:
    from dotenv import load_dotenv
    import os
    from pathlib import Path

    # Try to find .env file in current directory or parent directories
    current_dir = Path.cwd()
    env_file = None

    # Look for .env file up to 3 levels up
    for i in range(4):
        potential_env = current_dir / ".env"
        if potential_env.exists():
            env_file = potential_env
            break
        current_dir = current_dir.parent
        if current_dir == current_dir.parent:  # reached root
            break

    if env_file:
        load_dotenv(env_file)

except ImportError:
    # python-dotenv not available, skip
    pass
except Exception:
    # Any other error, skip silently
    pass


async def start_task(prompt: str, config_path: str):
    """
    Start a task with the given prompt and configuration.
    
    This is a convenience function that creates an XAgent instance
    and initializes it with the given prompt.
    
    Args:
        prompt: The initial prompt for the task
        config_path: Path to the team configuration file
        
    Returns:
        XAgent: An initialized XAgent instance
    """
    from pathlib import Path
    
    # Load team configuration
    team_config = load_team_config(str(config_path))
    
    # Create XAgent instance
    xagent = XAgent(
        team_config=team_config,
        initial_prompt=prompt
    )
    
    # Initialize with the prompt
    await xagent._initialize_with_prompt(prompt)
    
    return xagent
