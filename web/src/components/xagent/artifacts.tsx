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
  Code,
  FileText,
  FileImage,
  FileVideo,
  FileAudio,
  Database,
  Settings,
  Globe,
  Palette,
  Package,
  Archive,
  BookOpen,
  Terminal,
  XCircle,
} from "lucide-react";
import { Icons } from "../icons";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { Toggle } from "@/components/ui/toggle";
import { Label } from "@/components/ui/label";
import { EmptyState } from "./empty-state";
import { useXAgentContext } from "@/contexts/xagent";
import { useArtifact } from "@/hooks/use-xagent";
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

// File icon mapping based on extensions
function getFileIcon(filename: string) {
  const extension = filename.split(".").pop()?.toLowerCase() || "";

  const iconMap: Record<string, { icon: any; color: string }> = {
    // Code files
    js: { icon: Code, color: "text-yellow-500" },
    jsx: { icon: Code, color: "text-blue-400" },
    ts: { icon: Code, color: "text-blue-600" },
    tsx: { icon: Code, color: "text-blue-400" },
    py: { icon: Code, color: "text-green-500" },
    java: { icon: Code, color: "text-orange-600" },
    cpp: { icon: Code, color: "text-blue-700" },
    c: { icon: Code, color: "text-blue-700" },
    go: { icon: Code, color: "text-cyan-500" },
    rust: { icon: Code, color: "text-orange-700" },
    php: { icon: Code, color: "text-purple-600" },
    rb: { icon: Code, color: "text-red-600" },

    // Web files
    html: { icon: Globe, color: "text-orange-500" },
    htm: { icon: Globe, color: "text-orange-500" },
    css: { icon: Palette, color: "text-blue-500" },
    scss: { icon: Palette, color: "text-pink-500" },
    sass: { icon: Palette, color: "text-pink-500" },
    less: { icon: Palette, color: "text-blue-400" },

    // Data files
    json: { icon: Icons.json, color: "text-yellow-600" },
    xml: { icon: Settings, color: "text-green-600" },
    yaml: { icon: Settings, color: "text-purple-500" },
    yml: { icon: Settings, color: "text-purple-500" },
    toml: { icon: Settings, color: "text-gray-600" },
    ini: { icon: Settings, color: "text-gray-500" },
    env: { icon: Settings, color: "text-green-400" },
    csv: { icon: Icons.csv, color: "text-green-500" },
    xls: { icon: Icons.excel, color: "text-green-600" },
    xlsx: { icon: Icons.excel, color: "text-green-600" },
    ppt: { icon: Icons.powerpoint, color: "text-orange-600" },
    pptx: { icon: Icons.powerpoint, color: "text-orange-600" },

    // Database
    sql: { icon: Database, color: "text-blue-600" },
    db: { icon: Database, color: "text-blue-700" },
    sqlite: { icon: Database, color: "text-blue-700" },

    // Documents
    md: { icon: Icons.markdown, color: "text-blue-600" },
    txt: { icon: Icons.txt, color: "text-gray-600" },
    rtf: { icon: FileText, color: "text-gray-600" },
    pdf: { icon: Icons.pdf, color: "text-red-600" },
    doc: { icon: Icons.word, color: "text-blue-700" },
    docx: { icon: Icons.word, color: "text-blue-700" },

    // Images
    png: { icon: FileImage, color: "text-green-500" },
    jpg: { icon: FileImage, color: "text-green-500" },
    jpeg: { icon: FileImage, color: "text-green-500" },
    gif: { icon: FileImage, color: "text-pink-500" },
    svg: { icon: FileImage, color: "text-purple-500" },
    webp: { icon: FileImage, color: "text-green-400" },
    ico: { icon: FileImage, color: "text-blue-400" },

    // Video
    mp4: { icon: FileVideo, color: "text-red-500" },
    avi: { icon: FileVideo, color: "text-red-500" },
    mov: { icon: FileVideo, color: "text-red-500" },
    wmv: { icon: FileVideo, color: "text-red-500" },
    flv: { icon: FileVideo, color: "text-red-500" },
    webm: { icon: FileVideo, color: "text-red-500" },

    // Audio
    mp3: { icon: FileAudio, color: "text-purple-500" },
    wav: { icon: FileAudio, color: "text-purple-500" },
    flac: { icon: FileAudio, color: "text-purple-500" },
    ogg: { icon: FileAudio, color: "text-purple-500" },

    // Archives
    zip: { icon: Archive, color: "text-yellow-600" },
    rar: { icon: Archive, color: "text-yellow-600" },
    tar: { icon: Archive, color: "text-yellow-600" },
    gz: { icon: Archive, color: "text-yellow-600" },
    "7z": { icon: Archive, color: "text-yellow-600" },

    // Package files
    pkg: { icon: Package, color: "text-brown-600" },
    deb: { icon: Package, color: "text-brown-600" },
    rpm: { icon: Package, color: "text-brown-600" },
    dmg: { icon: Package, color: "text-brown-600" },

    // Shell/Terminal
    sh: { icon: Terminal, color: "text-green-600" },
    bash: { icon: Terminal, color: "text-green-600" },
    zsh: { icon: Terminal, color: "text-green-600" },
    fish: { icon: Terminal, color: "text-green-600" },
    ps1: { icon: Terminal, color: "text-blue-600" },
    bat: { icon: Terminal, color: "text-gray-600" },
    cmd: { icon: Terminal, color: "text-gray-600" },
  };

  return iconMap[extension] || { icon: FileIcon, color: "text-gray-500" };
}

function ArtifactHoverContent({
  xagentId,
  path,
}: {
  xagentId: string;
  path: string;
}) {
  const [showRawJson, setShowRawJson] = useState(false);

  // Generate the corresponding meta.json path
  const metaPath = `${path}.meta.json`;

  const {
    data: artifactData,
    isLoading,
    error,
  } = useArtifact({
    xagentId,
    path: metaPath,
    enabled: true,
  });

  if (isLoading) {
    return <div className="p-2 text-sm text-muted-foreground">Loading...</div>;
  }

  if (error) {
    return (
      <div className="p-2 text-sm text-muted-foreground">
        No metadata file found
      </div>
    );
  }

  if (!artifactData?.content) {
    return (
      <div className="p-2 text-sm text-muted-foreground">
        No metadata available
      </div>
    );
  }

  // Parse the JSON metadata
  let parsedMeta;
  let rawContent = artifactData.content;
  try {
    parsedMeta = JSON.parse(artifactData.content);
  } catch (e) {
    // If parsing fails, show raw content
    return (
      <div className="max-w-lg p-3">
        <div className="text-sm font-medium mb-2">Invalid JSON metadata</div>
        <pre className="text-xs bg-muted p-2 rounded overflow-auto max-h-32">
          {rawContent}
        </pre>
      </div>
    );
  }

  // Render structured form view
  const renderFormView = () => (
    <div className="space-y-3">
      {Object.entries(parsedMeta).map(([key, value]) => (
        <div key={key} className="space-y-1">
          <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            {key.replace(/_/g, " ")}
          </Label>
          <div className="text-sm bg-muted/30 rounded px-2 py-1 border">
            {typeof value === "object" ? (
              <pre className="text-xs font-mono">
                {JSON.stringify(value, null, 2)}
              </pre>
            ) : (
              <span className="font-mono">{String(value)}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );

  // Render raw JSON view
  const renderJsonView = () => {
    const formattedJson = JSON.stringify(parsedMeta, null, 2);
    const maxLength = 800;
    const truncated =
      formattedJson.length > maxLength
        ? formattedJson.substring(0, maxLength) + "..."
        : formattedJson;

    return (
      <div className="text-xs rounded border overflow-auto max-h-64 bg-slate-950 text-slate-100 p-3">
        <pre className="whitespace-pre-wrap font-mono text-green-400">
          {truncated}
        </pre>
      </div>
    );
  };

  return (
    <div className="max-w-lg">
      <div className="p-0 space-y-3">
        {/* Header */}
        <div className="flex items-center p-2 gap-2 mb-0 bg-muted">
          <div className="w-4 h-4">
            {(() => {
              const { icon: IconComponent, color } = getFileIcon(path);
              return <IconComponent className={`w-4 h-4 ${color}`} />;
            })()}
          </div>
          <div className="font-medium flex-1 text-sm truncate">{path}</div>
          <div className="flex items-center gap-2">
            <Toggle
              size="sm"
              pressed={showRawJson}
              onPressedChange={setShowRawJson}
              className="h-6 w-6"
            >
              <Code className="w-4 h-4" />
            </Toggle>
          </div>
        </div>

        {/* Content */}
        <div className="max-h-80 overflow-auto p-2">
          {showRawJson ? renderJsonView() : renderFormView()}
        </div>
      </div>
    </div>
  );
}

export function Artifacts({ xagentId, onArtifactSelect }: ArtifactsProps) {
  const { artifacts, isLoadingArtifacts, error, artifactsError } = useXAgentContext();
  const [expandedDirectories, setExpandedDirectories] = useState<Set<string>>(
    new Set()
  );

  // Check for authorization errors
  const authError = error?.response?.status === 403 || 
                   error?.response?.status === 401 ||
                   artifactsError?.response?.status === 403 || 
                   artifactsError?.response?.status === 401;

  // Filter out meta.json files
  const filteredArtifacts =
    artifacts?.filter(
      (artifact: Artifact) => !artifact.path.endsWith("meta.json")
    ) || [];

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
      const parts = artifact.path.split("/").filter((part) => part.length > 0);
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
              (() => {
                const { icon: IconComponent, color } = getFileIcon(name);
                return <IconComponent className={`w-4 h-4 ${color}`} />;
              })()
            )}
            {!isDirectory && node.artifact ? (
              <HoverCard openDelay={500} closeDelay={200}>
                <HoverCardTrigger asChild>
                  <div className="flex-1 flex items-center justify-between gap-2 cursor-pointer hover:text-primary transition-colors">
                    <span className="text-sm">{name}</span>
                    <Badge variant="outline" className="text-xs px-1 py-0 h-4">
                      {name.split(".").pop()?.toUpperCase() || "FILE"}
                    </Badge>
                  </div>
                </HoverCardTrigger>
                <HoverCardContent side="bottom" className="w-auto p-0">
                  <ArtifactHoverContent
                    xagentId={xagentId}
                    path={node.artifact.path}
                  />
                </HoverCardContent>
              </HoverCard>
            ) : (
              <span className="text-sm flex-1">{name}</span>
            )}
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

  // Show authorization error first
  if (authError) {
    return (
      <EmptyState
        icon={XCircle}
        title="Access Denied"
        description="You don't have permission to access this project"
        size="md"
      />
    );
  }

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

  const tree = buildTree(filteredArtifacts);

  if (filteredArtifacts.length === 0) {
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
