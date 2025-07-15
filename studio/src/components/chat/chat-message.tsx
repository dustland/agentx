"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { ChatMessage as ChatMessageType } from "@/types/chat";
import { Bot, User, Loader2 } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

interface ChatMessageProps {
  message: ChatMessageType;
  isStreaming?: boolean;
}

export function ChatMessage({ message, isStreaming }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  const isSystem = message.role === "system";

  return (
    <div className="group flex gap-3">
      {/* Avatar */}
      <Avatar className="h-8 w-8 flex-shrink-0">
        <AvatarFallback
          className={cn(
            isUser && "bg-primary text-primary-foreground",
            isAssistant && "bg-secondary",
            isSystem && "bg-muted"
          )}
        >
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      {/* Message Content */}
      <div className="flex-1 space-y-2">
        {/* Header */}
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm">
            {isUser ? "You" : isAssistant ? "Assistant" : "System"}
          </span>
          <span className="text-xs text-muted-foreground">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
          {isStreaming && (
            <Badge variant="secondary" className="gap-1 text-xs">
              <Loader2 className="h-2 w-2 animate-spin" />
              Thinking
            </Badge>
          )}
        </div>

        {/* Message Body */}
        <div
          className={cn(
            "prose prose-sm max-w-none",
            isUser && "text-foreground",
            isSystem && "text-muted-foreground"
          )}
        >
          {message.content}
          {isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse rounded-sm" />
          )}
        </div>

        {/* Tool Calls */}
        {message.metadata?.toolCalls &&
          message.metadata.toolCalls.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {message.metadata.toolCalls.map((tool, idx) => (
                <Badge
                  key={idx}
                  variant={
                    tool.status === "failed" ? "destructive" : "secondary"
                  }
                  className="text-xs"
                >
                  {tool.name}
                  {tool.status === "running" && (
                    <Loader2 className="ml-1 h-2 w-2 animate-spin" />
                  )}
                </Badge>
              ))}
            </div>
          )}
      </div>
    </div>
  );
}
