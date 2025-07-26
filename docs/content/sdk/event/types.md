# Memory Types

*Module: [`vibex.event.types`](https://github.com/dustland/vibex/blob/main/src/vibex/event/types.py)*

Event system type definitions.

## EventPriority <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/types.py#L26" class="source-link" title="View source code">source</a>

Event priority levels.

## EventMetadata <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/types.py#L34" class="source-link" title="View source code">source</a>

Metadata for events.

## Event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/types.py#L46" class="source-link" title="View source code">source</a>

Base event wrapper with metadata.

### event_type <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/types.py#L52" class="source-link" title="View source code">source</a>

```python
def event_type(self) -> str
```

Get the event type from the data.

### event_id <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/types.py#L59" class="source-link" title="View source code">source</a>

```python
def event_id(self) -> str
```

Get the event ID.

### timestamp <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/types.py#L64" class="source-link" title="View source code">source</a>

```python
def timestamp(self) -> datetime
```

Get the event timestamp.

## EventSubscription <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/types.py#L69" class="source-link" title="View source code">source</a>

Event subscription configuration.

## EventBusStats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/types.py#L81" class="source-link" title="View source code">source</a>

Event bus statistics.
