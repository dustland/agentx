from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional, Literal, Union
from datetime import datetime
from enum import Enum

class ExecutionMode(str, Enum):
    """Execution modes for task processing."""
    AUTONOMOUS = "autonomous"
    STEP_THROUGH = "step_through"

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    CUSTOM = "custom"

class ToolType(str, Enum):
    """Types of tools supported by the framework."""
    PYTHON_FUNCTION = "python_function"
    SHELL_SCRIPT = "shell_script"
    MCP_TOOL = "mcp_tool"
    BUILTIN = "builtin"

class CollaborationPatternType(str, Enum):
    """Types of collaboration patterns."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONSENSUS = "consensus"
    DYNAMIC = "dynamic"

class GuardrailType(str, Enum):
    """Types of guardrails."""
    INPUT_VALIDATION = "input_validation"
    OUTPUT_FILTERING = "output_filtering"
    RATE_LIMITING = "rate_limiting"
    CONTENT_SAFETY = "content_safety"

class BrainConfig(BaseModel):
    """Brain configuration with DeepSeek as default provider."""
    provider: str = "deepseek"  # Default provider (Req #17)
    model: str = "deepseek-chat"  # Default model (Req #17)
    temperature: float = 0.7
    max_tokens: int = 8000  # Maximum supported by deepseek-chat model
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    supports_function_calls: bool = True  # Whether the model supports native function calling
    streaming: bool = True  # Whether to use streaming mode

    @model_validator(mode='after')
    def set_default_base_url(self):
        if self.base_url is None and self.provider == 'deepseek':
            self.base_url = 'https://api.deepseek.com'
        return self

class ToolConfig(BaseModel):
    """Tool configuration supporting multiple tool types."""
    name: str
    type: Union[ToolType, str]  # Accept both enum and string values
    description: Optional[str] = None
    source: Optional[str] = None  # For python_function tools
    parameters: Optional[Dict[str, Any]] = None  # JSON schema for parameters
    config: Dict[str, Any] = Field(default_factory=dict)
    # For custom tools
    path: Optional[str] = None
    function: Optional[str] = None
    # For MCP tools
    server_url: Optional[str] = None
    # For HITL tools
    timeout: Optional[int] = None
    escalation_policy: Optional[str] = None

class Handoff(BaseModel):
    """Defines when and how agents should hand off control."""
    from_agent: str
    to_agent: str
    condition: str  # Natural language description of when to handoff (AG2-consistent)
    priority: int = 1  # Higher numbers = higher priority

class CollaborationPattern(BaseModel):
    """Custom collaboration pattern configuration."""
    name: str
    type: str  # "parallel", "consensus", "custom"
    agents: List[str]
    coordination_agent: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)

class GuardrailPolicy(BaseModel):
    """Guardrail policy for safety and compliance."""
    name: str
    type: str  # "input_validation", "content_filter", "rate_limit", "compliance"
    rules: List[Dict[str, Any]]
    severity: str = "medium"
    action: str = "warn"  # "block", "warn", "log"

class MemoryConfig(BaseModel):
    """Memory system configuration."""
    enabled: bool = True
    max_context_tokens: int = 8000
    semantic_search_enabled: bool = True
    short_term_limit: int = 10000  # tokens
    long_term_enabled: bool = True
    consolidation_interval: int = 3600  # seconds
    vector_db_config: Dict[str, Any] = Field(default_factory=dict)

class AgentConfig(BaseModel):
    """Unified agent configuration for file definition and runtime."""
    name: str
    description: Optional[str] = ""

    # Prompt can be provided directly, via a file path, or a default will be used.
    system_message: Optional[str] = None # Direct prompt content
    prompt_file: Optional[str] = None # Path to prompt file
    prompt_template: Optional[str] = None # The resolved, runtime prompt content

    # Runtime and tool configurations
    brain_config: Optional[BrainConfig] = None  # Override default Brain
    tools: List[str] = Field(default_factory=list)

    # Fields from the old AgentConfigFile
    role: str = "assistant"
    enable_code_execution: bool = False
    enable_human_interaction: bool = False
    enable_memory: bool = True
    max_consecutive_replies: int = 10
    auto_reply: bool = True

    # Core runtime fields
    memory_config: Optional[MemoryConfig] = None
    guardrail_policies: List[str] = Field(default_factory=list)
    collaboration_patterns: List[str] = Field(default_factory=list)
    max_parallel_tasks: int = 1

    class Config:
        extra = 'allow'

class OrchestratorConfig(BaseModel):
    """Configuration for the orchestrator's Brain and behavior."""
    brain_config: Optional[BrainConfig] = None  # Orchestrator's Brain config for routing decisions
    max_rounds: int = 50
    timeout: int = 3600

    def get_default_brain_config(self) -> BrainConfig:
        """Get default Brain config for orchestrator if none specified."""
        return BrainConfig(
            provider="deepseek",
            model="deepseek-chat",
            temperature=0.3,  # Moderate temperature for creative planning
            max_tokens=8000,  # Maximum supported by deepseek-chat model
            timeout=120       # Reasonable timeout for complex planning
        )

class TaskConfig(BaseModel):
    """Task-specific configuration for execution control."""
    mode: str = "autonomous"  # "autonomous", "step_through"
    max_rounds: int = 10  # Maximum conversation rounds - default to 10 for most use cases
    timeout_seconds: int = 300  # Task timeout
    initial_agent: Optional[str] = None  # Initial agent to start with
    step_through_enabled: bool = False
    max_steps: Optional[int] = None
    breakpoints: List[str] = Field(default_factory=list)
    human_intervention_points: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    failure_criteria: List[str] = Field(default_factory=list)
    orchestrator: OrchestratorConfig = Field(default_factory=OrchestratorConfig)
    deployment_config: Dict[str, Any] = Field(default_factory=dict)

    # Dynamic context variables for agent coordination
    context_variables: Dict[str, Any] = Field(default_factory=dict)

    # Legacy fields for backward compatibility
    timeout: int = 3600
    after_work_behavior: str = "return_to_user"  # Default behavior when no more handoffs available

class TeamConfig(BaseModel):
    """Configuration for a team of agents."""
    name: str
    description: str = ""
    output_dir: str = "workspace"
    agents: List[AgentConfig] = Field(default_factory=list)
    handoffs: List[Handoff] = Field(default_factory=list)
    collaboration_patterns: List[CollaborationPattern] = Field(default_factory=list)
    tools: List[ToolConfig] = Field(default_factory=list)
    guardrail_policies: List[GuardrailPolicy] = Field(default_factory=list)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    execution: TaskConfig = Field(default_factory=TaskConfig)
    orchestrator: OrchestratorConfig = Field(default_factory=OrchestratorConfig)
    deployment_config: Dict[str, Any] = Field(default_factory=dict)

    # LLM provider configuration at team level
    llm_provider: Optional[BrainConfig] = None

    # Collaboration settings
    speaker_selection_method: str = "auto"  # "auto", "round_robin", "manual"
    termination_condition: str = "TERMINATE"  # Default termination keyword

    # Dynamic context variables for agent coordination
    context_variables: Dict[str, Any] = Field(default_factory=dict)

    # Legacy fields for backward compatibility
    max_rounds: int = 10  # Default to 10 rounds, more reasonable for most use cases
    timeout: int = 3600
    after_work_behavior: str = "return_to_user"  # Default behavior when no more handoffs available

class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass
