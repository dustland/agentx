"use client";

import React, { useRef, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Paperclip, ArrowUp, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
  taskStatus?: string;
}

export function ChatInput({
  onSendMessage,
  isLoading = false,
  disabled = false,
  placeholder = "Type a message...",
  taskStatus,
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    if (input.trim() && !isComposing && !isLoading && !disabled) {
      onSendMessage(input.trim());
      setInput("");
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const getStatusMessage = () => {
    if (taskStatus === "running") return "AI is processing...";
    if (taskStatus === "paused") return "Task paused";
    if (taskStatus === "completed") return "Task completed";
    if (taskStatus === "error") return "Error occurred";
    return null;
  };

  const statusMessage = getStatusMessage();

  return (
    <div className="relative mx-auto w-full max-w-3xl px-3 pb-3">
      <div className="relative">
        {/* Textarea with integrated buttons */}
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={() => setIsComposing(true)}
          onCompositionEnd={() => setIsComposing(false)}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          className={cn(
            "w-full resize-none rounded-2xl border bg-background",
            "pl-12 pr-12 py-3",
            "min-h-[52px] max-h-[200px]",
            "placeholder:text-muted-foreground/60",
            "focus:outline-none focus:border-primary/50 focus-visible:ring-0 focus-visible:ring-offset-0",
            "transition-colors duration-200",
            "scrollbar-thin scrollbar-thumb-border",
            disabled && "opacity-50 cursor-not-allowed"
          )}
          rows={1}
        />

        {/* Attachment Button */}
        <Button
          size="icon"
          variant="ghost"
          disabled={disabled || isLoading}
          className="absolute left-2 bottom-2 h-8 w-8 rounded-full hover:bg-accent"
        >
          <Paperclip className="h-4 w-4" />
        </Button>

        {/* Submit Button */}
        <Button
          size="icon"
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading || disabled}
          className={cn(
            "absolute right-2 bottom-2 h-8 w-8 rounded-full",
            "transition-all duration-200",
            input.trim() && !isLoading && !disabled
              ? "bg-primary hover:bg-primary/90 text-primary-foreground"
              : "bg-muted text-muted-foreground hover:bg-muted"
          )}
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <ArrowUp className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Status Message */}
      {statusMessage && (
        <div className="mt-2 text-center">
          <span className="text-xs text-muted-foreground flex items-center justify-center gap-1">
            {taskStatus === "running" && (
              <Loader2 className="h-3 w-3 animate-spin" />
            )}
            {statusMessage}
          </span>
        </div>
      )}
    </div>
  );
}
