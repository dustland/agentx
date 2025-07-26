# Event Bus

*Module: [`vibex.event.bus`](https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py)*

Event Bus implementation for VibeX framework.

Provides a centralized event system with publish/subscribe patterns,
middleware support, and comprehensive observability features.

## EventBus <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L27" class="source-link" title="View source code">source</a>

Centralized event bus for publish/subscribe messaging.

Features:
- Async/sync event publishing
- Priority-based event processing
- Event filtering and routing
- Middleware support
- Comprehensive statistics
- Error handling and retries

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L40" class="source-link" title="View source code">source</a>

```python
def __init__(self, name: str = 'default')
```
### start <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L52" class="source-link" title="View source code">source</a>

```python
async def start(self) -> None
```

Start the event bus worker.

### stop <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L61" class="source-link" title="View source code">source</a>

```python
async def stop(self) -> None
```

Stop the event bus worker.

### add_middleware <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L77" class="source-link" title="View source code">source</a>

```python
def add_middleware(self, middleware: EventMiddleware) -> None
```

Add middleware to the event bus.

### subscribe <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L82" class="source-link" title="View source code">source</a>

```python
def subscribe(self, event_types: Union[str, List[str]], handler: EventHandler, filter_func: Optional[EventFilter] = None, priority: EventPriority = EventPriority.NORMAL, subscription_id: Optional[str] = None) -> str
```

Subscribe to events.

**Args:**
    event_types: Event type(s) to subscribe to. Supports wildcards:
                - "*" matches any characters
                - "?" matches single character
                - "Agent*" matches "AgentStartEvent", "AgentCompleteEvent", etc.
                - "*Event" matches all events ending with "Event"
    handler: Event handler function
    filter_func: Optional filter function
    priority: Subscription priority
    subscription_id: Optional custom subscription ID

**Returns:**
    Subscription ID

### unsubscribe <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L132" class="source-link" title="View source code">source</a>

```python
def unsubscribe(self, subscription_id: str) -> bool
```

Unsubscribe from events.

**Args:**
    subscription_id: Subscription ID to remove

**Returns:**
    True if subscription was found and removed

### publish <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L159" class="source-link" title="View source code">source</a>

```python
async def publish(self, event_data: Any, event_type: Optional[str] = None, priority: EventPriority = EventPriority.NORMAL, source: Optional[str] = None, correlation_id: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> str
```

Publish an event.

**Args:**
    event_data: Event data (should be a Pydantic model)
    event_type: Optional event type override
    priority: Event priority
    source: Event source identifier
    correlation_id: Correlation ID for tracing
    tags: Additional tags

**Returns:**
    Event ID

### publish_sync <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L222" class="source-link" title="View source code">source</a>

```python
def publish_sync(self, event_data: Any, event_type: Optional[str] = None, priority: EventPriority = EventPriority.NORMAL, source: Optional[str] = None, correlation_id: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> str
```

Synchronous wrapper for publish.

**Note:** This creates a task but doesn't wait for it in sync context.
Use publish() in async contexts for proper awaiting.

### get_stats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L354" class="source-link" title="View source code">source</a>

```python
def get_stats(self) -> EventBusStats
```

Get event bus statistics.

### get_subscriptions <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L358" class="source-link" title="View source code">source</a>

```python
def get_subscriptions(self) -> Dict[str, List[str]]
```

Get current subscriptions by event type.

### health_check <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L365" class="source-link" title="View source code">source</a>

```python
async def health_check(self) -> Dict[str, Any]
```

Perform health check.

## Functions

## get_event_bus <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L383" class="source-link" title="View source code">source</a>

```python
def get_event_bus(name: str = 'default') -> EventBus
```

Get or create the global event bus instance.

## initialize_event_bus <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/bus.py#L393" class="source-link" title="View source code">source</a>

```python
async def initialize_event_bus(name: str = 'default') -> EventBus
```

Initialize and start the global event bus.
