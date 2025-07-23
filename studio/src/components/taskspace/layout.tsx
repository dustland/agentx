"use client";

import React, { useState, useEffect, useRef } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardHeader } from "@/components/ui/card";
import { Activity, Folder, Monitor, Goal } from "lucide-react";
import { useTask, useTaskPlan } from "@/hooks/use-task";

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
  status: "pending" | "completed" | "error";
}

interface TaskspaceLayoutProps {
  taskId: string;
  onToolCallSelect?: (handler: (toolCall: ToolCall) => void) => void;
}

export function TaskspaceLayout({
  taskId,
  onToolCallSelect,
}: TaskspaceLayoutProps) {
  const { plan, isLoading: isPlanLoading } = useTaskPlan(taskId);
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(
    null
  );
  const [selectedToolCall, setSelectedToolCall] = useState<ToolCall | null>(
    null
  );
  const [activeTab, setActiveTab] = useState("artifacts");
  const initialTabSetRef = useRef(false);

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

  // Check for plan existence and set default tab
  useEffect(() => {
    const hasPlan = !!plan;

    // Set plan as default tab if it exists and we haven't set initial tab yet
    if (hasPlan && !initialTabSetRef.current && !isPlanLoading) {
      setActiveTab("plan");
      initialTabSetRef.current = true;
    }
  }, [plan, isPlanLoading]);

  const hasPlan = !!plan;

  return (
    <div className="h-full flex flex-col px-2 py-3">
      <Card className="h-full flex flex-col rounded-xl">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="h-full flex flex-col"
        >
          <CardHeader className="p-2 flex-shrink-0">
            <TabsList className="h-7 text-xs">
              {hasPlan && (
                <TabsTrigger value="plan" className="text-xs gap-1 py-1">
                  <Goal className="h-3 w-3 mr-1" />
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
