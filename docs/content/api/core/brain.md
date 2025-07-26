# Brain (LLM Interface)

*Module: [`vibex.core.brain`](https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py)*

Brain Component - Pure LLM Gateway

Handles all LLM interactions for agents, including provider abstraction,
prompt formatting, and response parsing. Does NOT handle tool execution -
that's the orchestrator's responsibility.

## BrainMessage <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py#L23" class="source-link" title="View source code">source</a>

Standard message format for brain interactions.

## BrainResponse <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py#L33" class="source-link" title="View source code">source</a>

Response from brain call, which can be either text content or a request to call tools.

## Brain <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py#L43" class="source-link" title="View source code">source</a>

Brain component that handles all LLM interactions for an agent.

This is a PURE LLM interface - it does not execute tools or handle
conversation flow. Those responsibilities belong to the orchestrator.

The Brain's only job is:
1. Format messages for the LLM
2. Make API calls
3. Parse and return responses

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py#L56" class="source-link" title="View source code">source</a>

```python
def __init__(self, config: BrainConfig)
```

Initialize Brain with Brain configuration.

**Args:**
    config: Brain configuration including provider, model, etc.

### from_config <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py#L68" class="source-link" title="View source code">source</a>

```python
def from_config(cls, brain_config: BrainConfig) -> 'Brain'
```

Create Brain instance from configuration.

### add_usage_callback <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py#L72" class="source-link" title="View source code">source</a>

```python
def add_usage_callback(self, callback)
```

Add a callback function to be called after each LLM request.

The callback will be called with (model, usage_data, response) parameters.
- For streaming: callback(model, usage_data, None)
- For non-streaming: callback(model, None, response)

**Args:**
    callback: Function to call with usage data

### remove_usage_callback <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py#L85" class="source-link" title="View source code">source</a>

```python
def remove_usage_callback(self, callback)
```

Remove a usage callback.

### generate_response <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py#L209" class="source-link" title="View source code">source</a>

```python
async def generate_response(self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None, temperature: Optional[float] = None, tools: Optional[List[Dict[str, Any]]] = None, json_mode: bool = False) -> BrainResponse
```

Generate a single response from the LLM.

This is a PURE LLM call - no tool execution, no conversation management.
If the LLM requests tool calls, they are returned in the response for
the orchestrator to handle.

**Args:**
    messages: Conversation history
    system_prompt: Optional system prompt
    temperature: Override temperature
    tools: Available tools for the LLM

**Returns:**
    LLM response (may contain tool call requests)

### think <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py#L267" class="source-link" title="View source code">source</a>

```python
async def think(self, prompt: str, system_prompt: Optional[str] = None, temperature: Optional[float] = None) -> str
```

Simple thinking interface - takes a prompt and returns text response.

This is a convenience method for simple AI interactions where you just
want to send a prompt and get back text content without dealing with
message structures or tool calls.

**Args:**
    prompt: The user prompt/question
    system_prompt: Optional system prompt
    temperature: Optional temperature override

**Returns:**
    The AI's text response

### stream_response <a href="https://github.com/dustland/vibex/blob/main/src/vibex/core/brain.py#L297" class="source-link" title="View source code">source</a>

```python
async def stream_response(self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None, temperature: Optional[float] = None, tools: Optional[List[Dict[str, Any]]] = None) -> AsyncGenerator[Dict[str, Any], None]
```

Stream response from the LLM with integrated tool call detection.

Handles both native function calling models and text-based tool calling,
always emitting structured tool-call and tool-result chunks for client visualization.

**Args:**
    messages: Conversation history
    system_prompt: Optional system prompt
    temperature: Override temperature
    tools: Available tools for the LLM

Yields:
    Dict[str, Any]: Structured chunks with type and data:
    - {'type': 'text-delta', 'content': str} - Text content chunks
    - {'type': 'tool-call', 'tool_call': obj} - Tool call requests
    - {'type': 'tool-result', 'tool_call_id': str, 'result': any} - Tool results
    - {'type': 'finish', 'finish_reason': str} - Stream completion
    - {'type': 'error', 'content': str} - Error messages
