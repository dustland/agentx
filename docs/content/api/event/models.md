# Tool Models

*Module: [`vibex.event.models`](https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py)*

Event subsystem models - Self-contained data models for event management.

This module contains all data models related to event management, following the
architectural rule that subsystems should be self-contained and not import from core.

## EventType <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L28" class="source-link" title="View source code">source</a>

Types of events in the system.

## EventPriority <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L68" class="source-link" title="View source code">source</a>

Event priority levels.

## EventStatus <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L76" class="source-link" title="View source code">source</a>

Event processing status.

## Event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L89" class="source-link" title="View source code">source</a>

Base event model for the VibeX framework.

### to_dict <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L111" class="source-link" title="View source code">source</a>

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary for serialization.

## ProjectEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L134" class="source-link" title="View source code">source</a>

Project-related events.

## ProjectStartEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L146" class="source-link" title="View source code">source</a>

Event emitted when a project starts.

## ProjectCompleteEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L153" class="source-link" title="View source code">source</a>

Event emitted when a project completes.

## ProjectFailEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L161" class="source-link" title="View source code">source</a>

Event emitted when a project fails.

## AgentEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L169" class="source-link" title="View source code">source</a>

Agent-related events.

## AgentStartEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L180" class="source-link" title="View source code">source</a>

Event emitted when an agent starts processing.

## AgentCompleteEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L187" class="source-link" title="View source code">source</a>

Event emitted when an agent completes processing.

## AgentHandoffEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L195" class="source-link" title="View source code">source</a>

Event emitted when an agent hands off to another agent.

## ToolEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L203" class="source-link" title="View source code">source</a>

Tool-related events.

## ToolCallStartEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L214" class="source-link" title="View source code">source</a>

Event emitted when a tool call starts.

## ToolCallCompleteEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L221" class="source-link" title="View source code">source</a>

Event emitted when a tool call completes.

## ToolCallFailEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L229" class="source-link" title="View source code">source</a>

Event emitted when a tool call fails.

## MemoryEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L237" class="source-link" title="View source code">source</a>

Memory-related events.

## StorageEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L246" class="source-link" title="View source code">source</a>

Storage-related events.

## SystemEvent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L256" class="source-link" title="View source code">source</a>

System-related events.

## EventSubscription <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L283" class="source-link" title="View source code">source</a>

Event subscription configuration.

## EventSubscriptionStats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L295" class="source-link" title="View source code">source</a>

Statistics for event subscriptions.

## EventBusConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L309" class="source-link" title="View source code">source</a>

Configuration for the event bus.

## EventBusStats <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L320" class="source-link" title="View source code">source</a>

Event bus statistics.

## EventBusHealth <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L331" class="source-link" title="View source code">source</a>

Event bus health status.

## EventMiddleware <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L345" class="source-link" title="View source code">source</a>

Abstract base class for event middleware.

### process_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L349" class="source-link" title="View source code">source</a>

```python
async def process_event(self, event: Event) -> Event
```

Process an event and return the modified event.

### get_name <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L354" class="source-link" title="View source code">source</a>

```python
def get_name(self) -> str
```

Get the middleware name.

## EventMiddlewareConfig <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L359" class="source-link" title="View source code">source</a>

Configuration for event middleware.

## EventLogEntry <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L371" class="source-link" title="View source code">source</a>

Event log entry for audit purposes.

## EventAuditFilter <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L381" class="source-link" title="View source code">source</a>

Filter for event audit queries.

## EventStream <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L397" class="source-link" title="View source code">source</a>

Event stream configuration.

## EventBatch <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L408" class="source-link" title="View source code">source</a>

Batch of events for streaming.

## Functions

## generate_short_id <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L18" class="source-link" title="View source code">source</a>

```python
def generate_short_id(length: int = 8) -> str
```

Generate a short, URL-friendly, cryptographically secure random ID.

## create_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L421" class="source-link" title="View source code">source</a>

```python
def create_event(event_type: EventType, source: str, data: Dict[str, Any] = None, project_id: str = None, agent_name: str = None, tool_name: str = None, priority: EventPriority = EventPriority.NORMAL) -> Event
```

Create a new event with the specified parameters.

## create_project_start_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L436" class="source-link" title="View source code">source</a>

```python
def create_project_start_event(project_id: str, source: str, task_config: Dict[str, Any] = None, initial_prompt: str = None) -> ProjectStartEvent
```

Create a project start event.

## create_tool_call_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L447" class="source-link" title="View source code">source</a>

```python
def create_tool_call_event(tool_name: str, tool_call_id: str, source: str, args: Dict[str, Any] = None, project_id: str = None, agent_name: str = None) -> ToolCallStartEvent
```

Create a tool call start event.

## create_agent_handoff_event <a href="https://github.com/dustland/vibex/blob/main/src/vibex/event/models.py#L461" class="source-link" title="View source code">source</a>

```python
def create_agent_handoff_event(from_agent: str, to_agent: str, source: str, project_id: str = None, handoff_reason: str = None) -> AgentHandoffEvent
```

Create an agent handoff event.
