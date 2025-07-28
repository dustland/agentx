import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApi } from "@/lib/api-client";
import { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { ChatMessage } from "@/types/chat";
import { nanoid } from "nanoid";
import type { ToolCallPart, ToolResultPart } from "@/components/chat/message-parts";

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
  const [streamingMessages, setStreamingMessages] = useState<
    Map<string, ChatMessage>
  >(new Map());

  // Queries
  const xagentQuery = useQuery({
    queryKey: xagentKeys.detail(xagentId),
    queryFn: () => vibex.getXAgent(xagentId),
    enabled: !!xagentId && xagentId !== "dummy-task-id",
    staleTime: 0, // Always fetch fresh data for task status updates
    refetchOnMount: true,
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
          parts: msg.parts || undefined, // Include parts if available
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
      messageMap.set(msg.id, msg);
    });
    
    // Log streaming messages for debugging
    if (streamingMessages.size > 0) {
      console.log("[useXAgent] Active streaming messages:", Array.from(streamingMessages.entries()).map(([id, msg]) => ({
        id,
        status: msg.status,
        parts_count: msg.parts?.length,
        content_length: msg.content?.length,
        content_preview: msg.content?.substring(0, 100)
      })));
    }

    // Add streaming messages, but only if they don't conflict with real messages
    Array.from(streamingMessages.values()).forEach((msg) => {
      const realMessage = messageMap.get(msg.id);

      // If there's a real message with the same ID and it's complete, skip the streaming version
      if (realMessage && realMessage.status === "complete") {
        return;
      }

      // If there's a real message with similar content, skip the streaming version
      const isDuplicate = Array.from(messageMap.values()).some((realMsg) => {
        return (
          realMsg.content &&
          msg.content &&
          realMsg.content.trim() === msg.content.trim() &&
          Math.abs(realMsg.timestamp.getTime() - msg.timestamp.getTime()) <
            10000
        ); // Within 10 seconds
      });

      if (!isDuplicate) {
        messageMap.set(msg.id, msg);
      }
    });

    // Add optimistic messages if they don't already exist
    optimisticMessages.forEach((msg) => {
      if (!messageMap.has(msg.id)) {
        messageMap.set(msg.id, msg);
      }
    });

    // Convert back to array and sort by timestamp
    const result = Array.from(messageMap.values()).sort(
      (a, b) => a.timestamp.getTime() - b.timestamp.getTime()
    );

    return result;
  }, [messages, optimisticMessages, streamingMessages]);

  const artifactsQuery = useQuery({
    queryKey: xagentKeys.artifacts(xagentId),
    queryFn: () => vibex.listArtifacts(xagentId),
    enabled: !!xagentId && xagentId !== "dummy-task-id",
    staleTime: 0, // Always fetch fresh data for artifact updates
    refetchOnMount: true,
  });

  // Subscribe to real-time updates
  useEffect(() => {
    if (!xagentId || xagentId === "dummy-task-id") return;

    console.log("[useXAgent] Setting up SSE connection for agent:", xagentId);

    const cleanup = vibex.subscribeToXAgentUpdates(
      xagentId,
      (data) => {
        console.log("[useXAgent] Received SSE data:", data);
        console.log("[useXAgent] Event type:", data.event);
        console.log("[useXAgent] Event data:", data.data);

        // Handle new message part streaming events
        if (data.event === "message_start") {
          const { message_id, role } = data.data;
          console.log("[useXAgent] message_start event:", { message_id, role });
          setStreamingMessages((prev) => {
            const updated = new Map(prev);
            updated.set(message_id, {
              id: message_id,
              role: role as "assistant" | "user" | "system",
              content: "",
              parts: [],
              timestamp: new Date(),
              status: "streaming",
            });
            console.log("[useXAgent] Created new streaming message:", message_id);
            return updated;
          });
          return;
        }

        if (data.event === "part_delta") {
          const { message_id, part_index, delta, type } = data.data;
          console.log("[useXAgent] part_delta event:", { 
            message_id, 
            part_index, 
            delta_length: delta?.length, 
            type,
            delta_preview: delta?.substring(0, 50)
          });
          setStreamingMessages((prev) => {
            const updated = new Map(prev);
            const message = updated.get(message_id);
            if (message) {
              // Clone the message to avoid mutations
              const updatedMessage = { ...message };
              
              // Ensure parts array exists and has enough slots
              if (!updatedMessage.parts) {
                updatedMessage.parts = [];
              }
              
              // Clone parts array to avoid mutations
              updatedMessage.parts = [...updatedMessage.parts];
              
              // Ensure we have enough parts
              while (updatedMessage.parts.length <= part_index) {
                updatedMessage.parts.push({ type: "text", text: "" });
              }

              // Clone and update the specific part
              const part = { ...updatedMessage.parts[part_index] };
              if (part.type === "text" && delta) {
                part.text = (part.text || "") + delta;
                updatedMessage.parts[part_index] = part;
              }

              // Rebuild content from parts - only use text from each part once
              updatedMessage.content = updatedMessage.parts
                .filter((p: any) => p.type === "text")
                .map((p: any) => p.text || "")
                .join("");

              updated.set(message_id, updatedMessage);
            }
            return updated;
          });
          return;
        }

        if (data.event === "part_complete") {
          const { message_id, part_index, part } = data.data;
          console.log("[useXAgent] part_complete event:", { message_id, part_index, part_type: part?.type, part });
          setStreamingMessages((prev) => {
            const updated = new Map(prev);
            const message = updated.get(message_id);
            if (message) {
              // Ensure parts array exists and has enough slots
              if (!message.parts) {
                message.parts = [];
              }
              while (message.parts.length <= part_index) {
                message.parts.push({ type: "text", text: "" });
              }

              // Replace the part at the index
              message.parts[part_index] = part;
              updated.set(message_id, { ...message });
            }
            return updated;
          });
          return;
        }

        if (data.event === "message_complete") {
          const { message } = data.data;
          console.log("[useXAgent] message_complete event:", { 
            message_id: message.id, 
            parts_count: message.parts?.length,
            content_length: message.content?.length,
            message
          });
          setStreamingMessages((prev) => {
            const updated = new Map(prev);
            const existingMessage = updated.get(message.id);
            if (existingMessage) {
              // Update with complete message data
              updated.set(message.id, {
                ...message,
                timestamp: new Date(message.timestamp),
                status: "complete",
              });
            }
            return updated;
          });

          // Invalidate messages query after a delay
          setTimeout(() => {
            queryClient.invalidateQueries({
              queryKey: xagentKeys.messages(xagentId),
            });
            // Remove streaming message
            setStreamingMessages((prev) => {
              const updated = new Map(prev);
              updated.delete(message.id);
              return updated;
            });
          }, 1000);
          return;
        }

        if (data.event === "message") {
          // Handle complete message events
          let messageData;
          try {
            messageData =
              typeof data.data === "string" ? JSON.parse(data.data) : data.data;
          } catch (e) {
            console.error("[useXAgent] Failed to parse message data:", e);
            return;
          }
          queryClient.invalidateQueries({
            queryKey: xagentKeys.messages(xagentId),
          });
        } else if (data.event === "tool_call_start") {
          // Handle tool call start events
          console.log("[useXAgent] Tool call start received:", data.data);
          // Update streaming messages with tool call info
          const toolData = data.data;
          setStreamingMessages((prev) => {
            const updated = new Map(prev);
            // Find the latest streaming message and add tool call part
            const latestMessage = Array.from(updated.values()).find(
              (msg) => msg.status === "streaming"
            );
            if (latestMessage) {
              const updatedMessage = {
                ...latestMessage,
                parts: [
                  ...(latestMessage.parts || []),
                  {
                    type: "tool-call" as const,
                    toolCallId: toolData.tool_call_id,
                    toolName: toolData.tool_name,
                    args: toolData.args,
                    status: "running",
                  } as ToolCallPart,
                ],
              };
              updated.set(latestMessage.id, updatedMessage);
            }
            return updated;
          });
        } else if (data.event === "tool_call_result") {
          // Handle tool call result events
          console.log("[useXAgent] Tool call result received:", data.data);
          const toolData = data.data;
          setStreamingMessages((prev) => {
            const updated = new Map(prev);
            // Find the message with this tool call and update it
            updated.forEach((msg, id) => {
              if (msg.parts) {
                const partIndex = msg.parts.findIndex(
                  (p: any) =>
                    p.type === "tool_call" &&
                    p.tool_call_id === toolData.tool_call_id
                );
                if (partIndex !== -1) {
                  const updatedParts = [...msg.parts];
                  updatedParts[partIndex] = {
                    ...updatedParts[partIndex],
                    status: toolData.is_error ? "failed" : "completed",
                  } as any;
                  // Add tool result part
                  updatedParts.push({
                    type: "tool-result" as const,
                    toolCallId: toolData.tool_call_id,
                    toolName: toolData.tool_name,
                    result: toolData.result,
                    isError: toolData.is_error,
                  } as ToolResultPart);
                  updated.set(id, {
                    ...msg,
                    parts: updatedParts,
                  });
                }
              }
            });
            return updated;
          });
        } else if (data.event === "message_part") {
          // Handle message part events
          console.log("[useXAgent] Message part received:", data.data);
          const partData = data.data;
          setStreamingMessages((prev) => {
            const updated = new Map(prev);
            const messageId = `streaming-${partData.message_id || Date.now()}`;
            const existing = updated.get(messageId);

            if (existing) {
              updated.set(messageId, {
                ...existing,
                parts: [...(existing.parts || []), partData.part],
              });
            }
            return updated;
          });
        } else if (data.event === "task_update") {
          // Handle task status updates - these should refresh the summary
          console.log("[useXAgent] Task update received:", data.data);
          queryClient.invalidateQueries({
            queryKey: xagentKeys.detail(xagentId),
          });
        } else if (data.event === "artifact_update") {
          // Handle artifact updates - refresh the artifacts list
          console.log("[useXAgent] Artifact update received:", data.data);
          queryClient.invalidateQueries({
            queryKey: xagentKeys.artifacts(xagentId),
          });
        } else {
          // Handle other events (xagent_update, etc.)
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
        }
      },
      (error) => {
        console.error("[useXAgent] SSE error:", error);
      }
    );

    // Store cleanup function in ref for proper cleanup
    sseCleanupRef.current = () => cleanup.close();

    return () => {
      console.log(
        "[useXAgent] Cleaning up SSE connection for agent:",
        xagentId
      );
      if (cleanup) cleanup.close();
    };
  }, [xagentId, queryClient]);

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
    (message: string, mode?: "chat" | "agent") => {
      // Allow empty messages for continuing execution
      const trimmedMessage = message.trim();
      
      // Add optimistic message (even if empty)
      const optimisticMsg: ChatMessage = {
        id: `optimistic-${Date.now()}`,
        role: "user",
        content: trimmedMessage,
        timestamp: new Date(),
        status: "complete",
        parts: trimmedMessage ? [{ type: "text", text: trimmedMessage }] : [],
      };

      setOptimisticMessages((prev) => [...prev, optimisticMsg]);
      setInput(""); // Clear input immediately

      // Send the actual message (empty messages are allowed)
      sendMessage.mutate(trimmedMessage, {
        onError: (error) => {
          console.error("Failed to send message:", error);
          // Remove the optimistic message on error
          setOptimisticMessages((prev) =>
            prev.filter((msg) => msg.content !== trimmedMessage)
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
    queryFn: () => vibex.searchMemory({ xagent_id: xagentId, query, limit }),
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

  const createXAgent = useMutation({
    mutationFn: ({
      goal,
      configPath,
      context,
    }: {
      goal: string;
      configPath: string;
      context?: object;
    }) => vibex.createXAgent(goal, configPath, context),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: xagentKeys.list() });
    },
  });

  const deleteXAgent = useMutation({
    mutationFn: (xagentId: string) => vibex.deleteXAgent(xagentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: xagentKeys.list() });
    },
  });

  return {
    xagents: query.data?.xagents || [],
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
    createXAgent,
    deleteXAgent,
  };
}
