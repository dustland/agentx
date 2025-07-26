# Event API

*Module: [`vibex.server.api`](https://github.com/dustland/vibex/blob/main/src/vibex/server/api.py)*

VibeX Server API v2 - Clean Architecture

A thin API layer that only handles HTTP concerns.
All business logic is delegated to XAgent instances.

## get_user_id <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/api.py#L28" class="source-link" title="View source code">source</a>

```python
async def get_user_id() -> str
```

Temporary stub that returns a default user ID.

## create_app <a href="https://github.com/dustland/vibex/blob/main/src/vibex/server/api.py#L35" class="source-link" title="View source code">source</a>

```python
def create_app() -> FastAPI
```

Create the FastAPI application with clean architecture.
