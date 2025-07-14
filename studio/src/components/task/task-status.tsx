"use client";

import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle, XCircle, PlayCircle, Clock } from "lucide-react";

type TaskStatus = "pending" | "planning" | "executing" | "running" | "completed" | "failed";

interface TaskStatusProps {
  status: TaskStatus;
}

const statusConfig = {
  pending: {
    label: "Pending",
    icon: Clock,
    variant: "secondary" as const,
  },
  planning: {
    label: "Planning",
    icon: PlayCircle,
    variant: "outline" as const,
  },
  executing: {
    label: "Executing",
    icon: Loader2,
    variant: "default" as const,
  },
  running: {
    label: "Running",
    icon: Loader2,
    variant: "default" as const,
  },
  completed: {
    label: "Completed",
    icon: CheckCircle,
    variant: "secondary" as const,
  },
  failed: {
    label: "Failed",
    icon: XCircle,
    variant: "destructive" as const,
  },
};

export function TaskStatus({ status }: TaskStatusProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className="flex items-center gap-1">
      <Icon
        className={`h-3 w-3 ${status === "executing" || status === "running" ? "animate-spin" : ""}`}
      />
      {config.label}
    </Badge>
  );
}
