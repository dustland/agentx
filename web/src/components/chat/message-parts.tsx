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
  Search,
  Database,
  Brain,
  Globe,
  Copy,
  ExternalLink,
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
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  
  if (!part.text) return null;

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  return (
    <div className="text-sm leading-relaxed">
      <ReactMarkdown
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const isInline = !className;
            const codeString = String(children).replace(/\n$/, "");
            
            return !isInline && match ? (
              <div className="relative my-2 group">
                <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0"
                    onClick={() => handleCopyCode(codeString)}
                  >
                    {copiedCode === codeString ? (
                      <CheckCircle2 className="h-3 w-3" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{
                    fontSize: '0.875rem',
                    padding: '1rem',
                    paddingRight: '3rem',
                    borderRadius: '0.375rem',
                  }}
                >
                  {codeString}
                </SyntaxHighlighter>
              </div>
            ) : (
              <code
                className={cn(
                  "bg-muted px-1.5 py-0.5 rounded-md text-xs font-mono",
                  className
                )}
                {...props}
              >
                {children}
              </code>
            );
          },
          p: ({ children }) => <p className="mb-2">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-inside mb-2 ml-3">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 ml-3">{children}</ol>,
          li: ({ children }) => <li className="mb-1">{children}</li>,
          h1: ({ children }) => <h1 className="text-lg font-semibold mb-2 mt-3">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-semibold mb-2 mt-3">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-semibold mb-1.5 mt-2">{children}</h3>,
        }}
      >
        {part.text}
      </ReactMarkdown>
    </div>
  );
}

function ToolCallPartComponent({ part }: { part: ToolCallPart }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
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
      case "append_file":
        return <FileEdit className="w-3 h-3" />;
      case "edit_file":
        return <FileText className="w-3 h-3" />;
      case "read_file":
        return <FileSearch className="w-3 h-3" />;
      case "list_files":
      case "list_directory":
        return <FolderOpen className="w-3 h-3" />;
      case "search_files":
      case "search_web":
        return <Search className="w-3 h-3" />;
      case "add_memory":
      case "search_memory":
        return <Brain className="w-3 h-3" />;
      case "store_artifact":
        return <Database className="w-3 h-3" />;
      case "web_research":
      case "fetch_url":
        return <Globe className="w-3 h-3" />;
      case "run_bash":
      case "execute_command":
        return <Terminal className="w-3 h-3" />;
      default:
        return <Terminal className="w-3 h-3" />;
    }
  };

  // Create a human-readable summary of the tool call
  const getToolCallSummary = () => {
    if (part.toolName === "write_file" && part.args.filename) {
      return `Writing to ${part.args.filename}`;
    }
    if (part.toolName === "edit_file" && part.args.filename) {
      return `Editing ${part.args.filename}`;
    }
    if (part.toolName === "read_file" && part.args.filename) {
      return `Reading ${part.args.filename}`;
    }
    if (part.toolName === "list_files") {
      return part.args.path ? `Listing ${part.args.path}` : "Listing files";
    }
    if (part.toolName === "run_bash" && part.args.command) {
      const cmd = part.args.command;
      return cmd.length > 40 ? cmd.substring(0, 40) + "..." : cmd;
    }
    if (part.toolName === "search_files" && part.args.query) {
      return `Searching for "${part.args.query}"`;
    }
    if (part.toolName === "add_memory" && part.args.content) {
      const content = part.args.content;
      return content.length > 40 ? `Storing: ${content.substring(0, 40)}...` : `Storing: ${content}`;
    }
    if (part.toolName === "search_memory" && part.args.query) {
      return `Searching memory for "${part.args.query}"`;
    }
    if (part.toolName === "web_research" && part.args.query) {
      return `Researching "${part.args.query}"`;
    }
    if (part.toolName === "store_artifact" && part.args.name) {
      return `Storing artifact: ${part.args.name}`;
    }
    
    // Default: show first parameter
    const entries = Object.entries(part.args || {});
    if (entries.length > 0) {
      const [key, value] = entries[0];
      const valueStr = typeof value === "string" ? value : JSON.stringify(value);
      return valueStr.length > 40 ? valueStr.substring(0, 40) + "..." : valueStr;
    }
    
    return "";
  };

  const hasDetailedArgs = part.args && Object.keys(part.args).length > 0;

  return (
    <div className="rounded-md border border-border bg-card/50 dark:bg-card/30 my-2">
      <div className="flex items-center gap-2 px-3 py-2">
        {/* Status Icon */}
        <div className={cn("flex-shrink-0", getStatusColor())}>
          {getStatusIcon()}
        </div>

        {/* Tool Icon */}
        <div className="flex-shrink-0 text-muted-foreground">
          {getToolIcon()}
        </div>

        {/* Tool Name */}
        <span className="font-mono text-sm font-medium">
          {part.toolName}
        </span>

        {/* Tool Call Summary */}
        <span className="text-sm text-muted-foreground flex-1 min-w-0 truncate">
          {getToolCallSummary()}
        </span>

        {/* Duration */}
        {part.duration && (
          <span className="text-xs text-muted-foreground flex-shrink-0">
            {(part.duration / 1000).toFixed(1)}s
          </span>
        )}

        {/* Expand button for args */}
        {hasDetailedArgs && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0 flex-shrink-0"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </Button>
        )}
      </div>
      
      {/* Expanded arguments */}
      {isExpanded && hasDetailedArgs && (
        <div className="px-3 pb-3 border-t border-border">
          <pre className="text-xs p-2 mt-2 rounded-md bg-muted/50 dark:bg-muted/30 overflow-x-auto">
            {JSON.stringify(part.args, null, 2)}
          </pre>
        </div>
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
      
  // Check if we should hide the expanded view (for clean structured results)
  const shouldHideExpanded = () => {
    if (typeof part.result !== "object" || !part.result) return false;
    
    // Hide expanded view for clean structured responses
    const toolsWithCleanResults = [
      "write_file", "edit_file", "append_file", "delete_file",
      "list_files", "file_exists", "create_directory",
      "add_memory", "search_memory", "list_memories",
      "store_artifact"
    ];
    
    return toolsWithCleanResults.includes(part.toolName);
  };

  // Check if this is a file operation result with a path
  const isFileOperationResult = (part.toolName === "write_file" || part.toolName === "edit_file" || part.toolName === "append_file") && 
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
    // Handle error results
    if (part.isError) {
      if (typeof part.result === "object" && part.result && 'error' in part.result) {
        return (part.result as any).error;
      }
      return "Operation failed";
    }
    
    // Special handling for different tool types
    if (part.toolName === "write_file" || part.toolName === "edit_file" || part.toolName === "append_file") {
      if (typeof part.result === "object" && part.result) {
        const resultObj = part.result as any;
        if ('path' in resultObj) {
          const fileName = resultObj.path.split('/').pop();
          const size = resultObj.size;
          let action = "Modified";
          if (part.toolName === "write_file") action = "Created";
          if (part.toolName === "edit_file") action = "Updated";
          if (part.toolName === "append_file") action = "Appended to";
          return `${action} ${fileName}${size ? ` (${formatFileSize(size)})` : ''}`;
        }
        if (resultObj.message) return resultObj.message;
      }
    }
    
    if (part.toolName === "read_file") {
      if (typeof part.result === "string") {
        const lines = part.result.split('\n').length;
        return `Read ${lines} lines`;
      } else if (typeof part.result === "object" && part.result) {
        const resultObj = part.result as any;
        if (resultObj.content) {
          const lines = resultObj.content.split('\n').length;
          return `Read ${lines} lines from ${resultObj.filename || 'file'}`;
        }
      }
    }
    
    if (part.toolName === "list_files" || part.toolName === "list_directory") {
      if (typeof part.result === "object" && part.result) {
        const resultObj = part.result as any;
        if ('files' in resultObj && Array.isArray(resultObj.files)) {
          const fileCount = resultObj.files.filter((f: any) => !f.type || f.type === "file").length;
          const dirCount = resultObj.files.filter((f: any) => f.type === "directory").length;
          if (fileCount && dirCount) {
            return `Found ${fileCount} files and ${dirCount} directories`;
          } else if (fileCount) {
            return `Found ${fileCount} file${fileCount > 1 ? 's' : ''}`;
          } else if (dirCount) {
            return `Found ${dirCount} director${dirCount > 1 ? 'ies' : 'y'}`;
          } else {
            return "Empty directory";
          }
        }
        if ('items' in resultObj) {
          return resultObj.message || `Found ${resultObj.items.length} items`;
        }
      }
      if (Array.isArray(part.result)) {
        return `Found ${part.result.length} items`;
      }
    }
    
    if (part.toolName === "run_bash") {
      if (typeof part.result === "object" && part.result) {
        const resultObj = part.result as any;
        if ('exit_code' in resultObj) {
          return resultObj.exit_code === 0 ? "Command executed successfully" : `Command failed (exit code: ${resultObj.exit_code})`;
        }
      }
      return "Command executed";
    }
    
    if (part.toolName === "search_files" && typeof part.result === "object") {
      const results = (part.result as any).results || [];
      const query = (part.result as any).query;
      return query ? `Found ${results.length} matches for "${query}"` : `Found ${results.length} matches`;
    }
    
    if (part.toolName === "search_memory" && typeof part.result === "object") {
      const resultObj = part.result as any;
      if ('results' in resultObj) {
        return resultObj.count ? `Found ${resultObj.count} memories` : "No memories found";
      }
    }
    
    if (part.toolName === "add_memory" && typeof part.result === "object") {
      const resultObj = part.result as any;
      if (resultObj.success) {
        return resultObj.message || "Memory stored successfully";
      }
    }
    
    if (part.toolName === "file_exists" && typeof part.result === "object") {
      const exists = (part.result as any).exists;
      const filename = (part.result as any).filename;
      return exists ? `${filename} exists` : `${filename} does not exist`;
    }
    
    if (part.toolName === "delete_file" && typeof part.result === "object") {
      const deleted = (part.result as any).deleted;
      const filename = (part.result as any).filename;
      return deleted ? `Deleted ${filename}` : `Failed to delete ${filename}`;
    }
    
    if (part.toolName === "create_directory" && typeof part.result === "object") {
      const resultObj = part.result as any;
      if (resultObj.created) {
        return `Created directory ${resultObj.path}`;
      } else if (resultObj.exists) {
        return `Directory ${resultObj.path} already exists`;
      }
      return resultObj.message || "Directory operation completed";
    }

    if (hasArtifacts()) {
      const artifacts = getArtifacts();
      return `Generated ${artifacts.length} artifact${artifacts.length > 1 ? "s" : ""}`;
    }
    
    // Check for message field in result
    if (typeof part.result === "object" && part.result && 'message' in part.result) {
      return (part.result as any).message;
    }

    // Default summary - avoid showing raw JSON
    if (typeof part.result === "object" && part.result) {
      // Try to create a meaningful summary without showing JSON
      const keys = Object.keys(part.result);
      if (keys.length === 0) return "Completed";
      
      // Look for common success indicators
      const resultObj = part.result as any;
      if (resultObj.success === false) return resultObj.error || "Operation failed";
      if (resultObj.success === true) return resultObj.message || "Operation completed";
      
      // For unknown structures, just indicate completion
      return "Operation completed";
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
        "rounded-md border my-2",
        part.isError
          ? "border-destructive/50 bg-destructive/10 dark:bg-destructive/5"
          : "border-border bg-card/50 dark:bg-card/30"
      )}
    >
      {/* Compact header */}
      <div className="flex items-center gap-2 px-3 py-2">
        {/* Status Icon */}
        <div className="flex-shrink-0">
          {part.isError ? (
            <XCircle className="w-4 h-4 text-destructive" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-500" />
          )}
        </div>

        {/* Result summary */}
        <span className="text-sm font-medium flex-1 min-w-0">
          {getResultSummary()}
        </span>

        {/* Duration */}
        {part.duration && (
          <span className="text-xs text-muted-foreground flex-shrink-0">
            {(part.duration / 1000).toFixed(1)}s
          </span>
        )}

        {/* Expand button for details */}
        {(resultString.length > 100 || hasArtifacts()) && !shouldHideExpanded() && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0 flex-shrink-0"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </Button>
        )}
      </div>

      {/* File link for file operation results */}
      {isFileOperationResult && onArtifactSelect && (
        <div className="px-3 pb-2 border-t border-border/50">
          <div className="flex items-center gap-2 mt-2">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs px-2 text-primary hover:text-primary hover:bg-primary/10 flex-1 justify-start"
              onClick={() => handleArtifactClick((part.result as any).path)}
            >
              <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
              Open {(part.result as any).path}
            </Button>
          </div>
        </div>
      )}

      {/* Artifacts list (if any) */}
      {hasArtifacts() && onArtifactSelect && (
        <div className="px-3 pb-2 border-t border-border/50">
          <div className="mt-2">
            <span className="text-xs font-medium text-muted-foreground">Generated artifacts:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {getArtifacts().map((artifact: any, idx: number) => (
                <Button
                  key={idx}
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs px-2 text-primary hover:text-primary hover:bg-primary/10"
                  onClick={() =>
                    handleArtifactClick(artifact.path || artifact.name)
                  }
                >
                  <FileText className="w-3.5 h-3.5 mr-1" />
                  {artifact.name || artifact.path || `artifact-${idx + 1}`}
                </Button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Expanded content */}
      {isExpanded && !shouldHideExpanded() && (
        <div className="px-3 pb-3 border-t border-border">
          <div className="mt-2">
            {/* Special rendering for file content */}
            {part.toolName === "read_file" && typeof part.result === "string" ? (
              <div className="rounded-md bg-muted/50 dark:bg-muted/30 p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-muted-foreground">File Contents</span>
                  <Badge variant="secondary" className="text-xs">
                    {part.result.split('\n').length} lines
                  </Badge>
                </div>
                <pre className="text-xs overflow-x-auto max-h-96 font-mono">
                  <code>{part.result}</code>
                </pre>
              </div>
            ) : part.toolName === "list_files" && typeof part.result === "object" && 'files' in part.result ? (
              <div className="rounded-md bg-muted/50 dark:bg-muted/30 p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-muted-foreground">Files</span>
                  <Badge variant="secondary" className="text-xs">
                    {(part.result as any).count || (part.result as any).files.length} items
                  </Badge>
                </div>
                <div className="space-y-1">
                  {(part.result as any).files.map((file: any, idx: number) => (
                    <div key={idx} className="flex items-center gap-2 px-2 py-1 rounded hover:bg-background/50 text-sm group">
                      {file.type === "directory" ? (
                        <FolderOpen className="w-4 h-4 text-muted-foreground" />
                      ) : (
                        <FileText className="w-4 h-4 text-muted-foreground" />
                      )}
                      <span className="font-mono flex-1">{file.name}</span>
                      {file.size !== undefined && file.type !== "directory" && (
                        <span className="text-xs text-muted-foreground">
                          {formatFileSize(file.size)}
                        </span>
                      )}
                      {file.version_count && file.version_count > 1 && (
                        <Badge variant="outline" className="text-xs">
                          {file.version_count} versions
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : part.toolName === "search_memory" && typeof part.result === "object" && 'results' in part.result ? (
              <div className="rounded-md bg-muted/50 dark:bg-muted/30 p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Brain className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs font-medium text-muted-foreground">Memory Search Results</span>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {(part.result as any).count || 0} memories
                  </Badge>
                </div>
                {(part.result as any).results && (part.result as any).results.length > 0 ? (
                  <div className="space-y-2">
                    {(part.result as any).results.map((memory: any, idx: number) => (
                      <div key={idx} className="p-2 rounded bg-background/50 text-sm">
                        <div className="font-mono text-xs text-muted-foreground mb-1">
                          {new Date(memory.timestamp).toLocaleString()}
                        </div>
                        <div>{memory.content}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground italic">No memories found</div>
                )}
              </div>
            ) : part.toolName === "run_bash" && typeof part.result === "object" && 'output' in part.result ? (
              <div className="rounded-md bg-muted/50 dark:bg-muted/30 p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs font-medium text-muted-foreground">Command Output</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {(part.result as any).duration && (
                      <Badge variant="outline" className="text-xs">
                        {((part.result as any).duration / 1000).toFixed(2)}s
                      </Badge>
                    )}
                    {(part.result as any).exit_code !== undefined && (
                      <Badge 
                        variant={(part.result as any).exit_code === 0 ? "secondary" : "destructive"} 
                        className="text-xs"
                      >
                        Exit: {(part.result as any).exit_code}
                      </Badge>
                    )}
                  </div>
                </div>
                {(part.result as any).command && (
                  <div className="mb-2 p-2 bg-background/50 rounded">
                    <div className="text-xs text-muted-foreground mb-1">Command:</div>
                    <code className="text-xs font-mono">{(part.result as any).command}</code>
                  </div>
                )}
                <pre className="text-xs overflow-x-auto max-h-96 font-mono whitespace-pre-wrap bg-background/50 rounded p-2">
                  <code>{(part.result as any).output || (part.result as any).stdout || (part.result as any).stderr || "(no output)"}</code>
                </pre>
              </div>
            ) : (
              <div className="rounded-md bg-muted/50 dark:bg-muted/30 p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-muted-foreground">Result Details</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0"
                    onClick={() => {
                      navigator.clipboard.writeText(resultString);
                    }}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
                <pre className="text-xs overflow-x-auto max-h-64 font-mono">
                  {resultString}
                </pre>
              </div>
            )}
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
      <div className="rounded-md border border-border bg-muted/20 dark:bg-muted/10 p-3 my-2">
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
            className="max-w-full rounded-md border"
          />
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}

function ErrorPartComponent({ part }: { part: ErrorPart }) {
  return (
    <div className="rounded-md border border-destructive/50 bg-destructive/10 dark:bg-destructive/5 p-3 my-2">
      <div className="flex items-center gap-2">
        <XCircle className="w-4 h-4 text-destructive" />
        <span className="font-medium text-sm">Error</span>
        {part.errorCode && (
          <span className="text-xs text-muted-foreground">
            ({part.errorCode})
          </span>
        )}
      </div>
      <div className="mt-2 text-sm text-destructive">
        {part.error}
      </div>
    </div>
  );
}

// Helper function to format file sizes
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Main component
export function MessageParts({
  parts,
  isStreaming,
  onArtifactSelect,
}: MessagePartsProps) {
  if (!parts || parts.length === 0) return null;

  return (
    <div className="space-y-1">
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
