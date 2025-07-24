# REST API

VibeX provides a comprehensive REST API for managing agents, tasks, and real-time communication. The API server can be started with:

```bash
uv run start --port 7770
```

## API Documentation

The VibeX server provides interactive API documentation through two interfaces:

- **[REST API Explorer](/api-explorer)** - Interactive documentation with ReDoc/Swagger UI
- **OpenAPI Specification** - Available at `http://localhost:7770/openapi.json`

## Base URL

```
http://localhost:7770
```

## Authentication

If user authentication is enabled, include the `user_id` parameter in your requests:

```bash
curl "http://localhost:7770/tasks?user_id=your_user_id"
```

## Key Endpoints

### Task Management

- `POST /tasks` - Create a new task
- `GET /tasks` - List all tasks
- `GET /tasks/{task_id}` - Get task details
- `DELETE /tasks/{task_id}` - Delete a task

### Chat & Conversation

- `GET /tasks/{task_id}/chat` - Get chat history
- `POST /tasks/{task_id}/chat` - Send a message
- `DELETE /tasks/{task_id}/chat` - Clear chat history

### Artifacts & Logs

- `GET /tasks/{task_id}/artifacts` - List task artifacts
- `GET /tasks/{task_id}/artifacts/{path}` - Get artifact content
- `GET /tasks/{task_id}/logs` - Get execution logs

### Real-time Streaming

- `GET /tasks/{task_id}/stream` - Server-sent events for real-time updates

### Memory Management

- `POST /tasks/{task_id}/memory` - Add to task memory
- `GET /tasks/{task_id}/memory` - Search task memory
- `DELETE /tasks/{task_id}/memory` - Clear task memory

## Example Usage

### Creating a Task

```bash
curl -X POST "http://localhost:7770/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "config_path": "examples/simple_writer/config/team.yaml",
    "task_description": "Write a blog post about AI",
    "user_id": "optional_user_id"
  }'
```

### Streaming Task Events

```javascript
const eventSource = new EventSource(
  "http://localhost:7770/tasks/TASK_ID/stream"
);

eventSource.addEventListener("agent_message", (event) => {
  const data = JSON.parse(event.data);
  console.log("Agent message:", data);
});

eventSource.addEventListener("task_update", (event) => {
  const data = JSON.parse(event.data);
  console.log("Task status:", data.status);
});
```

## Response Formats

All responses are in JSON format. Successful responses include the requested data, while errors follow this format:

```json
{
  "detail": "Error message description"
}
```

## Rate Limiting

The API does not currently enforce rate limits, but this may change in future versions. Design your applications to handle potential rate limiting responses.

## CORS

The API server enables CORS by default, allowing requests from any origin. In production, you should configure this appropriately for your security requirements.

## Common Issues

### Server Not Running

If you receive connection errors, ensure the VibeX server is running:

```bash
uv run start --port 7770
```

### Port Conflicts

If port 7770 is already in use, you can specify a different port:

```bash
uv run start --port 7771
```

### Missing Dependencies

Ensure all dependencies are installed:

```bash
uv sync
```

## SDK Integration

For Python applications, use the [VibeX SDK](/sdk) instead of calling the REST API directly. The SDK provides a more convenient and type-safe interface.

## Further Reading

- [SDK Reference](/api) - For programmatic access from Python
- [Server Architecture](/docs/design/system-architecture) - Understanding the server design
- [Getting Started](/docs/getting-started) - Quick start guide
