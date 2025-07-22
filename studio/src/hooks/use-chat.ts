import { useState, useCallback, useRef, useEffect } from "react";
import { ChatMessage } from "@/types/chat";
import { nanoid } from "nanoid";
import { useTask } from "./use-task";

interface StreamingMessage extends ChatMessage {
  status: "streaming" | "error";
  streamMessageId?: string; // Temporary ID used during streaming
}

interface UseChatOptions {
  taskId: string;
  onError?: (error: Error) => void;
}

interface UseChatHelpers {
  messages: ChatMessage[];
  input: string;
  isLoading: boolean;
  error: Error | undefined;
  streamingMessage: StreamingMessage | null;

  // Actions
  handleInputChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
  handleSubmit: (e?: React.FormEvent | string) => void;
  reload: () => Promise<void>;
  stop: () => void;
  setInput: (input: string) => void;
}

/**
 * Chat UI hook that depends on useTask for persistence
 * Handles chat interactions, streaming, and UI state
 */
export function useChat({ taskId, onError }: UseChatOptions): UseChatHelpers {
  const {
    messages: persistedMessages,
    taskStatus,
    sendMessage,
    addMessage,
    stopTask,
    reload: reloadTask,
    subscribe,
    initialMessage,
  } = useTask(taskId);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | undefined>();
  const [streamingMessage, setStreamingMessage] =
    useState<StreamingMessage | null>(null);

  const streamingIdRef = useRef<string | null>(null);

  // Subscribe to task events
  useEffect(() => {
    const unsubscribe = subscribe({
      onMessage: (message) => {
        // Complete message received - replace any streaming message
        console.log("Received persisted message from backend:", message);

        // If we have a streaming message, replace it with the complete one
        if (streamingMessage && message.role === "assistant") {
          setStreamingMessage(null);
          streamingIdRef.current = null;
        }
      },
      onStreamChunk: (chunk) => {
        console.log("[useChat] Received stream chunk:", {
          message_id: chunk.message_id,
          chunk_length: chunk.chunk?.length || 0,
          is_final: chunk.is_final,
          has_error: !!chunk.error,
          current_streaming_id: streamingIdRef.current,
        });

        // Handle streaming chunks for real-time UI
        if (
          !streamingMessage ||
          streamingMessage.streamMessageId !== chunk.message_id
        ) {
          // Start new streaming message
          console.log(
            "[useChat] Starting new streaming message for:",
            chunk.message_id
          );
          const newStreamingMessage: StreamingMessage = {
            id: nanoid(),
            role: "assistant",
            content: chunk.chunk,
            timestamp: new Date(chunk.timestamp),
            status: "streaming",
            streamMessageId: chunk.message_id,
          };
          setStreamingMessage(newStreamingMessage);
          streamingIdRef.current = chunk.message_id;
        } else {
          // Append to existing streaming message
          console.log(
            "[useChat] Appending to existing streaming message:",
            chunk.message_id
          );
          setStreamingMessage((prev) =>
            prev
              ? {
                  ...prev,
                  content: prev.content + chunk.chunk,
                }
              : null
          );
        }

        // Handle error chunks
        if (chunk.error) {
          console.error("[useChat] Stream chunk contains error:", chunk.error);
          setStreamingMessage((prev) =>
            prev
              ? {
                  ...prev,
                  content: prev.content + `\n\n❌ Error: ${chunk.error}`,
                  status: "error",
                }
              : null
          );
          setError(new Error(chunk.error));
          setIsLoading(false);
          return;
        }

        // If final chunk, mark as complete but keep showing until replaced
        if (chunk.is_final && streamingMessage) {
          console.log("[useChat] Final chunk received for:", chunk.message_id);
          setStreamingMessage((prev) =>
            prev
              ? {
                  ...prev,
                  status: "streaming", // Keep as streaming until replaced by complete message
                }
              : null
          );
        }
      },
      onStatusChange: (status) => {
        setIsLoading(status === "running");
      },
    });

    return unsubscribe;
  }, [subscribe, streamingMessage]);

  // Send initial message if provided
  useEffect(() => {
    if (initialMessage && persistedMessages.length === 0) {
      setInput(initialMessage);
      // Auto-submit after a short delay
      setTimeout(() => {
        handleSubmit();
      }, 100);
    }
  }, [initialMessage, persistedMessages.length]);

  // Handle form submission
  const handleSubmit = useCallback(
    async (e?: React.FormEvent | string) => {
      // If a string is passed directly, use it as the message
      const directMessage = typeof e === "string" ? e : null;

      if (directMessage === null) {
        (e as React.FormEvent)?.preventDefault();
      }

      const messageContent = directMessage || input.trim();
      if (!messageContent || isLoading) return;

      // Only clear input if it wasn't passed directly
      if (!directMessage) {
        setInput("");
      }
      setIsLoading(true);
      setError(undefined);

      try {
        // Send to backend - let the backend handle persistence and echo back via SSE
        await sendMessage(messageContent);

        // Start expecting a streaming response
        streamingIdRef.current = nanoid();
      } catch (err) {
        const error =
          err instanceof Error ? err : new Error("Failed to send message");
        setError(error);
        onError?.(error);
        setIsLoading(false);
      }
    },
    [input, isLoading, addMessage, sendMessage, onError]
  );

  // Handle input change
  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setInput(e.target.value);
    },
    []
  );

  // Reload the last message
  const reload = useCallback(async () => {
    if (persistedMessages.length === 0) return;

    const lastUserMessageIndex = persistedMessages.findLastIndex(
      (m) => m.role === "user"
    );
    if (lastUserMessageIndex === -1) return;

    // Get the last user message content
    const lastUserMessage = persistedMessages[lastUserMessageIndex];

    // Clear streaming message
    setStreamingMessage(null);
    streamingIdRef.current = null;

    try {
      // Resend the last user message
      await sendMessage(lastUserMessage.content);

      // Start expecting a new streaming response
      streamingIdRef.current = nanoid();
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to reload");
      setError(error);
      onError?.(error);
    }
  }, [persistedMessages, sendMessage, onError]);

  // Stop the current operation
  const stop = useCallback(() => {
    // Stop the task
    stopTask();

    // Clear streaming message when stopped
    setStreamingMessage(null);
    streamingIdRef.current = null;

    setIsLoading(false);
  }, [stopTask]);

  // Combine persisted messages with streaming message
  const allMessages = [...persistedMessages];
  if (streamingMessage) {
    allMessages.push(streamingMessage as ChatMessage);
  }

  return {
    messages: allMessages,
    input,
    isLoading,
    error,
    streamingMessage,
    handleInputChange,
    handleSubmit,
    reload,
    stop,
    setInput,
  };
}
