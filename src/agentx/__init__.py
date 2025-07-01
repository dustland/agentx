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
from .tool.models import Tool, tool

# No configuration loading needed - users pass config paths to start_task/execute_task

# Logging utilities
from .utils.logger import setup_clean_chat_logging, set_log_level, get_logger

from agentx.core.agent import Agent
from agentx.core.task import Task, TaskExecutor
from agentx.core.lead import BaseLead

from agentx.core.agent import Agent
from agentx.core.task import Task, TaskExecutor
from agentx.core.lead import BaseLead

__version__ = "0.13.5"

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

    "Agent",
    "Task",
    "TaskExecutor",
    "BaseLead",
]
