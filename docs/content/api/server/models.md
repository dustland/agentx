# Tool Models

*Module: [`vibex.server.models`](https://github.com/dustland/vibex/blob/main/src/vibex/server/models.py)*

Server Models

Data models for the VibeX REST API.

## TaskStatus <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/models.py#L18" class="source-link" title="View source code">source</a>

Task status enumeration - aligns with XAgent task statuses

## CreateXAgentRequest <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/models.py#L27" class="source-link" title="View source code">source</a>

Request to create and run an XAgent instance

## XAgentResponse <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/models.py#L35" class="source-link" title="View source code">source</a>

Response from XAgent operations

## TaskRunInfo <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/models.py#L50" class="source-link" title="View source code">source</a>

Detailed information about a task run

## XAgentListResponse <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/models.py#L63" class="source-link" title="View source code">source</a>

Response for listing XAgents

## MemoryRequest <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/models.py#L68" class="source-link" title="View source code">source</a>

Request for memory operations

## MemoryResponse <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/models.py#L75" class="source-link" title="View source code">source</a>

Response from memory operations

## HealthResponse <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/models.py#L83" class="source-link" title="View source code">source</a>

Health check response

## Functions

## utc_now <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/models.py#L13" class="source-link" title="View source code">source</a>

```python
def utc_now() -> datetime
```

Get current UTC datetime - replaces deprecated datetime.now()
