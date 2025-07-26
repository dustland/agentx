"use client";

import React, { useRef, useEffect, useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { SendButton } from "./send-button";
import { Button } from "../ui/button";

interface ChatInputProps {
  onSendMessage: (message: string, mode?: "agent" | "chat") => void;
  onStop?: () => void;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
  allowEmptyMessage?: boolean;
}

export function ChatInput({
  onSendMessage,
  onStop,
  isLoading = false,
  disabled = false,
  placeholder = "Type a message...",
  allowEmptyMessage = false,
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

  const handleSubmit = (e?: React.MouseEvent | React.FormEvent) => {
    // Prevent default form submission if it's a form event
    if (e) {
      e.preventDefault();
    }

    if (
      (input.trim() || allowEmptyMessage) &&
      !isComposing &&
      !isLoading &&
      !disabled
    ) {
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
      <div className="relative group">
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={() => setIsComposing(true)}
          onCompositionEnd={() => setIsComposing(false)}
          placeholder={
            mode === "agent"
              ? allowEmptyMessage
                ? "Type a message or press Send to continue..."
                : "Describe a task for agents to complete..."
              : "Type a message..."
          }
          disabled={disabled || isLoading}
          className={cn(
            "w-full resize-none rounded-2xl bg-background",
            "pl-4 pr-12 pt-[14px] pb-[50px]",
            "min-h-[80px] max-h-[200px]",
            "placeholder:text-muted-foreground/60",
            "transition-all duration-200",
            "scrollbar-hide hover:scrollbar-default",
            disabled && "opacity-50 cursor-not-allowed",
            // Use semantic border colors
            "border border-border",
            "group-hover:border-muted-foreground/50",
            "focus:border-muted-foreground/50",
            "focus:outline-none focus:ring-0 focus:ring-transparent",
            "focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:ring-transparent"
          )}
          style={
            {
              overflowY: input.split("\n").length > 3 ? "auto" : "hidden",
              "--tw-ring-color": "transparent",
              boxShadow: "none",
            } as React.CSSProperties
          }
          rows={1}
        />

        {/* Mode toggle - bottom left inside textarea */}
        <div className="absolute left-3 bottom-2">
          <div className="flex items-center gap-1">
            {["agent", "chat"].map((m) => (
              <Button
                key={m}
                size="sm"
                variant="ghost"
                onClick={() => setMode(m as "agent" | "chat")}
                className={`text-xs h-6 rounded-full transition-all border ${
                  mode === m
                    ? "shadow-sm border-accent"
                    : "border-transparent bg-transparent text-muted-foreground"
                }`}
              >
                <span className="capitalize">{m}</span>
              </Button>
            ))}
          </div>
        </div>

        {/* Submit/Stop Button */}
        <SendButton
          isLoading={isLoading}
          disabled={!input.trim() && !isLoading && !allowEmptyMessage}
          onClick={handleSubmit}
          onStop={onStop}
          size="sm"
          type="button"
          className="absolute right-2 bottom-2"
        />
      </div>
    </div>
  );
}
