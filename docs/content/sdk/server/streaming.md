# Streaming

*Module: [`vibex.server.streaming`](https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py)*

Streaming support for VibeX API

## ProjectEventStream <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L15" class="source-link" title="View source code">source</a>

Manages event streams for projects

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L18" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### create_stream <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L21" class="source-link" title="View source code">source</a>

```python
def create_stream(self, project_id: str) -> asyncio.Queue
```

Create a new event stream for a project

### get_stream <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L27" class="source-link" title="View source code">source</a>

```python
def get_stream(self, project_id: str) -> Optional[asyncio.Queue]
```

Get existing stream for a project

### send_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L31" class="source-link" title="View source code">source</a>

```python
async def send_event(self, project_id: str, event_type: str, data: Any)
```

Send an event to all listeners of a project

### stream_events <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L49" class="source-link" title="View source code">source</a>

```python
async def stream_events(self, project_id: str) -> AsyncGenerator[Dict[str, Any], None]
```

Stream events for a project as dictionaries for EventSourceResponse

### close_stream <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L89" class="source-link" title="View source code">source</a>

```python
def close_stream(self, project_id: str)
```

Close and remove a stream

## Functions

## send_agent_status <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L99" class="source-link" title="View source code">source</a>

```python
async def send_agent_status(project_id: str, agent_id: str, status: str, progress: int = 0)
```

Send an agent status update

## send_project_update <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L111" class="source-link" title="View source code">source</a>

```python
async def send_project_update(project_id: str, status: str, result: Optional[Any] = None)
```

Send a project status update

## send_tool_call <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L124" class="source-link" title="View source code">source</a>

```python
async def send_tool_call(project_id: str, agent_id: str, tool_name: str, parameters: Dict, result: Optional[Any] = None, status: str = 'pending')
```

Send a tool call event

## send_streaming_chunk <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L138" class="source-link" title="View source code">source</a>

```python
async def send_streaming_chunk(project_id: str, taskspace_path: str, chunk: StreamChunk)
```

Send a streaming message chunk and handle persistence.

## send_complete_message <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L158" class="source-link" title="View source code">source</a>

```python
async def send_complete_message(project_id: str, taskspace_path: str, message: Message)
```

Send a complete message and persist it.

## send_message_object <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L175" class="source-link" title="View source code">source</a>

```python
async def send_message_object(project_id: str, message: Message)
```

Send a Message object directly via SSE without persistence (already handled in core).

## send_stream_chunk <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L193" class="source-link" title="View source code">source</a>

```python
async def send_stream_chunk(project_id: str, chunk: str, message_id: str, is_final: bool = False, error: Optional[str] = None)
```

Send a streaming text chunk for real-time UI updates.

## send_tool_call_start <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L211" class="source-link" title="View source code">source</a>

```python
async def send_tool_call_start(project_id: str, tool_call_id: str, tool_name: str, args: Dict[str, Any])
```

Send a tool call start event for streaming.

## send_tool_call_result <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/streaming.py#L224" class="source-link" title="View source code">source</a>

```python
async def send_tool_call_result(project_id: str, tool_call_id: str, tool_name: str, result: Any, is_error: bool = False)
```

Send a tool call result event for streaming.
