# VibeX Simple Chat Example

A minimal chat interface for VibeX - perfect for getting started.

## Quick Start

```bash
cd examples/simple_chat
python main.py
```

That's it! You're now chatting with VibeX.

## Usage

```
Chat started! Type 'quit' or 'q' to exit.
Initializing X...
You: Hello!
X: Hello! I'm X, your AI assistant. How can I help you today?
You: Plan a weekend trip
X: I'll help you plan a weekend trip. Let me create a plan for that...
  (Shows plan creation and execution info)
You: quit
```

## Features

- Simple conversational interface
- Automatic plan creation and execution
- Shows task progress inline
- Minimal setup required

## How It Works

1. XAgent loads the configuration from `config/team.yaml`
2. You type messages, XAgent responds
3. Complex requests trigger automatic planning
4. Type 'quit' or 'q' to exit

## Configuration

The assistant is configured in `config/team.yaml`. The default setup includes a helpful AI assistant ready to tackle any task.

## Next Steps

- For automation and scripting, see the `stream_chat` example
- For multi-agent teams, check out `simple_team`
- For custom tools, explore `tool_chat`

## Why Simple Chat?

This example demonstrates the core VibeX experience with minimal code:
- No command-line arguments
- No complex setup
- Just pure conversation

Perfect for understanding how VibeX works before diving into advanced features.