#!/usr/bin/env python3
"""
Generate API documentation for VibeX framework.
Simple, focused script that extracts docstrings and creates clean MD files.
"""

import os
import ast
import inspect
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add src to path so we can import vibex modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def extract_docstring(node) -> Optional[str]:
    """Extract docstring from AST node."""
    if (isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and
        node.body and isinstance(node.body[0], ast.Expr) and
        isinstance(node.body[0].value, ast.Constant) and
        isinstance(node.body[0].value.value, str)):
        return node.body[0].value.value
    return None

def get_function_signature(node) -> str:
    """Get function signature from AST node."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        args = []

        # Regular arguments
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                try:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                except:
                    arg_str += ": ..."  # Fallback for complex annotations
            args.append(arg_str)

        # Add defaults
        defaults = node.args.defaults
        if defaults:
            num_defaults = len(defaults)
            for i, default in enumerate(defaults):
                arg_idx = len(args) - num_defaults + i
                if arg_idx >= 0 and arg_idx < len(args):
                    try:
                        args[arg_idx] += f" = {ast.unparse(default)}"
                    except:
                        args[arg_idx] += " = ..."  # Fallback for complex defaults

        # Return type
        return_type = ""
        if node.returns:
            try:
                return_type = f" -> {ast.unparse(node.returns)}"
            except:
                return_type = " -> ..."  # Fallback for complex return types

        prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        return f"{prefix}def {node.name}({', '.join(args)}){return_type}"

    return f"def {node.name}(...)"

def format_docstring(docstring: str) -> str:
    """Format docstring for markdown output."""
    if not docstring:
        return ""

    lines = docstring.strip().split('\n')
    if not lines:
        return ""

    # Remove common leading whitespace
    min_indent = float('inf')
    for line in lines[1:]:  # Skip first line
        if line.strip():
            indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, indent)

    if min_indent == float('inf'):
        min_indent = 0

    formatted_lines = [lines[0]]  # First line as-is
    for line in lines[1:]:
        if line.strip():
            formatted_lines.append(line[min_indent:])
        else:
            formatted_lines.append("")

    return '\n'.join(formatted_lines)

def get_github_link(module_name: str, class_name: str = None, method_name: str = None, line_number: int = None) -> str:
    """Generate GitHub link to source code."""
    # GitHub repository base URL
    github_base = "https://github.com/dustland/vibex/blob/main/src"

    # Convert module name to file path
    module_path = module_name.replace('.', '/')

    # Handle special cases for __init__.py files
    if module_path.endswith('.__init__'):
        module_path = module_path[:-9]  # Remove .__init__
        file_path = f"{module_path}/__init__.py"
    else:
        # For regular modules, convert to .py file
        parts = module_path.split('/')
        if len(parts) > 1:
            # e.g., vibex/core/agent -> vibex/core/agent.py
            file_path = f"{module_path}.py"
        else:
            file_path = f"{module_path}.py"

    # Build the full GitHub URL
    github_url = f"{github_base}/{file_path}"

    # Add line number anchor if available
    if line_number:
        github_url += f"#L{line_number}"

    return github_url

def extract_line_number(node, source_lines: List[str]) -> Optional[int]:
    """Extract line number for a node from the source code."""
    if hasattr(node, 'lineno'):
        return node.lineno
    return None

def process_module(module_path: Path, module_name: str) -> Dict[str, Any]:
    """Process a Python module and extract documentation."""
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Keep source lines for line number extraction
        source_lines = content.split('\n')
        tree = ast.parse(content)

        # Extract module docstring
        module_doc = ""
        if (tree.body and isinstance(tree.body[0], ast.Expr) and
            isinstance(tree.body[0].value, ast.Constant) and
            isinstance(tree.body[0].value.value, str)):
            module_doc = tree.body[0].value.value

        classes = []
        functions = []

        # Process only top-level nodes to avoid nested iteration issues
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_doc = extract_docstring(node)
                class_line = extract_line_number(node, source_lines)
                methods = []

                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not item.name.startswith('_') or item.name in ['__init__', '__str__', '__repr__']:
                            method_doc = extract_docstring(item)
                            method_line = extract_line_number(item, source_lines)
                            methods.append({
                                'name': item.name,
                                'signature': get_function_signature(item),
                                'docstring': method_doc,
                                'line_number': method_line
                            })

                classes.append({
                    'name': node.name,
                    'docstring': class_doc,
                    'methods': methods,
                    'line_number': class_line
                })

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):
                    func_doc = extract_docstring(node)
                    func_line = extract_line_number(node, source_lines)
                    functions.append({
                        'name': node.name,
                        'signature': get_function_signature(node),
                        'docstring': func_doc,
                        'line_number': func_line
                    })

        return {
            'name': module_name,
            'docstring': module_doc,
            'classes': classes,
            'functions': functions,
            'file_path': str(module_path)
        }

    except Exception as e:
        print(f"Error processing {module_path}: {e}")
        return {
            'name': module_name,
            'docstring': f"Error processing module: {e}",
            'classes': [],
            'functions': [],
            'file_path': str(module_path)
        }

def get_document_title(module_name: str, module_data: Dict[str, Any]) -> str:
    """Generate a user-friendly title for the documentation."""
    # Extract the actual module name (last part after dots)
    base_name = module_name.split('.')[-1]

    # Custom titles for specific modules
    title_map = {
        # Core modules
        'agent': 'Agent',
        'brain': 'Brain (LLM Interface)',
        'config': 'Configuration Models',
        'event': 'Event System',
        'exceptions': 'Exceptions',
        'guardrails': 'Guardrails',
        'memory': 'Memory System',
        'message': 'Message Types',
        'orchestrator': 'Orchestrator',
        'plan': 'Planning System',
        'task': 'Task Management',
        'tool': 'Tool System',

        # Builtin tools
        'context': 'Context Tool',
        'file': 'File Operations',
        'search': 'Web Search',
        'web': 'Web Scraping',

        # CLI modules
        'bootstrap': 'Project Bootstrap',
        'debug': 'Debug Commands',
        'main': 'CLI Interface',
        'parser': 'Argument Parser',
        'status': 'Status Commands',
        'templates': 'Project Templates',
        'tools': 'Tool Commands',

        # Config modules
        'agent_loader': 'Agent Configuration Loader',
        'prompt_loader': 'Prompt Loader',
        'team_loader': 'Team Configuration Loader',

        # Event modules
        'api': 'Event API',
        'bus': 'Event Bus',
        'middleware': 'Event Middleware',
        'models': 'Event Models',
        'subscribers': 'Event Subscribers',
        'types': 'Event Types',

        # Memory modules
        'backend': 'Memory Backend',
        'factory': 'Memory Factory',
        'mem0_backend': 'Mem0 Backend',
        'memory_system': 'Memory System',
        'synthesis_engine': 'Memory Synthesis Engine',
        'types': 'Memory Types',

        # Search modules
        'interfaces': 'Search Interfaces',
        'search_manager': 'Search Manager',
        'serpapi_backend': 'SerpAPI Backend',

        # Storage modules
        'backends': 'Storage Backends',
        'factory': 'Storage Factory',
        'git_storage': 'Git Storage',
        'interfaces': 'Storage Interfaces',
        'models': 'Storage Models',
        'taskspace': 'Taskspace Management',

        # Tool modules
        'executor': 'Tool Executor',
        'manager': 'Tool Manager',
        'models': 'Tool Models',
        'registry': 'Tool Registry',

        # Utils
        'id': 'ID Utilities',
        'logger': 'Logging Utilities',
    }

    # Use custom title if available, otherwise create a nice default
    if base_name in title_map:
        return title_map[base_name]

    # Fallback: capitalize and clean up the base name
    return base_name.replace('_', ' ').title()

def generate_markdown(module_data: Dict[str, Any]) -> str:
    """Generate markdown documentation from module data."""
    lines = []

    # Text-based source link (no emoji)
    source_text = "source"

    # Get a nice title instead of the full module name
    title = get_document_title(module_data['name'], module_data)

    # Module header with friendly title
    lines.append(f"# {title}")
    lines.append("")

    # Add module path as subtitle for reference with GitHub link
    if module_data['name'] != title.lower().replace(' ', '_'):
        module_github_link = get_github_link(module_data['name'])
        lines.append(f"*Module: [`{module_data['name']}`]({module_github_link})*")
        lines.append("")

    # Module docstring
    if module_data['docstring']:
        lines.append(format_docstring(module_data['docstring']))
        lines.append("")

    # Classes
    if module_data['classes']:
        for cls in module_data['classes']:
            # Class header with GitHub link using text-based link (inline)
            class_github_link = get_github_link(module_data['name'], cls['name'], line_number=cls.get('line_number'))
            lines.append(f"## {cls['name']} <a href=\"{class_github_link}\" class=\"source-link\" title=\"View source code\">{source_text}</a>")

            if cls['docstring']:
                lines.append("")
                lines.append(format_docstring(cls['docstring']))
                lines.append("")

            # Methods
            if cls['methods']:
                for method in cls['methods']:
                    # Method header with GitHub link using text-based link (inline)
                    method_github_link = get_github_link(module_data['name'], cls['name'], method['name'], line_number=method.get('line_number'))
                    lines.append(f"### {method['name']} <a href=\"{method_github_link}\" class=\"source-link\" title=\"View source code\">{source_text}</a>")

                    # Method signature with enhanced styling
                    lines.append("")
                    lines.append("```python")
                    lines.append(method['signature'])
                    lines.append("```")

                    # Method docstring with better formatting
                    if method['docstring']:
                        lines.append("")
                        formatted_doc = format_docstring(method['docstring'])
                        # Enhance Args: and Returns: sections
                        formatted_doc = formatted_doc.replace('Args:', '**Args:**')
                        formatted_doc = formatted_doc.replace('Returns:', '**Returns:**')
                        formatted_doc = formatted_doc.replace('Raises:', '**Raises:**')
                        formatted_doc = formatted_doc.replace('Note:', '**Note:**')
                        formatted_doc = formatted_doc.replace('Example:', '**Example:**')
                        lines.append(formatted_doc)
                        lines.append("")

    # Functions
    if module_data['functions']:
        if module_data['classes']:  # Add separator if we have both classes and functions
            lines.append("## Functions")
            lines.append("")

        for func in module_data['functions']:
            # Function header with GitHub link using text-based link (inline)
            func_github_link = get_github_link(module_data['name'], line_number=func.get('line_number'))
            lines.append(f"## {func['name']} <a href=\"{func_github_link}\" class=\"source-link\" title=\"View source code\">{source_text}</a>")

            # Function signature with enhanced styling
            lines.append("")
            lines.append("```python")
            lines.append(func['signature'])
            lines.append("```")

            # Function docstring with better formatting
            if func['docstring']:
                lines.append("")
                formatted_doc = format_docstring(func['docstring'])
                # Enhance Args: and Returns: sections
                formatted_doc = formatted_doc.replace('Args:', '**Args:**')
                formatted_doc = formatted_doc.replace('Returns:', '**Returns:**')
                formatted_doc = formatted_doc.replace('Raises:', '**Raises:**')
                formatted_doc = formatted_doc.replace('Note:', '**Note:**')
                formatted_doc = formatted_doc.replace('Example:', '**Example:**')
                lines.append(formatted_doc)
                lines.append("")

    return '\n'.join(lines)

def main():
    """Generate API documentation for all VibeX modules."""
    src_path = Path(__file__).parent.parent / "src" / "vibex"
    docs_path = Path(__file__).parent.parent / "docs" / "content" / "sdk"

    # Clean existing docs
    if docs_path.exists():
        import shutil
        shutil.rmtree(docs_path)

    docs_path.mkdir(parents=True, exist_ok=True)

    # Modules to document
    modules = [
        ("core", "Core Framework"),
        ("builtin_tools", "Builtin Tools"),
        ("cli", "Command Line Interface"),
        ("config", "Configuration"),
        ("event", "Event System"),
        ("memory", "Memory Management"),
        ("search", "Search Capabilities"),
        ("server", "Server & API"),
        ("storage", "Storage & Taskspace"),
        ("tool", "Tool Management"),
        ("utils", "Utilities")
    ]

    # Process each module
    for module_name, display_name in modules:
        module_path = src_path / module_name

        if not module_path.exists():
            print(f"⚠️  Module {module_name} not found at {module_path}")
            continue

        print(f"📖 Processing {display_name}...")

        # Create module directory
        module_docs_path = docs_path / module_name
        module_docs_path.mkdir(exist_ok=True)

        # Process __init__.py first
        init_file = module_path / "__init__.py"
        if init_file.exists():
            module_data = process_module(init_file, f"vibex.{module_name}")
            markdown = generate_markdown(module_data)

            with open(module_docs_path / "index.md", 'w', encoding='utf-8') as f:
                f.write(markdown)

        # Process other Python files in the module
        for py_file in sorted(module_path.glob("*.py")):
            if py_file.name != "__init__.py" and not py_file.name.startswith("_"):
                file_name = py_file.stem
                module_data = process_module(py_file, f"vibex.{module_name}.{file_name}")
                markdown = generate_markdown(module_data)

                with open(module_docs_path / f"{file_name}.md", 'w', encoding='utf-8') as f:
                    f.write(markdown)

    # Create API index page
    index_content = """# API Reference

Complete API reference for the VibeX framework.

VibeX is a modern, AI-powered multi-agent framework for building intelligent systems. This API reference covers all the core modules and components.

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

- **Project Bootstrap** - `vibex init` command and project templates
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

To start using VibeX, install it via pip:

```bash
pip install vibex
```

Then create your first agent:

```python
from vibex import Agent

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
"""

    with open(docs_path / "index.md", 'w', encoding='utf-8') as f:
        f.write(index_content)

    # Create Nextra _meta.js
    meta_content = """export default {
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
"""

    with open(docs_path / "_meta.js", 'w', encoding='utf-8') as f:
        f.write(meta_content)

    print("✅ API Documentation generated successfully!")
    print(f"📖 Documentation available at: {docs_path}")

if __name__ == "__main__":
    main()
