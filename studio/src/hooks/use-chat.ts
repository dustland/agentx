import { useState, useCallback, useEffect, useMemo } from "react";
import { ChatMessage } from "@/types/chat";
import { nanoid } from "nanoid";
import { useTask } from "./use-task";

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
      const realMessageContents = new Set(messages.map(m => m.content));
      setOptimisticMessages(prev => 
        prev.filter(msg => !realMessageContents.has(msg.content))
      );
    }
  }, [messages, optimisticMessages.length]);
  
  // Combine all messages in the correct order
  const allMessages = useMemo(() => {
    const combined = [...messages];
    
    // Add optimistic messages that aren't duplicates
    const messageContents = new Set(messages.map(m => m.content));
    optimisticMessages.forEach(msg => {
      if (!messageContents.has(msg.content)) {
        combined.push(msg);
      }
    });
    
    // Add streaming message if present
    if (streamingMessage) {
      combined.push(streamingMessage);
    }
    
    // Sort by timestamp to ensure correct order
    return combined.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }, [messages, optimisticMessages, streamingMessage]);
  
  // Subscribe to SSE for streaming
  useEffect(() => {
    const unsubscribe = subscribe({
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
  }, [subscribe, streamingMessage]);
  
  const handleSubmit = useCallback((message: string) => {
    if (!message.trim()) return;
    
    // Add optimistic message IMMEDIATELY
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
    
    // Send the actual message
    sendMessage.mutate(message, {
      onError: (error) => {
        console.error("Failed to send message:", error);
        // Remove the optimistic message on error
        setOptimisticMessages(prev => 
          prev.filter(msg => msg.id !== optimisticMsg.id)
        );
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