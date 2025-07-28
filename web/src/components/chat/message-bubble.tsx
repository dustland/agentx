"use client";

import React, { useState } from "react";
import { Check, Copy, Loader2, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { MessageParts } from "./message-parts";
import { ThinkingIndicator } from "../thinking-indicator";
import ReactMarkdown from "react-markdown";
import type { ChatMessage } from "@/types/chat";

interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
  displayPath?: string;
}

interface MessageBubbleProps {
  message: ChatMessage;
  onRetry?: () => void;
  onArtifactSelect?: ((artifact: Artifact) => void) | null;
}

export function MessageBubble({
  message,
  onRetry,
  onArtifactSelect,
}: MessageBubbleProps) {
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
        "group relative border-b border-border/50 last:border-b-0",
        isUser ? "flex justify-end" : ""
      )}
    >
      <div
        className={cn(
          "relative",
          isUser
            ? [
                "max-w-[85%] md:max-w-[75%] lg:max-w-[65%]",
                "bg-card rounded-xl border border-border",
                "px-4 py-3 mb-4",
                "hover:shadow-sm",
              ]
            : [
                "max-w-full",
                "py-3 pb-4",
              ],
          "transition-all duration-200",
          message.status === "error" && "text-destructive"
        )}
      >
        {/* Content */}
        <div className="text-foreground overflow-hidden min-w-0">
          {/* Show message parts if available */}
          {message.parts && message.parts.length > 0 ? (
            <div className="min-w-0 max-w-full">
              <MessageParts
                parts={message.parts}
                isStreaming={isStreaming}
                onArtifactSelect={onArtifactSelect}
              />
            </div>
          ) : (
            <>
              {/* Fallback to regular content display */}
              {isAssistant ? (
                <div className="markdown-message overflow-hidden min-w-0 max-w-full" style={{ maxWidth: "100%" }}>
                  <ReactMarkdown
                    components={{
                      // Override table to ensure it doesn't break layout
                      table: ({ node, ...props }) => (
                        <div className="overflow-x-auto max-w-full">
                          <table {...props} className="min-w-full" />
                        </div>
                      ),
                      // Override pre to ensure code blocks don't break layout
                      pre: ({ node, ...props }) => (
                        <pre {...props} className="overflow-x-auto max-w-full" />
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="text-sm leading-relaxed whitespace-pre-wrap break-words overflow-x-auto min-w-0 max-w-full">
                  {message.content}
                </div>
              )}
              {/* Only show ThinkingIndicator for messages without parts */}
              {isStreaming && <ThinkingIndicator />}
            </>
          )}
        </div>

        {/* Tool Usage - Only show if no message parts (backward compatibility) */}
        {!message.parts &&
          message.metadata?.toolCalls &&
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

        {/* Action buttons - absolute positioned */}
        {isAssistant && (
          <div className="absolute -top-1 -right-1 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all duration-200">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 bg-background/80 backdrop-blur-sm border"
              onClick={handleCopy}
            >
              {copied ? (
                <Check className="h-3 w-3" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
            {message.status === "error" && onRetry && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 bg-background/80 backdrop-blur-sm border"
                onClick={onRetry}
              >
                <XCircle className="h-3 w-3" />
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
