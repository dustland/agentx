import { useEffect, useRef } from "react";
import { StreamEvent } from "@/types/chat";

interface UseTaskStreamProps {
  taskId: string;
  enabled?: boolean;
  onEvent: (event: StreamEvent) => void;
  onError?: (error: Error) => void;
}

export function useTaskStream({
  taskId,
  enabled = true,
  onEvent,
  onError,
}: UseTaskStreamProps) {
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!taskId || !enabled) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7770";
    const eventSource = new EventSource(`${apiUrl}/tasks/${taskId}/stream`);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onEvent({
          type: data.type || "message",
          data: data,
          timestamp: new Date(),
        });
      } catch (error) {
        console.error("Failed to parse stream message:", error);
        onError?.(error as Error);
      }
    };

    eventSource.onerror = (error) => {
      console.error("EventSource error:", error);
      onError?.(new Error("Stream connection error"));
    };

    return () => {
      eventSource.close();
    };
  }, [taskId, enabled, onEvent, onError]);

  return {
    close: () => eventSourceRef.current?.close(),
  };
}
