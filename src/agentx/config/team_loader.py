"""
Team configuration loading system.
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Type

from .models import ConfigurationError, AgentConfig, TeamConfig, BrainConfig, LLMProviderConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TeamLoader:
    """
    Loads team configurations from YAML files, supporting standard presets.
    """
    def __init__(self):
        self.logger = get_logger(__name__)
        self.standard_agents_dir = Path(__file__).parent.parent / "presets"
        self.config_dir = None
        self._preset_configs = None  # Cache for preset configurations

    def _load_preset_configs(self) -> Dict[str, Any]:
        """Load preset agent configurations from config.yaml."""
        if self._preset_configs is None:
            config_path = self.standard_agents_dir / "config.yaml"
            if not config_path.exists():
                raise ConfigurationError(f"Preset agent config file not found: {config_path}")
            
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
            
            self._preset_configs = data.get('preset_agents', {})
            logger.info(f"Loaded {len(self._preset_configs)} preset agent configurations")
        
        return self._preset_configs

    def load_team_config(self, config_path: str) -> TeamConfig:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Team config file not found: {config_path}")
        
        self.config_dir = config_file.parent
        data = self._load_yaml(config_file)
        self._validate_config(data)

        agent_configs = []
        
        # Load agents from unified agents field (supports both preset strings and custom objects)
        agents_data = data.get("agents", [])
        for agent_data in agents_data:
            if isinstance(agent_data, str):
                # Preset agent (string reference)
                preset_config = self.load_preset_agent(agent_data)
                agent_configs.append(preset_config)
            else:
                # Custom agent (object)
                agent_config = self.load_agent_config(agent_data)
                agent_configs.append(agent_config)

        self._validate_agent_names(agent_configs)

        # Parse orchestrator configuration parameters (no class loading)
        orchestrator_config = data.get("orchestrator") or data.get("lead", {})  # Support both names
        
        agent_configs_for_team = [ac.model_dump() for ac in agent_configs]

        team_config = TeamConfig(
            name=data.get("name"),
            description=data.get("description"),
            tool_modules=data.get("tool_modules", []),
            agents=agent_configs_for_team,
            orchestrator_config=orchestrator_config
        )
        
        return team_config

    def load_preset_agent(self, agent_name: str) -> AgentConfig:
        """Load a preset agent from the framework's agents configuration."""
        preset_configs = self._load_preset_configs()
        
        if agent_name not in preset_configs:
            available_presets = list(preset_configs.keys())
            raise ConfigurationError(f"Preset agent '{agent_name}' not found. Available presets: {available_presets}")
        
        preset_config = preset_configs[agent_name]
        
        # Check for local override in config/agents/ first
        local_override_path = self.config_dir / "agents" / f"{agent_name}.md"
        if local_override_path.exists():
            preset_config['prompt_file'] = str(local_override_path)
            logger.info(f"Using local override for preset agent '{agent_name}': {local_override_path}")
        else:
            # Use framework prompt file
            prompt_file = preset_config.get('prompt_file')
            if prompt_file:
                prompt_path = self.standard_agents_dir / prompt_file
                if not prompt_path.exists():
                    raise ConfigurationError(f"Prompt file for preset agent '{agent_name}' not found at {prompt_path}")
                preset_config['prompt_file'] = str(prompt_path)
        
        # Extract brain configuration
        brain_config_data = preset_config.get('brain_config', {})
        brain_config = BrainConfig(**brain_config_data)
        
        return AgentConfig(
            name=agent_name,
            description=preset_config.get('description', f"Preset {agent_name} agent from AgentX framework"),
            role=preset_config.get('role', 'specialist'),
            brain_config=brain_config,
            prompt_file=preset_config.get('prompt_file'),
            tools=preset_config.get('tools', [])
        )

    def load_agent_config(self, agent_config_data: dict | str) -> AgentConfig:
        if isinstance(agent_config_data, str):
            if agent_config_data.startswith("standard:"):
                agent_name = agent_config_data.split(":", 1)[1]
                prompt_path = self.standard_agents_dir / f"agents/{agent_name}.md"
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
        
        # Check that we have agents
        has_agents = data.get('agents') and len(data['agents']) > 0
        
        if not has_agents:
            raise ConfigurationError("Team config must have at least one agent in the 'agents' field")


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

def list_preset_agents() -> List[str]:
    """List all available preset agents in the framework."""
    loader = TeamLoader()
    try:
        preset_configs = loader._load_preset_configs()
        return sorted(preset_configs.keys())
    except Exception as e:
        logger.warning(f"Could not load preset agent configurations: {e}")
        return [] 