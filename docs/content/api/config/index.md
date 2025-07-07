---
sidebar_label: config
title: agentx.config
---

Configuration loading system for AgentX.

Public API:
- load_team_config: Load team configuration from YAML files (if needed)
- MemoryConfig: Memory system configuration (used by memory backends)  
- TeamConfig, LLMProviderConfig: Core config models (if needed)

Recommended usage:
    from agentx import execute_task
    result = execute_task(&quot;config_dir&quot;, &quot;Your task here&quot;)

## load\_agents\_config

## load\_single\_agent\_config

## create\_team\_config\_template

## create\_single\_agent\_template

## validate\_config\_file

## PromptLoader

## load\_team\_config

