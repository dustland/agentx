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

__version__ = "0.28.0"

__all__ = [
    # Main API - primary entry points (v2.0)
    "XAgent",
    
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
