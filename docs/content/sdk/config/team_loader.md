# Team Configuration Loader

*Module: [`vibex.config.team_loader`](https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py)*

Team configuration loading system.

## TeamLoader <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py#L13" class="source-link" title="View source code">source</a>

Loads team configurations from YAML files, supporting standard presets.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py#L17" class="source-link" title="View source code">source</a>

```python
def __init__(self, config_dir: Optional[str] = None)
```
### load_team_config <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py#L44" class="source-link" title="View source code">source</a>

```python
def load_team_config(self, config_path: str) -> TeamConfig
```
### load_preset_agent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py#L108" class="source-link" title="View source code">source</a>

```python
def load_preset_agent(self, agent_name: str) -> AgentConfig
```

Load a preset agent from the framework's agents configuration.

### load_agent_config <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py#L158" class="source-link" title="View source code">source</a>

```python
def load_agent_config(self, agent_config_data: dict | str) -> AgentConfig
```
### create_agents <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py#L220" class="source-link" title="View source code">source</a>

```python
def create_agents(self, team_config: TeamConfig) -> List[tuple]
```

Create agents from team configuration.

**Returns:**
    List of (agent_config, tools) tuples

## Functions

## load_team_config <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py#L260" class="source-link" title="View source code">source</a>

```python
def load_team_config(config_path: str) -> TeamConfig
```

Loads a team configuration from a given path.

## create_team_from_config <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py#L266" class="source-link" title="View source code">source</a>

```python
def create_team_from_config(team_config: TeamConfig)
```

Create a Team object from team configuration.
This would be the Team.from_config() method.

**Args:**
    team_config: Team configuration

**Returns:**
    Team object

## validate_team_config <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py#L281" class="source-link" title="View source code">source</a>

```python
def validate_team_config(config_path: str) -> Dict[str, Any]
```

Validate a team configuration file.

**Args:**
    config_path: Path to team.yaml file

**Returns:**
    Dictionary with validation results

## list_preset_agents <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/team_loader.py#L316" class="source-link" title="View source code">source</a>

```python
def list_preset_agents() -> List[str]
```

List all available preset agents in the framework.
