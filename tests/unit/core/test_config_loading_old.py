import pytest
import tempfile
import yaml
from pathlib import Path
from pydantic import ValidationError
from vibex.core.xagent import XAgent
from vibex.core.agent import Agent
from vibex.tool.registry import get_tool_registry
from vibex.core.config import TeamConfig, AgentConfig, BrainConfig, ToolConfig, ProjectConfig, ConfigurationError

# It's better to use absolute paths in tests to avoid issues with the test runner's CWD
# This finds the project root based on the test file's location.
# This assumes tests are run from the project root or the tests folder.
# A more robust solution might use a dedicated fixture in conftest.py
try:
    # This works when tests are run from the project root
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
    # Check if a known file exists to validate root
    if not (PROJECT_ROOT / 'pyproject.toml').exists():
        # This works when the CWD is inside the tests folder
        PROJECT_ROOT = Path.cwd().parent
except FileNotFoundError:
    PROJECT_ROOT = Path.cwd()


SIMPLE_TEAM_CONFIG_PATH = PROJECT_ROOT / "examples" / "simple-research-team" / "team.json"

@pytest.fixture
def tool_registry():
    """Fixture to get a clean tool registry for each test."""
    registry = get_tool_registry()
    registry.clear()
    yield registry
    registry.clear()

@pytest.fixture
def sample_team_config_path():
    """Fixture that provides the path to the sample team config."""
    return "tests/test_taskspaces/sample_team/team.yaml"

@pytest.fixture(autouse=True)
def clear_tool_registry_fixture():
    """Fixture to automatically clear the tool registry before each test."""
    registry = get_tool_registry()
    registry.clear()
    yield
    registry.clear()

# REMOVED: XAgent no longer accepts config path as constructor argument
# def test_load_team_from_config(sample_team_config_path: str):
    """
    Tests that an XAgent can be successfully loaded from a YAML config file.
    """
    # Act
    xagent = XAgent(sample_team_config_path)

    # Assert
    assert xagent.team_config.name == "sample_team"
    assert len(xagent.specialist_agents) == 3  # coordinator, analyst, writer
    assert "coordinator" in xagent.specialist_agents
    assert "analyst" in xagent.specialist_agents
    assert "writer" in xagent.specialist_agents

    # Check max rounds - this comes from team_config.max_rounds (default 10)
    assert xagent.team_config.max_rounds == 10

# REMOVED: XAgent no longer accepts config path as constructor argument
# def test_load_team_with_nonexistent_config():
    """
    Tests that loading a non-existent config file raises ConfigurationError.
    """
    with pytest.raises(ConfigurationError):
        XAgent("non_existent_path/team.yaml")

# REMOVED: XAgent no longer accepts config path as constructor argument
# def test_load_team_with_invalid_yaml(tmp_path: Path):
    """
    Tests that loading a malformed YAML file raises a parsing error.
    """
    invalid_yaml = "name: Test Team\n  agents: - name: agent1" # Bad indentation
    config_path = tmp_path / "invalid_team.yaml"
    config_path.write_text(invalid_yaml)

    with pytest.raises(ConfigurationError):
        XAgent(str(config_path))

# REMOVED: XAgent no longer accepts config path as constructor argument
# def test_load_team_with_validation_error(tmp_path: Path):
    """
    Tests that a config with missing required fields raises a configuration error.
    """
    # 'name' field is missing, which should cause a validation error
    invalid_config = """
version: "1.0"
agents:
  - name: "researcher"
    description: "A researcher agent"
    prompt_template: "prompt.jinja2"
    tools: []
"""
    config_path = tmp_path / "invalid_team.yaml"
    (tmp_path / "prompt.jinja2").write_text("dummy prompt")
    config_path.write_text(invalid_config)

    with pytest.raises(ConfigurationError):
        XAgent(str(config_path))

# REMOVED: XAgent no longer accepts config path as constructor argument
# def test_load_team_with_invalid_tool_source(tmp_path: Path):
    """
    Tests that an invalid tool source string is handled gracefully.
    """
    invalid_config = """
version: "1.0"
name: "Test Team"
description: "A test team"
agents:
  - name: "test_agent"
    description: "Test agent"
    prompt_template: "prompt.jinja2"
    tools: []
tools:
  - name: "bad_tool"
    type: "python_function"
    source: "non.existent.module.NonExistentTool"
"""
    config_path = tmp_path / "team.yaml"
    (tmp_path / "prompt.jinja2").write_text("dummy prompt")
    config_path.write_text(invalid_config)

    # This should load successfully since we don't validate tool sources at load time
    xagent = XAgent(str(config_path))
    assert xagent.team_config.name == "Test Team"

# REMOVED: XAgent no longer accepts config path as constructor argument  
# def test_load_team_with_undefined_agent_tool(tmp_path: Path):
    """
    Tests that an agent referencing an undefined tool is handled gracefully.
    """
    config = """
version: "1.0"
name: "Test Team"
description: "A test team"
agents:
  - name: "agent1"
    description: "Test agent"
    prompt_template: "prompt.jinja2"
    tools: ["some_tool_that_does_not_exist"]
tools: []
"""
    config_path = tmp_path / "team.yaml"
    (tmp_path / "prompt.jinja2").write_text("prompt")
    config_path.write_text(config)

    # This should load successfully
    xagent = XAgent(str(config_path))
    assert xagent.team_config.name == "Test Team"

def test_basic_team_config_loading():
    """Test loading a basic team configuration."""

    # Create a minimal team configuration
    config_data = {
        'name': 'test_team',
        'description': 'A test team configuration',
        'agents': [
            {
                'name': 'assistant',
                'description': 'A helpful assistant agent',
                'prompt_template': 'assistant.jinja2',
                'tools': ['file_ops']
            }
        ],
        'tools': [
            {
                'name': 'file_ops',
                'type': 'builtin',
                'description': 'File operations'
            }
        ]
    }

    # Create TeamConfig from dict
    team_config = TeamConfig(**config_data)

    # Verify the configuration
    assert team_config.name == 'test_team'
    assert team_config.description == 'A test team configuration'
    assert len(team_config.agents) == 1
    assert len(team_config.tools) == 1
    assert team_config.agents[0].name == 'assistant'
    assert team_config.tools[0].name == 'file_ops'

def test_team_config_validation():
    """Test that team configuration validation works correctly."""

    # Test missing required fields
    with pytest.raises(Exception):  # Should raise validation error
        TeamConfig()

    # Test valid minimal config
    config = TeamConfig(
        name="test",
        description="test team",
        agents=[
            AgentConfig(
                name="test_agent",
                description="test agent",
                prompt_template="test.jinja2"
            )
        ]
    )

    assert config.name == "test"
    assert len(config.agents) == 1

def test_brain_config_defaults():
    """Test that Brain configuration uses proper defaults."""

    # Test with minimal Brain config
    brain_config = BrainConfig(provider='deepseek', model='deepseek-chat', api_key='test-key')

    assert brain_config.provider == 'deepseek'
    assert brain_config.model == 'deepseek-chat'
    assert brain_config.temperature == 0.7  # Default value
    assert brain_config.max_tokens == 8000  # Default value
    assert brain_config.base_url == 'https://api.deepseek.com'  # Default for deepseek
    assert brain_config.timeout == 30  # Default value

def test_project_config():
    """Test project configuration."""

    # Test default values
    project_config = ProjectConfig()

    assert project_config.mode == "autonomous"
    assert project_config.max_rounds == 10  # Updated to match current default
    assert project_config.timeout_seconds == 300
    assert project_config.step_through_enabled == False

    # Test custom values
    project_config = ProjectConfig(
        mode="step_through",
        max_rounds=50,
        timeout_seconds=600,
        step_through_enabled=True
    )

    assert project_config.mode == "step_through"
    assert project_config.max_rounds == 50
    assert project_config.timeout_seconds == 600
    assert project_config.step_through_enabled == True
