"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  PlayIcon,
  PauseIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  RefreshCwIcon,
  TrashIcon,
} from "lucide-react";
import { useAgentXAPI } from "@/lib/api-client";
import { Task as TaskResponse } from "@/types/agentx";
import { formatDate } from "@/lib/utils";

interface TaskListProps {
  onTaskSelect?: (task: TaskResponse) => void;
  selectedTaskId?: string;
}

export function TaskList({ onTaskSelect, selectedTaskId }: TaskListProps) {
  const apiClient = useAgentXAPI();
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getTasks();
      setTasks(response.tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
    // Refresh every 5 seconds
    const interval = setInterval(loadTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <RefreshCwIcon className="w-4 h-4 animate-spin" />;
      case "completed":
        return <CheckCircleIcon className="w-4 h-4" />;
      case "failed":
        return <XCircleIcon className="w-4 h-4" />;
      case "pending":
        return <ClockIcon className="w-4 h-4" />;
      default:
        return <ClockIcon className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running":
        return "bg-blue-500";
      case "completed":
        return "bg-green-500";
      case "failed":
        return "bg-red-500";
      case "pending":
        return "bg-yellow-500";
      default:
        return "bg-gray-500";
    }
  };

  const handleDelete = async (taskId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient.deleteTask(taskId);
      await loadTasks();
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  };

  if (loading && tasks.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <RefreshCwIcon className="w-8 h-8 animate-spin mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">Loading tasks...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 dark:border-red-800">
        <CardContent className="p-8 text-center">
          <XCircleIcon className="w-8 h-8 mx-auto mb-4 text-red-500" />
          <p className="text-red-500">{error}</p>
          <Button
            onClick={loadTasks}
            variant="outline"
            size="sm"
            className="mt-4"
          >
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (tasks.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground">
            No tasks yet. Create one to get started!
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle>Tasks</CardTitle>
          <Button size="sm" variant="ghost" onClick={loadTasks}>
            <RefreshCwIcon className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[600px]">
          <div className="space-y-2 p-4">
            {tasks.map((task) => (
              <Card
                key={task.task_id}
                className={`cursor-pointer transition-colors hover:bg-accent ${
                  selectedTaskId === task.task_id ? "ring-2 ring-primary" : ""
                }`}
                onClick={() => onTaskSelect?.(task)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-2 h-2 rounded-full ${getStatusColor(
                          task.status
                        )}`}
                      />
                      <span className="font-medium text-sm">
                        Task {task.task_id.slice(0, 8)}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={
                          task.status === "completed"
                            ? "default"
                            : task.status === "failed"
                            ? "destructive"
                            : task.status === "running"
                            ? "secondary"
                            : "outline"
                        }
                      >
                        <span className="flex items-center gap-1">
                          {getStatusIcon(task.status)}
                          {task.status}
                        </span>
                      </Badge>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={(e) => handleDelete(task.task_id, e)}
                      >
                        <TrashIcon className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>

                  <div className="text-xs text-muted-foreground">
                    <p>Created: {formatDate(new Date(task.created_at))}</p>
                    {task.completed_at && (
                      <p>
                        Completed: {formatDate(new Date(task.completed_at))}
                      </p>
                    )}
                  </div>

                  {task.error && (
                    <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 rounded text-xs text-red-600 dark:text-red-400">
                      {task.error}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
