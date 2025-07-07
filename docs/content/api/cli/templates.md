# Project Templates

*Module: [`agentx.cli.templates`](https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py)*

Bootstrap Template Generation

Handles generation of project templates, configurations, and files for the bootstrap system.

## generate_template_config <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py#L13" class="source-link" title="View source code">source</a>

```python
def generate_template_config(template: str, model: str) -> str
```

Generate team configuration based on template using preset agents.

## generate_template_prompts <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py#L80" class="source-link" title="View source code">source</a>

```python
def generate_template_prompts(template: str) -> Dict[str, str]
```

Generate prompt files based on template - now minimal since we use presets.

## generate_main_py <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py#L88" class="source-link" title="View source code">source</a>

```python
def generate_main_py(project_name: str, template: str) -> str
```

Generate main.py file for the project.

## generate_env_example <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py#L152" class="source-link" title="View source code">source</a>

```python
def generate_env_example(model: str) -> str
```

Generate .env.example file with API key templates.

## generate_readme <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py#L202" class="source-link" title="View source code">source</a>

```python
def generate_readme(project_name: str, template: str, model: str) -> str
```

Generate README.md for the project.

## get_template_description <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py#L311" class="source-link" title="View source code">source</a>

```python
def get_template_description(template: str) -> str
```

Get detailed description for template.

## get_default_model <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py#L347" class="source-link" title="View source code">source</a>

```python
def get_default_model(model: str) -> str
```

Get default model name for provider.

## get_agents_description <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py#L358" class="source-link" title="View source code">source</a>

```python
def get_agents_description(template: str) -> str
```

Get agents description for template.

## get_config_lines <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py#L382" class="source-link" title="View source code">source</a>

```python
def get_config_lines(template: str) -> str
```

Get number of configuration lines for template.

## get_sample_config <a href="https://github.com/dustland/agentx/blob/main/src/agentx/cli/templates.py#L388" class="source-link" title="View source code">source</a>

```python
def get_sample_config(template: str) -> str
```

Get sample configuration for template.
