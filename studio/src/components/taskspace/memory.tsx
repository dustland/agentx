import React, { useState, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Brain, Database, RefreshCw } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { useAgentXAPI } from "@/lib/api-client";

interface Memory {
  agent_id?: string;
  type?: string;
  content: string;
  metadata?: any;
  created_at?: string;
}

interface MemoryProps {
  taskId: string;
}

export function Memory({ taskId }: MemoryProps) {
  const apiClient = useAgentXAPI();
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loadingMemories, setLoadingMemories] = useState(false);

  // Load memories when component mounts or taskId changes
  useEffect(() => {
    if (taskId) {
      loadMemories();
    }
  }, [taskId]);

  // Helper function to load memories
  const loadMemories = async () => {
    setLoadingMemories(true);
    try {
      // For now, using search with empty query to get all memories
      const memoryResults = await apiClient.searchMemory(taskId, {
        query: "",
        limit: 100,
      });
      setMemories(memoryResults);
    } catch (error) {
      console.error("Failed to load memories:", error);
      setMemories([]);
    } finally {
      setLoadingMemories(false);
    }
  };

  return (
    <div className="h-full relative">
      <div className="absolute top-2 right-2 z-10">
        <Button
          size="sm"
          variant="ghost"
          onClick={loadMemories}
          disabled={loadingMemories}
          className="h-7 w-7 p-0"
        >
          <RefreshCw
            className={`h-3 w-3 ${loadingMemories ? "animate-spin" : ""}`}
          />
        </Button>
      </div>
      <ScrollArea className="h-full">
        {loadingMemories ? (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <Brain className="w-6 h-6 mx-auto mb-2 opacity-50" />
              <p>Loading memories...</p>
            </div>
          </div>
        ) : memories.length === 0 ? (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <Brain className="w-6 h-6 mx-auto mb-2 opacity-50" />
              <p>No memories stored yet</p>
              <p className="text-xs mt-2">
                Memories will appear as agents store information during task
                execution
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-2 p-4">
            {memories.map((memory, idx) => (
              <Card key={idx} className="p-3">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4 text-muted-foreground" />
                    <span className="font-medium text-sm">
                      {memory.agent_id || "System"}
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
        )}
      </ScrollArea>
    </div>
  );
}
