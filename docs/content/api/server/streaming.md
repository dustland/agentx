# Streaming

*Module: [`agentx.server.streaming`](https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py)*

Streaming support for AgentX API

## TaskEventStream <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L13" class="source-link" title="View source code">source</a>

Manages event streams for tasks

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L16" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### create_stream <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L19" class="source-link" title="View source code">source</a>

```python
def create_stream(self, task_id: str) -> asyncio.Queue
```

Create a new event stream for a task

### get_stream <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L25" class="source-link" title="View source code">source</a>

```python
def get_stream(self, task_id: str) -> Optional[asyncio.Queue]
```

Get existing stream for a task

### send_event <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L29" class="source-link" title="View source code">source</a>

```python
async def send_event(self, task_id: str, event_type: str, data: Any)
```

Send an event to all listeners of a task

### stream_events <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L42" class="source-link" title="View source code">source</a>

```python
async def stream_events(self, task_id: str) -> AsyncGenerator[str, None]
```

Stream events for a task as SSE format

### close_stream <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L65" class="source-link" title="View source code">source</a>

```python
def close_stream(self, task_id: str)
```

Close and remove a stream

## Functions

## send_agent_message <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L73" class="source-link" title="View source code">source</a>

```python
async def send_agent_message(task_id: str, agent_id: str, message: str, metadata: Optional[Dict] = None)
```

Send an agent message event

## send_agent_status <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L85" class="source-link" title="View source code">source</a>

```python
async def send_agent_status(task_id: str, agent_id: str, status: str, progress: int = 0)
```

Send an agent status update

## send_task_update <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L97" class="source-link" title="View source code">source</a>

```python
async def send_task_update(task_id: str, status: str, result: Optional[Any] = None)
```

Send a task status update

## send_tool_call <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/streaming.py#L109" class="source-link" title="View source code">source</a>

```python
async def send_tool_call(task_id: str, agent_id: str, tool_name: str, parameters: Dict, result: Optional[Any] = None, status: str = 'pending')
```

Send a tool call event
