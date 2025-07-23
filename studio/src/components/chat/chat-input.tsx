"use client";

import React, { useRef, useEffect, useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { SendButton } from "./send-button";

interface ChatInputProps {
  onSendMessage: (message: string, mode?: "agent" | "chat") => void;
  onStop?: () => void;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
  taskStatus?: string;
  hasPlan?: boolean;
}

export function ChatInput({
  onSendMessage,
  onStop,
  isLoading = false,
  disabled = false,
  placeholder = "Type a message...",
  taskStatus,
  hasPlan = false,
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const [isComposing, setIsComposing] = useState(false);
  const [mode, setMode] = useState<"agent" | "chat">("agent");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    // Allow sending empty message if there's a plan
    if ((input.trim() || hasPlan) && !isComposing && !isLoading && !disabled) {
      onSendMessage(input.trim() || "", mode);
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative mx-auto w-full max-w-3xl px-3 pb-3">
      <div className="relative">
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={() => setIsComposing(true)}
          onCompositionEnd={() => setIsComposing(false)}
          placeholder={hasPlan && mode === "agent"
            ? "Press Enter or click Send to continue plan execution..."
            : mode === "agent" 
            ? "Describe a task for agents to complete..." 
            : "Type a message..."}
          disabled={disabled || isLoading}
          className={cn(
            "w-full resize-none rounded-2xl bg-background",
            "pl-4 pr-12 pt-[14px] pb-[50px]",
            "min-h-[80px] max-h-[200px]",
            "placeholder:text-muted-foreground/60",
            "transition-all duration-200",
            "scrollbar-hide hover:scrollbar-default",
            disabled && "opacity-50 cursor-not-allowed",
            // Override all border and focus styles
            "[&]:border [&]:border-gray-300 dark:[&]:border-gray-700",
            "[&:hover]:border-gray-400 dark:[&:hover]:border-gray-600",
            "[&:focus]:border-gray-400 dark:[&:focus]:border-gray-600",
            "[&:focus]:outline-none [&:focus]:ring-0",
            "[&:focus-visible]:outline-none [&:focus-visible]:ring-0 [&:focus-visible]:ring-offset-0"
          )}
          style={{
            overflowY: input.split('\n').length > 3 ? 'auto' : 'hidden'
          }}
          rows={1}
        />

        {/* Mode toggle - bottom left inside textarea */}
        <div className="absolute left-3 bottom-2">
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => setMode("agent")}
              className={cn(
                "px-2.5 py-1 text-xs rounded-lg transition-all border",
                mode === "agent" 
                  ? "text-foreground font-medium bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600" 
                  : "text-muted-foreground hover:text-foreground hover:bg-gray-100 dark:hover:bg-gray-800 border-transparent"
              )}
            >
              Agent
            </button>
            <button
              type="button"
              onClick={() => setMode("chat")}
              className={cn(
                "px-2.5 py-1 text-xs rounded-lg transition-all border",
                mode === "chat" 
                  ? "text-foreground font-medium bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600" 
                  : "text-muted-foreground hover:text-foreground hover:bg-gray-100 dark:hover:bg-gray-800 border-transparent"
              )}
            >
              Chat
            </button>
          </div>
        </div>

        {/* Submit/Stop Button */}
        <SendButton
          isLoading={isLoading}
          disabled={!input.trim() && !isLoading && !hasPlan}
          onClick={handleSubmit}
          onStop={onStop}
          size="sm"
          className="absolute right-2 bottom-2"
        />
      </div>
    </div>
  );
}
