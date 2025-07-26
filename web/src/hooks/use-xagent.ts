import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApi } from "@/lib/api-client";
import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { ChatMessage } from "@/types/chat";
import { nanoid } from "nanoid";

/**
 * Query keys for XAgent-related data
 */
export const xagentKeys = {
  all: ["xagents"] as const,
  list: () => [...xagentKeys.all, "list"] as const,
  detail: (id: string) => [...xagentKeys.all, id] as const,
  messages: (id: string) => [...xagentKeys.detail(id), "messages"] as const,
  artifacts: (id: string) => [...xagentKeys.detail(id), "artifacts"] as const,
  logs: (id: string, options?: any) =>
    [...xagentKeys.detail(id), "logs", options] as const,
  memory: (id: string, query: string, limit: number) =>
    [...xagentKeys.detail(id), "memory", { query, limit }] as const,
};

/**
 * Comprehensive XAgent hook using React Query
 * Returns data directly for easy consumption
 */
export function useXAgent(xagentId: string) {
  const vibex = useApi();
  const queryClient = useQueryClient();
  const sseCleanupRef = useRef<(() => void) | null>(null);

  // Chat state
  const [input, setInput] = useState("");
  const [optimisticMessages, setOptimisticMessages] = useState<ChatMessage[]>(
    []
  );

  // Queries
  const xagentQuery = useQuery({
    queryKey: xagentKeys.detail(xagentId),
    queryFn: () => vibex.getXAgent(xagentId),
    enabled: !!xagentId && xagentId !== "dummy-task-id",
  });

  const messagesQuery = useQuery({
    queryKey: xagentKeys.messages(xagentId),
    queryFn: () => vibex.getMessages(xagentId),
    enabled: !!xagentId && xagentId !== "dummy-task-id",
    staleTime: 0, // Always fetch fresh data
    refetchOnMount: true,
  });

  // Transform raw messages to ChatMessage format
  const messages: ChatMessage[] = useMemo(
    () =>
      (Array.isArray(messagesQuery.data)
        ? messagesQuery.data
        : messagesQuery.data?.messages || []
      ).map((msg: any) => ({
        id: msg.id || msg.message_id || nanoid(),
        role: msg.role as "user" | "assistant" | "system",
        content:
          typeof msg.content === "string"
            ? msg.content
            : JSON.stringify(msg.content),
        timestamp: new Date(msg.timestamp),
        status: "complete" as const,
        metadata: msg.metadata,
      })),
    [messagesQuery.data]
  );

  // Remove optimistic messages that now exist in real messages
  useEffect(() => {
    if (optimisticMessages.length > 0 && messages.length > 0) {
      const realMessageContents = new Set(messages.map((m) => m.content));
      setOptimisticMessages((prev) =>
        prev.filter((msg) => !realMessageContents.has(msg.content))
      );
    }
  }, [messages, optimisticMessages.length]);

  // Combine all messages in the correct order
  const allMessages = useMemo(() => {
    const messageMap = new Map<string, ChatMessage>();

    // Add real messages first
    messages.forEach((msg) => {
      messageMap.set(msg.content, msg);
    });

    // Add optimistic messages if they don't already exist
    optimisticMessages.forEach((msg) => {
      if (!messageMap.has(msg.content)) {
        messageMap.set(msg.content, msg);
      }
    });

    // Convert back to array and sort by timestamp
    return Array.from(messageMap.values()).sort(
      (a, b) => a.timestamp.getTime() - b.timestamp.getTime()
    );
  }, [messages, optimisticMessages]);

  const artifactsQuery = useQuery({
    queryKey: xagentKeys.artifacts(xagentId),
    queryFn: () => vibex.listArtifacts(xagentId),
    enabled: !!xagentId && xagentId !== "dummy-task-id",
  });

  // Subscribe to real-time updates
  useEffect(() => {
    if (!xagentId || xagentId === "dummy-task-id") return;

    const cleanup = vibex.subscribeToXAgentUpdates(
      xagentId,
      (data) => {
        console.log("[useXAgent] Received SSE data:", data);

        // Invalidate and refetch relevant queries based on event type
        queryClient.invalidateQueries({
          queryKey: xagentKeys.messages(xagentId),
        });
        queryClient.invalidateQueries({
          queryKey: xagentKeys.artifacts(xagentId),
        });

        if (data.event === "xagent_update") {
          queryClient.invalidateQueries({
            queryKey: xagentKeys.detail(xagentId),
          });
          queryClient.invalidateQueries({
            queryKey: xagentKeys.artifacts(xagentId),
          });
        }
      },
      (error) => {
        console.error("[useXAgent] SSE error:", error);
      }
    );

    return () => {
      if (cleanup) cleanup.close();
    };
  }, [xagentId, vibex, queryClient]);

  // Chat functionality
  const sendMessage = useMutation({
    mutationFn: (message: string) => vibex.sendMessage(xagentId, message),
    onSuccess: () => {
      // Invalidate messages to show the new message
      queryClient.invalidateQueries({
        queryKey: xagentKeys.messages(xagentId),
      });
      queryClient.invalidateQueries({
        queryKey: xagentKeys.detail(xagentId),
      });
    },
  });

  const handleSubmit = useCallback(
    (message: string, mode?: "chat" | "command") => {
      if (!message.trim()) return;

      // Add optimistic message
      const optimisticMsg: ChatMessage = {
        id: `optimistic-${Date.now()}`,
        role: "user",
        content: message.trim(),
        timestamp: new Date(),
        status: "complete",
      };

      setOptimisticMessages((prev) => [...prev, optimisticMsg]);
      setInput(""); // Clear input immediately

      // Send the actual message
      sendMessage.mutate(message.trim(), {
        onError: (error) => {
          console.error("Failed to send message:", error);
          // Remove the optimistic message on error
          setOptimisticMessages((prev) =>
            prev.filter((msg) => msg.content !== message.trim())
          );
        },
      });
    },
    [sendMessage]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setInput(e.target.value);
    },
    []
  );

  // TODO: Add executeXAgent mutation when API method is implemented

  const deleteXAgent = useMutation({
    mutationFn: () => vibex.deleteXAgent(xagentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: xagentKeys.list() });
    },
  });

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (sseCleanupRef.current) {
        sseCleanupRef.current();
      }
    };
  }, []);

  return {
    // Data
    xagent: xagentQuery.data,
    messages: allMessages,
    artifacts: artifactsQuery.data,

    // Loading states
    isLoading: xagentQuery.isLoading,
    isMessagesLoading: messagesQuery.isLoading,
    isLoadingArtifacts: artifactsQuery.isLoading,

    // Error states
    error: xagentQuery.error,
    messagesError: messagesQuery.error,
    artifactsError: artifactsQuery.error,

    // Chat functionality
    input,
    handleSubmit,
    handleInputChange,
    setInput,

    // Chat loading state
    isSendingMessage: sendMessage.isPending,

    // Mutations
    deleteXAgent,
  };
}

/**
 * Hook for XAgent logs
 */
export function useLogs(
  xagentId: string,
  options: { level?: string; limit?: number; enabled?: boolean } = {}
) {
  const vibex = useApi();

  const query = useQuery({
    queryKey: xagentKeys.logs(xagentId, options),
    queryFn: () => vibex.getLogs(xagentId),
    enabled:
      (options.enabled ?? true) && !!xagentId && xagentId !== "dummy-task-id",
    staleTime: 2000, // Cache for 2 seconds to prevent excessive requests
  });

  return {
    logs: query.data?.logs || [],
    hasMore: false, // TODO: Implement pagination when backend supports it
    isLoading: query.isLoading,
    refetch: query.refetch,
    error: query.error,
  };
}

/**
 * Hook for XAgent artifact content
 */
export function useArtifact({
  xagentId,
  path,
  enabled = true,
}: {
  xagentId: string;
  path: string;
  enabled?: boolean;
}) {
  const vibex = useApi();

  return useQuery({
    queryKey: [...xagentKeys.artifacts(xagentId), path],
    queryFn: () => vibex.getArtifact(xagentId, path),
    enabled: enabled && !!xagentId && !!path && xagentId !== "dummy-task-id",
  });
}

/**
 * Hook for XAgent memory search
 */
export function useMemory(xagentId: string, query: string, limit: number = 10) {
  const vibex = useApi();

  return useQuery({
    queryKey: xagentKeys.memory(xagentId, query, limit),
    queryFn: () => vibex.searchMemory({ agent_id: xagentId, query, limit }),
    enabled: !!xagentId && !!query && xagentId !== "dummy-task-id",
  });
}

/**
 * Hook for XAgent list
 */
export function useXAgents() {
  const vibex = useApi();
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: xagentKeys.list(),
    queryFn: () => vibex.listXAgents(),
  });

  const deleteXAgent = useMutation({
    mutationFn: (xagentId: string) => vibex.deleteXAgent(xagentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: xagentKeys.list() });
    },
  });

  return {
    xagents: query.data?.runs || [],
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
    deleteXAgent,
  };
}
