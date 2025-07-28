"use client";

import React, { useEffect, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardHeader } from "@/components/ui/card";
import { Activity, Folder, Monitor, Goal } from "lucide-react";

// Import the new tab components
import { Artifacts } from "./artifacts";
import { Inspector } from "./inspector";
import { Logs } from "./logs";
import { Memory } from "./memory";
import { Summary } from "./summary";

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
  xagent_id: string;
  tool_name: string;
  parameters: any;
  result?: any;
  timestamp: string;
  status: "pending" | "completed" | "error";
}

interface WorkspaceProps {
  xagentId: string;
  onToolCallSelect?: (handler: (toolCall: ToolCall) => void) => void;
  onArtifactHandlerRegister?: (handler: (artifact: Artifact) => void) => void;
}

export function Workspace({
  xagentId,
  onToolCallSelect,
  onArtifactHandlerRegister,
}: WorkspaceProps) {
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(
    null
  );
  const [selectedToolCall, setSelectedToolCall] = useState<ToolCall | null>(
    null
  );
  const [activeTab, setActiveTab] = useState("plan");

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

  // Register the artifact selection handler
  useEffect(() => {
    if (onArtifactHandlerRegister) {
      onArtifactHandlerRegister(handleArtifactSelect);
    }
  }, [onArtifactHandlerRegister]);

  return (
    <div className="h-full flex flex-col px-2 py-3">
      <Card className="h-full flex flex-col rounded-xl overflow-hidden">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="h-full flex flex-col gap-0"
        >
          <CardHeader className="p-2 flex-shrink-0">
            <TabsList className="h-7 text-xs">
              <TabsTrigger value="plan" className="text-xs gap-1 py-1">
                <Goal className="h-3 w-3 mr-1" />
                Summary
              </TabsTrigger>
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

          {/* Summary Tab */}
          <TabsContent value="plan" className="flex-1 m-0 min-h-0 overflow-hidden">
            <Summary xagentId={xagentId} />
          </TabsContent>

          {/* Artifacts Tab */}
          <TabsContent value="artifacts" className="flex-1 m-0 min-h-0 overflow-hidden">
            <Artifacts
              xagentId={xagentId}
              onArtifactSelect={handleArtifactSelect}
            />
          </TabsContent>

          {/* Viewer Tab */}
          <TabsContent value="inspector" className="flex-1 m-0 min-h-0 overflow-hidden">
            <Inspector
              selectedArtifact={selectedArtifact}
              selectedToolCall={selectedToolCall}
              xagentId={xagentId}
            />
          </TabsContent>

          {/* Memory Tab */}
          <TabsContent value="memory" className="flex-1 m-0 min-h-0 overflow-hidden">
            <Memory xagentId={xagentId} />
          </TabsContent>

          {/* Logs Tab */}
          <TabsContent value="logs" className="flex-1 m-0 min-h-0 overflow-hidden">
            {activeTab === "logs" && <Logs xagentId={xagentId} />}
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
}
