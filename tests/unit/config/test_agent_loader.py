"""
Unit tests for agent configuration loading and validation.
Tests agent YAML loading, tool validation, and template generation.
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from vibex.config.agent_loader import (
    load_agents_config,
    load_single_agent_config,
    create_team_config_template,
    create_single_agent_template,
    validate_config_file
)
from vibex.core.config import AgentConfig, ConfigurationError


class TestAgentConfig:
    """Test AgentConfig dataclass."""

    def test_agent_config_defaults(self):
        """Test AgentConfig with default values."""
        config = AgentConfig(name="test_agent")

        assert config.name == "test_agent"
        assert config.role == "assistant"
        assert config.system_message is None
        assert config.prompt_file is None
        assert config.tools == []
        assert config.enable_memory == True
        assert config.auto_reply == True

    def test_agent_config_custom_values(self):
        """Test AgentConfig with custom values."""
        config = AgentConfig(
            name="custom_agent",
            description="Custom agent description",
            role="system",
            system_message="Custom message",
            prompt_file="prompts/custom.md",
            tools=["search", "memory"],
            enable_code_execution=True,
            enable_memory=False
        )

        assert config.name == "custom_agent"
        assert config.description == "Custom agent description"
        assert config.role == "system"
        assert config.system_message == "Custom message"
        assert config.prompt_file == "prompts/custom.md"
        assert config.tools == ["search", "memory"]
        assert config.enable_code_execution == True
        assert config.enable_memory == False

    def test_agent_config_with_brain_config(self):
        """Test AgentConfig with brain configuration."""
        from vibex.core.config import BrainConfig

        brain_config = BrainConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.5
        )

        config = AgentConfig(
            name="test_agent",
            brain_config=brain_config
        )

        assert config.brain_config.provider == "openai"
        assert config.brain_config.model == "gpt-4"
        assert config.brain_config.temperature == 0.5


class TestLoadAgentsConfig:
    """Test loading agent configurations from YAML files."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for test files."""
        return tmp_path

    def test_load_single_agent_config_format(self, temp_dir):
        """Test loading single agent configuration format."""
        agent_yaml = {
            "name": "researcher",
            "description": "Research agent",
            "role": "assistant",
            "system_message": "You are a researcher.",
            "tools": ["search"]
        }

        config_file = temp_dir / "agent.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(agent_yaml, f)

        agents = load_agents_config(str(config_file))

        assert len(agents) == 1
        agent_config = agents[0]
        assert agent_config.name == "researcher"
        assert agent_config.description == "Research agent"
        assert agent_config.system_message == "You are a researcher."
        assert agent_config.tools == ["search"]

    def test_load_multiple_agents_config_format(self, temp_dir):
        """Test loading multiple agents configuration format."""
        agents_yaml = {
            "agents": [
                {
                    "name": "researcher",
                    "description": "Research agent",
                    "role": "assistant",
                    "system_message": "You are a researcher.",
                    "tools": ["search"]
                },
                {
                    "name": "writer",
                    "description": "Writing agent",
                    "role": "assistant",
                    "system_message": "You are a writer.",
                    "tools": []
                }
            ]
        }

        config_file = temp_dir / "agents.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(agents_yaml, f)

        agents = load_agents_config(str(config_file))

        assert len(agents) == 2

        researcher_config = agents[0]
        assert researcher_config.name == "researcher"
        assert researcher_config.tools == ["search"]

        writer_config = agents[1]
        assert writer_config.name == "writer"
        assert writer_config.tools == []

    def test_load_agents_config_with_prompt_file(self, temp_dir):
        """Test loading agent config that specifies prompt_file."""
        agent_yaml = {
            "name": "prompt_agent",
            "description": "Agent with prompt file",
            "role": "assistant",
            "prompt_file": "prompts/agent.md",
            "tools": []
        }

        config_file = temp_dir / "agent.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(agent_yaml, f)

        agents = load_agents_config(str(config_file))

        assert len(agents) == 1
        agent_config = agents[0]
        assert agent_config.prompt_file == "prompts/agent.md"

    def test_load_agents_config_with_preset(self, temp_dir):
        """Test loading agents config with preset agents."""
        agents_yaml = {
            "agents": [
                "researcher",  # This should be a preset
                {
                    "name": "custom_agent",
                    "description": "Custom agent",
                    "system_message": "Custom message"
                }
            ]
        }

        config_file = temp_dir / "agents.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(agents_yaml, f)

        # This might fail if preset doesn't exist, but that's expected behavior
        try:
            agents = load_agents_config(str(config_file))
            # If it works, verify structure
            assert len(agents) >= 1
        except ConfigurationError as e:
            # This is expected if preset doesn't exist
            assert "not found" in str(e).lower()


class TestLoadSingleAgentConfig:
    """Test loading single agent configurations."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for test files."""
        return tmp_path

    def test_load_single_from_single_config(self, temp_dir):
        """Test loading single agent from single-agent config file."""
        agent_yaml = {
            "name": "solo_agent",
            "description": "Solo agent",
            "role": "assistant",
            "system_message": "Solo agent"
        }

        config_file = temp_dir / "solo.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(agent_yaml, f)

        agent_config, tools = load_single_agent_config(str(config_file))

        assert agent_config.name == "solo_agent"
        assert agent_config.system_message == "Solo agent"
        assert tools == []

    def test_load_single_from_multi_config(self, temp_dir):
        """Test loading specific agent from multi-agent config file."""
        agents_yaml = {
            "agents": [
                {"name": "agent1", "description": "Agent 1", "system_message": "Agent 1"},
                {"name": "agent2", "description": "Agent 2", "system_message": "Agent 2"}
            ]
        }

        config_file = temp_dir / "multi.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(agents_yaml, f)

        # Load specific agent
        agent_config, tools = load_single_agent_config(str(config_file), "agent2")

        assert agent_config.name == "agent2"
        assert agent_config.system_message == "Agent 2"

    def test_load_single_agent_not_found(self, temp_dir):
        """Test error when requested agent not found."""
        agents_yaml = {
            "agents": [
                {"name": "agent1", "description": "Agent 1", "system_message": "Agent 1"}
            ]
        }

        config_file = temp_dir / "single.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(agents_yaml, f)

        with pytest.raises(ConfigurationError) as exc_info:
            load_single_agent_config(str(config_file), "nonexistent_agent")

        assert "not found" in str(exc_info.value).lower()


class TestTemplateGeneration:
    """Test template generation functions."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for test files."""
        return tmp_path

    @patch('vibex.config.agent_loader.list_tools')
    @patch('vibex.config.agent_loader.suggest_tools_for_agent')
    def test_create_team_config_template(self, mock_suggest, mock_list, temp_dir):
        """Test creating team configuration template."""
        mock_list.return_value = ["search", "file_ops", "memory"]
        mock_suggest.return_value = ["search"]

        template_path = temp_dir / "team_template.yaml"

        result_path = create_team_config_template(
            team_name="Test Team",
            agent_names=["agent1", "agent2"],
            output_path=str(template_path),
            include_suggestions=True
        )

        assert template_path.exists()
        content = template_path.read_text()
        assert "Test Team" in content
        assert "agent1" in content
        assert "agent2" in content
        assert "search" in content

    @patch('vibex.config.agent_loader.list_tools')
    @patch('vibex.config.agent_loader.suggest_tools_for_agent')
    def test_create_single_agent_template(self, mock_suggest, mock_list, temp_dir):
        """Test creating single agent configuration template."""
        mock_list.return_value = ["search", "file_ops"]
        mock_suggest.return_value = ["search"]

        template_path = temp_dir / "agent_template.yaml"

        result_path = create_single_agent_template(
            agent_name="test_agent",
            output_path=str(template_path),
            include_suggestions=True
        )

        assert template_path.exists()
        content = template_path.read_text()
        assert "test_agent" in content
        assert "search" in content

    def test_template_without_suggestions(self, temp_dir):
        """Test creating template without tool suggestions."""
        template_path = temp_dir / "no_suggestions.yaml"

        with patch('vibex.config.agent_loader.list_tools') as mock_list:
            mock_list.return_value = ["search", "file_ops"]

            result_path = create_single_agent_template(
                agent_name="simple_agent",
                output_path=str(template_path),
                include_suggestions=False
            )

        assert template_path.exists()
        content = template_path.read_text()
        assert "simple_agent" in content


class TestValidateConfigFile:
    """Test configuration file validation."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for test files."""
        return tmp_path

    def test_validate_valid_config(self, temp_dir):
        """Test validation of valid configuration."""
        valid_config = {
            "name": "Test Team",
            "description": "Test team configuration",
            "agents": [
                {
                    "name": "test_agent",
                    "description": "Test agent",
                    "system_message": "You are a test agent.",
                    "tools": ["search"]
                }
            ]
        }

        config_file = temp_dir / "valid.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(valid_config, f)

        result = validate_config_file(str(config_file))

        assert result["valid"] == True
        assert "agents" in result
        assert len(result["agents"]) == 1

    def test_validate_invalid_config(self, temp_dir):
        """Test validation of invalid configuration."""
        invalid_config = {
            "invalid_field": "value"
        }

        config_file = temp_dir / "invalid.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(invalid_config, f)

        result = validate_config_file(str(config_file))

        assert result["valid"] == False
        assert "error" in result or "errors" in result


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_missing_config_file(self):
        """Test error when config file doesn't exist."""
        with pytest.raises(ConfigurationError) as exc_info:
            load_agents_config("nonexistent.yaml")

        assert "not found" in str(exc_info.value).lower()

    def test_invalid_yaml_syntax(self, tmp_path):
        """Test error when YAML syntax is invalid."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: syntax: [")

        with pytest.raises(ConfigurationError) as exc_info:
            load_agents_config(str(config_file))

        assert "yaml" in str(exc_info.value).lower()

    def test_invalid_config_structure(self, tmp_path):
        """Test error when config structure is invalid."""
        invalid_config = {
            "not_agents": "invalid"
        }

        config_file = tmp_path / "invalid_structure.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(invalid_config, f)

        with pytest.raises(ConfigurationError) as exc_info:
            load_agents_config(str(config_file))

        assert "invalid config format" in str(exc_info.value).lower()

    def test_invalid_agent_structure(self, tmp_path):
        """Test error when agent structure is invalid."""
        invalid_agents = {
            "agents": [
                {
                    "invalid_field": "no_name"
                }
            ]
        }

        config_file = tmp_path / "invalid_agents.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(invalid_agents, f)

        with pytest.raises(ConfigurationError) as exc_info:
            load_agents_config(str(config_file))

        assert "invalid agent config" in str(exc_info.value).lower()


@pytest.fixture
def sample_agent_configs():
    """Sample agent configurations for testing."""
    return [
        {
            "name": "researcher",
            "description": "Research agent",
            "system_message": "You are a researcher.",
            "tools": ["search", "memory"]
        },
        {
            "name": "writer",
            "description": "Writing agent",
            "system_message": "You are a writer.",
            "tools": ["file_ops", "memory"]
        }
    ]
