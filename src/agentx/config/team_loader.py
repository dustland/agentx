"""
Team configuration loading system.
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Type

from .models import ConfigurationError, AgentConfig, TeamConfig, BrainConfig, LLMProviderConfig
from ..utils.logger import get_logger
from agentx.core.lead import BaseLead, Lead

logger = get_logger(__name__)

class TeamLoader:
    """
    Loads team configurations from YAML files, supporting standard presets.
    """
    def __init__(self):
        self.logger = get_logger(__name__)
        self.standard_agents_dir = Path(__file__).parent.parent / "agents"
        self.config_dir = None

    def load_team_config(self, config_path: str) -> TeamConfig:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Team config file not found: {config_path}")
        
        self.config_dir = config_file.parent
        data = self._load_yaml(config_file)
        self._validate_config(data)

        agent_configs = []
        agent_configs_data = data.get("agents", [])
        for agent_data in agent_configs_data:
            agent_config = self.load_agent_config(agent_data)
            agent_configs.append(agent_config)

        self._validate_agent_names(agent_configs)

        lead_class = None
        lead_config_data = data.get("lead")
        if lead_config_data:
            lead_class = self.load_lead(lead_config_data)

        agent_configs_for_team = [ac.model_dump() for ac in agent_configs]

        team_config = TeamConfig(
            name=data.get("name"),
            description=data.get("description"),
            tool_modules=data.get("tool_modules", []),
            agents=agent_configs_for_team,
            lead=lead_class
        )
        
        return team_config

    def load_lead(self, lead_config_data: str) -> Optional[Type[BaseLead]]:
        if lead_config_data == "default":
            return Lead
        return None

    def load_agent_config(self, agent_config_data: dict | str) -> AgentConfig:
        if isinstance(agent_config_data, str):
            if agent_config_data.startswith("standard:"):
                agent_name = agent_config_data.split(":", 1)[1]
                prompt_path = self.standard_agents_dir / f"{agent_name}.md"
                if not prompt_path.exists():
                    raise ConfigurationError(f"Standard agent '{agent_name}' not found at {prompt_path}")
                
                default_llm_config = LLMProviderConfig(provider="deepseek", model="deepseek/deepseek-coder")
                default_brain_config = BrainConfig(
                    provider="deepseek",
                    model="deepseek/deepseek-coder",
                    temperature=0.7,
                    max_tokens=4000,
                    supports_function_calls=True,
                    streaming=True
                )

                return AgentConfig(
                    name=agent_name.capitalize(),
                    role='specialist',
                    brain_config=default_brain_config,
                    prompt_file=str(prompt_path),
                    tools=[]
                )
            else:
                raise ConfigurationError(f"Invalid agent string definition: '{agent_config_data}'. Must start with 'standard:'.")
        
        # Resolve relative paths for custom agents defined with dicts
        if "prompt_file" in agent_config_data:
            prompt_file_path = Path(agent_config_data["prompt_file"])
            if not prompt_file_path.is_absolute():
                absolute_prompt_path = self.config_dir / prompt_file_path
                if absolute_prompt_path.exists():
                    agent_config_data["prompt_file"] = str(absolute_prompt_path)
                else:
                    logger.warning(f"Prompt file not found: {absolute_prompt_path}")
        
        return AgentConfig(**agent_config_data)

    def _validate_agent_names(self, agents: List[AgentConfig]):
        names = set()
        for agent in agents:
            if agent.name in names:
                raise ConfigurationError(f"Duplicate agent name found: {agent.name}")
            names.add(agent.name)

    def _load_yaml(self, config_file: Path) -> dict:
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {config_file}: {e}")

    def _validate_config(self, data: dict):
        if not isinstance(data, dict):
            raise ConfigurationError("Invalid team config format")
        if 'name' not in data:
            raise ConfigurationError("Team config must have a 'name' field")
        if 'agents' not in data or not data['agents']:
            raise ConfigurationError("Team config must have at least one agent")

    def _import_class(self, class_path: str, base_class: type) -> type:
        try:
            module_name, class_name = class_path.rsplit('.', 1)
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            if not issubclass(cls, base_class):
                raise TypeError(f"{class_path} is not a subclass of {base_class.__name__}")
            return cls
        except (ImportError, AttributeError, TypeError) as e:
            raise ConfigurationError(f"Could not import class '{class_path}': {e}")

def load_team_config(config_path: str) -> TeamConfig:
    """Loads a team configuration from a given path."""
    loader = TeamLoader()
    return loader.load_team_config(config_path)


def create_team_from_config(team_config: TeamConfig):
    """
    Create a Team object from team configuration.
    This would be the Team.from_config() method.
    
    Args:
        team_config: Team configuration
        
    Returns:
        Team object
    """
    loader = TeamLoader()
    return loader.create_team_from_config(team_config)


def validate_team_config(config_path: str) -> Dict[str, Any]:
    """
    Validate a team configuration file.
    
    Args:
        config_path: Path to team.yaml file
        
    Returns:
        Dictionary with validation results
    """
    try:
        team_config = load_team_config(config_path)
        loader = TeamLoader()
        agents = loader.create_agents(team_config)
        
        return {
            "valid": True,
            "team_name": team_config.name,
            "agents": [config.name for config, _ in agents],
            "total_agents": len(agents),
            "message": f"Team configuration is valid ({len(agents)} agents)"
        }
    except ConfigurationError as e:
        return {
            "valid": False,
            "error": str(e),
            "message": "Team configuration validation failed"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Unexpected error: {str(e)}",
            "message": "Team configuration validation failed"
        } 