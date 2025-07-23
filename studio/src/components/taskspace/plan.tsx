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
      const content = response.content || "";
      setPlanContent(content);
    } catch (error: any) {
      // Check if it's a 404 error (plan doesn't exist yet)
      if (error?.message?.includes("404")) {
        // This is expected - plan hasn't been created yet
        setPlanContent(null);
      } else {
        console.error("Failed to load plan:", error);
        setPlanContent(null);
      }
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
