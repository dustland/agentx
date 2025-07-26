# Configuration Models

*Module: [`vibex.config`](https://github.com/dustland/vibex/blob/main/src/vibex/config.py)*

Configuration loading system for VibeX.

Public API:
- load_team_config: Load team configuration from YAML files (if needed)
- MemoryConfig: Memory system configuration (used by memory backends)
- TeamConfig, LLMProviderConfig: Core config models (if needed)

Recommended usage:
    from vibex import execute_task
    result = execute_task("config_dir", "Your task here")
