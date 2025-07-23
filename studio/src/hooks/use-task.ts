import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useRef } from "react";
import { useAPI } from "@/lib/api-client";
import { StreamEvent } from "@/types/agentx";

/**
 * Query keys for task-related data
 */
export const taskKeys = {
  all: ["tasks"] as const,
  list: () => [...taskKeys.all, "list"] as const,
  detail: (id: string) => [...taskKeys.all, id] as const,
  messages: (id: string) => [...taskKeys.detail(id), "messages"] as const,
  artifacts: (id: string) => [...taskKeys.detail(id), "artifacts"] as const,
  logs: (id: string, options?: any) => [...taskKeys.detail(id), "logs", options] as const,
  memory: (id: string, query: string, limit: number) => [...taskKeys.detail(id), "memory", { query, limit }] as const,
};

/**
 * Comprehensive task hook using React Query
 * Returns data directly for easy consumption
 */
export function useTask(taskId: string) {
  const apiClient = useAPI();
  const queryClient = useQueryClient();
  const sseCleanupRef = useRef<(() => void) | null>(null);

  // Queries
  const taskQuery = useQuery({
    queryKey: taskKeys.detail(taskId),
    queryFn: () => apiClient.getTask(taskId),
    enabled: !!taskId && taskId !== "dummy-task-id",
  });

  const messagesQuery = useQuery({
    queryKey: taskKeys.messages(taskId),
    queryFn: () => apiClient.getMessages(taskId),
    enabled: !!taskId && taskId !== "dummy-task-id",
    staleTime: 0, // Always fetch fresh data
    refetchOnMount: true,
  });

  const artifactsQuery = useQuery({
    queryKey: taskKeys.artifacts(taskId),
    queryFn: () => apiClient.getTaskArtifacts(taskId),
    enabled: !!taskId && taskId !== "dummy-task-id",
  });

  // Mutations
  const sendMessage = useMutation({
    mutationFn: ({ message, mode }: { message: string; mode?: "agent" | "chat" }) => 
      apiClient.sendMessage(taskId, { content: message, mode }),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: taskKeys.messages(taskId) });
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(taskId) });
    },
  });

  const deleteTask = useMutation({
    mutationFn: () => apiClient.deleteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.list() });
    },
  });

  // SSE subscription
  const subscribe = useCallback(
    (handlers: {
      onMessage?: (message: any) => void;
      onStreamChunk?: (data: any) => void;
      onToolCallStart?: (data: any) => void;
      onToolCallResult?: (data: any) => void;
      onStatusChange?: (status: string) => void;
    }) => {
      if (!taskId || taskId === "dummy-task-id") {
        return () => {}; // Return no-op unsubscribe
      }

      const cleanup = apiClient.subscribeToTaskUpdates(
        taskId,
        (event: StreamEvent) => {
          switch (event.type) {
            case "message":
              handlers.onMessage?.(event.data);
              break;
            case "stream_chunk":
              handlers.onStreamChunk?.(event.data);
              break;
            case "tool_call_start":
              handlers.onToolCallStart?.(event.data);
              break;
            case "tool_call_result":
              handlers.onToolCallResult?.(event.data);
              break;
            case "task_update":
              if (event.data.status) {
                handlers.onStatusChange?.(event.data.status);
              }
              break;
          }
        }
      );

      sseCleanupRef.current = cleanup;
      return cleanup;
    },
    [taskId, apiClient]
  );

  // Stop SSE connection
  const stop = useCallback(() => {
    if (sseCleanupRef.current) {
      sseCleanupRef.current();
      sseCleanupRef.current = null;
    }
  }, []);

  // Helper functions for on-demand queries (only when really needed)
  const getArtifactContent = async (path: string) => {
    return queryClient.fetchQuery({
      queryKey: [...taskKeys.artifacts(taskId), path],
      queryFn: () => apiClient.getArtifactContent(taskId, path),
    });
  };

  const searchMemory = async (query: string, limit = 10) => {
    return queryClient.fetchQuery({
      queryKey: taskKeys.memory(taskId, query, limit),
      queryFn: () => apiClient.searchMemory(taskId, { query, limit }),
    });
  };

  return {
    // Direct data access
    task: taskQuery.data,
    messages: messagesQuery.data?.messages || [],
    artifacts: artifactsQuery.data?.artifacts || [],
    
    // Loading states
    isLoading: taskQuery.isLoading || messagesQuery.isLoading,
    isTaskLoading: taskQuery.isLoading,
    isMessagesLoading: messagesQuery.isLoading,
    isArtifactsLoading: artifactsQuery.isLoading,
    
    // Errors
    error: taskQuery.error || messagesQuery.error || artifactsQuery.error,
    
    // Mutations
    sendMessage,
    deleteTask,
    
    // SSE
    subscribe,
    stop,
    
    // On-demand functions (rarely used)
    getArtifactContent,
    searchMemory,
    
    // Legacy compatibility
    getArtifacts: async () => artifactsQuery.data?.artifacts || [],
    getLogs: async (options?: any) => {
      return queryClient.fetchQuery({
        queryKey: taskKeys.logs(taskId, options),
        queryFn: () => apiClient.getTaskLogs(taskId, options),
      });
    },
    stopTask: stop,
  };
}

/**
 * Hook for task logs with direct data access
 */
export function useTaskLogs(taskId: string, options?: { limit?: number; offset?: number; tail?: boolean }) {
  const apiClient = useAPI();
  
  const query = useQuery({
    queryKey: taskKeys.logs(taskId, options),
    queryFn: () => apiClient.getTaskLogs(taskId, options),
    enabled: !!taskId && taskId !== "dummy-task-id",
  });
  
  return {
    logs: query.data?.logs || [],
    fileSize: query.data?.file_size || 0,
    hasMore: query.data?.has_more || false,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  };
}

/**
 * Hook for tasks list
 */
export function useTasks() {
  const apiClient = useAPI();
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: taskKeys.list(),
    queryFn: () => apiClient.getTasks(),
    refetchInterval: 10000, // Poll every 10 seconds
  });

  const deleteTask = useMutation({
    mutationFn: (taskId: string) => apiClient.deleteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.list() });
    },
  });

  return {
    tasks: query.data?.tasks || [],
    isLoading: query.isLoading,
    error: query.error,
    deleteTask,
  };
}