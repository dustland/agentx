# Prompt Loader

*Module: [`vibex.config.prompt_loader`](https://github.com/dustland/vibex/blob/main/src/vibex/config/prompt_loader.py)*

Prompt loading and templating system for VibeX.
Handles loading prompts from markdown files with Jinja2 variable substitution.

## PromptLoader <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/prompt_loader.py#L19" class="source-link" title="View source code">source</a>

Loads and processes prompt templates from markdown files.
Supports Jinja2 templating with {{ variable_name }} syntax.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/prompt_loader.py#L25" class="source-link" title="View source code">source</a>

```python
def __init__(self, prompts_dir: str)
```

Initialize the prompt loader.

**Args:**
    prompts_dir: Directory containing prompt markdown files

### load_prompt <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/prompt_loader.py#L46" class="source-link" title="View source code">source</a>

```python
def load_prompt(self, prompt_file: str, variables: Optional[Dict[str, Any]] = None) -> str
```

Load a prompt from a markdown file with Jinja2 variable substitution.

**Args:**
    prompt_file: Name of the prompt file (e.g., "writer_agent.md")
    variables: Dictionary of variables for substitution

**Returns:**
    Processed prompt text with variables substituted

**Raises:**
    ConfigurationError: If prompt file not found or rendering fails

### list_available_prompts <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/prompt_loader.py#L82" class="source-link" title="View source code">source</a>

```python
def list_available_prompts(self) -> list[str]
```

List all available prompt files in the prompts directory.

**Returns:**
    List of prompt file names

### clear_cache <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/prompt_loader.py#L91" class="source-link" title="View source code">source</a>

```python
def clear_cache(self) -> None
```

Clear the prompt cache.

### get_template_variables <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/prompt_loader.py#L95" class="source-link" title="View source code">source</a>

```python
def get_template_variables(self, prompt_file: str) -> list[str]
```

Extract template variables from a prompt file.

**Args:**
    prompt_file: Name of the prompt file

**Returns:**
    List of variable names found in the template

### validate_template <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/prompt_loader.py#L120" class="source-link" title="View source code">source</a>

```python
def validate_template(self, prompt_file: str, variables: Dict[str, Any]) -> bool
```

Validate that a template can be rendered with given variables.

**Args:**
    prompt_file: Name of the prompt file
    variables: Variables to test with

**Returns:**
    True if template renders successfully

**Raises:**
    ConfigurationError: If template validation fails

### render_prompt_with_fallbacks <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/prompt_loader.py#L140" class="source-link" title="View source code">source</a>

```python
def render_prompt_with_fallbacks(self, prompt_file: str, variables: Dict[str, Any], fallback_values: Optional[Dict[str, Any]] = None) -> str
```

Render a prompt with fallback values for missing variables.

**Args:**
    prompt_file: Name of the prompt file
    variables: Primary variables dictionary
    fallback_values: Fallback values for missing variables

**Returns:**
    Rendered prompt text

## Functions

## create_prompt_loader <a href="https://github.com/dustland/vibex/blob/main/src/vibex/config/prompt_loader.py#L160" class="source-link" title="View source code">source</a>

```python
def create_prompt_loader(config_dir: str) -> PromptLoader
```

Factory function to create a PromptLoader instance.

**Args:**
    config_dir: Configuration directory containing prompts/ subdirectory

**Returns:**
    PromptLoader instance
