# Agent

*Module: [`vibex.core.agent`](https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py)*

## AgentState <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L13" class="source-link" title="View source code">source</a>

Current state of an agent during execution.

## Agent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L26" class="source-link" title="View source code">source</a>

Represents an autonomous agent that manages its own conversation flow.

Key Principles:
- Each agent is autonomous and manages its own conversation flow
- Agents communicate with other agents through public interfaces only
- The brain is private to the agent - no external access
- Tool execution is handled through the injected tool manager

This combines:
- AgentConfig (configuration data)
- Brain (private LLM interaction)
- Conversation management with integrated tool execution

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L42" class="source-link" title="View source code">source</a>

```python
def __init__(self, config: AgentConfig, tool_manager = None)
```

Initialize agent with configuration and optional tool manager.

**Args:**
    config: Agent configuration
    tool_manager: Optional tool manager (injected by TaskExecutor)

### get_max_context_tokens <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L165" class="source-link" title="View source code">source</a>

```python
def get_max_context_tokens(self) -> int
```

Get the maximum context tokens for this agent.

### get_tools_json <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L178" class="source-link" title="View source code">source</a>

```python
def get_tools_json(self) -> List[Dict[str, Any]]
```

Get the JSON schemas for the tools available to this agent.

### generate_response <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L203" class="source-link" title="View source code">source</a>

```python
async def generate_response(self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None, max_tool_rounds: int = 10) -> str
```

Generate response with tool execution.

This is a simpler, non-streaming version that returns the final response.

**Args:**
    messages: Conversation messages in LLM format
    system_prompt: Optional system prompt override
    max_tool_rounds: Maximum tool execution rounds

**Returns:**
    Final response string

### stream_response <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L241" class="source-link" title="View source code">source</a>

```python
async def stream_response(self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None, max_tool_rounds: int = 10) -> AsyncGenerator[str, None]
```

Stream response with tool execution.

This matches Brain's interface but includes tool execution loop.

**Args:**
    messages: Conversation messages in LLM format
    system_prompt: Optional system prompt override
    max_tool_rounds: Maximum tool execution rounds

Yields:
    Response chunks and tool execution status updates

### build_system_prompt <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L555" class="source-link" title="View source code">source</a>

```python
def build_system_prompt(self, context: Dict[str, Any] = None) -> str
```

Build the system prompt for the agent, including dynamic context and tool definitions.

### get_capabilities <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L634" class="source-link" title="View source code">source</a>

```python
def get_capabilities(self) -> Dict[str, Any]
```

Get agent capabilities summary.

### reset_state <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L645" class="source-link" title="View source code">source</a>

```python
def reset_state(self)
```

Reset agent state.

### add_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L649" class="source-link" title="View source code">source</a>

```python
def add_tool(self, tool)
```

Add a tool to the agent's capabilities.

### remove_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L665" class="source-link" title="View source code">source</a>

```python
def remove_tool(self, tool_name: str)
```

Remove a tool from the agent's capabilities.

### update_config <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L670" class="source-link" title="View source code">source</a>

```python
def update_config(self)
```

Update agent configuration.

### __str__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L676" class="source-link" title="View source code">source</a>

```python
def __str__(self) -> str
```
### __repr__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L679" class="source-link" title="View source code">source</a>

```python
def __repr__(self) -> str
```
## Functions

## create_assistant_agent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/agent.py#L683" class="source-link" title="View source code">source</a>

```python
def create_assistant_agent(name: str, system_message: str = '') -> Agent
```

Create a simple assistant agent with default configuration.
