"use client";

import React, { useRef, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowUp, Loader2 } from "lucide-react";
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

      // Adjust line-height for single line to center text
      const lineCount = input.split("\n").length;
      if (lineCount === 1 && !input.includes("\n")) {
        textareaRef.current.style.lineHeight = "52px";
      } else {
        textareaRef.current.style.lineHeight = "1.5";
      }
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
            "pl-4 pr-12 py-0",
            "min-h-[52px] max-h-[200px]",
            "placeholder:text-muted-foreground/60",
            "focus:outline-none focus:!border-border focus-visible:ring-0 focus-visible:ring-offset-0",
            "transition-colors duration-200",
            "overflow-hidden",
            disabled && "opacity-50 cursor-not-allowed"
          )}
          rows={1}
        />

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
    </div>
  );
}
