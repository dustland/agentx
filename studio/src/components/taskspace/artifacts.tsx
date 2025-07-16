"use client";

import React, { useState, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  FileText,
  Download,
  Copy,
  FileIcon,
  FolderIcon,
  ChevronRightIcon,
} from "lucide-react";
import { useAgentXAPI } from "@/lib/api-client";
import { formatBytes, formatDate } from "@/lib/utils";

interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
  displayPath?: string;
}

interface ArtifactsProps {
  taskId: string;
  onArtifactSelect: (artifact: Artifact) => void;
}

export function Artifacts({ taskId, onArtifactSelect }: ArtifactsProps) {
  const apiClient = useAgentXAPI();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [loadingArtifacts, setLoadingArtifacts] = useState(false);
  const [expandedDirectories, setExpandedDirectories] = useState<Set<string>>(
    new Set()
  );

  // Load artifacts when component mounts or taskId changes
  useEffect(() => {
    if (taskId) {
      loadArtifacts();
    }
  }, [taskId]);

  // Helper function to load artifacts
  const loadArtifacts = async () => {
    setLoadingArtifacts(true);
    try {
      const response = await apiClient.getTaskArtifacts(taskId);

      // Filter artifacts to only show those in the artifacts/ folder and exclude .git
      const filteredArtifacts = response.artifacts
        .filter((artifact: Artifact) => {
          // Only include items that start with 'artifacts/'
          if (!artifact.path.startsWith("artifacts/")) return false;

          // Exclude .git directories and files
          if (
            artifact.path.includes("/.git/") ||
            artifact.path.endsWith("/.git")
          )
            return false;

          return true;
        })
        .map((artifact: Artifact) => ({
          ...artifact,
          // Remove the 'artifacts/' prefix from the path for display
          displayPath: artifact.path.replace(/^artifacts\//, ""),
        }));

      setArtifacts(filteredArtifacts);
    } catch (error) {
      console.error("Failed to load artifacts:", error);
    } finally {
      setLoadingArtifacts(false);
    }
  };

  // Rest of the component logic stays the same...
  const toggleDirectory = (path: string) => {
    const newExpanded = new Set(expandedDirectories);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedDirectories(newExpanded);
  };

  const downloadFile = async (artifact: Artifact) => {
    try {
      const response = await apiClient.getArtifactContent(
        taskId,
        artifact.path
      );
      const content = response.content || "";
      const blob = new Blob([content], { type: "text/plain" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = artifact.displayPath || artifact.path;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download file:", error);
    }
  };

  const copyToClipboard = async (artifact: Artifact) => {
    try {
      const response = await apiClient.getArtifactContent(
        taskId,
        artifact.path
      );
      const content = response.content || "";
      await navigator.clipboard.writeText(content);
    } catch (error) {
      console.error("Failed to copy to clipboard:", error);
    }
  };

  // Build tree structure
  const buildTree = (artifacts: Artifact[]) => {
    const tree: any = {};

    artifacts.forEach((artifact) => {
      const parts = (artifact.displayPath || artifact.path).split("/");
      let current = tree;

      parts.forEach((part, index) => {
        if (!current[part]) {
          current[part] = {
            type: index === parts.length - 1 ? artifact.type : "directory",
            artifact: index === parts.length - 1 ? artifact : null,
            children: {},
          };
        }
        current = current[part].children;
      });
    });

    return tree;
  };

  const renderTree = (tree: any, path: string = "") => {
    return Object.entries(tree).map(([name, node]: [string, any]) => {
      const currentPath = path ? `${path}/${name}` : name;
      const isDirectory = node.type === "directory";
      const isExpanded = expandedDirectories.has(currentPath);

      return (
        <div key={currentPath} className="ml-0">
          <div
            className={`
              flex items-center gap-2 p-2 rounded cursor-pointer
              hover:bg-muted/50 transition-colors
              ${isDirectory ? "" : ""}
            `}
            onClick={() => {
              if (isDirectory) {
                toggleDirectory(currentPath);
              } else if (node.artifact) {
                onArtifactSelect(node.artifact);
              }
            }}
          >
            {isDirectory ? (
              <>
                <ChevronRightIcon
                  className={`w-4 h-4 transition-transform ${
                    isExpanded ? "rotate-90" : ""
                  }`}
                />
                <FolderIcon className="w-4 h-4 text-blue-500" />
              </>
            ) : (
              <>
                <div className="w-4" />
                <FileIcon className="w-4 h-4 text-gray-500" />
              </>
            )}
            <span className="text-sm flex-1">{name}</span>
            {!isDirectory && node.artifact && (
              <div className="flex items-center gap-1">
                <Badge variant="outline" className="text-xs">
                  {formatBytes(node.artifact.size || 0)}
                </Badge>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={(e) => {
                    e.stopPropagation();
                    downloadFile(node.artifact);
                  }}
                  className="h-6 w-6 p-0"
                >
                  <Download className="w-3 h-3" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={(e) => {
                    e.stopPropagation();
                    copyToClipboard(node.artifact);
                  }}
                  className="h-6 w-6 p-0"
                >
                  <Copy className="w-3 h-3" />
                </Button>
              </div>
            )}
          </div>
          {isDirectory && isExpanded && (
            <div className="ml-4 border-l border-border/50 pl-2">
              {renderTree(node.children, currentPath)}
            </div>
          )}
        </div>
      );
    });
  };

  const tree = buildTree(artifacts);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-lg font-semibold">Artifacts</h3>
        <Button
          size="sm"
          variant="ghost"
          onClick={loadArtifacts}
          disabled={loadingArtifacts}
        >
          <ChevronRightIcon
            className={`h-4 w-4 ${loadingArtifacts ? "animate-spin" : ""}`}
          />
        </Button>
      </div>
      <ScrollArea className="flex-1 min-h-0">
        {loadingArtifacts ? (
          <div className="text-center py-6 text-muted-foreground">
            <FileText className="w-6 h-6 mx-auto mb-2 opacity-50" />
            <p>Loading artifacts...</p>
          </div>
        ) : artifacts.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            <FileText className="w-6 h-6 mx-auto mb-2 opacity-50" />
            <p>No artifacts found</p>
          </div>
        ) : (
          <div className="p-4">{renderTree(tree)}</div>
        )}
      </ScrollArea>
    </div>
  );
}
