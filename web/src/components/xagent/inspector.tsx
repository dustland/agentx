"use client";

import React, { useState, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Code, BookOpenCheck, Monitor } from "lucide-react";
import { EmptyState } from "./empty-state";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import ReactMarkdown from "react-markdown";
import { useArtifact } from "@/hooks/use-xagent";

interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
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

interface ViewerProps {
  selectedArtifact: Artifact | null;
  selectedToolCall: ToolCall | null;
  xagentId: string;
}

export function Inspector({
  selectedArtifact,
  selectedToolCall,
  xagentId,
}: ViewerProps) {
  // Use the hook for the selected artifact
  const artifactQuery = useArtifact({
    xagentId,
    path: selectedArtifact?.path || "",
    enabled: !!selectedArtifact && !selectedArtifact.content,
  });

  // Determine what content to display
  const artifactContent =
    selectedArtifact?.content || artifactQuery.data?.content || null;
  const loadingContent = artifactQuery.isLoading;

  const getFileLanguage = (filename: string) => {
    const ext = filename.split(".").pop()?.toLowerCase();
    switch (ext) {
      case "js":
      case "jsx":
        return "javascript";
      case "ts":
      case "tsx":
        return "typescript";
      case "py":
        return "python";
      case "json":
        return "json";
      case "html":
        return "html";
      case "css":
        return "css";
      case "md":
        return "markdown";
      case "yaml":
      case "yml":
        return "yaml";
      case "sh":
        return "bash";
      case "sql":
        return "sql";
      default:
        return "text";
    }
  };

  // Loading state
  if (selectedArtifact && loadingContent) {
    return (
      <EmptyState
        icon={FileText}
        title="Loading content..."
        isLoading={true}
        size="md"
      />
    );
  }

  // Empty state
  if (!selectedToolCall && !selectedArtifact) {
    return (
      <EmptyState
        icon={Monitor}
        title="Nothing selected"
        description="Select an artifact or tool call to view details"
        size="md"
      />
    );
  }

  return (
    <ScrollArea className="h-full">
      {selectedToolCall ? (
        <div className="space-y-4 p-4">
          <div>
            <h4 className="text-sm font-medium mb-2">Agent</h4>
            <Badge variant="outline">{selectedToolCall.xagent_id}</Badge>
          </div>
          <div>
            <h4 className="text-sm font-medium mb-2">Parameters</h4>
            <pre className="text-xs bg-muted p-3 rounded overflow-x-auto max-w-full">
              {JSON.stringify(selectedToolCall.parameters, null, 2)}
            </pre>
          </div>
          {selectedToolCall.result && (
            <div>
              <h4 className="text-sm font-medium mb-2">Result</h4>
              <pre className="text-xs bg-muted p-3 rounded overflow-x-auto max-w-full">
                {typeof selectedToolCall.result === "string"
                  ? selectedToolCall.result
                  : JSON.stringify(selectedToolCall.result, null, 2)}
              </pre>
            </div>
          )}
          <div>
            <h4 className="text-sm font-medium mb-2">Status</h4>
            <Badge
              variant={
                selectedToolCall.status === "completed"
                  ? "default"
                  : selectedToolCall.status === "error"
                  ? "destructive"
                  : "secondary"
              }
            >
              {selectedToolCall.status}
            </Badge>
          </div>
        </div>
      ) : selectedArtifact && artifactContent ? (
        <div className="p-4">
          <div className="relative">
            {selectedArtifact.path.endsWith(".md") ? (
              <div className="markdown-content">
                <ReactMarkdown>{artifactContent}</ReactMarkdown>
              </div>
            ) : (
              <SyntaxHighlighter
                language={getFileLanguage(selectedArtifact.path)}
                style={vscDarkPlus}
                customStyle={{
                  margin: 0,
                  fontSize: "0.875rem",
                  borderRadius: "0.375rem",
                  maxWidth: "100%",
                  overflow: "auto",
                }}
                wrapLongLines={false}
              >
                {artifactContent || ""}
              </SyntaxHighlighter>
            )}
          </div>
        </div>
      ) : null}
    </ScrollArea>
  );
}
