"use client";

import React, { useState, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { ListIcon, RefreshCwIcon } from "lucide-react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { useTask } from "@/hooks/use-task";

interface PlanProps {
  taskId: string;
}

export function Plan({ taskId }: PlanProps) {
  const { getArtifactContent } = useTask(taskId);
  const [planContent, setPlanContent] = useState<string | null>(null);
  const [loadingPlan, setLoadingPlan] = useState(false);

  // Load plan function
  const loadPlan = async () => {
    if (!taskId) return;

    setLoadingPlan(true);
    try {
      const response = await getArtifactContent("plan.json");
      
      // The content might be a string that needs to be parsed
      let content = response.content || "";
      
      // If the content is a valid JSON string, format it nicely
      if (content) {
        try {
          const parsed = JSON.parse(content);
          content = JSON.stringify(parsed, null, 2);
        } catch (e) {
          // If it's not valid JSON, use as-is
          console.log("Plan content is not valid JSON, using as-is");
        }
      }
      
      setPlanContent(content);
    } catch (error: any) {
      console.error("Failed to load plan:", error);
      console.error("Error details:", {
        message: error.message,
        taskId,
        path: "plan.json"
      });
      setPlanContent(null);
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

  if (!planContent) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <div className="text-center">
          <ListIcon className="w-6 h-6 mx-auto mb-2 opacity-50" />
          <p>No plan available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-lg font-semibold">Plan</h3>
        <Button
          size="sm"
          variant="ghost"
          onClick={loadPlan}
          disabled={loadingPlan}
        >
          <RefreshCwIcon
            className={`h-4 w-4 ${loadingPlan ? "animate-spin" : ""}`}
          />
        </Button>
      </div>
      <ScrollArea className="flex-1 min-h-0">
        <div className="p-4 space-y-4">
          <SyntaxHighlighter
            language="json"
            style={vscDarkPlus}
            customStyle={{
              margin: 0,
              fontSize: "0.875rem",
              borderRadius: "0.375rem",
            }}
          >
            {planContent}
          </SyntaxHighlighter>
        </div>
      </ScrollArea>
    </div>
  );
}
