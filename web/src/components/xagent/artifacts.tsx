"use client";

import React, { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Download,
  Copy,
  FileIcon,
  FolderIcon,
  ChevronRightIcon,
  Inbox,
  Folder,
} from "lucide-react";
import { EmptyState } from "./empty-state";
import { useXAgentContext } from "@/contexts/xagent";
import { formatBytes } from "@/lib/utils";

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
  xagentId: string;
  onArtifactSelect: (artifact: Artifact) => void;
}

export function Artifacts({ xagentId, onArtifactSelect }: ArtifactsProps) {
  const { artifacts, isLoadingArtifacts } = useXAgentContext();
  const [expandedDirectories, setExpandedDirectories] = useState<Set<string>>(
    new Set()
  );

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

  // Build tree structure
  const buildTree = (artifacts: Artifact[]) => {
    const tree: any = {};

    artifacts.forEach((artifact) => {
      const parts = (artifact.displayPath || artifact.path)
        .split("/")
        .filter((part) => part.length > 0);
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
                    // This function is no longer used as API calls are removed
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
                    // This function is no longer used as API calls are removed
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

  if (isLoadingArtifacts || !artifacts) {
    return (
      <EmptyState
        icon={Folder}
        title="Loading artifacts..."
        isLoading={true}
        size="md"
      />
    );
  }

  const tree = buildTree(artifacts);

  if (artifacts.length === 0) {
    return (
      <EmptyState
        icon={Inbox}
        title="No artifacts created yet"
        description="Files will appear here when agents create them"
        size="md"
      />
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-4">{renderTree(tree)}</div>
    </ScrollArea>
  );
}
