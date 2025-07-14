# Configuration Models

*Module: [`agentx.config`](https://github.com/dustland/agentx/blob/main/src/agentx/config.py)*

Configuration loading system for AgentX.

Public API:
- load_team_config: Load team configuration from YAML files (if needed)
- MemoryConfig: Memory system configuration (used by memory backends)
- TeamConfig, LLMProviderConfig: Core config models (if needed)

Recommended usage:
    from agentx import execute_task
    result = execute_task("config_dir", "Your task here")
