# Event API

*Module: [`agentx.server.api`](https://github.com/dustland/agentx/blob/main/src/agentx/server/api.py)*

AgentX Server API

FastAPI-based REST API for task execution and memory management.
Provides endpoints for creating and managing tasks, and accessing task memory.

## create_task <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/api.py#L34" class="source-link" title="View source code">source</a>

```python
def create_task(config_path: str, user_id: str = None) -> XAgent
```

Create a new XAgent task instance.

## create_app <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/api.py#L45" class="source-link" title="View source code">source</a>

```python
def create_app(title: str = 'AgentX API', description: str = 'REST API for AgentX task execution and memory management', version: str = '0.4.0', enable_cors: bool = True) -> FastAPI
```

Create and configure the FastAPI application.

**Args:**
    title: API title
    description: API description
    version: API version
    enable_cors: Whether to enable CORS middleware

**Returns:**
    Configured FastAPI application

## add_routes <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/api.py#L85" class="source-link" title="View source code">source</a>

```python
def add_routes(app: FastAPI)
```

Add API routes to the FastAPI application

## run_server <a href="https://github.com/dustland/agentx/blob/main/src/agentx/server/api.py#L576" class="source-link" title="View source code">source</a>

```python
def run_server(host: str = '0.0.0.0', port: int = 8000, reload: bool = False, log_level: str = 'info')
```

Run the AgentX server with integrated observability.

**Args:**
    host: Host to bind to
    port: Port to bind to
    reload: Enable auto-reload for development
    log_level: Logging level
