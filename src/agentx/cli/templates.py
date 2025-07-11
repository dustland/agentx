#!/usr/bin/env python3
"""
Bootstrap Template Generation

Handles generation of project templates, configurations, and files for the bootstrap system.
"""

import yaml
from typing import Dict


def generate_template_config(template: str, model: str) -> str:
    """Generate team configuration based on template using preset agents."""

    if template == "writing":
        config = {
            "name": f"{template}_project",
            "description": "AgentX writing workflow with professional research and content creation",
            "agents": [
                "researcher",    # Professional market researcher
                "writer",        # Strategic business writer
                "reviewer",      # Quality assurance specialist
                "web_designer"   # Professional web designer for HTML/CSS
            ],
            "execution": {
                "mode": "autonomous",
                "max_rounds": 15,
                "timeout_seconds": 1800
            }
        }

    elif template == "coding":
        config = {
            "name": f"{template}_project",
            "description": "AgentX coding workflow with architecture, development, and testing",
            "orchestrator": {
                "max_rounds": 20,
                "timeout": 2400
            },
            "agents": [
                "planner",       # Strategic planning and architecture
                "developer",     # Code implementation (would need to be added to preset configs)
                "reviewer"       # Quality assurance and testing
            ]
        }

    elif template == "ops":
        config = {
            "name": f"{template}_project",
            "description": "AgentX ops workflow with analysis, execution, and monitoring",
            "orchestrator": {
                "max_rounds": 25,
                "timeout": 3600
            },
            "agents": [
                "researcher",    # Data analyst for requirements
                "planner",       # Operations planning
                "reviewer"       # Results monitoring
            ]
        }

    else:  # custom
        config = {
            "name": f"{template}_project",
            "description": "AgentX custom workflow with general-purpose assistant",
            "orchestrator": {
                "max_rounds": 10,
                "timeout": 1200
            },
            "agents": [
                "researcher",    # For information gathering
                "writer",        # For content creation
                "reviewer"       # For quality assurance
            ]
        }

    return yaml.dump(config, default_flow_style=False, sort_keys=False)


def generate_template_prompts(template: str) -> Dict[str, str]:
    """Generate prompt files based on template - now minimal since we use presets."""

    # With preset agents, we only need to generate custom prompts if any
    # For now, all templates use preset agents, so no custom prompts needed
    return {}


def generate_main_py(project_name: str, template: str) -> str:
    """Generate main.py file for the project."""
    return f'''#!/usr/bin/env python3
"""
{project_name} - AgentX {template.title()} Project

This project was generated using AgentX bootstrap with the {template} template.
It demonstrates the Vibe-X philosophy of human-AI collaboration using XAgent.
"""

import asyncio
from pathlib import Path
from agentx import start_task


async def main():
    """Main application entry point."""
    print("🚀 Starting {project_name}")
    print("=" * 50)

    # Configuration
    config_path = Path("config/team.yaml")

    if not config_path.exists():
        print("❌ Configuration file not found: {{config_path}}")
        print("Make sure you're running from the project root directory.")
        return

    print("🤖 AI agents are ready! What would you like to work on?")

    try:
        # Interactive session with XAgent
        x = None

        while True:
            user_input = input("\\n👤 You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                break

            if not user_input:
                continue

            # Start XAgent on first input
            if x is None:
                print("\\n🚀 Starting your AI team...")
                x = await start_task(user_input, str(config_path))
                print(f"📋 Task ID: {{x.task_id}}")
                print(f"📁 Workspace: {{x.workspace.get_workspace_path()}}")
                print()

            # Chat with X
            print("\\n🤖 X:")
            response = await x.chat(user_input)
            print(response.text)

            # Show work preservation info
            if response.preserved_steps:
                print(f"\\n   ✅ Preserved {{len(response.preserved_steps)}} completed steps")
            if response.regenerated_steps:
                print(f"   🔄 Updated {{len(response.regenerated_steps)}} steps")

    except KeyboardInterrupt:
        print("\\n\\n👋 Session ended. Your work is saved in the workspace!")

    if x:
        print(f"\\n📁 Check your results in: {{x.workspace.get_workspace_path()}}")


if __name__ == "__main__":
    asyncio.run(main())
'''


def generate_env_example(model: str) -> str:
    """Generate .env.example file with API key templates."""
    env_content = f"""# AgentX Environment Configuration
# Copy this file to .env and fill in your API keys

# Primary LLM Provider: {model}
"""

    if model == "deepseek":
        env_content += """DEEPSEEK_API_KEY=your_deepseek_api_key_here
# Get your key at: https://platform.deepseek.com

# Optional: Other providers for mixed workflows
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
"""
    elif model == "openai":
        env_content += """OPENAI_API_KEY=your_openai_api_key_here
# Get your key at: https://platform.openai.com

# Optional: Other providers for cost optimization
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
"""
    elif model == "claude":
        env_content += """ANTHROPIC_API_KEY=your_anthropic_api_key_here
# Get your key at: https://console.anthropic.com

# Optional: Other providers for different use cases
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
"""
    elif model == "gemini":
        env_content += """GOOGLE_API_KEY=your_google_api_key_here
# Get your key at: https://makersuite.google.com

# Optional: Other providers
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
"""

    env_content += """
# Optional: AgentX Configuration
# AGENTX_LOG_LEVEL=INFO
# AGENTX_WORKSPACE_DIR=./workspace
# AGENTX_MAX_ROUNDS=50
"""

    return env_content


def generate_readme(project_name: str, template: str, model: str) -> str:
    """Generate README.md for the project."""

    template_descriptions = {
        "writing": "document creation, research papers, and content workflows",
        "coding": "software development, debugging, and testing workflows",
        "ops": "automation, API integration, and real-world action workflows",
        "custom": "general-purpose AI assistance workflows"
    }

    description = template_descriptions.get(template, "AI workflow")

    return f'''# {project_name}

An AgentX project optimized for {description} using **preset agents**.

## Overview

This project was generated using the AgentX bootstrap wizard with the **{template}** template. It follows the Vibe-X philosophy of human-AI collaboration, providing persistent workspaces, transparent feedback loops, and cost-aware model orchestration.

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install agentx-py
   ```

2. **Configure API Keys**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the Project**
   ```bash
   python main.py
   ```

## Project Structure

```
{project_name}/
├── config/
│   └── team.yaml          # Preset agent configuration (ultra-clean!)
├── workspace/             # Project workspace (auto-generated)
├── main.py               # Application entry point
├── .env.example          # Environment template
└── README.md            # This file
```

## Template: {template.title()}

{get_template_description(template)}

## Preset Agents - Zero Configuration!

This project uses **AgentX preset agents**, eliminating the need for custom agent configuration:

{get_agents_description(template)}

**Why preset agents?**
- ✅ **Zero configuration** - No custom agent files needed
- ✅ **Professional quality** - Enterprise-grade prompts and configurations
- ✅ **Automatic updates** - Framework improvements benefit all projects
- ✅ **Consistent behavior** - Proven agent patterns across projects

## Configuration

The entire team configuration is just **{get_config_lines(template)} lines**:

```yaml
{get_sample_config(template)}
```

Compare this to traditional frameworks requiring 50-200+ lines of custom configuration!

## Cost Optimization

This project is configured for cost-effective operation:

- **Smart Model Selection**: Uses {model} for optimal cost/performance balance
- **Preset Efficiency**: Agents are pre-optimized for minimal token usage
- **Collaborative Workflow**: Agents work together to minimize redundant work

## Next Steps

1. **Experiment**: Start asking questions and see how preset agents collaborate
2. **Scale**: Add more preset agents like `web_designer` for enhanced output formatting
3. **Customize**: Only create custom agents when presets don't meet your needs
4. **Deploy**: Use `agentx start` to run as a service

## Learn More

- [AgentX Documentation](https://github.com/dustland/agentx)
- [Preset Agent System](https://github.com/dustland/agentx/blob/main/docs/preset-agents.md)
- [Vibe-X Philosophy](https://github.com/dustland/agentx/blob/main/docs/content/docs/design/vibe-x-philosophy.mdx)

## Support

- 🐛 [Report Issues](https://github.com/dustland/agentx/issues)
- 💬 [Discussions](https://github.com/dustland/agentx/discussions)
- 📧 [Contact](mailto:support@agentx.dev)

---

*Generated with ❤️ by AgentX Bootstrap using Preset Agents*
'''


def get_template_description(template: str) -> str:
    """Get detailed description for template."""
    descriptions = {
        "writing": """This template optimizes for **Vibe-Writing** workflows using preset agents:

- **Researcher**: Professional market researcher with industry expertise
- **Writer**: Strategic business writer producing executive-quality content
- **Reviewer**: Quality assurance specialist ensuring executive-level standards
- **Web Designer**: Professional web designer for modern, responsive HTML websites and visualizations

Perfect for creating research papers, technical documentation, marketing content, and comprehensive reports with beautiful web presentation.""",

        "coding": """This template optimizes for **Vibe-Coding** workflows using preset agents:

- **Planner**: Strategic planning and task decomposition specialist
- **Developer**: Code implementation specialist (custom recommended)
- **Reviewer**: Quality assurance specialist ensuring code quality

Perfect for building applications, creating libraries, debugging systems, and implementing technical solutions.""",

        "ops": """This template optimizes for **Vibe-Ops** workflows using preset agents:

- **Researcher**: Data analyst for understanding requirements and context
- **Planner**: Plans operations and execution strategies
- **Reviewer**: Validates results and provides feedback""",

        "custom": """This template provides a general-purpose foundation using preset agents:

- **Researcher**: For information gathering and analysis
- **Writer**: For content creation and documentation
- **Reviewer**: For quality assurance and optimization"""
    }

    return descriptions.get(template, "A flexible AgentX project template.")


def get_default_model(model: str) -> str:
    """Get default model name for provider."""
    models = {
        "deepseek": "deepseek-chat",
        "openai": "gpt-4o-mini",
        "claude": "claude-3-haiku-20240307",
        "gemini": "gemini-1.5-flash"
    }
    return models.get(model, "deepseek-chat")


def get_agents_description(template: str) -> str:
    """Get agents description for template."""
    descriptions = {
        "writing": """- **Researcher**: Gathers comprehensive information and credible sources
- **Writer**: Creates compelling, well-structured content
- **Reviewer**: Provides quality assurance and polish
- **Web Designer**: Creates modern, responsive HTML websites and data visualizations""",

        "coding": """- **Planner**: Plans system design and technical approach
- **Developer**: Implements clean, maintainable code (custom recommended)
- **Reviewer**: Ensures quality through comprehensive review""",

        "ops": """- **Researcher**: Understands requirements and gathers context
- **Planner**: Plans operations and execution strategies
- **Reviewer**: Validates results and provides feedback""",

        "custom": """- **Researcher**: Flexible information gathering and analysis
- **Writer**: General content creation and documentation
- **Reviewer**: Quality assurance and optimization"""
    }

    return descriptions.get(template, "General-purpose preset agents")


def get_config_lines(template: str) -> str:
    """Get number of configuration lines for template."""
    # All preset configurations are ultra-clean
    return "8-12"


def get_sample_config(template: str) -> str:
    """Get sample configuration for template."""
    if template == "writing":
        return '''name: "writing_project"
description: "AgentX writing workflow with professional research and content creation"
orchestrator:
  max_rounds: 15
  timeout: 1800
agents:
  - "researcher"
  - "writer"
  - "reviewer"
  - "web_designer"'''
    elif template == "coding":
        return '''name: "coding_project"
description: "AgentX coding workflow with architecture, development, and testing"
orchestrator:
  max_rounds: 20
  timeout: 2400
agents:
  - "planner"
  - "developer"
  - "reviewer"'''
    elif template == "ops":
        return '''name: "ops_project"
description: "AgentX ops workflow with analysis, execution, and monitoring"
orchestrator:
  max_rounds: 25
  timeout: 3600
agents:
  - "researcher"
  - "planner"
  - "reviewer"'''
    else:  # custom
        return '''name: "custom_project"
description: "AgentX custom workflow with general-purpose assistant"
orchestrator:
  max_rounds: 10
  timeout: 1200
agents:
  - "researcher"
  - "writer"
  - "reviewer"'''
