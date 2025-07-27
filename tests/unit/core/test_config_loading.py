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
        PROJECT_ROOT = Path.cwd()
        while not (PROJECT_ROOT / 'pyproject.toml').exists() and PROJECT_ROOT.parent != PROJECT_ROOT:
            PROJECT_ROOT = PROJECT_ROOT.parent
except:
    # Fallback: assume we're in the project root
    PROJECT_ROOT = Path.cwd()

@pytest.fixture(scope="module")
def project_root():
    return PROJECT_ROOT

@pytest.fixture
def sample_team_config_path(project_root):
    """Returns the path to a sample team configuration file."""
    return str(project_root / "examples" / "simple_team" / "config" / "team.yaml")

@pytest.fixture
def sample_prompt_path(project_root):
    """Returns the path to the sample prompt template."""
    return str(project_root / "examples" / "simple_team" / "config" / "prompts" / "analyst.jinja2")

@pytest.fixture(autouse=True)
def reset_tool_registry():
    """Reset the tool registry before each test to avoid conflicts."""
    registry = get_tool_registry()
    registry.clear()

# REMOVED: XAgent no longer accepts config path as constructor argument
# The following tests have been removed as they test outdated XAgent initialization:
# - test_load_team_from_config
# - test_load_team_with_nonexistent_config
# - test_load_team_with_invalid_yaml
# - test_load_team_with_validation_error
# - test_load_team_with_invalid_tool_source
# - test_load_team_with_undefined_agent_tool

def test_basic_team_config_loading():
    """
    Tests basic team configuration creation
    """
    # Create team config programmatically
    team_config = TeamConfig(
        name="Test Team",
        description="A test team configuration",
        agents=[
            AgentConfig(
                name="test_agent",
                description="A test agent",
                prompt_file="test_prompt.md",
                tools=[],
                brain_config=BrainConfig(
                    provider="test_provider",
                    model="test_model"
                ),
                context={
                    "test_key": "test_value"
                }
            )
        ],
        tools=[],
        max_rounds=20
    )

    # Assertions
    assert team_config.name == "Test Team"
    assert team_config.description == "A test team configuration"
    assert len(team_config.agents) == 1
    assert team_config.agents[0].name == "test_agent"
    assert team_config.agents[0].brain_config.provider == "test_provider"
    assert team_config.agents[0].context["test_key"] == "test_value"
    assert team_config.max_rounds == 20

def test_team_config_validation():
    """
    Tests that invalid team configurations raise validation errors
    """
    # Missing required field 'name'
    with pytest.raises(ValidationError):
        TeamConfig(
            description="Missing name field",
            agents=[],
            tools=[]
        )

    # Invalid agent configuration (missing name)
    with pytest.raises(ValidationError):
        TeamConfig(
            name="Invalid Team",
            description="Team with invalid agent",
            agents=[
                AgentConfig(
                    description="Agent missing name",
                    prompt_file="test.md",
                    tools=[]
                )
            ],
            tools=[]
        )

def test_brain_config_defaults():
    """Test brain configuration defaults."""
    # Test with minimal config
    brain_config = BrainConfig(
        provider="openai",
        model="gpt-4"
    )

    assert brain_config.provider == "openai"
    assert brain_config.model == "gpt-4"
    assert brain_config.temperature == 0.7  # default
    assert brain_config.max_tokens == 8000  # default
    assert brain_config.timeout == 30  # default

    # Test with custom values
    brain_config = BrainConfig(
        provider="anthropic",
        model="claude-3-opus",
        temperature=0.3,
        max_tokens=4000,
        timeout=120
    )

    assert brain_config.provider == "anthropic"
    assert brain_config.model == "claude-3-opus"
    assert brain_config.temperature == 0.3
    assert brain_config.max_tokens == 4000
    assert brain_config.timeout == 120

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