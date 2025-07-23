"use client";

import React, { useState, useEffect } from "react";
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
  ListIcon,
  RefreshCwIcon,
  CheckCircle2,
  Clock,
  AlertCircle,
  Target,
  Braces,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTaskPlan } from "@/hooks/use-task";

interface PlanTask {
  id: string;
  name: string;
  goal: string;
  agent: string;
  dependencies: string[];
  status: "pending" | "in_progress" | "completed" | "failed";
  on_failure: string;
}

interface PlanData {
  goal: string;
  tasks: PlanTask[];
}

interface PlanProps {
  taskId: string;
}

export function Plan({ taskId }: PlanProps) {
  const {
    plan: planResponse,
    isLoading: loadingPlan,
    refetch: loadPlan,
  } = useTaskPlan(taskId);
  const [planData, setPlanData] = useState<PlanData | null>(null);
  const [showRawJson, setShowRawJson] = useState(false);

  // Parse plan data when plan response changes
  useEffect(() => {
    if (planResponse?.content) {
      try {
        const parsed = JSON.parse(planResponse.content);
        setPlanData(parsed);
      } catch (e) {
        console.error("Plan content is not valid JSON:", e);
        setPlanData(null);
      }
    } else {
      setPlanData(null);
    }
  }, [planResponse]);

  // Helper functions
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "in_progress":
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      case "failed":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800 border-green-200";
      case "in_progress":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "failed":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-600 border-gray-200";
    }
  };

  const organizeTasksByLevel = (tasks: PlanTask[]) => {
    const taskMap = new Map(tasks.map((task) => [task.id, task]));
    const levels: PlanTask[][] = [];
    const visited = new Set<string>();

    const getTaskLevel = (taskId: string): number => {
      const task = taskMap.get(taskId);
      if (!task || visited.has(taskId)) return 0;

      visited.add(taskId);

      if (task.dependencies.length === 0) {
        return 0;
      }

      const maxDepLevel = Math.max(
        ...task.dependencies.map((depId) => getTaskLevel(depId))
      );
      return maxDepLevel + 1;
    };

    // Calculate levels for all tasks
    tasks.forEach((task) => {
      const level = getTaskLevel(task.id);
      if (!levels[level]) levels[level] = [];
      levels[level].push(task);
    });

    return levels.filter((level) => level.length > 0);
  };

  if (loadingPlan) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <div className="text-center">
          <ListIcon className="w-6 h-6 mx-auto mb-2 opacity-50 animate-pulse" />
          <p>Loading plan...</p>
        </div>
      </div>
    );
  }

  if (!planData) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <div className="text-center">
          <ListIcon className="w-6 h-6 mx-auto mb-2 opacity-50" />
          <p>No plan available</p>
        </div>
      </div>
    );
  }

  const taskLevels = organizeTasksByLevel(planData.tasks);

  return (
    <div className="h-full flex flex-col relative">
      {/* Floating Action Buttons */}
      <div className="absolute top-3 right-3 z-10 flex items-center gap-2">
        <Button
          size="icon"
          variant="ghost"
          onClick={() => setShowRawJson(!showRawJson)}
          className="bg-background/80 backdrop-blur-sm border h-8 w-8"
        >
          <Braces className="h-4 w-4" />
        </Button>
        <Button
          size="icon"
          variant="ghost"
          onClick={() => loadPlan()}
          disabled={loadingPlan}
          className="bg-background/80 backdrop-blur-sm border h-8 w-8"
        >
          <RefreshCwIcon
            className={cn("h-4 w-4", loadingPlan && "animate-spin")}
          />
        </Button>
      </div>

      <ScrollArea className="flex-1 h-full">
        {showRawJson ? (
          <div className="p-4">
            <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg text-sm overflow-auto">
              {JSON.stringify(planData, null, 2)}
            </pre>
          </div>
        ) : (
          <div className="p-4 pb-8 space-y-6">
            {/* Goal Section */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-primary" />
                <h4 className="text-base font-semibold">Goal</h4>
              </div>
              <p className="text-sm text-muted-foreground pl-6">
                {planData.goal}
              </p>
            </div>

            {/* Statistics */}
            <div className="bg-muted/30 rounded-lg p-4">
              <div className="grid grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-lg font-semibold text-green-600">
                    {
                      planData.tasks.filter((t) => t.status === "completed")
                        .length
                    }
                  </div>
                  <div className="text-xs text-muted-foreground">Completed</div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-blue-600">
                    {
                      planData.tasks.filter((t) => t.status === "in_progress")
                        .length
                    }
                  </div>
                  <div className="text-xs text-muted-foreground">
                    In Progress
                  </div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-gray-600">
                    {
                      planData.tasks.filter((t) => t.status === "pending")
                        .length
                    }
                  </div>
                  <div className="text-xs text-muted-foreground">Pending</div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-red-600">
                    {planData.tasks.filter((t) => t.status === "failed").length}
                  </div>
                  <div className="text-xs text-muted-foreground">Failed</div>
                </div>
              </div>
            </div>

            {/* Tasks as Accordion */}
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-muted-foreground">
                Workflow ({planData.tasks.length} tasks)
              </h4>

              <Accordion type="multiple" className="w-full">
                {planData.tasks.map((task) => (
                  <AccordionItem key={task.id} value={task.id} className="">
                    <AccordionTrigger className="py-3 hover:no-underline">
                      <div className="flex items-center gap-3 flex-1">
                        {getStatusIcon(task.status)}
                        <span className="font-medium text-sm truncate text-left flex-1">
                          {task.name}
                        </span>
                        <Badge
                          variant="outline"
                          className="text-xs font-mono ml-auto"
                        >
                          {task.id}
                        </Badge>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="space-y-3 pl-7">
                        <div>
                          <h6 className="text-xs font-medium text-muted-foreground mb-1">
                            Goal
                          </h6>
                          <p className="text-sm">{task.goal}</p>
                        </div>

                        {task.dependencies.length > 0 && (
                          <div>
                            <h6 className="text-xs font-medium text-muted-foreground mb-1">
                              Dependencies
                            </h6>
                            <div className="flex flex-wrap gap-1">
                              {task.dependencies.map((dep) => (
                                <Badge
                                  key={dep}
                                  variant="secondary"
                                  className="text-xs"
                                >
                                  {dep}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        <div>
                          <h6 className="text-xs font-medium text-muted-foreground mb-1">
                            Agent
                          </h6>
                          <Badge variant="outline" className="text-xs">
                            {task.agent}
                          </Badge>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </div>
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
