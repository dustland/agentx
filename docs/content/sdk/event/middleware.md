# Event Middleware

*Module: [`vibex.event.middleware`](https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py)*

Event middleware for the VibeX event system.

Provides middleware components for logging, metrics, and custom event processing.

## EventMiddleware <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L18" class="source-link" title="View source code">source</a>

Base class for event middleware.

### before_publish <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L22" class="source-link" title="View source code">source</a>

```python
async def before_publish(self, event: Event) -> None
```

Called before an event is published.

### before_process <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L27" class="source-link" title="View source code">source</a>

```python
async def before_process(self, event: Event) -> None
```

Called before an event is processed.

### after_process <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L32" class="source-link" title="View source code">source</a>

```python
async def after_process(self, event: Event) -> None
```

Called after an event is processed.

### on_error <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L37" class="source-link" title="View source code">source</a>

```python
async def on_error(self, event: Event, error: Exception) -> None
```

Called when an error occurs during event processing.

## LoggingMiddleware <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L42" class="source-link" title="View source code">source</a>

Middleware for logging events.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L45" class="source-link" title="View source code">source</a>

```python
def __init__(self, log_level: int = logging.INFO)
```
### before_publish <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L49" class="source-link" title="View source code">source</a>

```python
async def before_publish(self, event: Event) -> None
```

Log event publication.

### before_process <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L56" class="source-link" title="View source code">source</a>

```python
async def before_process(self, event: Event) -> None
```

Log event processing start.

### after_process <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L63" class="source-link" title="View source code">source</a>

```python
async def after_process(self, event: Event) -> None
```

Log event processing completion.

### on_error <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L70" class="source-link" title="View source code">source</a>

```python
async def on_error(self, event: Event, error: Exception) -> None
```

Log event processing error.

## MetricsMiddleware <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L78" class="source-link" title="View source code">source</a>

Middleware for collecting event metrics.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L81" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### before_publish <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L92" class="source-link" title="View source code">source</a>

```python
async def before_publish(self, event: Event) -> None
```

Record event publication metrics.

### before_process <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L102" class="source-link" title="View source code">source</a>

```python
async def before_process(self, event: Event) -> None
```

Record processing start time.

### after_process <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L106" class="source-link" title="View source code">source</a>

```python
async def after_process(self, event: Event) -> None
```

Record processing completion metrics.

### on_error <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L120" class="source-link" title="View source code">source</a>

```python
async def on_error(self, event: Event, error: Exception) -> None
```

Record error metrics.

### get_metrics <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L141" class="source-link" title="View source code">source</a>

```python
def get_metrics(self) -> Dict[str, Any]
```

Get current metrics.

### reset_metrics <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L153" class="source-link" title="View source code">source</a>

```python
def reset_metrics(self) -> None
```

Reset all metrics.

## FilterMiddleware <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L166" class="source-link" title="View source code">source</a>

Middleware for filtering events based on custom criteria.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L169" class="source-link" title="View source code">source</a>

```python
def __init__(self, filter_func: callable)
```
### before_publish <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L172" class="source-link" title="View source code">source</a>

```python
async def before_publish(self, event: Event) -> None
```

Apply filter before publishing.

### before_process <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L177" class="source-link" title="View source code">source</a>

```python
async def before_process(self, event: Event) -> None
```

Apply filter before processing.

### after_process <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L182" class="source-link" title="View source code">source</a>

```python
async def after_process(self, event: Event) -> None
```

No action needed after processing.

### on_error <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L186" class="source-link" title="View source code">source</a>

```python
async def on_error(self, event: Event, error: Exception) -> None
```

No action needed on error.

## CorrelationMiddleware <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L191" class="source-link" title="View source code">source</a>

Middleware for handling event correlation and tracing.

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L194" class="source-link" title="View source code">source</a>

```python
def __init__(self)
```
### before_publish <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L197" class="source-link" title="View source code">source</a>

```python
async def before_publish(self, event: Event) -> None
```

Track correlation before publishing.

### before_process <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L210" class="source-link" title="View source code">source</a>

```python
async def before_process(self, event: Event) -> None
```

Track correlation before processing.

### after_process <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L221" class="source-link" title="View source code">source</a>

```python
async def after_process(self, event: Event) -> None
```

Track correlation after processing.

### on_error <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L232" class="source-link" title="View source code">source</a>

```python
async def on_error(self, event: Event, error: Exception) -> None
```

Track correlation on error.

### get_correlation_trace <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L244" class="source-link" title="View source code">source</a>

```python
def get_correlation_trace(self, correlation_id: str) -> Optional[list]
```

Get the trace for a correlation ID.

### cleanup_old_correlations <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/middleware.py#L248" class="source-link" title="View source code">source</a>

```python
def cleanup_old_correlations(self, max_age_hours: int = 24) -> None
```

Clean up old correlation traces.
