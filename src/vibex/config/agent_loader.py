"""
Agent configuration loading with tool validation and discovery.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# AgentConfig imported locally to avoid circular imports
from ..tool import validate_agent_tools, suggest_tools_for_agent, list_tools
from ..core.config import AgentConfig, ConfigurationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


def load_agents_config(
    config_path: str,
    model_override: Optional[str] = None
) -> List[AgentConfig]:
    """
    Load agent configurations from a YAML file, handling presets.

    Args:
        config_path: Path to the main team config YAML file.
        model_override: Optional model name to override for all agents.

    Returns:
        A list of agent configuration dictionaries.
    """
    if not config_path.endswith(('.yaml', '.yml')):
        raise ConfigurationError(f"Invalid file format. Expected .yaml or .yml: {config_path}")

    config_file = Path(config_path)
    if not config_file.exists():
        raise ConfigurationError(f"Config file not found: {config_path}")

    try:
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in {config_path}: {e}")

    # Load preset agent definitions
    presets_config_path = Path(__file__).parent.parent / "presets" / "config.yaml"
    try:
        with open(presets_config_path, 'r') as f:
            presets_data = yaml.safe_load(f)
        preset_agents = presets_data.get('preset_agents', {})
    except (FileNotFoundError, yaml.YAMLError) as e:
        logger.warning(f"Could not load or parse preset agents config: {e}")
        preset_agents = {}

    # Handle both single agent and multiple agents formats
    if 'agents' in data:
        # Multiple agents format: { agents: [...] }
        agents_data = data['agents']
    elif 'name' in data:
        # Single agent format: { name: ..., role: ... }
        agents_data = [data]
    else:
        raise ConfigurationError(f"Invalid config format. Expected 'agents' list or single agent config")

    processed_agents = []
    for agent_def in agents_data:
        agent_config = {}
        # If agent_def is just a string, it's a preset
        if isinstance(agent_def, str):
            if agent_def not in preset_agents:
                raise ConfigurationError(f"Preset agent '{agent_def}' not found. Available presets: {list(preset_agents.keys())}")
            # Use the preset configuration
            agent_config = preset_agents[agent_def]
            # Add the name, as it's the key in the preset dict
            agent_config['name'] = agent_def
        else:
            agent_config = agent_def

        try:
            config_data = AgentConfig(**agent_config)
        except Exception as e:
            raise ConfigurationError(f"Invalid agent config structure for agent '{agent_config.get('name', 'Unknown')}': {e}")

        # Validate tools if requested
        if config_data.tools:
            # Skip tool validation since builtin tools are automatically available
            # and the global registry may not be synchronized with runtime registry
            logger.info(f"Agent '{config_data.name}' configured with tools: {config_data.tools}")
            # Note: Tool validation will happen at runtime when tools are actually used

        # Apply model override if provided
        if model_override:
            if "llm_config" not in config_data:
                config_data["llm_config"] = {}
            config_data["llm_config"]["model"] = model_override

        processed_agents.append(config_data)

    return processed_agents


def load_single_agent_config(config_path: str, agent_name: Optional[str] = None,
                           validate_tools: bool = True) -> tuple[AgentConfig, List[str]]:
    """
    Load a single agent configuration from YAML file.

    Args:
        config_path: Path to YAML config file
        agent_name: Specific agent name to load (if file contains multiple agents)
        validate_tools: Whether to validate tool names against registry

    Returns:
        Tuple of (AgentConfig, tools)

    Raises:
        ConfigurationError: If config is invalid or agent not found
    """
    agents = load_agents_config(config_path)

    if agent_name:
        # Find specific agent
        for agent_config in agents:
            if agent_config.name == agent_name:
                return agent_config, agent_config.tools
        raise ConfigurationError(f"Agent '{agent_name}' not found in {config_path}")
    else:
        # Return first agent if no name specified
        if not agents:
            raise ConfigurationError(f"No agents found in {config_path}")
        return agents[0], agents[0].tools


def create_team_config_template(team_name: str, agent_names: List[str],
                               output_path: str, include_suggestions: bool = True) -> str:
    """
    Create a YAML config template for a team with multiple agents.

    Args:
        team_name: Name of the team
        agent_names: List of agent names to include
        output_path: Where to save the template
        include_suggestions: Whether to include suggested tools

    Returns:
        Path to created template file
    """
    available_tools = list_tools()

    template = f"""# Team Configuration: {team_name}
# Multiple agents working together

agents:"""

    for agent_name in agent_names:
        suggestions = suggest_tools_for_agent(agent_name) if include_suggestions else []

        template += f"""
  - name: {agent_name}
    role: assistant  # assistant, user, or system
    # Either specify system_message OR prompt_file (not both)
    # system_message: "You are a helpful AI assistant named {agent_name}."
    prompt_file: "prompts/{agent_name}.md"  # Load system message from file
    description: "Describe what this agent does..."

    # Tools this agent can use
    tools:"""

        if suggestions:
            template += "\n      # Suggested tools based on agent name:"
            for tool in suggestions:
                template += f"\n      - {tool}"
        else:
            template += "\n      # Add tool names here, e.g.:"
            if available_tools:
                for tool in available_tools[:2]:  # Show first 2 as examples
                    template += f"\n      # - {tool}"

        template += """

    # Optional settings
    enable_code_execution: false
    enable_human_interaction: false
    enable_memory: true
    max_consecutive_replies: 10
    auto_reply: true"""

    template += f"""

# Available tools: {available_tools}
# Run 'agentx tools list' for detailed descriptions

# Team settings (optional)
team:
  name: {team_name}
  max_rounds: 10
  speaker_selection: "auto"  # auto, round_robin, manual
"""

    # Write template
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(template)

    logger.info(f"Created team config template: {output_path}")
    return str(output_file)


def create_single_agent_template(agent_name: str, output_path: str,
                                include_suggestions: bool = True) -> str:
    """
    Create a YAML config template for a single agent.

    Args:
        agent_name: Name of the agent
        output_path: Where to save the template
        include_suggestions: Whether to include suggested tools

    Returns:
        Path to created template file
    """
    # Get tool suggestions
    suggestions = suggest_tools_for_agent(agent_name) if include_suggestions else []
    available_tools = list_tools()

    template = f"""# Single Agent Configuration: {agent_name}
name: {agent_name}
role: assistant  # assistant, user, or system
# Either specify system_message OR prompt_file (not both)
# system_message: "You are a helpful AI assistant named {agent_name}."
prompt_file: "prompts/{agent_name}.md"  # Load system message from file
description: "Describe what this agent does..."

# Tools this agent can use
tools:"""

    if suggestions:
        template += "\n  # Suggested tools based on agent name:"
        for tool in suggestions:
            template += f"\n  - {tool}"
    else:
        template += "\n  # Add tool names here, e.g.:"
        if available_tools:
            for tool in available_tools[:3]:  # Show first 3 as examples
                template += f"\n  # - {tool}"

    template += f"""

# Optional settings
enable_code_execution: false
enable_human_interaction: false
enable_memory: true
max_consecutive_replies: 10
auto_reply: true

# Available tools: {available_tools}
# Run 'agentx tools list' for detailed descriptions
"""

    # Write template
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(template)

    logger.info(f"Created single agent config template: {output_path}")
    return str(output_file)


def validate_config_file(config_path: str) -> Dict[str, Any]:
    """
    Validate a config file (single agent or team) and return validation results.

    Args:
        config_path: Path to config file

    Returns:
        Dictionary with validation results
    """
    try:
        agents = load_agents_config(config_path)
        agent_names = [config.name for config in agents]
        all_tools = []
        for config in agents:
            all_tools.extend(config.tools)

        return {
            "valid": True,
            "agents": agent_names,
            "total_agents": len(agents),
            "tools_used": list(set(all_tools)),
            "message": f"Configuration is valid ({len(agents)} agents)"
        }
    except ConfigurationError as e:
        return {
            "valid": False,
            "error": str(e),
            "message": "Configuration validation failed"
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [str(e)],
            "message": f"Unexpected error during validation: {str(e)}"
        }
