<div align="center">
  <img src="https://dustland.github.io/agentx/logo.png" alt="AgentX Logo" width="120">
  <h1 align="center">AgentX</h1>
</div>

<p align="center">
  <b>An open-source framework for building autonomous AI agent teams.</b>
  <br />
  <a href="https://dustland.github.io/agentx"><strong>Explore the docs »</strong></a>
  <br />
  <br />
  <a href="https://pypi.org/project/agentx-py/"><img src="https://img.shields.io/pypi/v/agentx-py.svg" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/agentx-py/"><img src="https://img.shields.io/pypi/dm/agentx-py.svg" alt="PyPI downloads" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" /></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg"/></a>
  <a href="https://github.com/dustland/agentx/issues/new?assignees=&labels=bug&template=bug_report.md&title="><img src="https://img.shields.io/badge/Report%20an%20Issue-d73a4a?style=flat-square" alt="Report an Issue"/></a>
  <a href="https://github.com/dustland/agentx/issues/new?assignees=&labels=enhancement&template=feature_request.md&title="><img src="https://img.shields.io/badge/Request%20a%20Feature-0366d6?style=flat-square" alt="Request a Feature"/></a>
</p>

AgentX provides the backbone for creating, orchestrating, and observing sophisticated multi-agent systems. It moves beyond simple agent-to-agent communication to a robust, task-driven framework where teams of specialized agents collaborate to achieve complex goals.

## ✨ Key Features

Based on a refined and modular architecture, AgentX is built around a few core concepts:

- **🤖 Multi-Agent Teams**: Define teams of specialized agents in simple YAML files. Each agent can have its own role, tools, and configuration.
- **🗣️ Natural Language Orchestration**: Agents hand off tasks to each other using natural language. A central `TaskExecutor` interprets these handoffs and routes work to the appropriate agent, enabling complex, dynamic workflows.
- **🛠️ Secure & Extensible Tools**: Tools are defined with Python decorators and their schemas are automatically generated. Shell commands are executed in a secure Docker sandbox, providing safety and isolation. A flexible `ToolExecutor` manages the entire lifecycle.
- **🧠 Stateful & Context-Aware Memory**: Agents maintain long-term memory, enabling them to recall past interactions and context. The memory system supports semantic search, ensuring agents have the information they need, when they need it.
- **📡 Streamable Communication**: The entire lifecycle of a task, from agent thoughts to tool calls and results, is available as a real-time stream of events. This allows you to build rich, observable UIs like the Vercel AI SDK.
- **🎯 Task-Centric API**: Interact with the system through a simple, powerful API. Kick off complex workflows with `execute_task()` or manage interactive sessions with `start_task()`.

## 🚀 Getting Started

The best way to get started is by following our **[Getting Started](https://dustland.github.io/agentx/docs/getting-started/)**, which will walk you through building a simple chat application and a multi-agent writer/reviewer team.

### 1. Installation

Install AgentX from PyPI:

```sh
pip install agentx-py
```

Or for development, clone the repository:

```sh
git clone https://github.com/dustland/agentx.git
cd agentx
uv sync
```

### 2. Usage Examples

AgentX can be run directly from the command line or via its Python API. You can find complete, working examples in the `examples/` directory.

#### Running an Example

This demonstrates a basic multi-agent collaboration:

```bash
# Navigate to an example directory
cd examples/simple_team

# Run the main script
python main.py
```

#### Using the CLI

The framework includes a powerful CLI for managing your agent system:

```bash
# Bootstrap a new project with interactive wizard
agentx init

# Monitor tasks and events in your terminal
agentx monitor

# Launch the web dashboard for rich observability
agentx monitor --web

# List available tools
agentx tools list
```

#### Using the Python API

Here is a simple example of an autonomous run:

```python
import asyncio
from agentx import execute_task

async def main():
    # Execute a task with a simple prompt (completes when done)
    await execute_task(
        prompt="Write a brief report on renewable energy trends",
        config_path="config/team.yaml"
    )
    print("Task completed!")

asyncio.run(main())
```

_The script above shows a simple autonomous run. For more advanced patterns like message streaming and interactive sessions, please see the complete scripts in the `/examples` directory._

### Example Projects

- **[simple_writer](examples/simple_writer/)** - Single intelligent agent for both creative writing and market research
- **[simple_team](examples/simple_team/)** - Multi-agent writer/reviewer collaboration
- **[simple_chat](examples/simple_chat/)** - Interactive chat with an AI assistant
- **[auto_writer](examples/auto_writer/)** - Advanced multi-agent writing system

## 🔧 Development Workflow

AgentX includes a comprehensive development setup with automated tooling to ensure code quality and documentation consistency.

### Pre-commit Hooks

The project uses pre-commit hooks to automatically maintain code quality and keep documentation up-to-date:

```bash
# Set up pre-commit hooks (one-time setup)
uv run setup-hooks

# Now every commit will automatically:
# - Generate API documentation when Python files change
# - Format code and fix whitespace issues
# - Validate YAML and TOML files
# - Check for merge conflicts and large files
```

### Development Commands

```bash
# Generate API documentation
uv run docs

# Build documentation site
uv run build-docs

# Run tests
uv run test

# Run development server with auto-reload
uv run dev

# Monitor tasks and events
uv run monitor
```

### API Documentation

The API documentation is automatically generated from docstrings and kept in sync with the code:

- **Source**: Python docstrings in `src/agentx/`
- **Output**: Markdown files in `docs/content/api/`
- **Automation**: Generated on every commit via pre-commit hooks

To manually regenerate API docs:

```bash
uv run docs
```

## 📊 Observability & Monitoring

AgentX includes a comprehensive observability system for monitoring and debugging multi-agent workflows.

Launch a modern web dashboard built with FastAPI and Preline UI:

```bash
# Start web dashboard
agentx monitor --web
```

- **Dashboard**: System overview with metrics and recent activity.
- **Tasks**: Task conversation history viewer with export.
- **Events**: Real-time event monitoring with filtering.
- **Memory**: Memory browser with search and categories.
- **Messages**: Agent conversation history during execution.
- **Configuration**: System configuration and status viewer.

You can also use the observability features in CLI mode without the option `--web`.

## 🛠️ Tech Stack

AgentX is built on a robust foundation of modern Python technologies:

- **[LiteLLM](https://github.com/BerriAI/litellm)** - Unified interface for 100+ LLM providers
- **[Mem0](https://github.com/mem0ai/mem0)** - Intelligent memory layer for long-term context
- **[SerpAPI](https://serpapi.com/)** - Web search capabilities for agents
- **[Jina](https://www.jina.ai)** - Web content extraction
- **[Browser-use](https://browser-use.com/)** - Browser automation

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🙏 Acknowledgments

This project was initially inspired by and built upon concepts from [AG2 (AutoGen)](https://github.com/ag2ai/ag2), an excellent multi-agent conversation framework. While AgentX has evolved into its own distinct architecture and approach, we're grateful for the foundational ideas and patterns that AG2 provided to the multi-agent AI community.

Our message system and conversation architecture draws inspiration from [Vercel AI SDK](https://github.com/vercel/ai), particularly its elegant message format with role-based structure and parts array for handling complex content types. This design pattern has proven invaluable for building robust, extensible AI applications.

This project also referred to other open-source projects such as [OpenManus](https://github.com/FoundationAgents/OpenManus), [Suna](https://github.com/Kortix-ai/Suna) and [Magic](https://github.com/dtyq/magic/) etc.

## 📄 License

Licensed under the Apache License 2.0 - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ by [Dustland](https://github.com/dustland)**
