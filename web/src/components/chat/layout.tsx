"use client";

import React, { useEffect, useRef, useCallback } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Bot } from "lucide-react";
import { ChatInput } from "./input";
import { MessageBubble } from "./message-bubble";
import { useXAgentContext } from "@/contexts/xagent";

export function ChatLayout() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Use the XAgent context for all functionality
  const { xagent, messages, isLoading, isSendingMessage, handleSubmit } =
    useXAgentContext();

  // Auto-scroll to bottom when new messages arrive or during streaming
  useEffect(() => {
    const scrollToBottom = () => {
      if (scrollAreaRef.current) {
        const scrollElement = scrollAreaRef.current.querySelector(
          "[data-radix-scroll-area-viewport]"
        );
        if (scrollElement) {
          scrollElement.scrollTop = scrollElement.scrollHeight;
        }
      }
    };

    const hasStreamingMessages = messages.some(
      (msg) => msg.status === "streaming"
    );

    if (hasStreamingMessages) {
      // More frequent scrolling during streaming
      const interval = setInterval(scrollToBottom, 50); // Scroll every 50ms during streaming
      return () => clearInterval(interval);
    } else {
      // Single scroll for new messages or when streaming ends
      const timer = setTimeout(scrollToBottom, 10);
      return () => clearTimeout(timer);
    }
  }, [
    messages.length,
    messages.length > 0 ? messages[messages.length - 1]?.content?.length : 0,
    isSendingMessage,
  ]); // Trigger on message count, last message content length, and streaming state

  // Stop function for cancelling ongoing operations
  const handleStop = useCallback(() => {
    // TODO: Implement actual stop functionality when streaming is added
    console.log("Stop requested - not implemented yet");
  }, []);

  return (
    <div className="flex flex-col h-full">
      {/* Message List */}
      {messages.length === 0 ? (
        isLoading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Loading messages...</span>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-violet-500/10 to-purple-600/10 flex items-center justify-center mb-4">
              <Bot className="w-8 h-8 text-violet-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Start a conversation</h3>
            <p className="text-sm text-muted-foreground max-w-sm">
              Send a message to begin interacting with the AI assistant. I'm
              here to help with your task.
            </p>
          </div>
        )
      ) : (
        <ScrollArea className="flex-1 overflow-hidden" ref={scrollAreaRef}>
          <div className="p-4 space-y-3">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onRetry={() => {
                  // TODO: Implement retry functionality
                  console.log("Retry message", message.id);
                }}
              />
            ))}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>
      )}

      {/* Chat Input */}
      <div className="flex-shrink-0">
        <ChatInput
          onSendMessage={handleSubmit}
          onStop={handleStop}
          isLoading={isSendingMessage}
          allowEmptyMessage={!!xagent?.plan}
        />
      </div>
    </div>
  );
}
