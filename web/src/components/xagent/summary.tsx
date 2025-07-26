"use client";

import React, { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useXAgent } from "@/hooks/use-xagent";
import { EmptyState } from "./empty-state";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface PlanTask {
  id: string;
  action: string;
  agent: string;
  dependencies: string[];
  status: "pending" | "in_progress" | "completed" | "failed";
  on_failure: string;
}

interface PlanData {
  tasks: PlanTask[];
}

interface SummaryProps {
  xagentId: string;
}

export function Summary({ xagentId }: SummaryProps) {
  const { xagent, isLoading } = useXAgent(xagentId);
  const [showRawJson, setShowRawJson] = useState(false);

  // Helper functions
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
      case "in_progress":
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
      case "in_progress":
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

  const planData: PlanData | null = xagent.plan;

  return (
    <div className="h-full flex flex-col relative">
      {/* Floating JSON toggle */}
      <Button
        size="icon"
        variant="ghost"
        onClick={() => setShowRawJson(!showRawJson)}
        className="absolute top-0 right-1 z-10 h-7 w-7 bg-background/80 backdrop-blur-sm border shadow-sm hover:bg-background/90"
      >
        <Braces className="h-3 w-3" />
      </Button>

      <ScrollArea className="flex-1 h-full">
        {showRawJson ? (
          <div className="p-2">
            <SyntaxHighlighter
              language="json"
              style={vscDarkPlus}
              customStyle={{
                margin: 0,
                fontSize: "0.75rem",
                borderRadius: "0.5rem",
                border: "1px solid hsl(var(--border))",
              }}
              showLineNumbers={true}
            >
              {JSON.stringify(xagent, null, 2)}
            </SyntaxHighlighter>
          </div>
        ) : (
          <div className="p-2 space-y-2">
            {/* XAgent Overview */}
            <Card>
              <CardContent className="pt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Status</span>
                  <Badge
                    variant={getStatusVariant(xagent.status)}
                    className="gap-1"
                  >
                    {getStatusIcon(xagent.status)}
                    {xagent.status}
                  </Badge>
                </div>

                {xagent.goal && (
                  <div className="space-y-2">
                    <span className="text-sm font-medium">Goal</span>
                    <p className="text-sm text-muted-foreground leading-relaxed bg-muted/30 p-3 rounded-md">
                      {xagent.goal}
                    </p>
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <User className="h-4 w-4 text-muted-foreground" />
                      Agent ID
                    </div>
                    <code className="text-xs bg-muted/50 px-2 py-1 rounded font-mono">
                      {xagent.agent_id}
                    </code>
                  </div>

                  {xagent.created_at && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm font-medium">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        Created At
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(xagent.created_at)}
                      </p>
                    </div>
                  )}
                </div>

                {xagent.config_path && (
                  <div className="space-y-2 pt-2 border-t">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <Settings className="h-4 w-4 text-muted-foreground" />
                      Configuration Path
                    </div>
                    <code className="text-xs bg-muted/50 px-2 py-1 rounded font-mono break-all">
                      {xagent.config_path}
                    </code>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Execution Plan */}
            {planData ? (
              <Card>
                <CardContent className="pt-6 space-y-6">

                  {/* Task Statistics */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="text-center p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800">
                      <div className="text-2xl font-bold text-emerald-600">
                        {
                          planData.tasks.filter((t) => t.status === "completed")
                            .length
                        }
                      </div>
                      <div className="text-xs text-emerald-600 font-medium">
                        Completed
                      </div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800">
                      <div className="text-2xl font-bold text-blue-600">
                        {
                          planData.tasks.filter(
                            (t) => t.status === "in_progress"
                          ).length
                        }
                      </div>
                      <div className="text-xs text-blue-600 font-medium">
                        In Progress
                      </div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-slate-50 dark:bg-slate-950/20 border border-slate-200 dark:border-slate-800">
                      <div className="text-2xl font-bold text-slate-600">
                        {
                          planData.tasks.filter((t) => t.status === "pending")
                            .length
                        }
                      </div>
                      <div className="text-xs text-slate-600 font-medium">
                        Pending
                      </div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800">
                      <div className="text-2xl font-bold text-red-600">
                        {
                          planData.tasks.filter((t) => t.status === "failed")
                            .length
                        }
                      </div>
                      <div className="text-xs text-red-600 font-medium">
                        Failed
                      </div>
                    </div>
                  </div>

                  {/* Task List */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        Tasks ({planData.tasks.length} total)
                      </span>
                    </div>

                    <Accordion type="multiple" className="w-full space-y-2">
                      {planData.tasks.map((task, index) => (
                        <AccordionItem
                          key={task.id}
                          value={task.id}
                          className="border rounded-lg px-3 data-[state=open]:bg-muted/20"
                        >
                          <AccordionTrigger className="py-4 hover:no-underline">
                            <div className="flex items-center gap-3 flex-1">
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-mono bg-muted px-2 py-1 rounded">
                                  #{index + 1}
                                </span>
                                {getStatusIcon(task.status)}
                              </div>
                              <div className="flex-1 text-left">
                                <div className="font-medium text-sm truncate">
                                  {task.action}
                                </div>
                                <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                                  <User className="h-3 w-3" />
                                  {task.agent}
                                </div>
                              </div>
                              <Badge
                                variant="outline"
                                className="text-xs font-mono"
                              >
                                {task.id}
                              </Badge>
                            </div>
                          </AccordionTrigger>
                          <AccordionContent className="pb-4">
                            <div className="space-y-4 pt-2">

                              {task.dependencies.length > 0 && (
                                <div className="space-y-2">
                                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                                    Dependencies
                                  </span>
                                  <div className="flex flex-wrap gap-1">
                                    {task.dependencies.map((dep) => (
                                      <Badge
                                        key={dep}
                                        variant="secondary"
                                        className="text-xs gap-1"
                                      >
                                        <ArrowRight className="h-3 w-3" />
                                        {dep}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )}

                              <div className="flex items-center justify-between pt-2 border-t">
                                <div className="flex items-center gap-2">
                                  <span className="text-xs font-medium text-muted-foreground">
                                    Assigned to:
                                  </span>
                                  <Badge variant="outline" className="text-xs">
                                    {task.agent}
                                  </Badge>
                                </div>
                                <Badge
                                  variant={getStatusVariant(task.status)}
                                  className="text-xs gap-1"
                                >
                                  {getStatusIcon(task.status)}
                                  {task.status}
                                </Badge>
                              </div>
                            </div>
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="py-12">
                  <EmptyState
                    icon={Activity}
                    title="No execution plan available"
                    description="This XAgent doesn't have an associated execution plan yet"
                    size="md"
                  />
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
