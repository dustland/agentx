# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the AutoWriter example within the AgentX framework - a demonstration of a professional multi-agent research and writing system that produces consulting-grade HTML reports. AgentX is an open-source framework for building autonomous AI agent teams using natural language orchestration.

## Common Development Commands

### Setup and Dependencies
```bash
# Install dependencies using uv (the project's package manager)
uv sync
uv sync --dev  # Include development dependencies
```

### Running the Auto Writer Example
```bash
# From the auto_writer directory
python main.py

# The example uses config/team.yaml to define the agent team
```

### Development Workflow
```bash
# Start development server with hot reloading
agentx dev

# Run tests
agentx test
# Or: pytest tests/ -v --tb=short

# Set up pre-commit hooks (run once)
agentx setup-hooks

# Generate API documentation
agentx docs

# Run linting/formatting (via pre-commit)
pre-commit run --all-files
```

### Key Commands from AgentX Framework
```bash
agentx start     # Start the API server
agentx monitor   # Run observability monitor
agentx benchmark # Run performance benchmarks
```

## Architecture and Code Structure

### AutoWriter Example Structure
- **main.py**: Entry point that demonstrates the AgentX framework usage
- **config/team.yaml**: Defines the multi-agent team configuration with four agents:
  - Researcher: Gathers evidence-based research
  - Writer: Transforms research into executive narratives
  - Web Designer: Creates interactive HTML output
  - Reviewer: Quality assurance on final output

### AgentX Framework Architecture
- **Multi-Agent System**: Teams of AI agents collaborate through natural language
- **Task Orchestration**: Automatic task planning and delegation based on agent capabilities
- **Memory System**: Stateful conversations with semantic search (Mem0 backend)
- **Tool System**: Secure execution of various tools (web search, file operations, code execution)
- **REST API**: FastAPI-based server for agent task management

### Key Framework Components
- **models/**: Agent, task, and API data models
- **memory/**: Memory backend for stateful conversations
- **tools/**: Available tools for agents (file, web, search, code execution)
- **server/**: FastAPI server implementation
- **services/**: Core services for task execution and agent coordination

### Configuration System
- Agents are defined in YAML files under `config/`
- System prompts are Markdown files in `config/prompts/`
- No custom Python code required for basic agent definitions
- Uses LiteLLM for model provider abstraction

### Development Notes
- Python 3.11+ required
- Uses Black for formatting (88 char line length)
- Type hints are used throughout
- Pre-commit hooks automatically generate API docs
- The project follows a modular architecture with clear separation of concerns

### Testing Approach
- Test files located in `tests/` directory
- Run individual tests: `python tests/run_tests.py`
- Integration tests for the full agent workflow
- Unit tests for individual components

### Environment Variables
Required API keys (set in `.env`):
- OPENAI_API_KEY or DEEPSEEK_API_KEY or ANTHROPIC_API_KEY
- SERPAPI_API_KEY (for web search)
- JINA_API_KEY (for web reader)
