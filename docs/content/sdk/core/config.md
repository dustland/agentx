# Configuration Models

*Module: [`vibex.core.config`](https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py)*

## ExecutionMode <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L6" class="source-link" title="View source code">source</a>

Execution modes for task processing.

## LLMProvider <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L11" class="source-link" title="View source code">source</a>

Supported LLM providers.

## ToolType <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L19" class="source-link" title="View source code">source</a>

Types of tools supported by the framework.

## CollaborationPatternType <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L26" class="source-link" title="View source code">source</a>

Types of collaboration patterns.

## GuardrailType <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L33" class="source-link" title="View source code">source</a>

Types of guardrails.

## BrainConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L40" class="source-link" title="View source code">source</a>

Brain configuration with DeepSeek as default provider.

### set_default_base_url <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L54" class="source-link" title="View source code">source</a>

```python
def set_default_base_url(self)
```
## ToolConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L59" class="source-link" title="View source code">source</a>

Tool configuration supporting multiple tool types.

## Handoff <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L76" class="source-link" title="View source code">source</a>

Defines when and how agents should hand off control.

## CollaborationPattern <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L83" class="source-link" title="View source code">source</a>

Custom collaboration pattern configuration.

## GuardrailPolicy <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L91" class="source-link" title="View source code">source</a>

Guardrail policy for safety and compliance.

## MemoryConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L99" class="source-link" title="View source code">source</a>

Memory system configuration.

## AgentConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L109" class="source-link" title="View source code">source</a>

Unified agent configuration for file definition and runtime.

## OrchestratorConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L140" class="source-link" title="View source code">source</a>

Configuration for the orchestrator's Brain and behavior.

### get_default_brain_config <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L146" class="source-link" title="View source code">source</a>

```python
def get_default_brain_config(self) -> BrainConfig
```

Get default Brain config for orchestrator if none specified.

## ProjectConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L156" class="source-link" title="View source code">source</a>

Project-specific configuration for execution control.

## TeamConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L178" class="source-link" title="View source code">source</a>

Configuration for a team of agents.

## ConfigurationError <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/config.py#L208" class="source-link" title="View source code">source</a>

Custom exception for configuration errors.
