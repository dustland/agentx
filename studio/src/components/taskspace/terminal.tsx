"use client";

import React from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Terminal as TerminalIcon } from "lucide-react";

interface TerminalProps {
  taskId: string;
}

export function Terminal({ taskId }: TerminalProps) {
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-3 border-b">
        <h3 className="text-sm font-medium">Terminal Output</h3>
      </div>
      <div className="flex-1 min-h-0">
        <ScrollArea className="h-full">
          <div className="font-mono text-xs bg-black text-green-400 p-4 rounded-lg space-y-1 m-3">
            <div className="text-gray-400">$ agentx run --task-id {taskId}</div>
            <div className="mt-2">Initializing agents...</div>
            <div>Loading team configuration...</div>
            <div>Starting task execution...</div>
            <div className="mt-2 text-yellow-400">
              [researcher] Starting market analysis...
            </div>
            <div className="text-gray-400">
              └─ Searching for relevant data sources
            </div>
            <div className="text-gray-400">
              └─ Analyzing trends and patterns
            </div>
            <div className="mt-2 text-blue-400">
              [writer] Generating report...
            </div>
            <div className="text-gray-400">└─ Structuring findings</div>
            <div className="text-gray-400">└─ Creating visualizations</div>
            <div className="mt-2 text-green-400">
              ✓ Task completed successfully
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
