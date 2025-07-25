import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useRef, useEffect } from "react";
import { useAPI } from "@/lib/api-client";
import { StreamEvent } from "@/types/vibex";

/**
 * Query keys for task-related data
 */
export const projectKeys = {
  all: ["tasks"] as const,
  list: () => [...projectKeys.all, "list"] as const,
  detail: (id: string) => [...projectKeys.all, id] as const,
  messages: (id: string) => [...projectKeys.detail(id), "messages"] as const,
  artifacts: (id: string) => [...projectKeys.detail(id), "artifacts"] as const,
  plan: (id: string) => [...projectKeys.detail(id), "plan"] as const,
  logs: (id: string, options?: any) =>
    [...projectKeys.detail(id), "logs", options] as const,
  memory: (id: string, query: string, limit: number) =>
    [...projectKeys.detail(id), "memory", { query, limit }] as const,
};

/**
 * Comprehensive task hook using React Query
 * Returns data directly for easy consumption
 */
export function useProject(projectId: string) {
  const apiClient = useAPI();
  const queryClient = useQueryClient();
  const sseCleanupRef = useRef<(() => void) | null>(null);

  // Queries
  const taskQuery = useQuery({
    queryKey: projectKeys.detail(projectId),
    queryFn: () => apiClient.getProject(projectId),
    enabled: !!projectId && projectId !== "dummy-task-id",
  });

  const messagesQuery = useQuery({
    queryKey: projectKeys.messages(projectId),
    queryFn: () => apiClient.getMessages(projectId),
    enabled: !!projectId && projectId !== "dummy-task-id",
    staleTime: 0, // Always fetch fresh data
    refetchOnMount: true,
  });

  const artifactsQuery = useQuery({
    queryKey: projectKeys.artifacts(projectId),
    queryFn: () => apiClient.getProjectArtifacts(projectId),
    enabled: !!projectId && projectId !== "dummy-task-id",
  });

  // Auto-subscribe to task updates and invalidate queries
  useEffect(() => {
    if (!projectId || projectId === "dummy-task-id") return;

    const cleanup = apiClient.subscribeToProjectUpdates(
      projectId,
      (event: StreamEvent) => {
        switch (event.type) {
          case "message":
            // Invalidate messages when new messages arrive
            queryClient.invalidateQueries({
              queryKey: projectKeys.messages(projectId),
            });
            break;
          case "tool_call_result":
            // Invalidate artifacts when tools complete (they might create files)
            queryClient.invalidateQueries({
              queryKey: projectKeys.artifacts(projectId),
            });
            break;
          case "task_update":
            // Invalidate task status and potentially artifacts/plan
            queryClient.invalidateQueries({
              queryKey: projectKeys.detail(projectId),
            });
            if (event.data.status === "completed") {
              queryClient.invalidateQueries({
                queryKey: projectKeys.artifacts(projectId),
              });
              queryClient.invalidateQueries({
                queryKey: projectKeys.plan(projectId),
              });
            }
            break;
        }
      }
    );

    sseCleanupRef.current = cleanup;
    return cleanup;
  }, [projectId, apiClient, queryClient]);

  // Mutations
  const sendMessage = useMutation({
    mutationFn: ({
      message,
      mode,
    }: {
      message: string;
      mode?: "agent" | "chat";
    }) => apiClient.sendMessage(projectId, { content: message, mode }),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({
        queryKey: projectKeys.messages(projectId),
      });
      queryClient.invalidateQueries({
        queryKey: projectKeys.detail(projectId),
      });
    },
  });

  const executeProject = useMutation({
    mutationFn: () => apiClient.executeProjectPlan(projectId),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({
        queryKey: projectKeys.detail(projectId),
      });
    },
  });

  const deleteProject = useMutation({
    mutationFn: () => apiClient.deleteProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.list() });
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
    executeProject,
    deleteProject,

    // Cleanup
    stop,
  };
}

/**
 * Hook for task plan with real-time updates
 */
export function useProjectPlan(projectId: string) {
  const apiClient = useAPI();
  const queryClient = useQueryClient();
  const sseCleanupRef = useRef<(() => void) | null>(null);

  const query = useQuery({
    queryKey: projectKeys.plan(projectId),
    queryFn: () => apiClient.getProjectPlan(projectId),
    enabled: !!projectId && projectId !== "dummy-task-id",
  });

  // Subscribe to real-time plan updates
  useEffect(() => {
    if (!projectId || projectId === "dummy-task-id") return;

    const cleanup = apiClient.subscribeToProjectUpdates(
      projectId,
      (event: StreamEvent) => {
        if (event.type === "task_update") {
          // For plan-specific updates, invalidate the plan query to refetch
          queryClient.invalidateQueries({
            queryKey: projectKeys.plan(projectId),
          });
        }
      }
    );

    sseCleanupRef.current = cleanup;
    return cleanup;
  }, [projectId, apiClient, queryClient]);

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
export function useProjectLogs(
  projectId: string,
  options?: { limit?: number; offset?: number; tail?: boolean }
) {
  const apiClient = useAPI();

  const query = useQuery({
    queryKey: projectKeys.logs(projectId, options),
    queryFn: () => apiClient.getProjectLogs(projectId, options),
    enabled: !!projectId && projectId !== "dummy-task-id",
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
export function useProjectArtifact({
  projectId,
  path,
  enabled = true,
}: {
  projectId: string;
  path: string;
  enabled?: boolean;
}) {
  const apiClient = useAPI();

  const query = useQuery({
    queryKey: [...projectKeys.artifacts(projectId), path],
    queryFn: () => apiClient.getArtifactContent(projectId, path),
    enabled: enabled && !!projectId && !!path && projectId !== "dummy-task-id",
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
 * Hook for XAgent list
 */
export function useProjects() {
  const apiClient = useAPI();
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: projectKeys.list(),
    queryFn: () => apiClient.listXAgents(),
    refetchInterval: 10000, // Poll every 10 seconds
  });

  const deleteProject = useMutation({
    mutationFn: (agentId: string) => apiClient.deleteXAgent(agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.list() });
    },
  });

  return {
    tasks: query.data?.runs || [],
    isLoading: query.isLoading,
    error: query.error,
    deleteProject,
  };
}
