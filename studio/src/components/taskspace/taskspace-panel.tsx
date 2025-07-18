"use client";

import React, { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Activity, Brain, ListIcon, Eye, Target } from "lucide-react";
import { useAgentXAPI } from "@/lib/api-client";

// Import the new tab components
import { Artifacts } from "./artifacts";
import { Viewer } from "./viewer";
import { Terminal } from "./terminal";
import { Logs } from "./logs";
import { Memory } from "./memory";
import { Plan } from "./plan";

interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
  displayPath?: string;
}

interface ToolCall {
  id: string;
  agent_id: string;
  tool_name: string;
  parameters: any;
  result?: any;
  timestamp: string;
  status: "pending" | "completed" | "failed";
}

interface TaskSpacePanelProps {
  taskId: string;
  onToolCallSelect?: (handler: (toolCall: ToolCall) => void) => void;
}

export function TaskSpacePanel({
  taskId,
  onToolCallSelect,
}: TaskSpacePanelProps) {
  const apiClient = useAgentXAPI();
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(
    null
  );
  const [selectedToolCall, setSelectedToolCall] = useState<ToolCall | null>(
    null
  );
  const [activeTab, setActiveTab] = useState("artifacts");
  const [hasPlan, setHasPlan] = useState(false);

  // Set up tool call selection handler
  useEffect(() => {
    if (onToolCallSelect) {
      onToolCallSelect((toolCall: ToolCall) => {
        setSelectedToolCall(toolCall);
        setActiveTab("viewer");
      });
    }
  }, [onToolCallSelect]);

  const handleArtifactSelect = (artifact: Artifact) => {
    setSelectedArtifact(artifact);
    setActiveTab("viewer");
  };

  // Set up SSE for real-time updates
  useEffect(() => {
    const eventSource = new EventSource(`/api/tasks/${taskId}/events`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.event === "artifact_created") {
        if (activeTab === "artifacts") {
          // Artifacts component handles its own refresh
        }
      }
      // Handle memory updates
      else if (data.event === "memory_updated") {
        if (activeTab === "memory") {
          // Memory component handles its own refresh
        }
      }
    };

    const cleanup = () => {
      eventSource.close();
    };

    // Cleanup on unmount or when taskId changes
    return cleanup;
  }, [taskId, activeTab]);

  // Check for plan existence
  useEffect(() => {
    if (!taskId) return;

    const checkPlan = async () => {
      try {
        const response = await apiClient.getTaskArtifacts(taskId);
        const planExists = response.artifacts.some(
          (artifact: Artifact) => artifact.path === "plan.json"
        );
        setHasPlan(planExists);
      } catch (error) {
        console.error("Failed to check plan:", error);
      }
    };

    checkPlan();
  }, [taskId]);

  return (
    <div className="h-full flex flex-col px-2 py-3">
      <Card className="h-full flex flex-col rounded-xl">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="h-full flex flex-col"
        >
          <CardHeader className="p-2 flex-shrink-0">
            <div className="flex items-center justify-between">
              <TabsList className="grid w-full grid-cols-5 h-7 text-xs">
                <TabsTrigger value="artifacts" className="text-xs gap-1 py-1">
                  <FileText className="h-3 w-3" />
                  Artifacts
                </TabsTrigger>
                <TabsTrigger value="viewer" className="text-xs gap-1 py-1">
                  <Eye className="h-3 w-3" />
                  Viewer
                </TabsTrigger>
                <TabsTrigger value="memory" className="text-xs gap-1 py-1">
                  <Brain className="h-3 w-3" />
                  Memory
                </TabsTrigger>
                <TabsTrigger value="logs" className="text-xs gap-1 py-1">
                  <Activity className="h-3 w-3" />
                  Logs
                </TabsTrigger>
                <TabsTrigger value="terminal" className="text-xs gap-1 py-1">
                  <Target className="h-3 w-3" />
                  Terminal
                </TabsTrigger>
              </TabsList>
              {hasPlan && (
                <TabsList className="ml-2 h-7">
                  <TabsTrigger value="plan" className="text-xs gap-1 py-1">
                    <ListIcon className="h-3 w-3" />
                    Plan
                  </TabsTrigger>
                </TabsList>
              )}
            </div>
          </CardHeader>

          {/* Artifacts Tab */}
          <TabsContent value="artifacts" className="flex-1 m-0 min-h-0">
            <Artifacts
              taskId={taskId}
              onArtifactSelect={handleArtifactSelect}
            />
          </TabsContent>

          {/* Plan Tab */}
          {hasPlan && (
            <TabsContent value="plan" className="flex-1 m-0 min-h-0">
              <Plan taskId={taskId} />
            </TabsContent>
          )}

          {/* Viewer Tab */}
          <TabsContent value="viewer" className="flex-1 m-0 min-h-0">
            <Viewer
              selectedArtifact={selectedArtifact}
              selectedToolCall={selectedToolCall}
              taskId={taskId}
            />
          </TabsContent>

          {/* Memory Tab */}
          <TabsContent value="memory" className="flex-1 m-0 min-h-0">
            <Memory taskId={taskId} />
          </TabsContent>

          {/* Logs Tab */}
          <TabsContent value="logs" className="flex-1 m-0 min-h-0">
            <Logs taskId={taskId} />
          </TabsContent>

          {/* Terminal Tab */}
          <TabsContent value="terminal" className="flex-1 m-0 min-h-0">
            <Terminal taskId={taskId} />
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
}
