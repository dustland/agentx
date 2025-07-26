import React from "react";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  isLoading?: boolean;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  isLoading = false,
  className,
  size = "md",
}: EmptyStateProps) {
  const iconSizes = {
    sm: "h-6 w-6",
    md: "h-8 w-8",
    lg: "h-12 w-12",
  };

  const textSizes = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg",
  };

  const descriptionSizes = {
    sm: "text-xs",
    md: "text-sm",
    lg: "text-base",
  };

  return (
    <div
      className={cn(
        "h-full flex items-center justify-center text-muted-foreground",
        className
      )}
    >
      <div className="text-center max-w-sm mx-auto">
        <Icon
          className={cn(
            iconSizes[size],
            "mx-auto mb-3 opacity-50",
            isLoading && "animate-pulse"
          )}
        />
        <p className={cn("font-medium mb-1", textSizes[size])}>{title}</p>
        {description && (
          <p
            className={cn("opacity-75 leading-relaxed", descriptionSizes[size])}
          >
            {description}
          </p>
        )}
      </div>
    </div>
  );
}
