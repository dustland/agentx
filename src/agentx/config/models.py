"""
Config subsystem models - Self-contained configuration data models.

This module contains all data models related to configuration management, following the
architectural rule that subsystems should be self-contained and not import from core.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Union, Literal
from pathlib import Path
from pydantic import BaseModel, Field, validator
from enum import Enum

from agentx.core.config import BrainConfig, AgentConfig  # Use canonical models from core


class ConfigurationError(Exception):
    """Configuration validation or loading error."""
    pass


class LLMProviderConfig(BaseModel):
    """Configuration for LLM providers."""
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1024


class AgentRole(str, Enum):
    """Standard agent roles."""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    REVIEWER = "reviewer"
    EXECUTOR = "executor"
    SPECIALIST = "specialist"


class TeamConfig(BaseModel):
    """Main configuration for agent teams."""
    name: str
    description: Optional[str] = None
    agents: List[AgentConfig] = []  # Use canonical AgentConfig from core
    tool_modules: List[str] = []
    max_rounds: int = 10
    orchestrator_config: Optional[Dict] = None


class FrameworkConfig(BaseModel):
    """
    Main configuration object for the AgentX framework.
    """
    log_level: str = "INFO"
    log_file: str = "agentx.log"
    max_concurrent_tasks: int = 10
    task_timeout: int = 3600  # in seconds
    environment: str = "development"  # "development", "staging", "production"
    debug: bool = False
    
    class Config:
        validate_assignment = True
        

def validate_team_config(config: TeamConfig) -> List[str]:
    """Validate a TeamConfig object."""
    errors = []
    
    if not config.name:
        errors.append("Team name cannot be empty")
        
    if not config.agents:
        errors.append("Team must have at least one agent")
        
    # Validate each agent has required fields
    for i, agent in enumerate(config.agents):
        if not agent.name:
            errors.append(f"Agent {i} missing required 'name' field")
        
        # Check for either system_message or prompt_file
        if not agent.system_message and not agent.prompt_file:
            errors.append(f"Agent '{agent.name}' must have either 'system_message' or 'prompt_file'")
    
    return errors
    

def get_default_team_config() -> TeamConfig:
    return TeamConfig(
        name="DefaultTeam",
        description="Default team configuration",
        agents=[
            AgentConfig(
                name="assistant",
                system_message="You are a helpful AI assistant.",
                brain_config=BrainConfig(
                    provider="openai",
                    model="gpt-4",
                    temperature=0.7,
                    max_tokens=4000,
                    supports_function_calls=True,
                    streaming=True
                )
            )
        ]
    )