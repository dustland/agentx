"use client";

import React, { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Pause, Play, Share2, MoreHorizontal, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { ChatInput } from "./chat-input";

interface ChatLayoutProps {
  taskId: string;
  taskName: string;
  taskStatus: "pending" | "running" | "completed" | "failed";
  messages: Array<{
    id: string;
    role: "user" | "assistant" | "system";
    content: string;
    timestamp: Date;
    status?: "streaming" | "complete" | "failed";
  }>;
  onSendMessage: (message: string) => void;
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
  onPauseResume,
  onShare,
  onMoreActions,
  isLoading,
}: ChatLayoutProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
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
      case "failed":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center gap-3">
          <h2 className="font-semibold text-lg">{taskName}</h2>
          <Badge className={cn("capitalize", getStatusColor())}>
            {taskStatus === "running" && (
              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            )}
            {taskStatus}
          </Badge>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Button
              size="icon"
              variant="ghost"
              onClick={onPauseResume}
              disabled={taskStatus !== "running" && taskStatus !== "pending"}
            >
              {taskStatus === "running" ? (
                <Pause className="h-4 w-4" />
              ) : (
                <Play className="h-4 w-4" />
              )}
            </Button>

            <Button size="icon" variant="ghost" onClick={onShare}>
              <Share2 className="h-4 w-4" />
            </Button>

            <Button size="icon" variant="ghost" onClick={onMoreActions}>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Message List */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Loading task...</span>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className="group">
                <div
                  className={cn(
                    "rounded-lg p-4 transition-all",
                    // User messages have a subtle left border
                    message.role === "user" && "border-l-2 border-primary ml-2",
                    // System messages have muted background
                    message.role === "system" &&
                      "bg-muted/50 text-muted-foreground",
                    // Assistant messages have different styles based on status
                    message.role === "assistant" && [
                      message.status === "streaming" &&
                        "border border-primary/20 bg-gradient-to-r from-transparent via-primary/5 to-transparent animate-gradient",
                      message.status === "complete" && "border border-border",
                      message.status === "failed" &&
                        "border border-destructive/50 bg-destructive/5",
                    ]
                  )}
                >
                  {/* Message header for assistant messages */}
                  {message.role === "assistant" && (
                    <div className="flex items-center gap-2 mb-2 text-xs text-muted-foreground">
                      <span className="font-medium">Assistant</span>
                      {message.status === "streaming" && (
                        <span className="text-primary animate-pulse">
                          • Thinking...
                        </span>
                      )}
                    </div>
                  )}

                  {/* Message content */}
                  <div
                    className={cn(
                      "text-sm whitespace-pre-wrap",
                      message.status === "streaming" && "text-foreground/80"
                    )}
                  >
                    {message.content}
                    {message.status === "streaming" && (
                      <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse rounded-sm" />
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* Chat Input */}
      <ChatInput
        onSendMessage={handleSubmit}
        isLoading={taskStatus === "running"}
        taskStatus={taskStatus}
      />
    </div>
  );
}
