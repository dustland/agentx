"use client";

import { useMemo } from "react";
import { usePathname } from "next/navigation";
import { Sidebar, SidebarItem } from "@/components/layout/sidebar";
import { useXAgents } from "@/hooks/use-xagent";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

const getTimeAgo = (date: Date): string => {
  const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);

  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
};

export default function TasksLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { xagents, isLoading } = useXAgents();

  // Get current agent ID from URL
  const currentAgentId = pathname.match(/\/agent\/([^\/]+)/)?.[1];

  // Check if we're on the homepage (root path or no specific agent)
  const isHomepage =
    pathname === "/" || pathname === "/agent" || !currentAgentId;

  // Transform XAgents to SidebarItems
  const sidebarItems: SidebarItem[] = useMemo(() => {
    return xagents.map((xagent: any) => ({
      id: xagent.agent_id,
      title: xagent.goal || "Untitled XAgent",
      status: xagent.status as "running" | "completed" | "error" | "pending",
      href: `/agent/${xagent.agent_id}`,
      metadata: {
        timeAgo: xagent.created_at
          ? getTimeAgo(new Date(xagent.created_at))
          : undefined,
        configPath: xagent.config_path,
      },
    }));
  }, [xagents]);

  // Check if item is active
  const isActiveItem = (item: SidebarItem) => item.id === currentAgentId;

  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <Sidebar
        title="XAgents"
        items={sidebarItems}
        isActiveItem={isActiveItem}
        isLoading={isLoading}
        placeholder={
          <div className="text-center text-muted-foreground">
            <div className="bg-muted/30 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
              <Plus className="h-5 w-5" />
            </div>
            <p className="text-sm font-medium mb-1">No XAgents found</p>
            <p className="text-xs opacity-75">
              Create a new XAgent to get started
            </p>
            {!isHomepage && (
              <Button
                size="sm"
                className="mt-3"
                onClick={() => (window.location.href = "/")}
              >
                <Plus className="h-4 w-4 mr-2" />
                New XAgent
              </Button>
            )}
          </div>
        }
      />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative bg-muted">
        {/* Page Content */}
        {children}
      </div>
    </div>
  );
}
