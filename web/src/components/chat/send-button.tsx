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

export const SendButton = React.forwardRef<HTMLButtonElement, SendButtonProps>((
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
      button: "h-8 w-8",
      icon: "h-4 w-4",
      square: "h-3 w-3",
    },
    md: {
      button: "h-10 w-10",
      icon: "h-5 w-5",
      square: "h-4 w-4",
    },
    lg: {
      button: "h-12 w-12",
      icon: "h-6 w-6",
      square: "h-5 w-5",
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

  return (
    <Button
      ref={ref}
      variant="default"
      size="icon"
      type={type}
      disabled={disabled && !isLoading}
      className={cn(
        "relative rounded-full transition-all duration-200",
        config.button,
        disabled && !isLoading
          ? "bg-muted text-muted-foreground hover:bg-muted"
          : "bg-primary text-primary-foreground hover:bg-primary/90",
        className
      )}
      aria-label={ariaLabel || (isLoading ? "Stop generating" : "Send message")}
      onClick={handleClick}
    >
      {/* Loading spinner - animated border */}
      {isLoading && (
        <div className="absolute inset-0 rounded-full overflow-hidden">
          <div className="absolute inset-0 rounded-full border-2 border-primary/20" />
          <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-primary animate-spin" />
        </div>
      )}

      {/* Center content */}
      <div className="relative z-10 flex items-center justify-center">
        {isLoading ? (
          <Square className={cn("shrink-0 fill-current", config.square)} />
        ) : (
          <ArrowUp className={cn("shrink-0", config.icon)} />
        )}
      </div>
    </Button>
  );
});

SendButton.displayName = "SendButton";