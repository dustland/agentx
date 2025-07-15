# Task Store

This directory contains Zustand stores for managing task-related state in the AgentX Studio.

## Task Store (`task-store.ts`)

The task store manages the initial message flow for new tasks. This solves the problem of using URL parameters for initial messages, which would persist across page refreshes and cause messages to be sent repeatedly.

### Problem Solved

Previously, when creating a task from the homepage, the initial message was passed as a URL parameter:

```
/x/task-id?message=Hello%20world
```

This approach had issues:

- The parameter persisted across page refreshes
- Refreshing the page would send the initial message again
- URL became cluttered with encoded messages

### Solution

The new flow uses Zustand with localStorage persistence:

1. **Homepage**: User enters prompt → Store in Zustand → Create task → Navigate to task page
2. **Task Page**: Check Zustand store → Consume initial message → Send as first chat message → Clear from store

### Usage

```typescript
import { useTaskStore } from "@/lib/stores/task-store";

// In homepage component
const { setInitialMessage } = useTaskStore();

// Store message before navigation
setInitialMessage("Hello world");
router.push(`/x/${taskId}`);

// In task page component
const { consumeInitialMessage } = useTaskStore();

// Consume message (returns and clears it)
const initialMessage = consumeInitialMessage();
if (initialMessage) {
  sendMessage(initialMessage);
}
```

### Benefits

- **No URL pollution**: Clean URLs without encoded parameters
- **No duplicate messages**: Message is consumed once and cleared
- **Persistent across navigation**: Uses localStorage for reliability
- **Type-safe**: Full TypeScript support
- **Lightweight**: Minimal state management footprint

### State Structure

```typescript
interface TaskState {
  initialMessage: string | null;
  setInitialMessage: (message: string) => void;
  clearInitialMessage: () => void;
  consumeInitialMessage: () => string | null;
}
```

The store is persisted to localStorage under the key `task-store` but only persists the `initialMessage` field.
