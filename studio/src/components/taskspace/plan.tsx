"use client";

import React, { useState, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { ListIcon, RefreshCwIcon } from "lucide-react";
import { useAgentXAPI } from "@/lib/api-client";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface PlanProps {
  taskId: string;
}

export function Plan({ taskId }: PlanProps) {
  const apiClient = useAgentXAPI();
  const [planContent, setPlanContent] = useState<string | null>(null);
  const [loadingPlan, setLoadingPlan] = useState(false);

  // Load plan function
  const loadPlan = async () => {
    if (!taskId) return;

    setLoadingPlan(true);
    try {
      const response = await apiClient.getArtifactContent(taskId, "plan.json");
      setPlanContent(response.content);
    } catch (error) {
      console.error("Failed to load plan:", error);
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
        {loadingPlan ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          </div>
        ) : planContent ? (
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
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <ListIcon className="w-8 h-8 mx-auto mb-2" />
            <p>No plan available</p>
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
