# AgentX Studio Integration

This document explains how the AgentX Studio frontend integrates with the AgentX backend.

## Architecture

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   Studio UI     │ ──────────────▶ │   AgentX API    │
│  (Next.js 15)   │                │   (FastAPI)     │
│   Port 3333     │ ◀────────────── │   Port 8000     │
└─────────────────┘                └─────────────────┘
```

## Setup

### 1. Start Both Services

**Option A: Start both together**
```bash
cd studio
pnpm run dev:full
```

**Option B: Start separately**
```bash
# Terminal 1: Start AgentX backend
cd studio
pnpm run backend

# Terminal 2: Start Studio frontend  
cd studio
pnpm run dev
```

### 2. Environment Configuration

Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```

Adjust the API URL if needed:
```env
NEXT_PUBLIC_AGENTX_API_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_TEAM_CONFIG=examples/auto_writer/config/team.yaml
```

## Features

### Task Creation and Execution

1. **Homepage**: Enter task description or click sample tasks
2. **Navigation**: Automatically routes to `/x/{task_id}`
3. **Real-time Updates**: Polls backend every 2 seconds for status updates
4. **Task Monitoring**: Shows execution status, results, and raw API data

### API Integration

The studio uses a comprehensive API client (`src/lib/api-client.ts`) that provides:

- **Task Management**: Create, get, list, delete tasks
- **Memory Management**: Add, search, clear task memory
- **Real-time Updates**: Polling and SSE support
- **Error Handling**: Comprehensive error reporting

### Supported Operations

```typescript
// Create a task
const task = await apiClient.createTask({
  config_path: 'examples/auto_writer/config/team.yaml',
  task_description: 'Create a market research report',
  context: {}
});

// Monitor task progress
const stopPolling = apiClient.pollTaskStatus(taskId, (updatedTask) => {
  console.log('Task status:', updatedTask.status);
});

// Add context to task memory
await apiClient.addMemory(taskId, {
  content: 'Additional context or instructions',
  metadata: { type: 'user_input' }
});
```

## Components

### Core Components

- **HomePage**: Task input and sample selection
- **TaskExecutor**: Main task execution interface
- **AgentXTask Hook**: React hook for task management
- **API Client**: Backend communication layer

### Task Flow

1. User enters task description on homepage
2. `generateId()` creates unique task identifier
3. Router navigates to `/x/{taskId}?description={encoded_description}`
4. TaskExecutor loads and displays initial description
5. User clicks "Execute Task" to start AgentX backend
6. Real-time polling shows task progress and results

## Backend Requirements

The AgentX backend must be running with:

1. **FastAPI server** on port 8000
2. **Team configurations** in `examples/auto_writer/config/`
3. **Python environment** with AgentX dependencies

### Expected API Endpoints

- `POST /tasks` - Create and start task
- `GET /tasks/{task_id}` - Get task status and results  
- `GET /tasks` - List all tasks
- `DELETE /tasks/{task_id}` - Delete task
- `POST /tasks/{task_id}/memory` - Add memory content
- `GET /tasks/{task_id}/memory` - Search memory
- `GET /health` - Health check

## Development

### Adding New Team Configurations

1. Create YAML config in AgentX backend
2. Update `getConfigPath()` in `use-agentx-task.ts`
3. Add new option to `TEAM_CONFIGS` in `task-executor.tsx`

### Customizing API Client

The API client supports:
- Custom base URLs
- Authentication headers
- Request/response interceptors
- Error handling strategies

### Real-time Updates

Currently uses polling every 2 seconds. Can be enhanced with:
- Server-Sent Events (SSE)
- WebSocket connections
- Push notifications

## Troubleshooting

### Common Issues

1. **Connection refused**: Backend not running on port 8000
2. **CORS errors**: Backend CORS configuration issues  
3. **Task creation fails**: Invalid team config path
4. **Polling stops**: Network disconnection or backend crash

### Debug Mode

Enable debug logging in browser console:
```javascript
localStorage.setItem('agentx:debug', 'true');
```

### Health Check

Visit `http://localhost:8000/health` to verify backend is running.

## Deployment

### Production Setup

1. Update `.env.local` with production API URL
2. Build studio: `pnpm run build`
3. Deploy backend with AgentX API server
4. Deploy frontend to Vercel/Railway/etc.

### Environment Variables

```env
# Production
NEXT_PUBLIC_AGENTX_API_URL=https://your-agentx-api.com
NODE_ENV=production

# Optional authentication
AGENTX_API_KEY=your-production-api-key
```