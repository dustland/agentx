"""
Team configuration loading system.
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Type

from agentx.core.config import AgentConfig, BrainConfig, ConfigurationError, TeamConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TeamLoader:
    """
    Loads team configurations from YAML files, supporting standard presets.
    """
    def __init__(self, config_dir: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.standard_agents_dir = Path(__file__).parent.parent / "presets"
        self.config_dir = Path(config_dir) if config_dir else None
        self._preset_configs = None  # Cache for preset configurations

        # Set up prompt loader if config directory has prompts
        self.prompt_loader = None
        if self.config_dir and (self.config_dir / "prompts").exists():
            from .prompt_loader import PromptLoader
            self.prompt_loader = PromptLoader(str(self.config_dir / "prompts"))

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
            raise ConfigurationError(f"Team config file not found: {config_path}")

        # Set config_dir if not already set in constructor
        if self.config_dir is None:
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

        # Build TeamConfig with only non-None values to use defaults properly
        team_config_data = {
            "name": data.get("name"),
            "agents": agent_configs,  # Keep as AgentConfig objects for type safety
            "orchestrator": orchestrator_config
        }

        # Include handoffs if present
        if "handoffs" in data:
            team_config_data["handoffs"] = data["handoffs"]

        # Only include description if it's provided
        if "description" in data and data["description"] is not None:
            team_config_data["description"] = data["description"]

        # Handle collaboration section for legacy compatibility
        if "collaboration" in data:
            collaboration = data["collaboration"]
            if "max_rounds" in collaboration:
                team_config_data["max_rounds"] = collaboration["max_rounds"]
            if "speaker_selection_method" in collaboration:
                team_config_data["speaker_selection_method"] = collaboration["speaker_selection_method"]
            if "termination_condition" in collaboration:
                team_config_data["termination_condition"] = collaboration["termination_condition"]

        # Handle llm_provider configuration
        if "llm_provider" in data:
            llm_provider_data = data["llm_provider"]
            team_config_data["llm_provider"] = BrainConfig(**llm_provider_data)

        team_config = TeamConfig(**team_config_data)

        return team_config

    def load_preset_agent(self, agent_name: str) -> AgentConfig:
        """Load a preset agent from the framework's agents configuration."""
        preset_configs = self._load_preset_configs()

        if agent_name not in preset_configs:
            available_presets = list(preset_configs.keys())
            raise ConfigurationError(f"Preset agent '{agent_name}' not found. Available presets: {available_presets}")

        preset_config = preset_configs[agent_name]

        # Check for local override in config/agents/ first
        if self.config_dir:
            local_override_path = self.config_dir / "agents" / f"{agent_name}.md"
            if local_override_path.exists():
                prompt_template = str(local_override_path)
                logger.info(f"Using local override for preset agent '{agent_name}': {local_override_path}")
            else:
                # Use framework prompt file
                prompt_file = preset_config.get('prompt_file')
                if prompt_file:
                    prompt_path = self.standard_agents_dir / prompt_file
                    if not prompt_path.exists():
                        raise ConfigurationError(f"Prompt file for preset agent '{agent_name}' not found at {prompt_path}")
                    prompt_template = str(prompt_path)
                else:
                    prompt_template = ""
        else:
            # Use framework prompt file
            prompt_file = preset_config.get('prompt_file')
            if prompt_file:
                prompt_path = self.standard_agents_dir / prompt_file
                if not prompt_path.exists():
                    raise ConfigurationError(f"Prompt file for preset agent '{agent_name}' not found at {prompt_path}")
                prompt_template = str(prompt_path)
            else:
                prompt_template = ""

        # Extract brain configuration
        brain_config_data = preset_config.get('brain_config', {})
        brain_config = BrainConfig(**brain_config_data)

        # Create canonical AgentConfig object
        return AgentConfig(
            name=agent_name,
            description=preset_config.get('description', f"Preset {agent_name} agent from AgentX framework"),
            prompt_template=prompt_template,  # Use canonical field name
            brain_config=brain_config,
            tools=preset_config.get('tools', [])
        )

    def load_agent_config(self, agent_config_data: dict | str) -> AgentConfig:
        if isinstance(agent_config_data, str):
            if agent_config_data.startswith("standard:"):
                agent_name = agent_config_data.split(":", 1)[1]
                prompt_path = self.standard_agents_dir / f"agents/{agent_name}.md"
                if not prompt_path.exists():
                    raise ConfigurationError(f"Standard agent '{agent_name}' not found at {prompt_path}")

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
                    description=f"Standard {agent_name} agent",
                    prompt_template=str(prompt_path),  # Use canonical field name
                    brain_config=default_brain_config,
                    tools=[]
                )
            else:
                raise ConfigurationError(f"Invalid agent string definition: '{agent_config_data}'. Must start with 'standard:'.")

        # Handle custom agent configuration (dict)
        # Resolve relative paths for prompt files and load content
        prompt_template = ""
        if "prompt_file" in agent_config_data:
            prompt_file_path = Path(agent_config_data["prompt_file"])
            if not prompt_file_path.is_absolute():
                absolute_prompt_path = self.config_dir / prompt_file_path
            else:
                absolute_prompt_path = prompt_file_path

            if absolute_prompt_path.exists():
                try:
                    prompt_template = absolute_prompt_path.read_text(encoding='utf-8')
                except Exception as e:
                    raise ConfigurationError(f"Failed to read prompt file {absolute_prompt_path}: {e}")
            else:
                raise ConfigurationError(f"Prompt file not found: {absolute_prompt_path}")
        elif "system_message" in agent_config_data:
            prompt_template = agent_config_data["system_message"]
        elif "prompt_template" in agent_config_data:
            prompt_template = agent_config_data["prompt_template"]

        # Extract brain configuration
        brain_config = None
        if "brain_config" in agent_config_data:
            brain_config = BrainConfig(**agent_config_data["brain_config"])

        return AgentConfig(
            name=agent_config_data["name"],
            description=agent_config_data.get("description", ""),
            prompt_template=prompt_template,
            brain_config=brain_config,
            tools=agent_config_data.get("tools", [])
        )

    def create_agents(self, team_config: TeamConfig) -> List[tuple]:
        """Create agents from team configuration.

        Returns:
            List of (agent_config, tools) tuples
        """
        agents = []
        for agent_config in team_config.agents:
            # For now, return empty tools list - this could be enhanced later
            tools = []
            agents.append((agent_config, tools))
        return agents

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
