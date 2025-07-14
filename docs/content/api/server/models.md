# Tool Models

*Module: [`agentx.server.models`](https://github.com/dustland/agentx/blob/main/src/agentx/server/models.py)*

Server Models

Data models for the AgentX REST API.

## TaskStatus <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/models.py#L18" class="source-link" title="View source code">source</a>

Task status enumeration

## TaskRequest <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/models.py#L26" class="source-link" title="View source code">source</a>

Request to create and run a task

## TaskResponse <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/models.py#L34" class="source-link" title="View source code">source</a>

Response from task operations

## TaskInfo <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/models.py#L45" class="source-link" title="View source code">source</a>

Information about a task

## MemoryRequest <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/models.py#L57" class="source-link" title="View source code">source</a>

Request for memory operations

## MemoryResponse <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/models.py#L65" class="source-link" title="View source code">source</a>

Response from memory operations

## HealthResponse <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/models.py#L74" class="source-link" title="View source code">source</a>

Health check response

## Functions

## utc_now <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/models.py#L13" class="source-link" title="View source code">source</a>

```python
def utc_now() -> datetime
```

Get current UTC datetime - replaces deprecated datetime.now()
