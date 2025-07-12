"""
AgentX - Multi-Agent Conversation Framework

A flexible framework for building AI agent teams with:
- Autonomous agents with private LLM interactions
- Centralized tool execution for security and monitoring
- Built-in storage, memory, and search capabilities
- Team coordination and task management
"""

# Main API - what users need to get started
from .core.task import execute_task, start_task

# Tool creation - for custom tools
from .core.tool import Tool, tool

# No configuration loading needed - users pass config paths to start_task/execute_task

# Logging utilities
from .utils.logger import setup_clean_chat_logging, set_log_level, get_logger

# Core classes for advanced usage
from agentx.core.agent import Agent
from agentx.core.task import Task
from agentx.core.xagent import XAgent

__version__ = "0.18.5"

__all__ = [
    # Main API - primary entry points
    "execute_task",
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
    "Task",
    "XAgent",
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
