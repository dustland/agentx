# Project Bootstrap

*Module: [`vibex.cli.bootstrap`](https://github.com/dustland/vibex/blob/main/src/vibex/cli/bootstrap.py)*

Bootstrap Project Creation

Handles the main bootstrap functionality for creating new VibeX projects.

## bootstrap_project <a href="https://github.com/dustland/vibex/blob/main/src/vibex/cli/bootstrap.py#L21" class="source-link" title="View source code">source</a>

```python
def bootstrap_project(project_name: Optional[str] = None, template: Optional[str] = None, model: str = 'deepseek', interactive: bool = True) -> int
```

Bootstrap a new VibeX project with interactive wizard.
