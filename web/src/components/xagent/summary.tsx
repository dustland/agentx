"use client";

import React, { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Target,
  Braces,
  CheckCircle2,
  Clock,
  AlertCircle,
  User,
  Calendar,
  Settings,
  Activity,
  ArrowRight,
  PlayCircle,
  XCircle,
  PauseCircle,
  Hash,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useXAgentContext } from "@/contexts/xagent";
import { EmptyState } from "./empty-state";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface PlanTask {
  id: string;
  action: string;
  agent: string;
  dependencies: string[];
  status: "pending" | "running" | "completed" | "failed";
  on_failure: string;
}

interface PlanData {
  tasks: PlanTask[];
}

interface SummaryProps {
  xagentId: string;
}

export function Summary({ xagentId }: SummaryProps) {
  const { xagent, isLoading, error, artifactsError } = useXAgentContext();
  const [showRawJson, setShowRawJson] = useState(false);

  // Check for authorization errors
  const authError = error?.response?.status === 403 || 
                   error?.response?.status === 401 ||
                   artifactsError?.response?.status === 403 || 
                   artifactsError?.response?.status === 401;

  // Helper functions
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
      case "running":
      case "running":
        return <PlayCircle className="h-4 w-4 text-blue-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <PauseCircle className="h-4 w-4 text-slate-400" />;
    }
  };

  const getStatusVariant = (status: string) => {
    switch (status) {
      case "completed":
        return "default";
      case "running":
      case "running":
        return "secondary";
      case "failed":
        return "destructive";
      default:
        return "outline";
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  // Show authorization error first
  if (authError) {
    return (
      <EmptyState
        icon={XCircle}
        title="Access Denied"
        description="You don't have permission to access this project"
        size="md"
      />
    );
  }

  if (isLoading) {
    return (
      <EmptyState
        icon={Activity}
        title="Loading summary..."
        isLoading={true}
        size="md"
      />
    );
  }

  if (!xagent) {
    return (
      <EmptyState
        icon={Activity}
        title="No data available"
        description="Unable to load XAgent information"
        size="md"
      />
    );
  }

  const planData: PlanData | null = xagent?.plan || null;

  return (
    <div className="h-full flex flex-col relative">
      {/* Floating JSON toggle */}
      <Button
        size="icon"
        variant="ghost"
        onClick={() => setShowRawJson(!showRawJson)}
        className="absolute top-2 right-2 z-10 h-8 w-8 bg-background/90 backdrop-blur-sm border shadow-sm hover:bg-background/95 transition-all duration-200"
      >
        <Braces className="h-4 w-4" />
      </Button>

      {showRawJson ? (
        <div className="h-full overflow-hidden">
          <div className="h-full">
            <div className="h-full w-full min-w-0 bg-slate-950">
              <pre className="h-full w-full overflow-auto p-4 text-xs text-green-400 font-mono whitespace-pre-wrap break-words">
                {JSON.stringify(xagent, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      ) : (
        <ScrollArea className="h-full">
          <div className="p-2 space-y-4">
            {/* Header with Status */}
            <div className="flex items-center justify-between pb-4 border-b border-border/50">
              <div className="space-y-1">
                <h2 className="text-lg font-semibold text-foreground">
                  XAgent Overview
                </h2>
                <p className="text-sm text-muted-foreground">{xagent?.goal}</p>
              </div>
              <Badge
                variant={getStatusVariant(xagent?.status || "pending")}
                className="gap-2 px-3 py-1.5 text-sm font-medium"
              >
                {getStatusIcon(xagent?.status || "pending")}
                {(xagent?.status || "pending").replace("_", " ")}
              </Badge>
            </div>

            {/* Goal Section */}
            {xagent?.goal && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                  <Target className="h-4 w-4 text-primary" />
                  Goal
                </div>
                <div className="bg-gradient-to-r from-primary/5 to-primary/10 border border-primary/20 rounded-lg p-4">
                  <p className="text-sm text-foreground leading-relaxed">
                    {xagent?.goal}
                  </p>
                </div>
              </div>
            )}

            {/* Agent Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                  <Hash className="h-4 w-4 text-muted-foreground" />
                  Agent ID
                </div>
                <div className="bg-muted/30 border border-border/50 rounded-md p-3">
                  <code className="text-xs font-mono text-foreground break-all">
                    {xagent?.xagent_id}
                  </code>
                </div>
              </div>

              {xagent?.created_at && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    Created At
                  </div>
                  <div className="bg-muted/30 border border-border/50 rounded-md p-3">
                    <p className="text-sm text-foreground">
                      {formatDate(xagent?.created_at)}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Configuration Path */}
            {xagent?.config_path && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  Configuration Path
                </div>
                <div className="bg-muted/30 border border-border/50 rounded-md p-3">
                  <code className="text-xs font-mono text-foreground break-all">
                    {xagent?.config_path}
                  </code>
                </div>
              </div>
            )}

            {/* Execution Plan */}
            {planData ? (
              <div className="space-y-2">
                {/* Task Statistics */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {[
                    {
                      status: "completed",
                      label: "Completed",
                      icon: CheckCircle2,
                      colors: {
                        bg: "from-emerald-50 to-emerald-100 dark:from-emerald-950/30 dark:to-emerald-900/20",
                        border: "border-emerald-200 dark:border-emerald-800",
                        text: "text-emerald-600 dark:text-emerald-400",
                        icon: "text-emerald-500/60",
                      },
                    },
                    {
                      status: "running",
                      label: "Running",
                      icon: PlayCircle,
                      colors: {
                        bg: "from-blue-50 to-blue-100 dark:from-blue-950/30 dark:to-blue-900/20",
                        border: "border-blue-200 dark:border-blue-800",
                        text: "text-blue-600 dark:text-blue-400",
                        icon: "text-blue-500/60",
                      },
                    },
                    {
                      status: "pending",
                      label: "Pending",
                      icon: PauseCircle,
                      colors: {
                        bg: "from-slate-50 to-slate-100 dark:from-slate-950/30 dark:to-slate-900/20",
                        border: "border-slate-200 dark:border-slate-800",
                        text: "text-slate-600 dark:text-slate-400",
                        icon: "text-slate-500/60",
                      },
                    },
                    {
                      status: "failed",
                      label: "Failed",
                      icon: XCircle,
                      colors: {
                        bg: "from-red-50 to-red-100 dark:from-red-950/30 dark:to-red-900/20",
                        border: "border-red-200 dark:border-red-800",
                        text: "text-red-600 dark:text-red-400",
                        icon: "text-red-500/60",
                      },
                    },
                  ].map(({ status, label, icon: Icon, colors }) => {
                    const count = planData.tasks.filter(
                      (t) =>
                        t.status === status ||
                        (status === "running" && t.status === "running")
                    ).length;
                    return (
                      <div
                        key={status}
                        className={`relative overflow-hidden rounded-md bg-gradient-to-br ${colors.bg} ${colors.border} py-2 px-4`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className={`text-xl font-bold ${colors.text}`}>
                              {count}
                            </div>
                            <div
                              className={`text-xs font-medium ${colors.text}`}
                            >
                              {label}
                            </div>
                          </div>
                          <Icon className={`h-8 w-8 ${colors.icon}`} />
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Task List */}
                <div className="space-y-4">
                  <Accordion type="multiple" className="w-full space-y-1">
                    {planData.tasks.map((task, index) => (
                      <AccordionItem
                        key={task.id}
                        value={task.id}
                        className="border border-border/50 rounded-lg px-2 py-0 data-[state=open]:bg-muted/20 data-[state=open]:border-primary/20 transition-all duration-200"
                      >
                        <AccordionTrigger className="py-4 hover:no-underline group">
                          <div className="flex items-center gap-4 flex-1">
                            <div className="flex items-center gap-3">
                              {getStatusIcon(task.status)}
                              <Badge
                                variant="outline"
                                className="flex items-center justify-center rounded-full text-xs"
                              >
                                #{index + 1}
                              </Badge>
                            </div>
                            <div className="flex-1 text-left">
                              <div className="font-medium text-sm text-foreground group-hover:text-primary transition-colors line-clamp-1">
                                {task.action}
                              </div>
                              {task.agent && (
                                <div className="text-xs text-muted-foreground flex items-center gap-2 mt-1">
                                  <User className="h-3 w-3" />
                                  {task.agent}
                                </div>
                              )}
                            </div>
                            <Badge
                              variant="outline"
                              className="text-xs font-mono bg-background/50"
                            >
                              {task.id}
                            </Badge>
                          </div>
                        </AccordionTrigger>
                        <AccordionContent className="pb-4">
                          <div className="space-y-4 pt-2">
                            <div className="space-y-3">
                              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                Action
                              </span>
                              <div className="flex flex-wrap gap-2">
                                {task.action}
                              </div>
                            </div>
                          </div>
                          <div className="space-y-4 pt-2">
                            {task.dependencies.length > 0 && (
                              <div className="space-y-3">
                                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                  Dependencies
                                </span>
                                <div className="flex flex-wrap gap-2">
                                  {task.dependencies.map((dep) => (
                                    <Badge
                                      key={dep}
                                      variant="secondary"
                                      className="text-xs gap-1 bg-primary/10 text-primary border-primary/20"
                                    >
                                      <ArrowRight className="h-3 w-3" />
                                      {dep}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}

                            <div className="flex items-center justify-between pt-3 border-t border-border/50">
                              <div className="flex items-center gap-3">
                                <span className="text-xs font-medium text-muted-foreground">
                                  Assigned to:
                                </span>
                                <Badge
                                  variant="outline"
                                  className="text-xs bg-background/50"
                                >
                                  {task.agent}
                                </Badge>
                              </div>
                              <Badge
                                variant={getStatusVariant(task.status)}
                                className="text-xs gap-1"
                              >
                                {getStatusIcon(task.status)}
                                {task.status.replace("_", " ")}
                              </Badge>
                            </div>
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center py-12">
                <EmptyState
                  icon={Activity}
                  title="No execution plan available"
                  description="This XAgent doesn't have an associated execution plan yet"
                  size="md"
                />
              </div>
            )}
          </div>
        </ScrollArea>
      )}
    </div>
  );
}
