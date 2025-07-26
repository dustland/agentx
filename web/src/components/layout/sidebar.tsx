"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Monitor,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Pin,
  PinOff,
  Loader2,
  BookOpen,
  Home,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import Image from "next/image";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { useUser } from "@/contexts/user-context";
import { LogOut, Settings, HelpCircle, ExternalLink } from "lucide-react";
import { UserAvatar } from "@/components/user-avatar";
import { ThemeSwitcher } from "../theme-switcher";
import { useAppStore } from "@/store/app";
import { useObservability } from "@/hooks/use-observability";
import { Icons } from "../icons";

export interface SidebarItem {
  id: string;
  title: string;
  subtitle?: string;
  status?: "running" | "completed" | "error" | "pending";
  href?: string;
  onClick?: () => void;
  metadata?: {
    timeAgo?: string;
    configPath?: string;
  };
}

interface SidebarProps {
  className?: string;
  title?: string;
  items?: SidebarItem[];
  isActiveItem?: (item: SidebarItem) => boolean;
  children?: React.ReactNode;
  isLoading?: boolean;
  placeholder?: React.ReactNode;
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

const getTimeAgo = (date: Date): string => {
  const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);

  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
};

export function Sidebar({
  className,
  title,
  items,
  isActiveItem,
  children,
  isLoading = false,
  placeholder,
}: SidebarProps) {
  const router = useRouter();
  const { user, logout } = useUser();
  const { sidebarPinned, setSidebarPinned } = useAppStore();
  const { systemHealth } = useObservability();
  const [isHovered, setIsHovered] = useState(false);

  // Handle pin/unpin toggle
  const handlePinToggle = () => {
    setSidebarPinned(!sidebarPinned);
  };

  const sidebarWidth = "w-72";

  // Render main content based on props
  const renderMainContent = () => {
    if (isLoading) {
      return (
        <div className="h-full flex items-center justify-center">
          <div className="flex flex-col items-center justify-center text-center">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground mb-2" />
            <p className="text-xs text-muted-foreground">Loading...</p>
          </div>
        </div>
      );
    }

    if (children) {
      return <ScrollArea className="flex-1 min-h-0">{children}</ScrollArea>;
    }

    if (items && items.length > 0) {
      return (
        <ScrollArea className="flex-1 min-h-0">
          <div className="p-2 space-y-1">
            {items.map((item) => {
              const isActive = isActiveItem ? isActiveItem(item) : false;

              return (
                <div
                  key={item.id}
                  className={cn(
                    "group relative rounded-lg cursor-pointer transition-all duration-200",
                    "border hover:shadow-sm",
                    isActive
                      ? "bg-accent border-accent-foreground/20 shadow-sm"
                      : "bg-card/50 border-border/50 hover:bg-card hover:border-border"
                  )}
                  onClick={
                    item.onClick || (() => item.href && router.push(item.href))
                  }
                >
                  {/* Status indicator bar */}
                  {item.status && (
                    <div
                      className={cn(
                        "absolute left-0 top-0 bottom-0 w-1 rounded-l-lg transition-all",
                        item.status === "running" && "bg-blue-500",
                        item.status === "completed" && "bg-green-500",
                        item.status === "error" && "bg-red-500",
                        item.status === "pending" && "bg-yellow-500"
                      )}
                    />
                  )}

                  <div className="p-3 pl-4">
                    <div className="flex items-start justify-between gap-2 mb-1.5">
                      <div className="flex-1 min-w-0">
                        <h4
                          className={cn(
                            "font-medium text-sm leading-tight line-clamp-2",
                            isActive
                              ? "text-accent-foreground"
                              : "text-foreground"
                          )}
                        >
                          {item.title}
                        </h4>
                        {item.subtitle && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {item.subtitle}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Metadata */}
                    {(item.status || item.metadata) && (
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        {item.status && (
                          <div className="flex items-center gap-1">
                            {getStatusIcon(item.status)}
                            <span className="capitalize">{item.status}</span>
                          </div>
                        )}

                        {item.metadata?.timeAgo && (
                          <>
                            <span className="opacity-40">•</span>
                            <span>{item.metadata.timeAgo}</span>
                          </>
                        )}

                        {item.metadata?.configPath && (
                          <>
                            <span className="opacity-40">•</span>
                            <span
                              className="truncate max-w-[80px]"
                              title={item.metadata.configPath}
                            >
                              {item.metadata.configPath
                                .split("/")
                                .pop()
                                ?.replace(/\.(yaml|yml)$/, "")}
                            </span>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </ScrollArea>
      );
    }

    // Empty state
    return (
      <div className="h-full flex items-center justify-center">
        {placeholder ? (
          placeholder
        ) : (
          <div className="text-center text-muted-foreground">
            <div className="bg-muted/30 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
              <AlertCircle className="h-5 w-5" />
            </div>
            <p className="text-sm font-medium mb-1">No items found</p>
            <p className="text-xs opacity-75">No items to display</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* Hover trigger area when unpinned */}
      {!sidebarPinned && (
        <div
          className="fixed left-0 top-0 w-4 h-full z-40"
          onMouseEnter={() => setIsHovered(true)}
        />
      )}

      <div
        className={cn(
          "bg-card flex flex-col transition-all duration-300",
          sidebarWidth,
          sidebarPinned
            ? "relative h-full border-r flex-shrink-0"
            : "fixed left-2 top-2 bottom-2 z-50 shadow-xl rounded-lg border h-[calc(100vh-1rem)]",
          !sidebarPinned && !isHovered
            ? "-translate-x-[calc(100%+1rem)]"
            : "translate-x-0",
          className
        )}
        onMouseLeave={() => !sidebarPinned && setIsHovered(false)}
      >
        {/* Header */}
        <div className="p-3">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 flex-1 min-w-0">
              <Link href="/" className="flex-shrink-0">
                <Image
                  src="/logo.png"
                  alt="VibeX"
                  width={20}
                  height={20}
                  className="object-contain"
                />
              </Link>
              <div className="flex-1 min-w-0">
                {title ? (
                  <h2 className="font-semibold text-sm leading-tight">
                    {title}
                  </h2>
                ) : (
                  <Link href="/" className="flex items-center">
                    <span className="font-semibold text-sm">
                      Vibe<span className="text-primary">X</span>
                    </span>
                  </Link>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1 flex-shrink-0">
              <Button
                size="sm"
                variant="ghost"
                className="h-7 w-7 p-0"
                onClick={handlePinToggle}
                title={sidebarPinned ? "Float sidebar" : "Pin sidebar"}
              >
                {sidebarPinned ? (
                  <PinOff className="h-3 w-3" />
                ) : (
                  <Pin className="h-3 w-3" />
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        {renderMainContent()}

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
                        href="https://dustland.github.io/vibex/docs"
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
                        href="https://github.com/dustland/vibex"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center"
                      >
                        <Icons.github className="h-4 w-4 mr-2" />
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
                        href="https://github.com/dustland/vibex/issues"
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
                    <div className="px-2 py-1.5 text-xs text-muted-foreground">
                      Version {systemHealth?.version || "loading..."}
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
            </div>
            <div className="flex items-center gap-1">
              <Link href="/">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 w-7 p-0"
                  title="Home"
                >
                  <Home className="h-3 w-3" />
                </Button>
              </Link>
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
                href="https://dustland.github.io/vibex/docs"
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
