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
  const [optimisticMessages, setOptimisticMessages] = useState<ChatMessage[]>(
    []
  );

  // Get everything we need from useTask
  const {
    task,
    messages: rawMessages,
    sendMessage,
    stop,
    isLoading,
    isMessagesLoading,
  } = useTask(taskId);

  // Transform raw messages to ChatMessage format
  const messages: ChatMessage[] = useMemo(
    () =>
      rawMessages.map((msg: any) => ({
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
    [rawMessages]
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
    // Use a Map to ensure unique messages by content (since IDs might differ)
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

  const handleSubmit = useCallback(
    (message: string, mode?: "agent" | "chat") => {
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

      // Send the actual message with mode
      sendMessage.mutate(
        { message: message.trim(), mode },
        {
          onError: (error) => {
            console.error("Failed to send message:", error);
            // Remove the optimistic message on error
            setOptimisticMessages((prev) =>
              prev.filter((msg) => msg.content !== message.trim())
            );
            onError?.(error as Error);
          },
        }
      );
    },
    [sendMessage, onError]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setInput(e.target.value);
    },
    []
  );

  return {
    messages: allMessages,
    input,
    isLoading: sendMessage.isPending || task?.status === "running",
    isMessagesLoading,
    error: sendMessage.error as Error | undefined,
    handleInputChange,
    handleSubmit,
    stop,
    setInput,
  };
}
