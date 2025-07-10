#!/usr/bin/env python3
"""
Bootstrap Project Creation

Handles the main bootstrap functionality for creating new AgentX projects.
"""

from pathlib import Path
from typing import Optional
from .templates import (
    generate_template_config,
    generate_template_prompts,
    generate_readme,
    generate_env_example,
    get_template_description,
    get_default_model,
    get_agents_description
)


def bootstrap_project(project_name: Optional[str] = None, template: Optional[str] = None,
                     model: str = "deepseek", interactive: bool = True) -> int:
    """Bootstrap a new AgentX project with interactive wizard."""

    print("🚀 AgentX Project Bootstrap")
    print("=" * 35)
    print("Creating an optimized AI workflow for the Vibe-X experience")
    print()

    # Get project name
    if not project_name:
        if interactive:
            project_name = input("📁 Project name: ").strip()
            if not project_name:
                print("❌ Project name is required")
                return 1
        else:
            print("❌ Project name is required")
            return 1

    # Get template
    if not template:
        if interactive:
            template = _get_template_interactive()
        else:
            template = "custom"  # Default for non-interactive

    # Get model if not specified and interactive
    if interactive and model == "deepseek":
        model = _get_model_interactive()

    # Create project directory
    project_path = Path(project_name)
    if project_path.exists():
        print(f"❌ Directory '{project_name}' already exists")
        return 1

    try:
        # Create project structure
        print(f"🏗️  Creating project: {project_name}")
        project_path.mkdir()

        # Create config directory
        config_dir = project_path / "config"
        config_dir.mkdir()

        # Create prompts directory (will be removed since we use preset agents)
        prompts_dir = config_dir / "prompts"
        prompts_dir.mkdir()

        # Create workspace directory
        workspace_dir = project_path / "workspace"
        workspace_dir.mkdir()

        # Generate team configuration
        print(f"⚙️  Generating {template} template configuration...")
        team_config = generate_template_config(template, model)
        (config_dir / "team.yaml").write_text(team_config)

        # No custom prompts needed - using preset agents!
        print("📝 Using preset agent system (no custom prompts needed)...")
        # Remove the prompts directory since we don't need it
        prompts_dir.rmdir()

        # Generate main.py
        print("🐍 Creating main.py...")
        main_py_content = _generate_main_py(project_name, template)
        (project_path / "main.py").write_text(main_py_content)

        # Generate .env.example
        print("🔑 Creating environment template...")
        env_content = generate_env_example(model)
        (project_path / ".env.example").write_text(env_content)

        # Generate README.md
        print("📚 Creating documentation...")
        readme_content = generate_readme(project_name, template, model)
        (project_path / "README.md").write_text(readme_content)

        # Success message
        print()
        print("✅ Project created successfully!")
        print("=" * 35)
        print(f"📁 Location: {project_path.absolute()}")
        print(f"🎯 Template: {template} ({get_template_description(template).split(':')[0]})")
        print(f"🤖 Model: {model} ({get_default_model(model)})")
        print()

        # Show agents
        print("👥 Your AI Team:")
        agents_desc = get_agents_description(template)
        for line in agents_desc.split('\n'):
            if line.strip():
                print(f"   {line}")
        print()

        # Next steps
        print("🚀 Next Steps:")
        print(f"   cd {project_name}")
        print("   cp .env.example .env")
        print("   # Edit .env with your API keys")
        print("   python main.py")
        print()
        print("💡 Need help? Check the README.md or visit:")
        print("   https://github.com/dustland/agentx")

        return 0

    except Exception as e:
        print(f"❌ Error creating project: {e}")
        # Clean up on failure
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)
        return 1


def _get_template_interactive() -> str:
    """Get template choice interactively."""
    print("🎯 Choose your workflow template:")
    print("   1. Writing   - Research papers, documentation, content creation")
    print("   2. Coding    - Software development, debugging, testing")
    print("   3. Ops       - Automation, API integration, real-world actions")
    print("   4. Custom    - General-purpose, flexible workflow")
    print()

    while True:
        choice = input("Select template (1-4): ").strip()
        if choice == "1":
            return "writing"
        elif choice == "2":
            return "coding"
        elif choice == "3":
            return "ops"
        elif choice == "4":
            return "custom"
        else:
            print("❌ Please enter 1, 2, 3, or 4")


def _get_model_interactive() -> str:
    """Get model choice interactively."""
    print()
    print("🤖 Choose your LLM provider:")
    print("   1. DeepSeek  - Fast, cost-effective (recommended)")
    print("   2. OpenAI    - GPT-4o-mini, reliable performance")
    print("   3. Claude    - Anthropic Haiku, great reasoning")
    print("   4. Gemini    - Google Flash, good balance")
    print()

    while True:
        choice = input("Select model (1-4, default: 1): ").strip()
        if not choice or choice == "1":
            return "deepseek"
        elif choice == "2":
            return "openai"
        elif choice == "3":
            return "claude"
        elif choice == "4":
            return "gemini"
        else:
            print("❌ Please enter 1, 2, 3, or 4")


def _generate_main_py(project_name: str, template: str) -> str:
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
