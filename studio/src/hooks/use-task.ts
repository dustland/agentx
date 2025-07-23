import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { nanoid } from "nanoid";
import { useAgentXAPI } from "@/lib/api-client";
import { useTaskStore } from "@/store/task";
import { ChatMessage } from "@/types/chat";
import {
  TaskStatus,
  StreamEvent,
  AgentMessageEvent,
  ToolCallStartEvent,
  ToolCallResultEvent,
  TaskUpdateEvent,
  StreamChunkEvent,
  getMessageText,
  ArtifactContent,
} from "@/types/agentx";

/**
 * Core hook for managing a single task
 * Handles task state, persistence, API calls, and SSE
 */
export function useTask(taskId: string) {
  const apiClient = useAgentXAPI();
  const router = useRouter();

  // Get store methods
  const store = useTaskStore();
  const {
    getTask,
    setTaskInfo,
    setTaskMessages,
    addTaskMessage,
    setTaskStatus: setTaskStatusInStore,
    updateTaskInList,
    consumeInitialMessage,
  } = store;

  // Get task data from store
  const cachedTask = getTask(taskId);
  const messages = cachedTask?.messages || [];

  // Local state
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);
  const [taskNotFound, setTaskNotFound] = useState(false);
  const [taskStatus, setTaskStatus] = useState<TaskStatus>(
    cachedTask?.status || "pending"
  );

  // SSE event handlers
  const eventHandlersRef = useRef<{
    onMessage?: (message: ChatMessage) => void;
    onStreamChunk?: (data: StreamChunkEvent) => void;
    onToolCallStart?: (data: ToolCallStartEvent) => void;
    onToolCallResult?: (data: ToolCallResultEvent) => void;
    onStatusChange?: (status: TaskStatus) => void;
  }>({});

  // SSE cleanup ref
  const sseCleanupRef = useRef<(() => void) | null>(null);

  // Update task status in both local state and store
  const updateTaskStatus = useCallback(
    (status: TaskStatus) => {
      setTaskStatus(status);
      setTaskStatusInStore(taskId, status);
      updateTaskInList(taskId, { status });
      eventHandlersRef.current.onStatusChange?.(status);
    },
    [taskId, setTaskStatusInStore, updateTaskInList]
  );

  // Update task info
  const updateTaskInfo = useCallback(
    (info: any) => {
      setTaskInfo(taskId, info);
      updateTaskInList(taskId, info);
    },
    [taskId, setTaskInfo, updateTaskInList]
  );

  // Add a message
  const addMessage = useCallback(
    (message: ChatMessage) => {
      addTaskMessage(taskId, message);
    },
    [taskId, addTaskMessage]
  );

  // Set all messages
  const setMessages = useCallback(
    (messages: ChatMessage[]) => {
      setTaskMessages(taskId, messages);
    },
    [taskId, setTaskMessages]
  );

  // Send a message to the backend
  const sendMessage = useCallback(
    async (message: string) => {
      if (!message.trim()) return;

      // Skip if no valid taskId
      if (!taskId || taskId === "dummy-task-id") {
        console.warn("Cannot send message without valid taskId");
        return;
      }

      try {
        // Add user message immediately for optimistic UI
        const userMessage: ChatMessage = {
          id: nanoid(),
          role: "user",
          content: message,
          timestamp: new Date(),
          status: "complete",
        };
        addMessage(userMessage);

        // Send message to backend
        await apiClient.sendMessage(taskId, message);
        updateTaskStatus("running");

        // Set a timeout to reset status if no update received
        setTimeout(() => {
          setTaskStatus((current) => {
            if (current === "running") {
              console.warn(
                "No task status update received, resetting to pending"
              );
              updateTaskStatus("pending");
              return "pending";
            }
            return current;
          });
        }, 30000); // 30 second timeout
      } catch (error) {
        console.error("Failed to send message:", error);
        updateTaskStatus("pending");
        throw error;
      }
    },
    [taskId, apiClient, updateTaskStatus, addMessage]
  );

  // Handle SSE events
  const handleStreamEvent = useCallback(
    (event: StreamEvent) => {
      console.log("[useTask] Received SSE event:", event.type, event);

      switch (event.type) {
        case "message": {
          // New event type for complete Message objects
          const data = event.data;
          console.log("Processing message:", data);

          const message: ChatMessage = {
            id: data.id,
            role: data.role as "user" | "assistant" | "system",
            content: data.content,
            timestamp: new Date(data.timestamp),
            status: "complete",
            metadata: data.metadata || {},
          };

          // Add to store - the backend is the source of truth
          addMessage(message);

          // Notify listeners
          eventHandlersRef.current.onMessage?.(message);
          break;
        }

        case "agent_message": {
          // Legacy event type - deprecated, use "message" events instead
          console.warn(
            "Received deprecated agent_message event, use 'message' events instead"
          );
          const data = event.data as AgentMessageEvent;
          console.log("Processing legacy agent_message:", data);

          // Convert to standard message format
          const messageId = data.message_id || nanoid();
          const timestamp = data.timestamp || new Date().toISOString();

          const message: ChatMessage = {
            id: messageId,
            role: data.agent_id === "user" ? "user" : "assistant",
            content: data.message,
            timestamp: new Date(timestamp),
            status: "complete",
            metadata: {
              agentId: data.agent_id,
              ...data.metadata,
            },
          };

          // Add to store - the backend is the source of truth
          addMessage(message);

          // Notify listeners
          eventHandlersRef.current.onMessage?.(message);
          break;
        }

        case "tool_call_start": {
          const data = event.data as ToolCallStartEvent;
          console.log("Tool call started:", data);
          eventHandlersRef.current.onToolCallStart?.(data);
          break;
        }

        case "tool_call_result": {
          const data = event.data as ToolCallResultEvent;
          console.log("Tool call result:", data);
          eventHandlersRef.current.onToolCallResult?.(data);
          break;
        }

        case "agent_status": {
          const data = event.data;
          updateTaskStatus(data.status === "working" ? "running" : "pending");
          break;
        }

        case "task_update": {
          const data = event.data as TaskUpdateEvent;
          if (data.status) {
            updateTaskStatus(data.status);
          }
          break;
        }

        case "stream_chunk": {
          const data = event.data as StreamChunkEvent;
          console.log("[useTask] Processing stream chunk:", {
            message_id: data.message_id,
            chunk_length: data.chunk?.length || 0,
            is_final: data.is_final,
            has_error: !!data.error,
            timestamp: data.timestamp,
          });
          console.log(
            "[useTask] Event handlers available:",
            Object.keys(eventHandlersRef.current)
          );

          // Notify listeners
          if (eventHandlersRef.current.onStreamChunk) {
            console.log(
              "[useTask] Calling onStreamChunk handler with data:",
              data
            );
            eventHandlersRef.current.onStreamChunk(data);
          } else {
            console.warn(
              "[useTask] No onStreamChunk handler registered! This will cause streaming to not work properly."
            );
          }
          break;
        }

        case "artifact_created":
        case "artifact_updated": {
          // Handled in taskspace panel
          break;
        }

        default:
          console.log("Unhandled event type:", event);
      }
    },
    [addMessage, updateTaskStatus]
  );

  // Load task data
  const loadTask = useCallback(async () => {
    // Skip if no valid taskId
    if (!taskId || taskId === "dummy-task-id") {
      setIsLoading(false);
      return;
    }

    try {
      console.log(`Loading task with ID: ${taskId}`);
      const task = await apiClient.getTask(taskId);
      console.log("Task loaded successfully:", task);

      // Update store
      updateTaskInfo(task);
      updateTaskStatus(task.status || "pending");

      // Load messages if not cached
      if (!cachedTask?.messages || cachedTask.messages.length === 0) {
        try {
          const messagesResponse = await apiClient.getMessages(taskId);
          if (
            messagesResponse.messages &&
            messagesResponse.messages.length > 0
          ) {
            const formattedMessages = messagesResponse.messages.map(
              (msg: any) => ({
                id: msg.message_id || nanoid(),
                role: msg.role as "user" | "assistant" | "system",
                content: getMessageText(msg),
                timestamp: new Date(msg.timestamp),
                status: "complete" as const,
                metadata: msg.metadata,
              })
            );
            setMessages(formattedMessages);
          }
        } catch (error) {
          console.log(
            "No existing messages or messages endpoint not available"
          );
        }
      }

      setIsLoading(false);
      setIsInitialized(true);

      // Set up SSE streaming
      try {
        const cleanup = apiClient.subscribeToTaskUpdates(
          taskId,
          handleStreamEvent
        );
        sseCleanupRef.current = cleanup;
      } catch (error) {
        console.error("Failed to set up SSE connection:", error);
      }
    } catch (error) {
      console.error("Failed to load task:", error);
      if ((error as any)?.message?.includes("404")) {
        setTaskNotFound(true);
      }
      setIsLoading(false);
    }
  }, [
    taskId,
    apiClient,
    cachedTask,
    updateTaskInfo,
    updateTaskStatus,
    setMessages,
    handleStreamEvent,
  ]);

  // Stop task execution
  const stopTask = useCallback(() => {
    // Close SSE connection
    if (sseCleanupRef.current) {
      sseCleanupRef.current();
      sseCleanupRef.current = null;
    }
    updateTaskStatus("pending");
    console.log("Stopping task execution");
  }, [updateTaskStatus]);

  // Subscribe to events
  const subscribe = useCallback(
    (handlers: typeof eventHandlersRef.current) => {
      // Don't subscribe if no valid taskId
      if (!taskId || taskId === "dummy-task-id") {
        return () => {}; // Return no-op unsubscribe
      }

      eventHandlersRef.current = { ...eventHandlersRef.current, ...handlers };

      // Return unsubscribe function
      return () => {
        eventHandlersRef.current = {};
      };
    },
    [taskId]
  );

  // Initial load
  useEffect(() => {
    if (!isInitialized) {
      loadTask();
    }

    return () => {
      // Cleanup SSE on unmount
      if (sseCleanupRef.current) {
        sseCleanupRef.current();
      }
    };
  }, [isInitialized, loadTask]);

  // Redirect if task not found
  useEffect(() => {
    if (taskNotFound) {
      router.push("/");
    }
  }, [taskNotFound, router]);

  // Get artifacts
  const getArtifacts = useCallback(async () => {
    try {
      const response = await apiClient.getTaskArtifacts(taskId);
      return response.artifacts || [];
    } catch (error) {
      console.error("Failed to get artifacts:", error);
      return [];
    }
  }, [taskId, apiClient]);

  // Get artifact content
  const getArtifactContent = useCallback(
    async (path: string): Promise<ArtifactContent> => {
      try {
        return await apiClient.getArtifactContent(taskId, path);
      } catch (error) {
        console.error("Failed to get artifact content:", error);
        return { path, content: null, size: 0 };
      }
    },
    [taskId, apiClient]
  );

  // Get logs
  const getLogs = useCallback(
    async (options?: any) => {
      try {
        const response = await apiClient.getTaskLogs(taskId, options);
        return response;
      } catch (error) {
        console.error("Failed to get logs:", error);
        return { logs: [], file_size: 0, has_more: false };
      }
    },
    [taskId, apiClient]
  );

  // Search memory
  const searchMemory = useCallback(
    async (query: string, limit = 10) => {
      try {
        const results = await apiClient.searchMemory(taskId, { query, limit });
        return results;
      } catch (error) {
        console.error("Failed to search memory:", error);
        return [];
      }
    },
    [taskId, apiClient]
  );

  return {
    // Data
    messages,
    taskStatus,
    taskInfo: cachedTask,
    isLoading,
    taskNotFound,
    initialMessage: consumeInitialMessage(),

    // Actions
    sendMessage,
    addMessage,
    stopTask,
    reload: loadTask,
    subscribe,

    // Task data access
    getArtifacts,
    getArtifactContent,
    getLogs,
    searchMemory,
  };
}
