# SDK Reference

Complete SDK reference for the AgentX framework.

This section contains the auto-generated documentation for all Python classes, functions, and modules in the AgentX SDK (`agentx-py`). For REST API endpoints and HTTP interface documentation, see the [REST API Explorer](/api-explorer).

## Core Modules

### [Core](/api/core)

Core framework components including agents, orchestration, and task management.

- **Agent** - Autonomous agent with conversation management
- **Brain** - LLM interface and response generation
- **Orchestrator** - Multi-agent coordination and tool execution
- **Task** - Task management and execution flow

### [Builtin Tools](/api/builtin_tools)

Built-in tools for file operations, web search, memory management, and more.

- **File Operations** - Taskspace file management with versioning
- **Web Search** - SerpAPI integration for web searches
- **Memory Tool** - Context and memory management
- **Web Scraping** - Content extraction from web pages

### [CLI](/api/cli)

Command-line interface and project bootstrapping tools.

- **Project Bootstrap** - `agentx init` command and project templates
- **CLI Interface** - Main command-line entry point
- **Debug Commands** - Development and debugging utilities

### [Configuration](/api/config)

Configuration loading and management utilities.

- **Agent Configuration** - Agent setup and prompt loading
- **Team Configuration** - Multi-agent team configuration
- **Prompt Management** - Template and prompt handling

### [Events](/api/event)

Event system for inter-agent communication and middleware.

- **Event Bus** - Publish/subscribe event system
- **Event Models** - Event data structures and types
- **Middleware** - Event processing and filtering

### [Memory](/api/memory)

Memory management and persistence systems.

- **Memory Backend** - Abstract memory storage interface
- **Memory System** - High-level memory management
- **Memory Synthesis** - Context synthesis and injection
- **Mem0 Integration** - Mem0 backend implementation

### [Search](/api/search)

Search capabilities and backend integrations.

- **Search Manager** - Search coordination and management
- **SerpAPI Backend** - Google search integration
- **Search Interfaces** - Abstract search contracts

### [Storage](/api/storage)

File storage and taskspace management.

- **Taskspace Management** - Project taskspace handling
- **Git Storage** - Version control integration
- **Storage Backends** - File storage abstractions

### [Tools](/api/tool)

Tool execution and registry management.

- **Tool Registry** - Tool discovery and registration
- **Tool Executor** - Safe tool execution environment
- **Tool Manager** - Tool lifecycle management

### [Utils](/api/utils)

Utility functions and helpers.

- **ID Utilities** - Unique identifier generation
- **Logging** - Framework logging configuration

## Getting Started

To start using AgentX, install it via pip:

```bash
pip install agentx-py
```

Then create your first agent:

```python
from agentx import Agent

agent = Agent(
    name="my_agent",
    model="gpt-4",
    instructions="You are a helpful assistant."
)
```

## Key Concepts

- **Agents** - Autonomous AI entities with specific roles and capabilities
- **Orchestration** - Coordination between multiple agents and tools
- **Tools** - Extensible capabilities that agents can use
- **Memory** - Persistent context and knowledge management
- **Events** - Communication system for agent coordination

For more detailed examples, see the [Documentation](/docs) section.
