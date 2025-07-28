"use client";

import { useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/sidebar";
import { useXAgents } from "@/hooks/use-xagent";
import {
  Plus,
  Search,
  Filter,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  X,
  MoreHorizontal,
  Edit,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuCheckboxItem,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const getTimeAgo = (date: Date): string => {
  const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);

  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "running":
    case "in_progress":
      return <AlertCircle className="h-3 w-3 text-blue-500" />;
    case "completed":
      return <CheckCircle className="h-3 w-3 text-emerald-500" />;
    case "error":
    case "failed":
      return <XCircle className="h-3 w-3 text-red-500" />;
    case "pending":
      return <Clock className="h-3 w-3 text-slate-400" />;
    default:
      return <Clock className="h-3 w-3 text-slate-400" />;
  }
};

const statusOptions = [
  { value: "all", label: "All" },
  { value: "running", label: "Running" },
  { value: "completed", label: "Completed" },
  { value: "error", label: "Error" },
  { value: "failed", label: "Failed" },
  { value: "pending", label: "Pending" },
];

export default function TasksLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { xagents, isLoading, deleteXAgent, refetch } = useXAgents();

  // Handle refetch with proper error handling
  const handleRefetch = async () => {
    try {
      await refetch();
    } catch (error) {
      console.error("Refetch failed:", error);
    }
  };
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string[]>(["all"]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [agentToDelete, setAgentToDelete] = useState<string | null>(null);

  // Get current agent ID from URL
  const currentAgentId = pathname.match(/\/x\/([^\/]+)/)?.[1];

  // Check if we're on the homepage (root path or no specific agent)
  const isHomepage =
    pathname === "/" || pathname === "/agent" || !currentAgentId;

  // Handle XAgent deletion
  const handleDeleteXAgent = (agentId: string) => {
    setAgentToDelete(agentId);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (!agentToDelete) return;

    deleteXAgent.mutate(agentToDelete, {
      onSuccess: () => {
        // If we're currently viewing the deleted agent, redirect to home
        if (currentAgentId === agentToDelete) {
          router.push("/");
        }
        setDeleteDialogOpen(false);
        setAgentToDelete(null);
      },
      onError: (error) => {
        console.error("Failed to delete XAgent:", error);
        alert("Failed to delete XAgent. Please try again.");
        setDeleteDialogOpen(false);
        setAgentToDelete(null);
      },
    });
  };

  const cancelDelete = () => {
    setDeleteDialogOpen(false);
    setAgentToDelete(null);
  };

  // Filter and search XAgents
  const filteredXAgents = useMemo(() => {
    let filtered = xagents;

    // Apply status filter
    if (!statusFilter.includes("all")) {
      filtered = filtered.filter((xagent: any) =>
        statusFilter.includes(xagent.status)
      );
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((xagent: any) => {
        const title = (xagent.goal || "Untitled XAgent").toLowerCase();
        const configName = xagent.config_path?.toLowerCase() || "";
        return title.includes(query) || configName.includes(query);
      });
    }

    return filtered;
  }, [xagents, searchQuery, statusFilter]);

  const handleXAgentClick = (agentId: string) => {
    router.push(`/x/${agentId}`);
  };

  const activeStatusCount = statusFilter.includes("all")
    ? 0
    : statusFilter.length;

  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <Sidebar
        isLoading={isLoading}
        showRefreshButton={true}
        onRefresh={handleRefetch}
        placeholder={
          <div className="text-center text-muted-foreground">
            <div className="bg-muted/30 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
              <Plus className="h-5 w-5" />
            </div>
            <p className="text-sm font-medium mb-1">No XAgents found</p>
            <p className="text-xs opacity-75 mb-4">
              {isHomepage
                ? "Enter a message or choose a sample goal to get started"
                : "Create your first XAgent to get started"}
            </p>
            {!isHomepage && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => (window.location.href = "/")}
              >
                <Plus className="h-4 w-4" />
                New XAgent
              </Button>
            )}
          </div>
        }
      >
        {xagents.length > 0 && (
          <>
            {/* Filters */}
            <div className="flex items-center w-full gap-2 p-2">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-3 w-3 text-muted-foreground" />
                <Input
                  placeholder="Search XAgents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-7 h-8 text-xs placeholder:text-xs"
                />
                {searchQuery ? (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-3 text-xs absolute right-0 top-1/2 transform -translate-y-1/2"
                    onClick={() => {
                      setSearchQuery("");
                      setStatusFilter(["all"]);
                    }}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                ) : (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="p-1 h-3 w-3 absolute right-2 top-1/2 transform -translate-y-1/2 text-muted-foreground"
                      >
                        <Filter className="h-3 w-3" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="start" className="w-40">
                      {statusOptions.map((option) => (
                        <DropdownMenuCheckboxItem
                          key={option.value}
                          className="cursor-pointer hover:bg-muted"
                          checked={statusFilter.includes(option.value)}
                          onCheckedChange={(checked) => {
                            if (option.value === "all") {
                              setStatusFilter(checked ? ["all"] : []);
                            } else {
                              setStatusFilter((prev) => {
                                const newFilter = prev.filter(
                                  (f) => f !== "all"
                                );
                                if (checked) {
                                  return [...newFilter, option.value];
                                } else {
                                  const filtered = newFilter.filter(
                                    (f) => f !== option.value
                                  );
                                  return filtered.length === 0
                                    ? ["all"]
                                    : filtered;
                                }
                              });
                            }
                          }}
                        >
                          {option.label}
                        </DropdownMenuCheckboxItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </div>
            </div>

            {/* XAgents List */}
            <ScrollArea className="flex-1">
              <div className="p-2 space-y-1">
                {filteredXAgents.map((xagent: any) => {
                  const isActive = xagent.xagent_id === currentAgentId;

                  return (
                    <div
                      key={xagent.xagent_id}
                      className={cn(
                        "group relative rounded-lg cursor-pointer transition-all duration-200",
                        "border overflow-hidden",
                        isActive
                          ? "bg-gradient-to-br from-accent/80 to-accent border-accent-foreground/20"
                          : "bg-gradient-to-br from-card/80 to-card/90 border-border/50 hover:from-card hover:to-card hover:border-border"
                      )}
                      onClick={() => handleXAgentClick(xagent.xagent_id)}
                    >
                      {/* Status indicator bar */}
                      {xagent.status && (
                        <div
                          className={cn(
                            "absolute left-0 top-0 bottom-0 w-1 rounded-l-lg transition-all",
                            (xagent.status === "running" ||
                              xagent.status === "in_progress") &&
                              "bg-gradient-to-b from-blue-500 to-blue-600",
                            xagent.status === "completed" &&
                              "bg-gradient-to-b from-emerald-500 to-emerald-600",
                            (xagent.status === "error" ||
                              xagent.status === "failed") &&
                              "bg-gradient-to-b from-red-500 to-red-600",
                            xagent.status === "pending" &&
                              "bg-gradient-to-b from-slate-400 to-slate-500"
                          )}
                        />
                      )}

                      <div className="p-3 pl-4">
                        <div className="flex items-start justify-between gap-2 mb-1.5">
                          <div className="flex-1 min-w-0">
                            <h4
                              className={cn(
                                "font-medium text-sm leading-tight line-clamp-1",
                                isActive
                                  ? "text-accent-foreground"
                                  : "text-foreground"
                              )}
                            >
                              {xagent.goal || "Untitled XAgent"}
                            </h4>
                          </div>
                        </div>

                        {/* Metadata */}
                        <div className="flex items-center justify-between gap-3 text-xs text-muted-foreground">
                          <div className="flex items-center gap-3">
                            {xagent.status && (
                              <div className="flex items-center gap-1">
                                {getStatusIcon(xagent.status)}
                                <span
                                  className={cn(
                                    "capitalize text-xs font-medium px-1.5 py-0.5 rounded",
                                    (xagent.status === "running" ||
                                      xagent.status === "in_progress") &&
                                      "bg-blue-100 text-blue-700 dark:bg-blue-950/30 dark:text-blue-300",
                                    xagent.status === "completed" &&
                                      "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300",
                                    (xagent.status === "error" ||
                                      xagent.status === "failed") &&
                                      "bg-red-100 text-red-700 dark:bg-red-950/30 dark:text-red-300",
                                    xagent.status === "pending" &&
                                      "bg-slate-100 text-slate-700 dark:bg-slate-950/30 dark:text-slate-300"
                                  )}
                                >
                                  {xagent.status === "in_progress"
                                    ? "running"
                                    : xagent.status.replace("_", " ")}
                                </span>
                              </div>
                            )}

                            {xagent.created_at && (
                              <>
                                <span className="opacity-40">•</span>
                                <span>
                                  {getTimeAgo(new Date(xagent.created_at))}
                                </span>
                              </>
                            )}

                            {xagent.config_path && (
                              <>
                                <span className="opacity-40">•</span>
                                <span
                                  className="truncate max-w-[80px]"
                                  title={xagent.config_path}
                                >
                                  {xagent.config_path
                                    .split("/")
                                    .pop()
                                    ?.replace(/\.(yaml|yml)$/, "")}
                                </span>
                              </>
                            )}
                          </div>

                          {/* Action Menu */}
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
                            <DropdownMenuContent
                              side="bottom"
                              align="start"
                              className="w-40"
                            >
                              <DropdownMenuItem
                                className="cursor-pointer"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  // TODO: Implement rename functionality
                                  console.log(
                                    "Rename XAgent:",
                                    xagent.xagent_id
                                  );
                                }}
                              >
                                <Edit className="h-3 w-3" />
                                Rename
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                className="cursor-pointer text-destructive"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteXAgent(xagent.xagent_id);
                                }}
                              >
                                <Trash2 className="h-3 w-3 text-destructive" />
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </div>
                    </div>
                  );
                })}

                {/* Empty state for filtered results */}
                {!isLoading &&
                  filteredXAgents.length === 0 &&
                  xagents.length > 0 && (
                    <div className="text-center text-muted-foreground py-8">
                      <div className="bg-muted/30 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                        <Search className="h-5 w-5" />
                      </div>
                      <p className="text-sm font-medium mb-1">
                        No matches found
                      </p>
                      <p className="text-xs opacity-75">
                        Try adjusting your search or filters
                      </p>
                    </div>
                  )}
              </div>
            </ScrollArea>
          </>
        )}
      </Sidebar>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative bg-muted">
        {/* Page Content */}
        {children}
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Deletion</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this XAgent? This action cannot be
              undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={cancelDelete}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
