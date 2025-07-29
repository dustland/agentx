"use client";

import React, { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { ChevronRight, ChevronDown, LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export interface GenericMessagePartProps {
  // Layout & Structure
  icon?: LucideIcon;
  iconClassName?: string;
  title: string;
  titleClassName?: string;
  summary?: ReactNode;
  badges?: Array<{
    label: string;
    variant?: "default" | "secondary" | "destructive" | "outline";
    className?: string;
  }>;

  // Status
  status?: "pending" | "running" | "completed" | "failed";
  statusIcon?: ReactNode;
  statusClassName?: string;

  // Expandable content
  expandable?: boolean;
  expanded?: boolean;
  onExpandedChange?: (expanded: boolean) => void;
  expandedContent?: ReactNode;

  // Actions
  actions?: ReactNode;

  // Styling
  variant?: "default" | "success" | "error" | "muted";
  className?: string;
  contentClassName?: string;
}

const variantStyles = {
  default: "border-border bg-card/50 dark:bg-card/30",
  success: "border-green-500/50 bg-green-500/10 dark:bg-green-500/5",
  error: "border-destructive/50 bg-destructive/10 dark:bg-destructive/5",
  muted: "border-border/50 bg-muted/20 dark:bg-muted/10",
};

export function GenericMessagePart({
  icon: Icon,
  iconClassName,
  title,
  titleClassName,
  summary,
  badges,
  status,
  statusIcon,
  statusClassName,
  expandable = false,
  expanded = false,
  onExpandedChange,
  expandedContent,
  actions,
  variant = "default",
  className,
  contentClassName,
}: GenericMessagePartProps) {
  const showExpandButton = expandable && expandedContent;

  return (
    <div
      className={cn(
        "rounded-lg border my-2",
        variantStyles[variant],
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2">
        {/* Status Icon */}
        {statusIcon && (
          <div className={cn("flex-shrink-0", statusClassName)}>
            {statusIcon}
          </div>
        )}

        {/* Tool Icon */}
        {Icon && (
          <div
            className={cn("flex-shrink-0 text-muted-foreground", iconClassName)}
          >
            <Icon className="w-3 h-3" />
          </div>
        )}

        {/* Title */}
        <Badge
          variant="outline"
          className={cn("text-sm font-medium", titleClassName)}
        >
          {title}
        </Badge>

        {/* Summary */}
        {summary && (
          <span className="text-sm text-muted-foreground flex-1 min-w-0 truncate">
            {summary}
          </span>
        )}

        {/* Badges */}
        {badges && badges.length > 0 && (
          <div className="flex items-center gap-1 flex-shrink-0">
            {badges.map((badge, idx) => (
              <Badge
                key={idx}
                variant={badge.variant || "secondary"}
                className={cn("text-xs", badge.className)}
              >
                {badge.label}
              </Badge>
            ))}
          </div>
        )}

        {/* Expand button */}
        {showExpandButton && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0 flex-shrink-0"
            onClick={() => onExpandedChange?.(!expanded)}
          >
            {expanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </Button>
        )}
      </div>

      {/* Actions (like file links) */}
      {actions && (
        <div className="px-3 pb-2 border-t border-border/50">
          <div className="mt-2">{actions}</div>
        </div>
      )}

      {/* Expanded content */}
      {expanded && expandedContent && (
        <div
          className={cn("px-3 pb-3 border-t border-border", contentClassName)}
        >
          <div className="mt-2">{expandedContent}</div>
        </div>
      )}
    </div>
  );
}
