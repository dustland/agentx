"use client";

import React, { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import {
  Pause,
  Play,
  Share2,
  MoreHorizontal,
  Loader2,
  Bot,
  Sparkles,
  User,
  Copy,
  Check,
  RotateCcw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ChatInput } from "./chat-input";
import { MessageBubble } from "./message-bubble";

interface ChatLayoutProps {
  taskId: string;
  taskName: string;
  taskStatus: "pending" | "running" | "completed" | "error";
  messages: Array<{
    id: string;
    role: "user" | "assistant" | "system";
    content: string;
    timestamp: Date;
    status?: "streaming" | "complete" | "error";
  }>;
  onSendMessage: (message: string) => void;
  onStop?: () => void;
  onPauseResume: () => void;
  onShare: () => void;
  onMoreActions: () => void;
  isLoading?: boolean;
}

export function ChatLayout({
  taskId,
  taskName,
  taskStatus,
  messages,
  onSendMessage,
  onStop,
  onPauseResume,
  onShare,
  onMoreActions,
  isLoading,
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

  const handleSubmit = (message: string) => {
    onSendMessage(message);
  };

  const getStatusColor = () => {
    switch (taskStatus) {
      case "running":
        return "bg-blue-500";
      case "completed":
        return "bg-green-500";
      case "error":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 flex-shrink-0">
        <div className="flex items-center gap-3">
          <h2 className="font-semibold text-lg">{taskName}</h2>
          <Badge className={cn("capitalize", getStatusColor())}>
            {taskStatus === "running" && (
              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            )}
            {taskStatus}
          </Badge>
        </div>
      </div>

      {/* Message List */}
      <ScrollArea className="flex-1 overflow-hidden">
        <div className="p-4 space-y-3">
          {messages.length === 0 ? (
            isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Loading task...</span>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-violet-500/10 to-purple-600/10 flex items-center justify-center mb-4">
                  <Bot className="w-8 h-8 text-violet-600" />
                </div>
                <h3 className="text-lg font-semibold mb-2">
                  Start a conversation
                </h3>
                <p className="text-sm text-muted-foreground max-w-sm">
                  Send a message to begin interacting with the AI assistant. I'm
                  here to help with your task.
                </p>
              </div>
            )
          ) : (
            messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onRetry={() => {
                  // TODO: Implement retry functionality
                  console.log("Retry message", message.id);
                }}
              />
            ))
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* Chat Input */}
      <div className="flex-shrink-0">
        <ChatInput
          onSendMessage={handleSubmit}
          onStop={onStop}
          isLoading={taskStatus === "running"}
          taskStatus={taskStatus}
        />
      </div>
    </div>
  );
}
