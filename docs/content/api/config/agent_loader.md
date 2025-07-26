# Agent Configuration Loader

*Module: [`vibex.config.agent_loader`](https://github.com/dustland/vibex/blob/main/src/vibex/config/agent_loader.py)*

Agent configuration loading with tool validation and discovery.

## load_agents_config <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/agent_loader.py#L18" class="source-link" title="View source code">source</a>

```python
def load_agents_config(config_path: str, model_override: Optional[str] = None) -> List[AgentConfig]
```

Load agent configurations from a YAML file, handling presets.

**Args:**
    config_path: Path to the main team config YAML file.
    model_override: Optional model name to override for all agents.

**Returns:**
    A list of agent configuration dictionaries.

## load_single_agent_config <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/agent_loader.py#L102" class="source-link" title="View source code">source</a>

```python
def load_single_agent_config(config_path: str, agent_name: Optional[str] = None, validate_tools: bool = True) -> tuple[AgentConfig, List[str]]
```

Load a single agent configuration from YAML file.

**Args:**
    config_path: Path to YAML config file
    agent_name: Specific agent name to load (if file contains multiple agents)
    validate_tools: Whether to validate tool names against registry

**Returns:**
    Tuple of (AgentConfig, tools)

**Raises:**
    ConfigurationError: If config is invalid or agent not found

## create_team_config_template <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/agent_loader.py#L133" class="source-link" title="View source code">source</a>

```python
def create_team_config_template(team_name: str, agent_names: List[str], output_path: str, include_suggestions: bool = True) -> str
```

Create a YAML config template for a team with multiple agents.

**Args:**
    team_name: Name of the team
    agent_names: List of agent names to include
    output_path: Where to save the template
    include_suggestions: Whether to include suggested tools

**Returns:**
    Path to created template file

## create_single_agent_template <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/agent_loader.py#L210" class="source-link" title="View source code">source</a>

```python
def create_single_agent_template(agent_name: str, output_path: str, include_suggestions: bool = True) -> str
```

Create a YAML config template for a single agent.

**Args:**
    agent_name: Name of the agent
    output_path: Where to save the template
    include_suggestions: Whether to include suggested tools

**Returns:**
    Path to created template file

## validate_config_file <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/agent_loader.py#L272" class="source-link" title="View source code">source</a>

```python
def validate_config_file(config_path: str) -> Dict[str, Any]
```

Validate a config file (single agent or team) and return validation results.

**Args:**
    config_path: Path to config file

**Returns:**
    Dictionary with validation results
