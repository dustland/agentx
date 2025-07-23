import { useState, useCallback, useEffect, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ChatMessage } from "@/types/chat";
import { nanoid } from "nanoid";
import { useTask, taskKeys } from "./use-task";

interface UseChatOptions {
  taskId: string;
  onError?: (error: Error) => void;
}

/**
 * Simplified chat hook focused on chat functionality
 */
export function useChat({ taskId, onError }: UseChatOptions) {
  const [input, setInput] = useState("");
  const [streamingMessage, setStreamingMessage] = useState<ChatMessage | null>(null);
  const [optimisticMessages, setOptimisticMessages] = useState<ChatMessage[]>([]);
  const queryClient = useQueryClient();
  
  // Get everything we need from useTask
  const { 
    task, 
    messages: rawMessages, 
    sendMessage, 
    subscribe, 
    stop,
    isLoading,
    isMessagesLoading
  } = useTask(taskId);
  
  // TODO: Backend /messages endpoint is returning empty array
  
  // Transform raw messages to ChatMessage format
  const messages: ChatMessage[] = useMemo(() => 
    rawMessages.map((msg: any) => ({
      id: msg.id || msg.message_id || nanoid(),
      role: msg.role as "user" | "assistant" | "system",
      content: typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content),
      timestamp: new Date(msg.timestamp),
      status: "complete" as const,
      metadata: msg.metadata,
    })), [rawMessages]
  );
  
  // Remove optimistic messages that now exist in real messages
  useEffect(() => {
    if (optimisticMessages.length > 0 && messages.length > 0) {
      const realMessageIds = new Set(messages.map(m => m.id));
      const realMessageContents = new Set(messages.map(m => m.content));
      setOptimisticMessages(prev => 
        prev.filter(msg => !realMessageIds.has(msg.id) && !realMessageContents.has(msg.content))
      );
    }
  }, [messages, optimisticMessages.length]);
  
  // Combine all messages in the correct order
  const allMessages = useMemo(() => {
    // Use a Map to ensure unique messages by ID
    const messageMap = new Map<string, ChatMessage>();
    
    // Add real messages first
    messages.forEach(msg => {
      messageMap.set(msg.id, msg);
    });
    
    // Add optimistic messages if they don't already exist
    optimisticMessages.forEach(msg => {
      if (!messageMap.has(msg.id)) {
        // Also check if content already exists to prevent duplicates
        const isDuplicate = Array.from(messageMap.values()).some(
          existing => existing.content === msg.content && existing.role === msg.role
        );
        if (!isDuplicate) {
          messageMap.set(msg.id, msg);
        }
      }
    });
    
    // Add streaming message if present and not duplicate
    if (streamingMessage && !messageMap.has(streamingMessage.id)) {
      messageMap.set(streamingMessage.id, streamingMessage);
    }
    
    // Convert back to array and sort by timestamp
    return Array.from(messageMap.values()).sort(
      (a, b) => a.timestamp.getTime() - b.timestamp.getTime()
    );
  }, [messages, optimisticMessages, streamingMessage]);
  
  // Subscribe to SSE for streaming and messages
  useEffect(() => {
    const unsubscribe = subscribe({
      onMessage: (message) => {
        // Handle complete messages from SSE (e.g., system messages from background execution)
        const newMessage: ChatMessage = {
          id: message.id,
          role: message.role,
          content: message.content,
          timestamp: new Date(message.timestamp),
          status: "complete",
        };
        
        // Add to optimistic messages to show immediately
        setOptimisticMessages(prev => {
          // Check if message already exists
          if (prev.some(m => m.id === newMessage.id)) {
            return prev;
          }
          return [...prev, newMessage];
        });
        
        // Also trigger a refetch to ensure consistency
        queryClient.invalidateQueries({ queryKey: taskKeys.messages(taskId) });
      },
      onStreamChunk: (chunk) => {
        if (!streamingMessage || streamingMessage.id !== chunk.message_id) {
          // New streaming message
          setStreamingMessage({
            id: chunk.message_id,
            role: "assistant",
            content: chunk.chunk,
            timestamp: new Date(chunk.timestamp),
            status: "streaming",
          });
        } else {
          // Append to existing streaming message
          setStreamingMessage(prev => prev ? {
            ...prev,
            content: prev.content + chunk.chunk,
          } : null);
        }
        
        // Clear streaming message when done
        if (chunk.is_final) {
          setStreamingMessage(null);
        }
      },
    });
    
    return unsubscribe;
  }, [subscribe, streamingMessage, queryClient, taskId]);
  
  const handleSubmit = useCallback((message: string, mode?: "agent" | "chat") => {
    if (!message.trim()) return;
    
    // Add optimistic message
    const optimisticMsg: ChatMessage = {
      id: `optimistic-${Date.now()}`,
      role: "user",
      content: message.trim(),
      timestamp: new Date(),
      status: "complete",
    };
    
    setOptimisticMessages(prev => [...prev, optimisticMsg]);
    setStreamingMessage(null);
    setInput(""); // Clear input immediately
    
    // Send the actual message with mode
    sendMessage.mutate({ message: message.trim(), mode }, {
      onError: (error) => {
        console.error("Failed to send message:", error);
        // Remove the last optimistic message on error
        setOptimisticMessages(prev => prev.slice(0, -1));
        onError?.(error as Error);
      },
    });
  }, [sendMessage, onError]);
  
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setInput(e.target.value);
  }, []);
  
  return {
    messages: allMessages,
    input,
    isLoading: sendMessage.isPending || task?.status === "running",
    isMessagesLoading,
    error: sendMessage.error as Error | undefined,
    streamingMessage,
    handleInputChange,
    handleSubmit,
    stop,
    setInput,
  };
}