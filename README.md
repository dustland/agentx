<img src="./assets/logo.png" alt="logo" width="80px" height="80px">

# RoboCo

A **Robo**t-driven **Co**mpany built with Multi-Agent Platform.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-00a393?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Built on AG2](https://img.shields.io/badge/Built%20on-AG2-orange)](https://github.com/ag2ai/ag2)

## Overview

RoboCo is a powerful platform that combines Domain-Driven Design with Multi-Agent Systems to create intelligent, collaborative AI teams. Built with a clean architecture that separates concerns into domain, application, infrastructure, and interface layers, RoboCo enables you to build sophisticated AI applications with minimal boilerplate.

## Key Features

- **Domain-Driven Design**: Clean architecture with proper separation of concerns and dependency injection
- **Multi-Agent Teams**: Specialized agents that collaborate to solve complex problems
- **Sprint Management**: Built-in project and sprint management for agile development
- **MCP Integration**: Model Context Protocol for enhanced agent communication and reasoning
- **Extensible Tools**: Plug-and-play tools for research, analysis, and interaction
- **REST API**: Comprehensive API with FastAPI for seamless integration
- **Workspace Management**: Organized workspaces for artifacts and project resources

## Quick Start

```bash
# Clone repository
git clone https://github.com/dustland/roboco.git
cd roboco

# Setup environment
./setup.sh  # On Unix/macOS
# or
setup.bat   # On Windows

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Start the API server
./start.sh  # Uses default host (127.0.0.1) and port (8000)
# Or with custom options
./start.sh --host=0.0.0.0 --port=8080 --reload

# If installed as a package
pip install -e .
roboco-api  # Starts the API server using installed package
roboco-api-dev  # Starts the API server in development mode with auto-reload
roboco-db-api  # Starts a minimal database API server
```

## Documentation

- [Config-Based Design](docs/config_based_design.md) - Team configuration
- [Object Model](docs/object_model.md) - Core domain models
- [Tool System](docs/tool.md) - Tool system
- [MCP](docs/mcp.md) - Model-Context-Protocol support

## Configuration

RoboCo uses environment variables for configuration with sensible defaults:

```
# .env
OPENAI_API_KEY=your_api_key_here
WORKSPACE_DIR=~/roboco_workspace
LOG_LEVEL=INFO
```

The `start.sh` script provides a convenient way to launch the API server with various configuration options:

```bash
# Basic usage
./start.sh

# Available options
./start.sh --host=0.0.0.0     # Bind to all interfaces
./start.sh --port=8080        # Use custom port
./start.sh --reload           # Enable auto-reload for development
./start.sh --workers=4        # Use multiple worker processes
./start.sh --help             # Show all available options
```

When using the `roboco-api` script, you can configure the server with environment variables:

```bash
# Set host and port via environment variables
HOST=0.0.0.0 PORT=8080 roboco-api

# Or export them for the session
export HOST=0.0.0.0
export PORT=8080
roboco-api
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details and our [Code of Conduct](CODE_OF_CONDUCT.md).

## Contact

- 🌐 X: [@dustland_ai](https://twitter.com/dustland_ai)
- 🌐 Github: [dustland](https//github.com/dustland)
- 🌐 Website: [dustland.ai](https://dustland.ai)

## Acknowledgments

- Built on top of [AG2](https://github.com/ag2ai/ag2)
- Inspired by [Manus](https://manus.im/) and [OpenManus](https://github.com/mannaandpoem/OpenManus/)
- Thanks to Anthropic for MCP(Model Context Protocol) design
- Logo generated with [GPT-4o](https://chatgpt.com)

## Citation

```bibtex
@misc{roboco2025,
  author = {Dustland Team},
  title = {RoboCo: A Robot-driven Company powered by Multi-agent System},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/dustland/roboco}},
}
```
