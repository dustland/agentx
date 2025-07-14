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
  Sun
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
import Image from "next/image";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { useTheme } from "next-themes";

interface TaskSidebarProps {
  className?: string;
  isFloating?: boolean;
  onFloatingChange?: (floating: boolean) => void;
}

// Mock task data - in real app this would come from a store/API
const mockTasks = [
  {
    id: "task_001",
    title: "Market Research Report",
    status: "running",
    createdAt: new Date(Date.now() - 1000 * 60 * 30), // 30 mins ago
    description: "Research and analyze current SaaS market trends",
  },
  {
    id: "task_002", 
    title: "Blog Post Generation",
    status: "completed",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    description: "Create engaging blog content with SEO optimization",
  },
  {
    id: "task_003",
    title: "Code Review Assistant",
    status: "failed", 
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4 hours ago
    description: "Analyze code quality and suggest improvements",
  },
  {
    id: "task_004",
    title: "Customer Data Analysis",
    status: "pending",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 6), // 6 hours ago
    description: "Process and analyze customer behavior data",
  },
];

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

export function TaskSidebar({ 
  className, 
  isFloating = false,
  onFloatingChange 
}: TaskSidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [searchQuery, setSearchQuery] = useState("");
  const [isHovered, setIsHovered] = useState(false);
  const [isPinned, setIsPinned] = useState(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("sidebar-pinned");
      return stored !== null ? stored === "true" : !isFloating;
    }
    return !isFloating;
  });
  
  const currentTaskId = pathname.match(/\/x\/([^\/]+)/)?.[1];
  
  const filteredTasks = mockTasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    if (onFloatingChange) {
      onFloatingChange(!isPinned);
    }
  }, [isPinned, onFloatingChange]);


  useEffect(() => {
    localStorage.setItem("sidebar-pinned", isPinned.toString());
  }, [isPinned]);

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
      
      <div className={cn(
        "bg-card flex flex-col transition-all duration-300",
        sidebarWidth,
        isPinned ? "relative h-full border-r" : "fixed left-2 top-2 bottom-2 z-50 shadow-xl rounded-lg border h-[calc(100vh-1rem)]",
        !isPinned && !isHovered ? "-translate-x-[calc(100%+1rem)]" : "translate-x-0",
        className
      )}
      onMouseLeave={() => !isPinned && setIsHovered(false)}
      >
      {/* Header */}
      <div className="p-3">
        <div className="flex items-center justify-between mb-3">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/logo.png" alt="AgentX" width={20} height={20} className="object-contain" />
            <span className="font-semibold text-sm">
              Agent<span className="text-primary">X</span>
            </span>
          </Link>
          <div className="flex items-center gap-1">
            <Button 
              size="sm" 
              variant="ghost" 
              className="h-7 w-7 p-0"
              onClick={() => setIsPinned(!isPinned)}
              title={isPinned ? "Float sidebar" : "Pin sidebar"}
            >
              {isPinned ? <PinOff className="h-3 w-3" /> : <Pin className="h-3 w-3" />}
            </Button>
          </div>
        </div>
        
        <Link href="/">
          <Button className="w-full gap-2" size="sm">
            <Plus className="h-4 w-4" />
            New Task
          </Button>
        </Link>
      </div>

      {/* Search */}
      <div className="p-3">
        <div className="relative">
          <Search className="absolute left-2 top-2 h-3 w-3 text-muted-foreground" />
          <Input
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-7 h-7 text-xs"
          />
        </div>
      </div>

      {/* Task List */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {filteredTasks.map((task) => {
            const isActive = currentTaskId === task.id;
            
            return (
              <div
                key={task.id}
                className={cn(
                  "group relative p-2 rounded-lg cursor-pointer transition-colors border-l-2",
                  getStatusColor(task.status),
                  isActive 
                    ? "bg-accent text-accent-foreground" 
                    : "hover:bg-accent/50"
                )}
                onClick={() => router.push(`/x/${task.id}`)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {getStatusIcon(task.status)}
                      <span className="text-xs font-medium truncate">
                        {task.title}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2 mb-1">
                      {task.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">
                        {formatTimeAgo(task.createdAt)}
                      </span>
                      <Badge variant="outline" className="text-xs h-4 px-1">
                        {task.status}
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
                      <DropdownMenuItem className="text-destructive">
                        <Trash2 className="h-3 w-3 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">{filteredTasks.length} tasks</span>
          <div className="flex items-center gap-1">
            <Link href="/observability">
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0" title="Monitor">
                <Monitor className="h-3 w-3" />
              </Button>
            </Link>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              title={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
            >
              {theme === 'dark' ? <Sun className="h-3 w-3" /> : <Moon className="h-3 w-3" />}
            </Button>
          </div>
        </div>
      </div>
      </div>
    </>
  );
}