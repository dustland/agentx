# Event Subscribers

*Module: [`vibex.event.subscribers`](https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py)*

Event subscribers for the VibeX event system.

Provides base classes and utilities for creating event subscribers.

## EventSubscriber <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L18" class="source-link" title="View source code">source</a>

Base class for event subscribers.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L21" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str)
```
### get_event_types <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L28" class="source-link" title="View source code">source</a>

```python
def get_event_types(self) -> List[str]
```

Return list of event types this subscriber handles.

### handle_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L33" class="source-link" title="View source code">source</a>

```python
def handle_event(self, event_data: Any) -> None
```

Handle an event.

### get_filter <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L37" class="source-link" title="View source code">source</a>

```python
def get_filter(self) -> Optional[EventFilter]
```

Return optional filter function for events.

### get_priority <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L41" class="source-link" title="View source code">source</a>

```python
def get_priority(self) -> EventPriority
```

Return subscription priority.

### start <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L45" class="source-link" title="View source code">source</a>

```python
def start(self) -> None
```

Start subscribing to events.

### stop <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L67" class="source-link" title="View source code">source</a>

```python
def stop(self) -> None
```

Stop subscribing to events.

### is_active <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L79" class="source-link" title="View source code">source</a>

```python
def is_active(self) -> bool
```

Check if subscriber is active.

## AsyncEventSubscriber <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L84" class="source-link" title="View source code">source</a>

Base class for async event subscribers.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L87" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str)
```
### get_event_types <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L94" class="source-link" title="View source code">source</a>

```python
def get_event_types(self) -> List[str]
```

Return list of event types this subscriber handles.

### handle_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L99" class="source-link" title="View source code">source</a>

```python
async def handle_event(self, event_data: Any) -> None
```

Handle an event asynchronously.

### get_filter <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L103" class="source-link" title="View source code">source</a>

```python
def get_filter(self) -> Optional[EventFilter]
```

Return optional filter function for events.

### get_priority <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L107" class="source-link" title="View source code">source</a>

```python
def get_priority(self) -> EventPriority
```

Return subscription priority.

### start <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L111" class="source-link" title="View source code">source</a>

```python
def start(self) -> None
```

Start subscribing to events.

### stop <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L133" class="source-link" title="View source code">source</a>

```python
def stop(self) -> None
```

Stop subscribing to events.

### is_active <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L145" class="source-link" title="View source code">source</a>

```python
def is_active(self) -> bool
```

Check if subscriber is active.

## ObservabilitySubscriber <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L150" class="source-link" title="View source code">source</a>

Subscriber for observability events.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L153" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str = 'observability')
```
### get_event_types <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L157" class="source-link" title="View source code">source</a>

```python
def get_event_types(self) -> List[str]
```

Subscribe to all event types for observability.

### handle_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L174" class="source-link" title="View source code">source</a>

```python
async def handle_event(self, event_data: Any) -> None
```

Handle observability events.

### get_recent_events <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L190" class="source-link" title="View source code">source</a>

```python
def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]
```

Get recent events for observability.

### get_events_by_type <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L194" class="source-link" title="View source code">source</a>

```python
def get_events_by_type(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]
```

Get events of a specific type.

## MetricsSubscriber <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L203" class="source-link" title="View source code">source</a>

Subscriber for collecting metrics from events.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L206" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str = 'metrics')
```
### get_event_types <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L217" class="source-link" title="View source code">source</a>

```python
def get_event_types(self) -> List[str]
```

Subscribe to metric-relevant events.

### handle_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L227" class="source-link" title="View source code">source</a>

```python
async def handle_event(self, event_data: Any) -> None
```

Handle metric events.

### get_metrics <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L269" class="source-link" title="View source code">source</a>

```python
def get_metrics(self) -> Dict[str, Any]
```

Get current metrics.

### reset_metrics <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/subscribers.py#L281" class="source-link" title="View source code">source</a>

```python
def reset_metrics(self) -> None
```

Reset all metrics.
