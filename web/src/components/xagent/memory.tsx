"use client";

import React from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { RefreshCw, Brain, Database } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { EmptyState } from "./empty-state";

interface Memory {
  id: string;
  content: string;
  type: string;
  xagent_id: string;
  metadata?: any;
  created_at: string;
}

interface MemoryProps {
  xagentId: string;
}

export function Memory({ xagentId }: MemoryProps) {
  // TODO: Implement useTaskMemory hook when memory functionality is needed
  const memories: Memory[] = [];
  const loadingMemories = false;

  if (loadingMemories) {
    return (
      <EmptyState
        icon={Brain}
        title="Loading memories..."
        isLoading={true}
        size="md"
      />
    );
  }

  if (memories.length === 0) {
    return (
      <EmptyState
        icon={Brain}
        title="No memories stored yet"
        description="Memories will appear as agents store information during task execution"
        size="md"
      />
    );
  }

  return (
    <div className="h-full relative">
      <div className="absolute top-2 right-2 z-10">
        <Button
          size="sm"
          variant="ghost"
          onClick={() => {
            /* TODO: implement refetch when hook is available */
          }}
          disabled={loadingMemories}
          className="h-7 w-7 p-0"
        >
          <RefreshCw
            className={`h-3 w-3 ${loadingMemories ? "animate-spin" : ""}`}
          />
        </Button>
      </div>
      <ScrollArea className="h-full">
        <div className="space-y-2 p-4">
          {memories.map((memory, idx) => (
            <Card key={idx} className="p-3">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-muted-foreground" />
                  <span className="font-medium text-sm">
                    {memory.xagent_id || "System"}
                  </span>
                </div>
                <Badge variant="outline" className="text-xs">
                  {memory.type || "general"}
                </Badge>
              </div>
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <p className="text-sm">{memory.content}</p>
              </div>
              {memory.metadata && (
                <div className="mt-2 pt-2 border-t">
                  <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                    {JSON.stringify(memory.metadata, null, 2)}
                  </pre>
                </div>
              )}
              <div className="text-xs text-muted-foreground mt-2">
                {formatDate(new Date(memory.created_at || Date.now()))}
              </div>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
