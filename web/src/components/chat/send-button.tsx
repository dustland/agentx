import React from "react";
import { ArrowUp, Square } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "../ui/button";

interface SendButtonProps {
  isLoading: boolean;
  disabled?: boolean;
  onClick?: (e: React.MouseEvent) => void;
  onStop?: () => void;
  type?: "button" | "submit";
  className?: string;
  size?: "sm" | "md" | "lg";
  "aria-label"?: string;
}

export const SendButton = React.forwardRef<HTMLButtonElement, SendButtonProps>(
  (
    {
      isLoading,
      disabled,
      onClick,
      onStop,
      type = "submit",
      className,
      size = "md",
      "aria-label": ariaLabel,
    },
    ref
  ) => {
    const sizeConfig = {
      sm: {
        button: "size-8",
        icon: "!size-5", // Force larger size with !important
        square: "!size-4", // Slightly smaller than arrow
      },
      md: {
        button: "size-10",
        icon: "!size-7", // Force larger size with !important
        square: "!size-5", // Slightly smaller than arrow
      },
      lg: {
        button: "size-12",
        icon: "!size-9", // Force larger size with !important
        square: "!size-6", // Slightly smaller than arrow
      },
    };

    const config = sizeConfig[size];

    const handleClick = (e: React.MouseEvent) => {
      if (isLoading && onStop) {
        onStop();
      } else if (onClick) {
        onClick(e);
      }
    };

    const isDisabled = disabled && !isLoading;

    return (
      <Button
        ref={ref}
        variant="default"
        size="icon"
        type={type}
        disabled={isDisabled}
        className={cn(
          "relative rounded-full transition-all duration-200 group",
          config.button,
          // Simplified styling similar to supen
          isDisabled
            ? "bg-secondary text-muted-foreground cursor-not-allowed hover:bg-secondary border border-border shadow-sm"
            : isLoading
            ? "bg-background text-foreground hover:bg-background shadow-sm border-none"
            : "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm hover:shadow-md",
          className
        )}
        aria-label={
          ariaLabel || (isLoading ? "Stop generating" : "Send message")
        }
        onClick={handleClick}
      >
        {/* Rotating 3/4 circle animation for loading state */}
        {isLoading && (
          <div className="absolute inset-0 rounded-full">
            {/* 3/4 circle border that rotates using border technique */}
            <div className="absolute inset-0 rounded-full animate-spin border-2 border-transparent border-t-primary border-r-primary border-b-primary" />
          </div>
        )}

        {/* Center content */}
        <div className="relative z-10 flex items-center justify-center">
          {isLoading ? (
            <Square
              className={cn(
                "shrink-0 fill-current transition-all duration-200",
                config.square,
                "text-primary"
              )}
            />
          ) : (
            <ArrowUp
              className={cn(
                "shrink-0 transition-all duration-200 group-hover:scale-105",
                config.icon
              )}
            />
          )}
        </div>

        {/* Subtle glow effect on hover for active state */}
        {!isDisabled && !isLoading && (
          <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-20 transition-opacity duration-200 bg-white dark:bg-black blur-md" />
        )}
      </Button>
    );
  }
);

SendButton.displayName = "SendButton";
