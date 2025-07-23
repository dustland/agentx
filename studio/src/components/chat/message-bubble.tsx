"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Copy, Check, RotateCcw, Loader2 } from "lucide-react";

interface MessageBubbleProps {
  message: {
    id: string;
    role: "user" | "assistant" | "system";
    content: string;
    timestamp: Date;
    status?: "streaming" | "complete" | "error";
    metadata?: any;
  };
  onRetry?: () => void;
}

export function MessageBubble({ message, onRetry }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  const isStreaming = message.status === "streaming";

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={cn("group relative", isUser ? "flex justify-end" : "w-full")}
    >
      <div
        className={cn(
          "relative",
          isUser
            ? [
                "max-w-[85%] md:max-w-[75%] lg:max-w-[65%]",
                "bg-card rounded-xl border border-border",
                "px-4 py-3",
                "hover:shadow-sm",
              ]
            : ["w-full", "py-3"],
          "transition-all duration-200",
          message.status === "error" && "text-destructive"
        )}
      >
        {/* Content */}
        <p
          className={cn(
            "text-sm leading-relaxed whitespace-pre-wrap break-words",
            "text-foreground"
          )}
        >
          {message.content}
          {isStreaming && (
            <span className="inline-flex items-center ml-2 space-x-1 streaming-dots">
              <span className="w-1 h-1 bg-current rounded-full" />
              <span className="w-1 h-1 bg-current rounded-full" />
              <span className="w-1 h-1 bg-current rounded-full" />
            </span>
          )}
        </p>

        {/* Tool Usage */}
        {message.metadata?.toolCalls &&
          message.metadata.toolCalls.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {message.metadata.toolCalls.map((tool: any, idx: number) => (
                <div
                  key={idx}
                  className={cn(
                    "inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs",
                    isUser
                      ? "bg-muted text-muted-foreground"
                      : "bg-muted/50 text-muted-foreground",
                    tool.status === "running" && "animate-pulse"
                  )}
                >
                  {tool.status === "running" ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : tool.status === "completed" ? (
                    <Check className="w-3 h-3" />
                  ) : (
                    <span className="w-1.5 h-1.5 rounded-full bg-current" />
                  )}
                  <span>{tool.name}</span>
                </div>
              ))}
            </div>
          )}

        {/* Action buttons */}
        {isAssistant && (
          <div
            className={cn(
              "flex items-center gap-1 mt-2",
              "opacity-0 group-hover:opacity-100 transition-all duration-200"
            )}
          >
            <Button
              variant="ghost"
              size="sm"
              className="h-7 px-2 text-xs"
              onClick={handleCopy}
            >
              {copied ? (
                <>
                  <Check className="h-3 w-3" />
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                </>
              )}
            </Button>
            {message.status === "error" && onRetry && (
              <Button
                variant="ghost"
                size="sm"
                className="h-7 px-2 text-xs"
                onClick={onRetry}
              >
                <RotateCcw className="h-3 w-3" />
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
