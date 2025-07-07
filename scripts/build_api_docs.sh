#!/bin/bash

# Build AgentX API Documentation using pydoc-markdown
# This script generates MDX files compatible with Nextra

set -e

echo "🔧 Building AgentX API Documentation..."

# Clean existing docs (remove both old agentx folder and any generated files)
rm -rf docs/content/api/agentx
rm -rf docs/content/api/core
rm -rf docs/content/api/builtin_tools
rm -rf docs/content/api/cli
rm -rf docs/content/api/config
rm -rf docs/content/api/event
rm -rf docs/content/api/memory
rm -rf docs/content/api/search
rm -rf docs/content/api/storage
rm -rf docs/content/api/tool
rm -rf docs/content/api/utils

# Generate new docs
pydoc-markdown

# Convert .md files to .mdx for Nextra compatibility
find docs/content/api -name "*.md" -exec sh -c 'mv "$1" "${1%.md}.mdx"' _ {} \;

# Flatten the structure by moving contents from agentx folder up one level
if [ -d "docs/content/api/agentx" ]; then
    cd docs/content/api
    mv agentx/* .
    rmdir agentx
    cd - > /dev/null
fi

# Rename all __init__.mdx files to index.mdx for Nextra compatibility
find docs/content/api -name "__init__.mdx" -exec sh -c 'mv "$1" "$(dirname "$1")/index.mdx"' _ {} \;

# Create API index page
cat > docs/content/api/index.mdx << 'EOF'
# API Reference

Complete API reference for the AgentX framework.

AgentX is a modern, AI-powered multi-agent framework for building intelligent systems. This API reference covers all the core modules and components.

## Core Modules

### [Core](/api/core)
Core framework components including agents, orchestration, and task management.

### [Builtin Tools](/api/builtin_tools)
Built-in tools for file operations, web search, memory management, and more.

### [CLI](/api/cli)
Command-line interface and project bootstrapping tools.

### [Configuration](/api/config)
Configuration loading and management utilities.

### [Events](/api/event)
Event system for inter-agent communication and middleware.

### [Memory](/api/memory)
Memory management and persistence systems.

### [Search](/api/search)
Search capabilities and backend integrations.

### [Storage](/api/storage)
File storage and workspace management.

### [Tools](/api/tool)
Tool execution and registry management.

### [Utils](/api/utils)
Utility functions and helpers.

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

For more detailed examples, see the [Documentation](/docs) section.
EOF

# Create proper Nextra _meta.js file
cat > docs/content/api/_meta.js << 'EOF'
export default {
  "index": "Overview",
  "core": "Core",
  "builtin_tools": "Builtin Tools",
  "cli": "CLI",
  "config": "Configuration",
  "event": "Events",
  "memory": "Memory",
  "search": "Search",
  "storage": "Storage",
  "tool": "Tools",
  "utils": "Utils"
}
EOF

echo "✅ API Documentation built successfully!"
echo "📖 Documentation available at: docs/content/api/" 