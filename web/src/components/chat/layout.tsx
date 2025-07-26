"use client";

import React, { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Bot } from "lucide-react";
import { ChatInput } from "./input";
import { MessageBubble } from "./message-bubble";

interface ChatLayoutProps {
  messages: Array<{
    id: string;
    role: "user" | "assistant" | "system";
    content: string;
    timestamp: Date;
    status?: "streaming" | "complete" | "error";
  }>;
  onSendMessage: (message: string, mode?: "agent" | "chat") => void;
  onStop?: () => void;
  isLoading?: boolean;
  allowEmptyMessage?: boolean;
}

export function ChatLayout({
  messages,
  onSendMessage,
  onStop,
  isLoading = false,
  allowEmptyMessage = false,
}: ChatLayoutProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    // Use a small delay to ensure DOM is updated
    const timer = setTimeout(() => {
      if (scrollRef.current) {
        scrollRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [messages]);

  const handleSubmit = (message: string, mode?: "agent" | "chat") => {
    onSendMessage(message, mode);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Message List */}
      {messages.length === 0 ? (
        isLoading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Loading task...</span>
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
        <ScrollArea className="flex-1 overflow-hidden">
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
          onStop={onStop}
          isLoading={isLoading}
          allowEmptyMessage={allowEmptyMessage}
        />
      </div>
    </div>
  );
}
