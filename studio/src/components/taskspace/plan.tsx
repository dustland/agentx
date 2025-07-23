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
  ArrowDown,
  Target,
  Braces
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTask } from "@/hooks/use-task";

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
  const { getTaskPlan } = useTask(taskId);
  const [planData, setPlanData] = useState<PlanData | null>(null);
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [showRawJson, setShowRawJson] = useState(false);

  // Load plan function
  const loadPlan = async () => {
    if (!taskId) return;

    setLoadingPlan(true);
    try {
      const response = await getTaskPlan();
      
      // Parse the JSON content
      const content = response.content || "";
      
      if (content) {
        try {
          const parsed = JSON.parse(content);
          setPlanData(parsed);
        } catch (e) {
          console.error("Plan content is not valid JSON:", e);
          setPlanData(null);
        }
      } else {
        setPlanData(null);
      }
    } catch (error: any) {
      console.error("Failed to load plan:", error);
      setPlanData(null);
    } finally {
      setLoadingPlan(false);
    }
  };

  // Load plan when component mounts or taskId changes
  useEffect(() => {
    if (taskId) {
      loadPlan();
    }
  }, [taskId]);

  // Helper functions
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "in_progress":
        return <Clock className="h-4 w-4 text-blue-500 animate-pulse" />;
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
    const taskMap = new Map(tasks.map(task => [task.id, task]));
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
        ...task.dependencies.map(depId => getTaskLevel(depId))
      );
      return maxDepLevel + 1;
    };
    
    // Calculate levels for all tasks
    tasks.forEach(task => {
      const level = getTaskLevel(task.id);
      if (!levels[level]) levels[level] = [];
      levels[level].push(task);
    });
    
    return levels.filter(level => level.length > 0);
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
          onClick={loadPlan}
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
          <div className="p-4">
            <Accordion type="multiple" defaultValue={["goal", "stats", "workflow"]} className="w-full">
              {/* Goal Section */}
              <AccordionItem value="goal">
                <AccordionTrigger className="text-left">
                  <div className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-primary" />
                    <span>Goal</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <p className="text-sm text-muted-foreground pl-6">{planData.goal}</p>
                </AccordionContent>
              </AccordionItem>

              {/* Statistics */}
              <AccordionItem value="stats">
                <AccordionTrigger className="text-left">
                  <span>Progress Statistics</span>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="bg-muted/30 rounded-lg p-4">
                    <div className="grid grid-cols-4 gap-4 text-center">
                      <div>
                        <div className="text-lg font-semibold text-green-600">
                          {planData.tasks.filter(t => t.status === "completed").length}
                        </div>
                        <div className="text-xs text-muted-foreground">Completed</div>
                      </div>
                      <div>
                        <div className="text-lg font-semibold text-blue-600">
                          {planData.tasks.filter(t => t.status === "in_progress").length}
                        </div>
                        <div className="text-xs text-muted-foreground">In Progress</div>
                      </div>
                      <div>
                        <div className="text-lg font-semibold text-gray-600">
                          {planData.tasks.filter(t => t.status === "pending").length}
                        </div>
                        <div className="text-xs text-muted-foreground">Pending</div>
                      </div>
                      <div>
                        <div className="text-lg font-semibold text-red-600">
                          {planData.tasks.filter(t => t.status === "failed").length}
                        </div>
                        <div className="text-xs text-muted-foreground">Failed</div>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Tasks Workflow */}
              <AccordionItem value="workflow">
                <AccordionTrigger className="text-left">
                  <span>Task Workflow ({planData.tasks.length} tasks)</span>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4">
                    {taskLevels.map((level, levelIndex) => (
                      <div key={levelIndex} className="space-y-3">
                        {/* Level indicator */}
                        {levelIndex > 0 && (
                          <div className="flex justify-center">
                            <ArrowDown className="h-4 w-4 text-muted-foreground" />
                          </div>
                        )}
                        
                        {/* Tasks in this level */}
                        <div className="grid gap-3">
                          {level.map((task) => (
                            <div key={task.id} className="border rounded-lg p-4 bg-background">
                              <div className="flex items-start gap-3">
                                {getStatusIcon(task.status)}
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-1">
                                    <h5 className="font-medium text-sm truncate">
                                      {task.name}
                                    </h5>
                                    <Badge 
                                      variant="outline"
                                      className={cn("text-xs", getStatusColor(task.status))}
                                    >
                                      {task.status}
                                    </Badge>
                                  </div>
                                  <p className="text-xs text-muted-foreground mb-2">
                                    {task.goal}
                                  </p>
                                  {task.dependencies.length > 0 && (
                                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                      <span>Depends on:</span>
                                      <span className="font-mono">
                                        {task.dependencies.join(", ")}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
