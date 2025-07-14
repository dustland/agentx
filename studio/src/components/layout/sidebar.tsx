"use client";

import { cn } from "@/lib/utils";
import {
  Bot,
  Workflow,
  Library,
  Monitor,
  MessageSquare,
  Settings,
  Plus,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Image from "next/image";

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
}

const navigationItems = [
  {
    id: "taskspace",
    label: "Agent Taskspace",
    icon: Bot,
    description: "Manage and interact with your AI agents",
    badge: null,
  },
  {
    id: "orchestrator",
    label: "Task Orchestrator",
    icon: Workflow,
    description: "Plan and execute multi-agent tasks",
    badge: null,
  },
  {
    id: "conversations",
    label: "Conversations",
    icon: MessageSquare,
    description: "Chat history and agent interactions",
    badge: "3",
  },
  {
    id: "library",
    label: "Agent Library",
    icon: Library,
    description: "Browse and install agent templates",
    badge: null,
  },
  {
    id: "monitor",
    label: "System Monitor",
    icon: Monitor,
    description: "Performance metrics and system health",
    badge: null,
  },
];

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
  return (
    <div className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-slate-900 dark:text-slate-100">
              AgentX Studio
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Multi-Agent Platform
            </p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
        <Button className="w-full justify-start gap-2" size="sm">
          <Plus className="w-4 h-4" />
          New Task
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors",
                "hover:bg-slate-100 dark:hover:bg-slate-800",
                isActive &&
                  "bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400"
              )}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm truncate">{item.label}</div>
                <div className="text-xs text-slate-500 dark:text-slate-400 truncate">
                  {item.description}
                </div>
              </div>
              {item.badge && (
                <Badge variant="secondary" className="text-xs">
                  {item.badge}
                </Badge>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Status */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
          <Activity className="w-4 h-4 text-green-500" />
          <span>System Online</span>
          <div className="ml-auto w-2 h-2 bg-green-500 rounded-full animate-pulse" />
        </div>
      </div>
    </div>
  );
}
