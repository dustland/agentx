# VibeX Stream Chat Example

An enhanced chat interface for VibeX with streaming visualization, auto-execution, and automation support.

## Features

- **Streaming Visualization**: See responses arrive in real-time with timing statistics
- **Auto-Execution**: Plans execute automatically after creation (can be disabled)
- **Single-Shot Mode**: Perfect for automation and CI/CD pipelines
- **Task Management**: Create, resume, and track tasks with custom IDs
- **Rich UI**: Color-coded output with progress indicators
- **Quiet Mode**: Minimal output for scripting

## Quick Start

```bash
cd examples/stream_chat

# Interactive mode (default)
python main.py

# Single message with auto-execution
python main.py --message "Plan a 3 day trip to Paris"

# With streaming visualization
python main.py --message "Write a poem about AI" --stream

# Disable auto-execution
python main.py --message "Create a web app" --no-auto-execute
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--message` | `-m` | Send a single message and exit | - |
| `--stream` | `-s` | Show streaming progress visualization | False |
| `--auto-execute` | `-a` | Automatically execute plans | True |
| `--no-auto-execute` | - | Disable automatic execution | - |
| `--task-id` | `-t` | Use custom task ID | Auto-generated |
| `--resume` | `-r` | Resume from existing task | - |
| `--config` | `-c` | Path to team config | config/team.yaml |
| `--quiet` | `-q` | Minimal output mode | False |

## Usage Examples

### Automated Task Execution

```bash
# Create and execute a complete plan
python main.py -m "Build a REST API with authentication"

# Output shows:
# ✓ Plan created with 5 tasks
# 🚀 Auto-executing plan...
# ✅ Task 1: Design API schema
# ✅ Task 2: Implement authentication
# ... (continues until completion)
```

### Streaming Visualization

```bash
python main.py -m "Explain quantum computing" --stream

# Shows response arriving chunk by chunk:
# X: Quantum computing is... [streaming in yellow]
# ✓ Response completed in 3.2s
```

### Task Continuation

```bash
# Start a task
python main.py -t project-api -m "Create a Python REST API"

# Continue later
python main.py -r .vibex/tasks/project-api -m "Add user authentication"
```

### Quiet Mode for Scripts

```bash
# Get just the response for scripting
RESPONSE=$(python main.py -q -m "What is 2+2?")
echo "Answer: $RESPONSE"
```

## Interactive Commands

When in interactive mode, these commands are available:

- `/help` - Show available commands
- `/status` - Show current task status and plan
- `/plan` - Display detailed execution plan
- `/clear` - Clear the screen
- `quit` or `q` - Exit

## Integration Examples

### Bash Script

```bash
#!/bin/bash
# Auto-generate documentation
python main.py -q -m "Generate API docs for auth.py" > docs/auth.md
```

### Python Integration

```python
import subprocess
import json

def execute_task(prompt):
    result = subprocess.run(
        ['python', 'main.py', '-q', '-m', prompt],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# Generate and execute a plan
output = execute_task("Create unit tests for user.py")
print(f"Task completed: {output}")
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Generate Test Plan
  run: |
    cd examples/stream_chat
    python main.py -q -m "Create integration tests for ${{ github.event.pull_request.title }}"
```

## Visual Features

The stream chat provides rich visual feedback:

- 🤖 **Blue**: User messages and prompts
- 🟨 **Yellow**: Streaming responses
- ✅ **Green**: Successful operations
- ❌ **Red**: Errors and failures
- ⚠️ **Yellow**: Warnings
- 🎉 **Magenta**: Completion celebrations
- ⏱️ **Timing**: Shows execution time for each step

## Advanced Usage

### Custom Configuration

```bash
# Use a different team configuration
python main.py -c ../my_team/config.yaml -m "Analyze this codebase"
```

### Parallel Execution

When auto-executing, the system automatically runs independent tasks in parallel:

```
🚀 Auto-executing plan...
Executing 3 tasks in parallel:
  ✅ Research hotels (2.3s)
  ✅ Find restaurants (2.1s)
  ✅ Plan activities (2.5s)
```

## Differences from simple_chat

- **simple_chat**: Minimal, straightforward chat interface
- **stream_chat**: Enhanced with streaming, auto-execution, and automation features

Choose simple_chat for basic interaction, stream_chat for production workflows.

## Tips

1. Use `--stream` to see real-time progress on long responses
2. Disable auto-execution with `--no-auto-execute` for manual control
3. Use task IDs for long-running projects that span multiple sessions
4. Quiet mode is perfect for integrating with other tools
5. The system preserves completed work when modifying plans