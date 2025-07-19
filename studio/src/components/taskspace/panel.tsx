"use client";

import React, { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Activity, Brain, ListIcon, Eye, Target, Folder, Monitor } from "lucide-react";
import { useAgentXAPI } from "@/lib/api-client";

// Import the new tab components
import { Artifacts } from "./artifacts";
import { Inspector } from "./inspector";
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
        setActiveTab("inspector");
      });
    }
  }, [onToolCallSelect]);

  const handleArtifactSelect = (artifact: Artifact) => {
    setSelectedArtifact(artifact);
    setActiveTab("inspector");
  };

  // Set up SSE for real-time updates
  useEffect(() => {
    const eventSource = new EventSource(`/api/agentx/tasks/${taskId}/stream`);

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
              <TabsList className="h-7 text-xs">
                {hasPlan && (
                  <TabsTrigger value="plan" className="text-xs gap-1 py-1">
                    <ListIcon className="h-3 w-3 mr-1" />
                    Plan
                  </TabsTrigger>
                )}
                <TabsTrigger value="artifacts" className="text-xs gap-1 py-1">
                  <Folder className="h-3 w-3 mr-1" />
                  Files
                </TabsTrigger>
                <TabsTrigger value="inspector" className="text-xs gap-1 py-1">
                  <Monitor className="h-3 w-3 mr-1" />
                  Inspector
                </TabsTrigger>
                {/* <TabsTrigger value="memory" className="text-xs gap-1 py-1">
                  <Brain className="h-3 w-3" />
                  Memory
                </TabsTrigger> */}
                <TabsTrigger value="logs" className="text-xs gap-1 py-1">
                  <Activity className="h-3 w-3 mr-1" />
                  Logs
                </TabsTrigger>
              </TabsList>

            </div>
          </CardHeader>

          {/* Plan Tab */}
          {hasPlan && (
            <TabsContent value="plan" className="flex-1 m-0 min-h-0">
              <Plan taskId={taskId} />
            </TabsContent>
          )}


          {/* Artifacts Tab */}
          <TabsContent value="artifacts" className="flex-1 m-0 min-h-0">
            <Artifacts
              taskId={taskId}
              onArtifactSelect={handleArtifactSelect}
            />
          </TabsContent>

          {/* Viewer Tab */}
          <TabsContent value="inspector" className="flex-1 m-0 min-h-0">
            <Inspector
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
        </Tabs>
      </Card>
    </div>
  );
}
