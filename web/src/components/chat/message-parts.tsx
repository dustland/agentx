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
    <div className="text-sm leading-relaxed">
      <ReactMarkdown
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const isInline = !className;
            return !isInline && match ? (
              <SyntaxHighlighter
                style={vscDarkPlus}
                language={match[1]}
                PreTag="div"
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            ) : (
              <code
                className={cn(
                  "bg-muted px-1 py-0.5 rounded text-xs",
                  className
                )}
                {...props}
              >
                {children}
              </code>
            );
          },
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
        return <Loader2 className="w-3 h-3 animate-spin text-yellow-500" />;
      case "completed":
        return <CheckCircle2 className="w-3 h-3 text-green-500" />;
      case "failed":
        return <XCircle className="w-3 h-3 text-red-500" />;
      default:
        return <Clock className="w-3 h-3 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (part.status) {
      case "running":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "completed":
        return "text-green-600 bg-green-50 border-green-200";
      case "failed":
        return "text-red-600 bg-red-50 border-red-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
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
    <div
      className={cn(
        "flex items-center gap-2 px-3 py-2 rounded-lg border my-1",
        "bg-muted/20 hover:bg-muted/30 transition-colors",
        getStatusColor()
      )}
    >
      {/* Status Icon */}
      <div className="flex-shrink-0">{getStatusIcon()}</div>

      {/* Tool Icon */}
      <Terminal className="w-4 h-4 flex-shrink-0" />

      {/* Tool Name */}
      <span className="font-mono text-sm font-medium flex-shrink-0">
        {part.toolName}
      </span>

      {/* Parameter Summary */}
      <span className="text-xs text-muted-foreground truncate flex-1 min-w-0">
        {getParamSummary()}
      </span>

      {/* Duration */}
      {part.duration && (
        <span className="text-xs text-muted-foreground flex-shrink-0">
          {(part.duration / 1000).toFixed(1)}s
        </span>
      )}

      {/* Status Badge */}
      <Badge variant="secondary" className="text-xs flex-shrink-0">
        {part.status || "pending"}
      </Badge>
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
    if (hasArtifacts()) {
      const artifacts = getArtifacts();
      return `Generated ${artifacts.length} artifact${
        artifacts.length > 1 ? "s" : ""
      }`;
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
        "rounded-lg border my-1",
        part.isError
          ? "border-red-200 bg-red-50"
          : "border-green-200 bg-green-50"
      )}
    >
      {/* Compact header */}
      <div className="flex items-center gap-2 px-3 py-2">
        {/* Status Icon */}
        <div className="flex-shrink-0">
          {part.isError ? (
            <XCircle className="w-3 h-3 text-red-500" />
          ) : (
            <CheckCircle2 className="w-3 h-3 text-green-500" />
          )}
        </div>

        {/* Tool name */}
        <span className="font-mono text-sm font-medium flex-shrink-0">
          {part.toolName}
        </span>

        {/* Result summary */}
        <span className="text-xs text-muted-foreground truncate flex-1 min-w-0">
          {getResultSummary()}
        </span>

        {/* Duration */}
        {part.duration && (
          <span className="text-xs text-muted-foreground flex-shrink-0">
            {(part.duration / 1000).toFixed(1)}s
          </span>
        )}

        {/* Expand button */}
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0 flex-shrink-0"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? (
            <ChevronDown className="w-3 h-3" />
          ) : (
            <ChevronRight className="w-3 h-3" />
          )}
        </Button>
      </div>

      {/* Artifacts list (if any) */}
      {hasArtifacts() && (
        <div className="px-3 pb-2">
          <div className="flex flex-wrap gap-1">
            {getArtifacts().map((artifact: any, idx: number) => (
              <Button
                key={idx}
                variant="outline"
                size="sm"
                className="h-6 text-xs px-2 hover:bg-background/80"
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
        <div className="px-3 pb-3 border-t border-current/10">
          <div className="mt-2">
            <pre
              className={cn(
                "text-xs p-2 rounded overflow-x-auto max-h-32",
                part.isError
                  ? "bg-red-100 text-red-800"
                  : "bg-green-100 text-green-800"
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
      <div className="rounded-lg border border-muted bg-muted/20 p-3 my-2">
        <CollapsibleTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start p-0 h-auto"
          >
            <div className="flex items-center gap-2 w-full text-muted-foreground">
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
              <FileCode className="w-4 h-4" />
              <span className="text-sm italic">Agent reasoning...</span>
            </div>
          </Button>
        </CollapsibleTrigger>

        <CollapsibleContent className="mt-3">
          <div className="pl-6">
            <div className="text-sm text-muted-foreground italic">
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
    <div className="flex items-center gap-2 my-3 text-muted-foreground">
      <div className="flex-1 h-px bg-border" />
      <span className="text-xs font-medium px-2">
        {part.stepName || `Step ${part.stepId}`}
      </span>
      <div className="flex-1 h-px bg-border" />
    </div>
  );
}

function ImagePartComponent({ part }: { part: ImagePart }) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
      <div className="my-2">
        <CollapsibleTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start p-0 h-auto mb-2"
          >
            <div className="flex items-center gap-2">
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
              <span className="text-sm">Image</span>
              {part.mimeType && (
                <span className="text-xs text-muted-foreground">
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
            className="max-w-full rounded-lg border"
          />
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}

function ErrorPartComponent({ part }: { part: ErrorPart }) {
  return (
    <div className="rounded-lg border border-red-500/50 bg-red-500/5 p-3 my-2">
      <div className="flex items-center gap-2">
        <XCircle className="w-4 h-4 text-red-500" />
        <span className="font-medium text-sm">Error</span>
        {part.errorCode && (
          <span className="text-xs text-muted-foreground">
            ({part.errorCode})
          </span>
        )}
      </div>
      <div className="mt-2 text-sm text-red-700 dark:text-red-400">
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
    <div className="space-y-2">
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
      {isStreaming && (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Thinking...</span>
        </div>
      )}
    </div>
  );
}
