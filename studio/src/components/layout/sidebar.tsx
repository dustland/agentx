"use client";

import React, { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import {
  Github,
  Plus,
  Monitor,
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
  Loader2,
  BookOpen,
  AlertTriangle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
import { useUser } from "@/contexts/user-context";
import { LogOut, Settings, HelpCircle, ExternalLink } from "lucide-react";
import { UserAvatar } from "@/components/ui/user-avatar";
import { ThemeSwitcher } from "../common/theme-switcher";
import { useTasks } from "@/hooks/use-tasks";

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
    case "error":
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
    case "error":
      return "border-l-red-500";
    case "pending":
      return "border-l-yellow-500";
    default:
      return "border-l-gray-500";
  }
};

export function Sidebar({
  className,
  isFloating = false,
  onFloatingChange,
}: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useUser();
  const { tasks, loading: isLoading, deleteTask } = useTasks();
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [isHovered, setIsHovered] = useState(false);
  const [isPinned, setIsPinned] = useState(!isFloating);

  // Load pinned state from localStorage after mount
  useEffect(() => {
    const stored = localStorage.getItem("sidebar-pinned");
    if (stored !== null) {
      setIsPinned(stored === "true");
    }
  }, []);

  // Sync isPinned with isFloating prop only on initial mount
  useEffect(() => {
    // Only sync if the internal state differs from the prop
    if (isPinned === isFloating) {
      setIsPinned(!isFloating);
    }
  }, [isFloating]);

  const currentTaskId = pathname.match(/\/x\/([^\/]+)/)?.[1];

  const filteredTasks = tasks.filter((task) => {
    if (statusFilter === "all") return true;
    return task.status === statusFilter;
  });

  // Count tasks by status
  const statusCounts = {
    all: tasks.length,
    running: tasks.filter((t) => t.status === "running").length,
    completed: tasks.filter((t) => t.status === "completed").length,
    failed: tasks.filter((t) => t.status === "error").length,
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
        <div className="px-2 pb-2">
          <ToggleGroup
            type="single"
            value={statusFilter}
            onValueChange={setStatusFilter}
            className="w-full border rounded-md bg-muted/20"
          >
            <ToggleGroupItem
              value="all"
              className="flex-1 h-7 text-xs px-1.5 font-medium"
            >
              All ({statusCounts.all})
            </ToggleGroupItem>
            <ToggleGroupItem
              value="running"
              className="flex-1 h-7 text-xs px-1"
            >
              <AlertCircle className="h-2.5 w-2.5 mr-0.5" />
              {statusCounts.running}
            </ToggleGroupItem>
            <ToggleGroupItem
              value="completed"
              className="flex-1 h-7 text-xs px-1"
            >
              <CheckCircle className="h-2.5 w-2.5 mr-0.5" />
              {statusCounts.completed}
            </ToggleGroupItem>
            <ToggleGroupItem value="error" className="flex-1 h-7 text-xs px-1">
              <AlertTriangle className="h-2.5 w-2.5 mr-0.5" />
              {statusCounts.failed}
            </ToggleGroupItem>
          </ToggleGroup>
        </div>

        {/* Task List */}
        <ScrollArea className="flex-1 min-h-0">
          <div className="p-2 space-y-1">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground mb-2" />
                <p className="text-xs text-muted-foreground">
                  Loading tasks...
                </p>
              </div>
            ) : filteredTasks.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <div className="bg-muted/30 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                  <AlertCircle className="h-5 w-5" />
                </div>
                <p className="text-sm font-medium mb-1">No tasks found</p>
                <p className="text-xs opacity-75">
                  Create a new task to get started
                </p>
              </div>
            ) : (
              filteredTasks.map((task, index) => {
                const isActive = currentTaskId === task.id;

                return (
                  <div
                    key={index}
                    className={cn(
                      "group relative rounded-lg cursor-pointer transition-all duration-150 border border-border/30 hover:border-border/60",
                      "bg-card/30 hover:bg-card/60",
                      isActive && "bg-accent/70 border-accent-foreground/30"
                    )}
                    onClick={() => router.push(`/x/${task.id}`)}
                  >
                    {/* Status indicator bar */}
                    <div
                      className={cn(
                        "absolute left-0 top-2 bottom-2 w-0.5 rounded-r-full",
                        getStatusColor(task.status).replace("border-l-", "bg-")
                      )}
                    />

                    <div className="p-2 pl-3">
                      {/* Header with status, title and actions */}
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-1.5 flex-1 min-w-0">
                          <div
                            className={cn(
                              "flex-shrink-0 w-2 h-2 rounded-full",
                              task.status === "running" && "bg-blue-500",
                              task.status === "completed" && "bg-green-500",
                              task.status === "error" && "bg-red-500",
                              task.status === "pending" && "bg-yellow-500"
                            )}
                          />
                          <span className="font-medium text-xs truncate text-foreground">
                            {task.task_description || "Untitled Task"}
                          </span>
                        </div>

                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-4 w-4 p-0 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <MoreHorizontal className="h-2.5 w-2.5" />
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
                                const success = await deleteTask(task.id);
                                if (success) {
                                  // If we deleted the current task, redirect to homepage
                                  if (currentTaskId === task.id) {
                                    router.push("/");
                                  }
                                } else {
                                  console.error("Failed to delete task");
                                }
                              }}
                            >
                              <Trash2 className="h-3 w-3 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>

                      {/* Footer with config and status */}
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span className="truncate flex-1 mr-2">
                          {task.config_path
                            ? task.config_path
                                .replace(/^.*\//, "")
                                .replace(/\.(yaml|yml)$/, "")
                            : task.status === "completed"
                            ? "Completed"
                            : task.status === "error"
                            ? "Error"
                            : task.status === "running"
                            ? "Running"
                            : "Pending"}
                        </span>

                        <span className="font-mono text-xs opacity-60">
                          {task.id.slice(-4)}
                        </span>
                      </div>
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
                      size="icon"
                      className="rounded-full outline-none focus:outline-none focus:ring-0 focus:ring-offset-0"
                      title="User menu"
                    >
                      <UserAvatar username={user.username} size="sm" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="start" className="w-56">
                    <div className="px-2 py-1.5 flex items-center gap-2">
                      <UserAvatar username={user.username} size="md" />
                      <div>
                        <p className="text-sm font-medium">{user.username}</p>
                        <p className="text-xs text-muted-foreground">
                          {user.email || "No email"}
                        </p>
                      </div>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link
                        href="https://dustland.github.io/agentx/docs"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center"
                      >
                        <BookOpen className="h-4 w-4 mr-2" />
                        Documentation
                        <ExternalLink className="h-3 w-3 ml-auto" />
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link
                        href="https://github.com/dustland/agentx"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center"
                      >
                        <Github className="h-4 w-4 mr-2" />
                        GitHub
                        <ExternalLink className="h-3 w-3 ml-auto" />
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link href="/observability" className="flex items-center">
                        <Monitor className="h-4 w-4 mr-2" />
                        Observability
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link href="/settings" className="flex items-center">
                        <Settings className="h-4 w-4 mr-2" />
                        Settings
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link
                        href="https://github.com/dustland/agentx/issues"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center"
                      >
                        <HelpCircle className="h-4 w-4 mr-2" />
                        Help & Support
                        <ExternalLink className="h-3 w-3 ml-auto" />
                      </Link>
                    </DropdownMenuItem>
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
