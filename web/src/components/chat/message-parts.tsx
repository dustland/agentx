"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import {
  ChevronRight,
  ChevronDown,
  Terminal,
  CheckCircle2,
  XCircle,
  Loader2,
  FileCode,
  Clock,
  AlertCircle,
  FileText,
  FileEdit,
  FileSearch,
  FolderOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

// Types matching Vercel AI SDK structure
export interface TextPart {
  type: "text";
  text: string;
}

export interface ToolCallPart {
  type: "tool-call";
  toolCallId: string;
  toolName: string;
  args: Record<string, any>;
  // UI-specific fields for streaming status
  status?: "pending" | "running" | "completed" | "failed";
  duration?: number;
}

export interface ToolResultPart {
  type: "tool-result";
  toolCallId: string;
  toolName: string;
  result: any;
  isError?: boolean;
  duration?: number;
}

export interface ImagePart {
  type: "image";
  image: string; // URL or base64
  mimeType?: string;
}

export interface FilePart {
  type: "file";
  data: string; // URL or base64
  mimeType: string;
}

export interface StepStartPart {
  type: "step-start";
  stepId: string;
  stepName?: string;
}

export interface ReasoningPart {
  type: "reasoning";
  content: string;
}

export interface ErrorPart {
  type: "error";
  error: string;
  errorCode?: string;
}

export type MessagePart =
  | TextPart
  | ToolCallPart
  | ToolResultPart
  | ImagePart
  | FilePart
  | StepStartPart
  | ReasoningPart
  | ErrorPart;

interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
  displayPath?: string;
}

interface MessagePartsProps {
  parts: MessagePart[];
  isStreaming?: boolean;
  onArtifactSelect?: ((artifact: Artifact) => void) | null;
}

// Individual part components
function TextPartComponent({ part }: { part: TextPart }) {
  if (!part.text) return null;

  return (
    <div className="text-xs leading-relaxed text-foreground/90">
      <ReactMarkdown
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const isInline = !className;
            return !isInline && match ? (
              <div className="my-1">
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{
                    fontSize: '11px',
                    padding: '8px',
                    borderRadius: '4px',
                    border: '1px solid rgba(255,255,255,0.1)'
                  }}
                >
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              </div>
            ) : (
              <code
                className={cn(
                  "bg-muted/50 px-1 py-0.5 rounded text-[11px] font-mono",
                  className
                )}
                {...props}
              >
                {children}
              </code>
            );
          },
          p: ({ children }) => <p className="mb-1">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-inside mb-1 ml-2">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-1 ml-2">{children}</ol>,
          li: ({ children }) => <li className="mb-0.5">{children}</li>,
          h1: ({ children }) => <h1 className="text-sm font-semibold mb-1 mt-2">{children}</h1>,
          h2: ({ children }) => <h2 className="text-sm font-semibold mb-1 mt-2">{children}</h2>,
          h3: ({ children }) => <h3 className="text-xs font-semibold mb-1 mt-1">{children}</h3>,
        }}
      >
        {part.text}
      </ReactMarkdown>
    </div>
  );
}

function ToolCallPartComponent({ part }: { part: ToolCallPart }) {
  const getStatusIcon = () => {
    switch (part.status) {
      case "running":
        return <Loader2 className="w-3 h-3 animate-spin" />;
      case "completed":
        return <CheckCircle2 className="w-3 h-3" />;
      case "failed":
        return <XCircle className="w-3 h-3" />;
      default:
        return <Clock className="w-3 h-3" />;
    }
  };

  const getStatusColor = () => {
    switch (part.status) {
      case "running":
        return "text-yellow-500 dark:text-yellow-400";
      case "completed":
        return "text-green-500 dark:text-green-400";
      case "failed":
        return "text-red-500 dark:text-red-400";
      default:
        return "text-muted-foreground";
    }
  };
  
  const getToolIcon = () => {
    switch (part.toolName) {
      case "write_file":
        return <FileEdit className="w-3 h-3" />;
      case "edit_file":
        return <FileText className="w-3 h-3" />;
      case "read_file":
        return <FileSearch className="w-3 h-3" />;
      case "list_files":
        return <FolderOpen className="w-3 h-3" />;
      default:
        return <Terminal className="w-3 h-3" />;
    }
  };

  // Create a brief summary of parameters
  const getParamSummary = () => {
    if (!part.args || Object.keys(part.args).length === 0) {
      return "no parameters";
    }

    const entries = Object.entries(part.args);
    if (entries.length === 1) {
      const [key, value] = entries[0];
      const valueStr =
        typeof value === "string" ? value : JSON.stringify(value);
      const truncated =
        valueStr.length > 30 ? valueStr.substring(0, 30) + "..." : valueStr;
      return `${key}: ${truncated}`;
    } else {
      return `${entries.length} parameters`;
    }
  };

  return (
    <div className="flex items-center gap-2 px-2 py-1 rounded border border-border/40 bg-muted/5 dark:bg-muted/10 my-0.5 text-xs">
      {/* Status Icon */}
      <div className={cn("flex-shrink-0", getStatusColor())}>
        {getStatusIcon()}
      </div>

      {/* Tool Icon */}
      <div className="flex-shrink-0 text-muted-foreground/70">
        {getToolIcon()}
      </div>

      {/* Tool Name */}
      <span className="font-mono text-foreground/90 text-[11px]">
        {part.toolName}
      </span>

      {/* Parameter Summary */}
      <span className="text-muted-foreground/60 truncate flex-1 min-w-0 text-[11px]">
        {getParamSummary()}
      </span>

      {/* Duration */}
      {part.duration && (
        <span className="text-muted-foreground/50 flex-shrink-0 text-[10px]">
          {(part.duration / 1000).toFixed(1)}s
        </span>
      )}
    </div>
  );
}

function ToolResultPartComponent({
  part,
  onArtifactSelect,
}: {
  part: ToolResultPart;
  onArtifactSelect?: ((artifact: Artifact) => void) | null;
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  const resultString =
    typeof part.result === "string"
      ? part.result
      : JSON.stringify(part.result, null, 2);

  // Check if this is a file operation result with a path
  const isFileOperationResult = (part.toolName === "write_file" || part.toolName === "edit_file") && 
    typeof part.result === "object" && 
    part.result !== null &&
    'path' in part.result;

  // Check if the result contains artifacts
  const hasArtifacts = () => {
    if (typeof part.result === "object" && part.result !== null) {
      const resultObj = part.result as any;
      return (
        resultObj.artifacts &&
        Array.isArray(resultObj.artifacts) &&
        resultObj.artifacts.length > 0
      );
    }
    return false;
  };

  const getArtifacts = () => {
    if (hasArtifacts()) {
      const resultObj = part.result as any;
      return resultObj.artifacts;
    }
    return [];
  };

  const getResultSummary = () => {
    // Special handling for different tool types
    if (part.toolName === "write_file" || part.toolName === "edit_file") {
      if (typeof part.result === "object" && part.result && 'path' in part.result) {
        const path = (part.result as any).path;
        const fileName = path.split('/').pop();
        return `${part.toolName === "write_file" ? "Created" : "Edited"} ${fileName}`;
      }
    }
    
    if (part.toolName === "read_file" && typeof part.result === "object") {
      const content = (part.result as any).content;
      if (content) {
        const lines = content.split('\n').length;
        return `Read ${lines} lines`;
      }
    }
    
    if (part.toolName === "list_files" && Array.isArray(part.result)) {
      return `Found ${part.result.length} items`;
    }
    
    if (part.toolName === "run_bash") {
      if (part.isError) {
        return "Command failed";
      }
      return "Command executed";
    }
    
    if (part.toolName === "search_files" && typeof part.result === "object") {
      const results = (part.result as any).results || [];
      return `Found ${results.length} matches`;
    }

    if (hasArtifacts()) {
      const artifacts = getArtifacts();
      return `Generated ${artifacts.length} artifact${artifacts.length > 1 ? "s" : ""}`;
    }

    const summary =
      resultString.length > 60
        ? resultString.substring(0, 60) + "..."
        : resultString;
    return summary.replace(/\n/g, " ");
  };

  const handleArtifactClick = (artifactPath: string) => {
    if (onArtifactSelect) {
      // Create artifact object that matches the workspace interface
      const artifact: Artifact = {
        path: artifactPath,
        type: "file" as const,
      };
      onArtifactSelect(artifact);
    }
  };

  return (
    <div
      className={cn(
        "rounded border my-0.5",
        part.isError
          ? "border-red-500/30 bg-red-500/5 dark:border-red-500/20 dark:bg-red-950/20"
          : "border-border/40 bg-muted/5 dark:bg-muted/10"
      )}
    >
      {/* Compact header */}
      <div className="flex items-center gap-2 px-2 py-1">
        {/* Status Icon */}
        <div className="flex-shrink-0">
          {part.isError ? (
            <XCircle className="w-3 h-3 text-red-500 dark:text-red-400" />
          ) : (
            <CheckCircle2 className="w-3 h-3 text-green-500 dark:text-green-400" />
          )}
        </div>

        {/* Result summary */}
        <span className="text-[11px] text-foreground/90 flex-1 min-w-0">
          {getResultSummary()}
        </span>

        {/* Duration */}
        {part.duration && (
          <span className="text-[10px] text-muted-foreground/50 flex-shrink-0">
            {(part.duration / 1000).toFixed(1)}s
          </span>
        )}

        {/* Expand button for details */}
        {(resultString.length > 100 || hasArtifacts()) && (
          <Button
            variant="ghost"
            size="sm"
            className="h-4 w-4 p-0 flex-shrink-0 hover:bg-muted/50"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? (
              <ChevronDown className="w-3 h-3 text-muted-foreground/60" />
            ) : (
              <ChevronRight className="w-3 h-3 text-muted-foreground/60" />
            )}
          </Button>
        )}
      </div>

      {/* File link for file operation results */}
      {isFileOperationResult && onArtifactSelect && (
        <div className="px-2 pb-1 border-t border-border/30">
          <Button
            variant="ghost"
            size="sm"
            className="h-5 text-[10px] px-1.5 text-primary/80 hover:text-primary hover:bg-primary/10 w-full justify-start mt-1"
            onClick={() => handleArtifactClick((part.result as any).path)}
          >
            {part.toolName === "write_file" ? (
              <FileEdit className="w-3 h-3 mr-1" />
            ) : (
              <FileText className="w-3 h-3 mr-1" />
            )}
            View in workspace
          </Button>
        </div>
      )}

      {/* Artifacts list (if any) */}
      {hasArtifacts() && (
        <div className="px-3 pb-2">
          <div className="flex flex-wrap gap-1">
            {getArtifacts().map((artifact: any, idx: number) => (
              <Button
                key={idx}
                variant="ghost"
                size="sm"
                className="h-6 text-xs px-2 text-primary hover:text-primary/80 hover:bg-primary/10"
                onClick={() =>
                  handleArtifactClick(artifact.path || artifact.name)
                }
              >
                <FileText className="w-3 h-3 mr-1" />
                {artifact.name || artifact.path || `artifact-${idx + 1}`}
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Expanded content */}
      {isExpanded && (
        <div className="px-2 pb-1.5 border-t border-border/30">
          <div className="mt-1">
            <pre
              className={cn(
                "text-[10px] p-1.5 rounded overflow-x-auto max-h-32",
                "bg-background/80 dark:bg-background/50 border border-border/30",
                "font-mono text-muted-foreground/80 leading-relaxed"
              )}
            >
              {resultString}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

function ReasoningPartComponent({ part }: { part: ReasoningPart }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
      <div className="rounded border border-border/30 bg-muted/5 dark:bg-muted/10 px-2 py-1 my-0.5">
        <CollapsibleTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start p-0 h-auto hover:bg-transparent"
          >
            <div className="flex items-center gap-1.5 w-full text-muted-foreground/60 text-[11px]">
              {isExpanded ? (
                <ChevronDown className="w-3 h-3" />
              ) : (
                <ChevronRight className="w-3 h-3" />
              )}
              <FileCode className="w-3 h-3" />
              <span className="italic">Reasoning...</span>
            </div>
          </Button>
        </CollapsibleTrigger>

        <CollapsibleContent className="mt-1">
          <div className="pl-4 pr-2 pb-1">
            <div className="text-[11px] text-muted-foreground/70 italic leading-relaxed">
              {part.content}
            </div>
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}

function StepStartPartComponent({ part }: { part: StepStartPart }) {
  return (
    <div className="flex items-center gap-2 my-1 text-muted-foreground/50">
      <div className="flex-1 h-px bg-border/30" />
      <span className="text-[10px] font-medium px-1.5">
        {part.stepName || `Step ${part.stepId}`}
      </span>
      <div className="flex-1 h-px bg-border/30" />
    </div>
  );
}

function ImagePartComponent({ part }: { part: ImagePart }) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
      <div className="my-0.5">
        <CollapsibleTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start p-0 h-auto mb-1 hover:bg-transparent"
          >
            <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground/70">
              {isExpanded ? (
                <ChevronDown className="w-3 h-3" />
              ) : (
                <ChevronRight className="w-3 h-3" />
              )}
              <span>Image</span>
              {part.mimeType && (
                <span className="text-[10px] text-muted-foreground/50">
                  ({part.mimeType})
                </span>
              )}
            </div>
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <img
            src={part.image}
            alt="Message image"
            className="max-w-full rounded border border-border/30 mt-1"
          />
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}

function ErrorPartComponent({ part }: { part: ErrorPart }) {
  return (
    <div className="rounded border border-red-500/30 bg-red-500/5 dark:bg-red-950/20 p-2 my-0.5">
      <div className="flex items-center gap-1.5">
        <XCircle className="w-3 h-3 text-red-500 dark:text-red-400" />
        <span className="font-medium text-[11px] text-red-600 dark:text-red-400">Error</span>
        {part.errorCode && (
          <span className="text-[10px] text-red-500/70">
            ({part.errorCode})
          </span>
        )}
      </div>
      <div className="mt-1 text-[11px] text-red-600 dark:text-red-400/90 leading-relaxed">
        {part.error}
      </div>
    </div>
  );
}

// Main component
export function MessageParts({
  parts,
  isStreaming,
  onArtifactSelect,
}: MessagePartsProps) {
  if (!parts || parts.length === 0) return null;

  return (
    <div className="space-y-0.5">
      {parts.map((part, index) => {
        const key = `part-${index}-${part.type}`;

        switch (part.type) {
          case "text":
            return <TextPartComponent key={key} part={part} />;
          case "tool-call":
            return (
              <ToolCallPartComponent key={key} part={part as ToolCallPart} />
            );
          case "tool-result":
            return (
              <ToolResultPartComponent
                key={key}
                part={part as ToolResultPart}
                onArtifactSelect={onArtifactSelect}
              />
            );
          case "reasoning":
            return (
              <ReasoningPartComponent key={key} part={part as ReasoningPart} />
            );
          case "step-start":
            return (
              <StepStartPartComponent key={key} part={part as StepStartPart} />
            );
          case "image":
            return <ImagePartComponent key={key} part={part as ImagePart} />;
          case "error":
            return <ErrorPartComponent key={key} part={part as ErrorPart} />;
          default:
            return null;
        }
      })}
    </div>
  );
}
