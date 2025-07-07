# Project Bootstrap

*Module: [`agentx.cli.bootstrap`](https://github.com/dustland/agentx/blob/main/src/agentx/cli/bootstrap.py)*

Bootstrap Project Creation

Handles the main bootstrap functionality for creating new AgentX projects.

## bootstrap_project <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/bootstrap.py#L21" class="source-link" title="View source code">source</a>

```python
def bootstrap_project(project_name: Optional[str] = None, template: Optional[str] = None, model: str = 'deepseek', interactive: bool = True) -> int
```

Bootstrap a new AgentX project with interactive wizard.
