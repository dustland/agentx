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
    status?: "streaming" | "complete" | "failed";
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
      className={cn(
        "group relative",
        isUser ? "flex justify-end" : "flex justify-start"
      )}
    >
      <div
        className={cn(
          "relative max-w-[85%] md:max-w-[75%] lg:max-w-[65%]",
          "bg-card rounded-xl border border-border",
          "px-4 py-3",
          "transition-all duration-200",
          "hover:shadow-sm",
          isStreaming && "border-primary/20",
          message.status === "failed" && "border-destructive/20"
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
            <span className="inline-flex items-center ml-2">
              <span className="w-1.5 h-4 bg-current rounded-sm animate-pulse" />
              <span className="w-1.5 h-4 bg-current rounded-sm animate-pulse animation-delay-150 ml-0.5" />
              <span className="w-1.5 h-4 bg-current rounded-sm animate-pulse animation-delay-300 ml-0.5" />
            </span>
          )}
        </p>

        {/* Tool Usage */}
        {message.metadata?.toolCalls && message.metadata.toolCalls.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {message.metadata.toolCalls.map((tool: any, idx: number) => (
              <div
                key={idx}
                className={cn(
                  "inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs",
                  "bg-muted text-muted-foreground",
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
              "absolute -bottom-8 right-0 flex items-center gap-1",
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
                  <Check className="h-3 w-3 mr-1" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3 mr-1" />
                  Copy
                </>
              )}
            </Button>
            {message.status === "failed" && onRetry && (
              <Button
                variant="ghost"
                size="sm"
                className="h-7 px-2 text-xs"
                onClick={onRetry}
              >
                <RotateCcw className="h-3 w-3 mr-1" />
                Retry
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}