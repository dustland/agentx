import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useRef, useEffect } from "react";
import { useAPI } from "@/lib/api-client";
import { StreamEvent } from "@/types/vibex";

/**
 * Query keys for task-related data
 */
export const taskKeys = {
  all: ["tasks"] as const,
  list: () => [...taskKeys.all, "list"] as const,
  detail: (id: string) => [...taskKeys.all, id] as const,
  messages: (id: string) => [...taskKeys.detail(id), "messages"] as const,
  artifacts: (id: string) => [...taskKeys.detail(id), "artifacts"] as const,
  plan: (id: string) => [...taskKeys.detail(id), "plan"] as const,
  logs: (id: string, options?: any) =>
    [...taskKeys.detail(id), "logs", options] as const,
  memory: (id: string, query: string, limit: number) =>
    [...taskKeys.detail(id), "memory", { query, limit }] as const,
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

  // Auto-subscribe to task updates and invalidate queries
  useEffect(() => {
    if (!taskId || taskId === "dummy-task-id") return;

    const cleanup = apiClient.subscribeToTaskUpdates(
      taskId,
      (event: StreamEvent) => {
        switch (event.type) {
          case "message":
            // Invalidate messages when new messages arrive
            queryClient.invalidateQueries({
              queryKey: taskKeys.messages(taskId),
            });
            break;
          case "tool_call_result":
            // Invalidate artifacts when tools complete (they might create files)
            queryClient.invalidateQueries({
              queryKey: taskKeys.artifacts(taskId),
            });
            break;
          case "task_update":
            // Invalidate task status and potentially artifacts/plan
            queryClient.invalidateQueries({
              queryKey: taskKeys.detail(taskId),
            });
            if (event.data.status === "completed") {
              queryClient.invalidateQueries({
                queryKey: taskKeys.artifacts(taskId),
              });
              queryClient.invalidateQueries({
                queryKey: taskKeys.plan(taskId),
              });
            }
            break;
        }
      }
    );

    sseCleanupRef.current = cleanup;
    return cleanup;
  }, [taskId, apiClient, queryClient]);

  // Mutations
  const sendMessage = useMutation({
    mutationFn: ({
      message,
      mode,
    }: {
      message: string;
      mode?: "agent" | "chat";
    }) => apiClient.sendMessage(taskId, { content: message, mode }),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: taskKeys.messages(taskId) });
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(taskId) });
    },
  });

  const executeTask = useMutation({
    mutationFn: () => apiClient.executeTaskPlan(taskId),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(taskId) });
    },
  });

  const deleteTask = useMutation({
    mutationFn: () => apiClient.deleteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.list() });
    },
  });

  // Stop SSE connection
  const stop = useCallback(() => {
    if (sseCleanupRef.current) {
      sseCleanupRef.current();
      sseCleanupRef.current = null;
    }
  }, []);

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
    executeTask,
    deleteTask,

    // Cleanup
    stop,
  };
}

/**
 * Hook for task plan with direct data access
 */
export function useTaskPlan(taskId: string) {
  const apiClient = useAPI();

  const query = useQuery({
    queryKey: taskKeys.plan(taskId),
    queryFn: () => apiClient.getTaskPlan(taskId),
    enabled: !!taskId && taskId !== "dummy-task-id",
  });

  return {
    plan: query.data,
    hasPlan: !!query.data && !query.isLoading && !query.error,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  };
}

/**
 * Hook for task logs with direct data access
 */
export function useTaskLogs(
  taskId: string,
  options?: { limit?: number; offset?: number; tail?: boolean }
) {
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
 * Hook for fetching individual artifact content
 */
export function useTaskArtifact({
  taskId,
  path,
  enabled = true,
}: {
  taskId: string;
  path: string;
  enabled?: boolean;
}) {
  const apiClient = useAPI();

  const query = useQuery({
    queryKey: [...taskKeys.artifacts(taskId), path],
    queryFn: () => apiClient.getArtifactContent(taskId, path),
    enabled: enabled && !!taskId && !!path && taskId !== "dummy-task-id",
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  return {
    content: query.data?.content,
    isLoading: query.isLoading,
    error: query.error,
    isBinary: query.data?.is_binary || false,
    size: query.data?.size || 0,
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
