# Tool Commands

*Module: [`vibex.cli.tools`](https://github.com/dustland/vibex/blob/main/src/vibex/cli/tools.py)*

CLI commands for tool management and discovery.

## tools <a href="https://github.com/dustland/vibex/blob/main/src/vibex/cli/tools.py#L45" class="source-link" title="View source code">source</a>

```python
def tools()
```

Tool management commands.

## list_cli <a href="https://github.com/dustland/vibex/blob/main/src/vibex/cli/tools.py#L51" class="source-link" title="View source code">source</a>

```python
def list_cli()
```

List all available tools with descriptions.

## validate <a href="https://github.com/dustland/vibex/blob/main/src/vibex/cli/tools.py#L59" class="source-link" title="View source code">source</a>

```python
def validate(tool_names)
```

Validate tool names against available tools.

## suggest <a href="https://github.com/dustland/vibex/blob/main/src/vibex/cli/tools.py#L90" class="source-link" title="View source code">source</a>

```python
def suggest(agent_name, description)
```

Suggest relevant tools for an agent based on name and description.
