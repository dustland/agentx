"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Pause,
  Play,
  Share2,
  MoreHorizontal,
  Loader2,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { TaskStatus } from "@/types/chat";
import { cn } from "@/lib/utils";

interface ChatHeaderProps {
  taskName: string;
  taskStatus: TaskStatus;
  onPauseResume: () => void;
  onShare: () => void;
  onMoreActions: () => void;
  canPause?: boolean;
}

export function ChatHeader({
  taskName,
  taskStatus,
  onPauseResume,
  onShare,
  onMoreActions,
  canPause = true,
}: ChatHeaderProps) {
  const getStatusIcon = () => {
    switch (taskStatus) {
      case "running":
        return <Loader2 className="h-3 w-3 animate-spin" />;
      case "completed":
        return <CheckCircle2 className="h-3 w-3" />;
      case "error":
        return <XCircle className="h-3 w-3" />;
      default:
        return null;
    }
  };

  const getStatusColor = () => {
    switch (taskStatus) {
      case "running":
        return "bg-blue-500";
      case "pending":
        return "bg-yellow-500";
      case "completed":
        return "bg-green-500";
      case "error":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="flex items-center justify-between p-4 border-b">
      {/* Left: Task Info */}
      <div className="flex items-center gap-3">
        <h2 className="font-semibold text-lg">{taskName}</h2>
        <Badge
          className={cn("capitalize text-xs", getStatusColor(), "text-white")}
        >
          {getStatusIcon()}
          <span className="ml-1">{taskStatus}</span>
        </Badge>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-1">
        {canPause && (
          <Button
            size="icon"
            variant="ghost"
            onClick={onPauseResume}
            disabled={taskStatus !== "running"}
            className="h-8 w-8"
          >
            {taskStatus === "running" ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>
        )}

        <Button
          size="icon"
          variant="ghost"
          onClick={onShare}
          className="h-8 w-8"
        >
          <Share2 className="h-4 w-4" />
        </Button>

        <Button
          size="icon"
          variant="ghost"
          onClick={onMoreActions}
          className="h-8 w-8"
        >
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
