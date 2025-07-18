"use client";

import React, { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import {
  Home,
  Plus,
  Monitor,
  Search,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  MoreHorizontal,
  Trash2,
  Archive,
  Star,
  Pin,
  PinOff,
  Moon,
  Sun,
  Loader2,
  Filter,
  BookOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import Image from "next/image";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { useTheme } from "next-themes";
import { useAgentXAPI } from "@/lib/api-client";
import { Task as TaskResponse } from "@/types/agentx";
import { useUser } from "@/contexts/user-context";
import { User as UserIcon, LogOut } from "lucide-react";
import { UserAvatar } from "@/components/ui/user-avatar";
import { ThemeSwitcher } from "../common/theme-switcher";

interface SidebarProps {
  className?: string;
  isFloating?: boolean;
  onFloatingChange?: (floating: boolean) => void;
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case "running":
      return <AlertCircle className="h-3 w-3 text-blue-500" />;
    case "completed":
      return <CheckCircle className="h-3 w-3 text-green-500" />;
    case "failed":
      return <XCircle className="h-3 w-3 text-red-500" />;
    case "pending":
      return <Clock className="h-3 w-3 text-yellow-500" />;
    default:
      return <Clock className="h-3 w-3 text-gray-500" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case "running":
      return "border-l-blue-500";
    case "completed":
      return "border-l-green-500";
    case "failed":
      return "border-l-red-500";
    case "pending":
      return "border-l-yellow-500";
    default:
      return "border-l-gray-500";
  }
};

const formatTimeAgo = (date: Date) => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

  if (diffMins < 60) {
    return `${diffMins}m ago`;
  } else {
    return `${diffHours}h ago`;
  }
};

export function Sidebar({
  className,
  isFloating = false,
  onFloatingChange,
}: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const { user, logout } = useUser();
  const apiClient = useAgentXAPI();
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [isHovered, setIsHovered] = useState(false);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isPinned, setIsPinned] = useState(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("sidebar-pinned");
      return stored !== null ? stored === "true" : !isFloating;
    }
    return !isFloating;
  });

  // Sync isPinned with isFloating prop only on initial mount
  useEffect(() => {
    // Only sync if the internal state differs from the prop
    if (isPinned === isFloating) {
      setIsPinned(!isFloating);
    }
  }, [isFloating]);

  const currentTaskId = pathname.match(/\/x\/([^\/]+)/)?.[1];

  // Load tasks from API
  useEffect(() => {
    const loadTasks = async () => {
      try {
        setIsLoading(true);
        console.log("Loading tasks from API...");
        const response = await apiClient.getTasks();
        console.log("Tasks response:", response);
        setTasks(response.tasks || []);
      } catch (error) {
        console.error("Failed to load tasks:", error);
        setTasks([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadTasks();

    // Refresh tasks every 10 seconds
    const interval = setInterval(loadTasks, 10000);
    return () => clearInterval(interval);
  }, []);

  const filteredTasks = tasks.filter((task) => {
    if (statusFilter === "all") return true;
    return task.status === statusFilter;
  });

  // Count tasks by status
  const statusCounts = {
    all: tasks.length,
    running: tasks.filter((t) => t.status === "running").length,
    completed: tasks.filter((t) => t.status === "completed").length,
    failed: tasks.filter((t) => t.status === "failed").length,
  };

  // Only notify parent when user manually changes the pin state
  const handlePinToggle = () => {
    const newPinnedState = !isPinned;
    setIsPinned(newPinnedState);
    if (onFloatingChange) {
      onFloatingChange(!newPinnedState);
    }
    localStorage.setItem("sidebar-pinned", newPinnedState.toString());
  };

  const sidebarWidth = "w-72";
  const shouldShow = isPinned || isHovered;

  return (
    <>
      {/* Hover trigger area when unpinned */}
      {!isPinned && (
        <div
          className="fixed left-0 top-0 w-4 h-full z-40"
          onMouseEnter={() => setIsHovered(true)}
        />
      )}

      <div
        className={cn(
          "bg-card flex flex-col transition-all duration-300",
          sidebarWidth,
          isPinned
            ? "relative h-full border-r"
            : "fixed left-2 top-2 bottom-2 z-50 shadow-xl rounded-lg border h-[calc(100vh-1rem)]",
          !isPinned && !isHovered
            ? "-translate-x-[calc(100%+1rem)]"
            : "translate-x-0",
          className
        )}
        onMouseLeave={() => !isPinned && setIsHovered(false)}
      >
        {/* Header */}
        <div className="p-3">
          <div className="flex items-center justify-between mb-3">
            <Link href="/" className="flex items-center gap-2">
              <Image
                src="/logo.png"
                alt="AgentX"
                width={20}
                height={20}
                className="object-contain"
              />
              <span className="font-semibold text-sm">
                Agent<span className="text-primary">X</span>
              </span>
            </Link>
            <div className="flex items-center gap-1">
              <Button
                size="sm"
                variant="ghost"
                className="h-7 w-7 p-0"
                onClick={handlePinToggle}
                title={isPinned ? "Float sidebar" : "Pin sidebar"}
              >
                {isPinned ? (
                  <PinOff className="h-3 w-3" />
                ) : (
                  <Pin className="h-3 w-3" />
                )}
              </Button>
            </div>
          </div>

          <Button
            className="w-full gap-2"
            size="sm"
            variant="outline"
            onClick={() => router.push("/")}
          >
            <Plus className="h-4 w-4" />
            New Task
          </Button>
        </div>

        {/* Status Filters */}
        <div className="px-3 pb-3">
          <ToggleGroup
            type="single"
            value={statusFilter}
            onValueChange={setStatusFilter}
            className="w-full"
          >
            <ToggleGroupItem value="all" className="flex-1 h-7 text-xs px-2">
              All ({statusCounts.all})
            </ToggleGroupItem>
            <ToggleGroupItem
              value="running"
              className="flex-1 h-7 text-xs px-1"
            >
              <AlertCircle className="h-3 w-3 mr-0.5" />
              {statusCounts.running}
            </ToggleGroupItem>
            <ToggleGroupItem
              value="completed"
              className="flex-1 h-7 text-xs px-1"
            >
              <CheckCircle className="h-3 w-3 mr-0.5" />
              {statusCounts.completed}
            </ToggleGroupItem>
            <ToggleGroupItem value="failed" className="flex-1 h-7 text-xs px-1">
              <XCircle className="h-3 w-3 mr-0.5" />
              {statusCounts.failed}
            </ToggleGroupItem>
          </ToggleGroup>
        </div>

        {/* Task List */}
        <ScrollArea className="flex-1 min-h-0">
          <div className="p-2 space-y-1">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              </div>
            ) : filteredTasks.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p className="text-xs">No tasks found</p>
              </div>
            ) : (
              filteredTasks.map((task) => {
                const isActive = currentTaskId === task.task_id;
                const createdAt = new Date(task.created_at);

                return (
                  <div
                    key={task.task_id}
                    className={cn(
                      "group relative p-2 rounded-lg cursor-pointer transition-colors border-l-2",
                      getStatusColor(task.status),
                      isActive
                        ? "bg-accent text-accent-foreground"
                        : "hover:bg-accent/50"
                    )}
                    onClick={() => router.push(`/x/${task.task_id}`)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          {getStatusIcon(task.status)}
                          <span className="text-xs font-medium truncate">
                            {task.task_description || "Untitled Task"}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground line-clamp-2 mb-1">
                          {task.config_path
                            ? task.config_path
                                .replace(/^.*\//, "")
                                .replace(/\.(yaml|yml)$/, "")
                            : task.status === "completed"
                            ? "Task completed"
                            : task.status === "failed"
                            ? "Task failed"
                            : task.status === "running"
                            ? "Task in progress"
                            : "Task pending"}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-muted-foreground">
                            {formatTimeAgo(createdAt)}
                          </span>
                          <Badge variant="outline" className="text-xs">
                            {task.task_id}
                          </Badge>
                        </div>
                      </div>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreHorizontal className="h-3 w-3" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-40">
                          <DropdownMenuItem>
                            <Star className="h-3 w-3 mr-2" />
                            Favorite
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Archive className="h-3 w-3 mr-2" />
                            Archive
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={async (e) => {
                              e.stopPropagation();
                              try {
                                await apiClient.deleteTask(task.task_id);
                                // Refresh tasks
                                const response = await apiClient.getTasks();
                                setTasks(response.tasks || []);
                              } catch (error) {
                                console.error("Failed to delete task:", error);
                              }
                            }}
                          >
                            <Trash2 className="h-3 w-3 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </ScrollArea>

        {/* Footer */}
        <div className="p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {user && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-9 w-9 p-0"
                      title="User menu"
                    >
                      <UserAvatar username={user.username} size="md" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="start" className="w-56">
                    <div className="px-2 py-1.5 flex items-center gap-2">
                      <UserAvatar username={user.username} size="sm" />
                      <div>
                        <p className="text-sm font-medium">{user.username}</p>
                        <p className="text-xs text-muted-foreground">
                          {user.email || "No email"}
                        </p>
                      </div>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      onClick={logout}
                      className="text-destructive"
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
              <span className="text-xs text-muted-foreground">
                {filteredTasks.length} tasks
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Link href="/observability">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 w-7 p-0"
                  title="Monitor"
                >
                  <Monitor className="h-3 w-3" />
                </Button>
              </Link>
              <Link
                href="https://dustland.github.io/agentx/docs"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 w-7 p-0"
                  title="Documentation"
                >
                  <BookOpen className="h-3 w-3" />
                </Button>
              </Link>
              <ThemeSwitcher />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
