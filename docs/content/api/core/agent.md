# Agent

*Module: [`agentx.core.agent`](https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py)*

## AgentState <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L17" class="source-link" title="View source code">source</a>

Current state of an agent during execution.

## Agent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L30" class="source-link" title="View source code">source</a>

Represents an autonomous agent that manages its own conversation flow.

Key Principles:
- Each agent is autonomous and manages its own conversation flow
- Agents communicate with other agents through public interfaces only
- The brain is private to the agent - no external access
- Tool execution is handled by orchestrator for security and control

This combines:
- AgentConfig (configuration data)
- Brain (private LLM interaction)
- Conversation management (delegates tool execution to orchestrator)

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L46" class="source-link" title="View source code">source</a>

```python
def __init__(self, config: AgentConfig, tool_manager = None)
```

Initialize agent with configuration and optional tool manager.

**Args:**
    config: Agent configuration
    tool_manager: Optional tool manager (injected by TaskExecutor)

### get_max_context_tokens <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L166" class="source-link" title="View source code">source</a>

```python
def get_max_context_tokens(self) -> int
```

Get the maximum context tokens for this agent.

### get_tools_json <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L179" class="source-link" title="View source code">source</a>

```python
def get_tools_json(self) -> List[Dict[str, Any]]
```

Get the JSON schemas for the tools available to this agent.

### generate_response <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L204" class="source-link" title="View source code">source</a>

```python
async def generate_response(self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None, orchestrator = None, max_tool_rounds: int = 10) -> str
```

Generate response with tool execution handled by orchestrator.

This is a simpler, non-streaming version that returns the final response.

**Args:**
    messages: Conversation messages in LLM format
    system_prompt: Optional system prompt override
    orchestrator: Orchestrator instance for tool execution
    max_tool_rounds: Maximum tool execution rounds

**Returns:**
    Final response string

### stream_response <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L244" class="source-link" title="View source code">source</a>

```python
async def stream_response(self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None, orchestrator = None, max_tool_rounds: int = 10) -> AsyncGenerator[str, None]
```

Stream response with tool execution handled by orchestrator.

This matches Brain's interface but includes tool execution loop.

**Args:**
    messages: Conversation messages in LLM format
    system_prompt: Optional system prompt override
    orchestrator: Orchestrator instance for tool execution
    max_tool_rounds: Maximum tool execution rounds

Yields:
    Response chunks and tool execution status updates

### build_system_prompt <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L563" class="source-link" title="View source code">source</a>

```python
def build_system_prompt(self, context: Dict[str, Any] = None) -> str
```

Build the system prompt for the agent, including dynamic context and tool definitions.

### get_capabilities <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L642" class="source-link" title="View source code">source</a>

```python
def get_capabilities(self) -> Dict[str, Any]
```

Get agent capabilities summary.

### reset_state <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L653" class="source-link" title="View source code">source</a>

```python
def reset_state(self)
```

Reset agent state.

### add_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L657" class="source-link" title="View source code">source</a>

```python
def add_tool(self, tool)
```

Add a tool to the agent's capabilities.

### remove_tool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L673" class="source-link" title="View source code">source</a>

```python
def remove_tool(self, tool_name: str)
```

Remove a tool from the agent's capabilities.

### update_config <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L678" class="source-link" title="View source code">source</a>

```python
def update_config(self)
```

Update agent configuration.

### __str__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L684" class="source-link" title="View source code">source</a>

```python
def __str__(self) -> str
```
### __repr__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L687" class="source-link" title="View source code">source</a>

```python
def __repr__(self) -> str
```
## Functions

## create_assistant_agent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/core/agent.py#L691" class="source-link" title="View source code">source</a>

```python
def create_assistant_agent(name: str, system_message: str = '') -> Agent
```

Create a simple assistant agent with default configuration.
