"use client";

import React, { useEffect, useRef, useCallback } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Bot, XCircle } from "lucide-react";
import { ChatInput } from "./input";
import { MessageBubble } from "./message-bubble";
import { useXAgentContext } from "@/contexts/xagent";

interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
  displayPath?: string;
}

interface ChatLayoutProps {
  onArtifactSelect?: ((artifact: Artifact) => void) | null;
}

export function ChatLayout({ onArtifactSelect }: ChatLayoutProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Use the XAgent context for all functionality
  const { xagent, messages, isLoading, isSendingMessage, handleSubmit, error, artifactsError } =
    useXAgentContext();

  // Check for authorization errors
  const authError = error?.response?.status === 403 || 
                   error?.response?.status === 401 ||
                   artifactsError?.response?.status === 403 || 
                   artifactsError?.response?.status === 401;

  // Auto-scroll to bottom during active streaming with content changes
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

    const lastMessage = messages[messages.length - 1];
    const isStreaming = lastMessage?.status === "streaming";
    
    if (isStreaming) {
      // Only scroll during streaming when content is actively changing
      scrollToBottom();
    }
    // Don't set up interval, just scroll when content changes
  }, [
    messages.length > 0 ? messages[messages.length - 1]?.content : null,
    messages.length > 0 ? messages[messages.length - 1]?.parts?.length : null,
  ]); // Only trigger on last message content/parts changes

  // Scroll to bottom on initial message load
  useEffect(() => {
    if (messages.length > 0 && !isLoading) {
      // Small delay to ensure DOM is updated
      setTimeout(() => {
        if (scrollAreaRef.current) {
          const scrollElement = scrollAreaRef.current.querySelector(
            "[data-radix-scroll-area-viewport]"
          );
          if (scrollElement) {
            scrollElement.scrollTop = scrollElement.scrollHeight;
          }
        }
      }, 100);
    }
  }, [messages.length > 0, isLoading]); // Only trigger when messages first appear

  // Stop function for cancelling ongoing operations
  const handleStop = useCallback(() => {
    // TODO: Implement actual stop functionality when streaming is added
    console.log("Stop requested - not implemented yet");
  }, []);

  return (
    <div className="flex flex-col h-full min-w-0">
      {/* Message List */}
      {authError ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-red-500/10 to-red-600/10 flex items-center justify-center mb-4">
            <XCircle className="w-8 h-8 text-red-600" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Access Denied</h3>
          <p className="text-sm text-muted-foreground max-w-sm">
            You don't have permission to access this project
          </p>
        </div>
      ) : messages.length === 0 ? (
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
        <ScrollArea className="flex-1 overflow-hidden min-w-0" ref={scrollAreaRef}>
          <div className="max-w-full overflow-hidden">
            <div className="p-4 min-w-0">
              <div className="space-y-0">
                {messages.map((message) => (
                  <MessageBubble
                    key={message.id}
                    message={message}
                    onRetry={() => {
                      // TODO: Implement retry functionality
                      console.log("Retry message", message.id);
                    }}
                    onArtifactSelect={onArtifactSelect}
                  />
                ))}
              </div>
              <div ref={scrollRef} />
            </div>
          </div>
        </ScrollArea>
      )}

      {/* Chat Input */}
      {!authError && (
        <div className="flex-shrink-0">
          <ChatInput
            onSendMessage={handleSubmit}
            onStop={handleStop}
            isLoading={isSendingMessage}
            allowEmptyMessage={!!xagent?.plan}
          />
        </div>
      )}
    </div>
  );
}
