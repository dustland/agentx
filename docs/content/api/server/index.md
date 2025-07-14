# Server API

*AgentX Server components for REST API and real-time communication.*

The AgentX Server provides a comprehensive REST API for task management, real-time streaming, and system monitoring. Built with FastAPI, it offers automatic OpenAPI documentation and robust error handling.

## Components

### [OpenAPI Documentation](openapi.mdx)
Interactive API documentation powered by FastAPI:
- **Live Documentation** - Always up-to-date with code changes
- **Interactive Testing** - Try API calls directly from browser
- **Schema Export** - Download OpenAPI specification
- **Client Generation** - Auto-generate client libraries

### [REST API Reference](rest-api.md)
Complete REST API documentation with endpoints for:
- **Task Management** - Create, monitor, and manage AI agent tasks
- **Real-time Streaming** - Server-Sent Events for live updates
- **Resource Access** - Artifacts, logs, and task outputs
- **Memory Management** - Context sharing and persistence
- **System Monitoring** - Health checks and observability

### [API Models](models.md)
Pydantic models for request/response validation:
- **TaskRequest** - Task creation and configuration
- **TaskResponse** - Task status and results
- **MemoryRequest** - Memory operations
- **HealthResponse** - System health information

### [Streaming](streaming.md)
Server-Sent Events implementation for real-time communication:
- **Event Types** - Agent messages, status updates, tool calls
- **Connection Management** - Stream lifecycle and cleanup
- **Error Handling** - Connection failures and recovery

## Quick Start

### Start the Server

```bash
# Development mode
uv run start --port 8000

# Production mode
uv run start --port 8000 --reload false
```

### Access Documentation

- **Interactive Docs**: `http://localhost:8000/docs`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`
- **Health Check**: `http://localhost:8000/health`

### Basic Usage

```python
import requests

# Create a task
response = requests.post('http://localhost:8000/tasks', json={
    'config_path': 'examples/simple_chat/config/team.yaml',
    'task_description': 'Hello, world!',
    'context': {'source': 'api_docs'}
})

task = response.json()
print(f"Task created: {task['task_id']}")
```

## Architecture

The server follows a clean architecture with:

- **FastAPI Application** - Modern async web framework
- **Pydantic Models** - Request/response validation
- **Background Tasks** - Non-blocking task execution
- **Server-Sent Events** - Real-time communication
- **Multi-tenant Support** - User isolation and security

## Configuration

The server can be configured via environment variables:

```bash
# Server configuration
export AGENTX_HOST=0.0.0.0
export AGENTX_PORT=8000
export AGENTX_RELOAD=false

# Security
export AGENTX_CORS_ORIGINS=*
export AGENTX_LOG_LEVEL=info
```

## Development

### Running Tests

```bash
# Run server tests
uv run pytest tests/server/

# Test specific endpoint
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"config_path": "examples/simple_chat/config/team.yaml", "task_description": "test"}'
```

### Adding New Endpoints

1. Add endpoint to `src/agentx/server/api.py`
2. Create Pydantic models in `src/agentx/server/models.py`
3. Add tests in `tests/server/`
4. Update documentation

## Performance

- **Async Architecture** - Non-blocking I/O operations
- **Background Tasks** - Long-running operations don't block requests
- **Streaming** - Real-time updates without polling
- **Memory Efficient** - Minimal memory footprint per task

## Security

- **Input Validation** - Pydantic model validation
- **Path Traversal Protection** - Secure file access
- **User Isolation** - Multi-tenant support
- **CORS Configuration** - Cross-origin request handling