"use client";

import React, { useState } from "react";
import {
  Terminal,
  CheckCircle2,
  XCircle,
  Loader2,
  Clock,
  FileEdit,
  FileText,
  FileSearch,
  FolderOpen,
  Search,
  Database,
  Brain,
  Globe,
  ExternalLink,
  Copy,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { GenericMessagePart } from "./generic-message-part";
import type { ToolCallPart, ToolResultPart } from "./message-parts";

interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
  displayPath?: string;
}

// Helper function to format file sizes
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Tool icons mapping
const toolIcons = {
  write_file: FileEdit,
  append_file: FileEdit,
  edit_file: FileText,
  read_file: FileSearch,
  list_files: FolderOpen,
  list_directory: FolderOpen,
  search_files: Search,
  search_web: Search,
  add_memory: Brain,
  search_memory: Brain,
  store_artifact: Database,
  web_research: Globe,
  fetch_url: Globe,
  run_bash: Terminal,
  execute_command: Terminal,
};

// Get status icon based on status
function getStatusIcon(status?: string) {
  switch (status) {
    case "running":
      return <Loader2 className="w-3 h-3 animate-spin" />;
    case "completed":
      return <CheckCircle2 className="w-3 h-3" />;
    case "failed":
      return <XCircle className="w-3 h-3" />;
    default:
      return <Clock className="w-3 h-3" />;
  }
}

// Get status color based on status
function getStatusColor(status?: string) {
  switch (status) {
    case "running":
      return "text-yellow-500 dark:text-yellow-400";
    case "completed":
      return "text-green-500 dark:text-green-400";
    case "failed":
      return "text-red-500 dark:text-red-400";
    default:
      return "text-muted-foreground";
  }
}

// Tool Call Component
export function ToolCall({ 
  part,
  onArtifactSelect 
}: { 
  part: ToolCallPart;
  onArtifactSelect?: ((artifact: Artifact) => void) | null;
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Get tool call summary
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
  const Icon = toolIcons[part.toolName as keyof typeof toolIcons] || Terminal;

  const badges = [];
  if (part.duration) {
    badges.push({
      label: `${(part.duration / 1000).toFixed(1)}s`,
      variant: "outline" as const,
    });
  }

  return (
    <GenericMessagePart
      icon={Icon}
      title={part.toolName}
      summary={getToolCallSummary()}
      statusIcon={getStatusIcon(part.status)}
      statusClassName={getStatusColor(part.status)}
      badges={badges}
      expandable={hasDetailedArgs}
      expanded={isExpanded}
      onExpandedChange={setIsExpanded}
      expandedContent={
        hasDetailedArgs && (
          <pre className="text-xs p-2 rounded-md bg-muted/50 dark:bg-muted/30 overflow-x-auto">
            {JSON.stringify(part.args, null, 2)}
          </pre>
        )
      }
    />
  );
}

// Tool Result Component
export function ToolResult({ 
  part,
  onArtifactSelect 
}: { 
  part: ToolResultPart;
  onArtifactSelect?: ((artifact: Artifact) => void) | null;
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  
  const resultString = typeof part.result === "string" 
    ? part.result 
    : JSON.stringify(part.result, null, 2);
    
  // Check if we should hide the expanded view
  const shouldHideExpanded = () => {
    if (typeof part.result !== "object" || !part.result) return false;
    
    const toolsWithCleanResults = [
      "write_file", "edit_file", "append_file", "delete_file",
      "list_files", "file_exists", "create_directory",
      "add_memory", "search_memory", "list_memories",
      "store_artifact"
    ];
    
    return toolsWithCleanResults.includes(part.toolName);
  };
  
  // Check if this is a file operation result with a path
  const isFileOperationResult = 
    (part.toolName === "write_file" || part.toolName === "edit_file" || part.toolName === "append_file") && 
    typeof part.result === "object" && 
    part.result !== null &&
    'path' in part.result;
    
  // Get result summary
  const getResultSummary = () => {
    // Handle error results
    if (part.isError) {
      if (typeof part.result === "object" && part.result && 'error' in part.result) {
        return (part.result as any).error;
      }
      return "Operation failed";
    }
    
    // File operations
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
    
    // Read file
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
    
    // List files
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
    
    // Bash command
    if (part.toolName === "run_bash") {
      if (typeof part.result === "object" && part.result) {
        const resultObj = part.result as any;
        if ('exit_code' in resultObj) {
          return resultObj.exit_code === 0 
            ? "Command executed successfully" 
            : `Command failed (exit code: ${resultObj.exit_code})`;
        }
      }
      return "Command executed";
    }
    
    // Memory operations
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
    
    // Check for message field
    if (typeof part.result === "object" && part.result && 'message' in part.result) {
      return (part.result as any).message;
    }
    
    // Default - avoid showing raw JSON
    if (typeof part.result === "object" && part.result) {
      const keys = Object.keys(part.result);
      if (keys.length === 0) return "Completed";
      
      const resultObj = part.result as any;
      if (resultObj.success === false) return resultObj.error || "Operation failed";
      if (resultObj.success === true) return resultObj.message || "Operation completed";
      
      return "Operation completed";
    }
    
    const summary = resultString.length > 60 
      ? resultString.substring(0, 60) + "..." 
      : resultString;
    return summary.replace(/\n/g, " ");
  };
  
  const handleArtifactClick = (artifactPath: string) => {
    if (onArtifactSelect) {
      const artifact: Artifact = {
        path: artifactPath,
        type: "file" as const,
      };
      onArtifactSelect(artifact);
    }
  };
  
  const handleCopy = () => {
    navigator.clipboard.writeText(resultString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const badges = [];
  if (part.duration) {
    badges.push({
      label: `${(part.duration / 1000).toFixed(1)}s`,
      variant: "outline" as const,
    });
  }
  
  // File operation actions
  const fileActions = isFileOperationResult && onArtifactSelect && (
    <div className="flex items-center gap-2">
      <Button
        variant="ghost"
        size="sm"
        className="h-7 text-xs px-2 text-primary hover:text-primary hover:bg-primary/10 flex-1 justify-start"
        onClick={() => handleArtifactClick((part.result as any).path)}
      >
        <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
        View in workspace
      </Button>
      {(part.result as any).version && (
        <Badge variant="outline" className="text-xs">
          v{(part.result as any).version}
        </Badge>
      )}
    </div>
  );
  
  // Custom expanded content based on tool type
  const getExpandedContent = () => {
    // Read file - show file content
    if (part.toolName === "read_file" && typeof part.result === "string") {
      return (
        <div className="rounded-md bg-muted/50 dark:bg-muted/30 p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-muted-foreground">File Contents</span>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                {part.result.split('\n').length} lines
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={handleCopy}
              >
                {copied ? <CheckCircle2 className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
              </Button>
            </div>
          </div>
          <pre className="text-xs overflow-x-auto max-h-96 font-mono">
            <code>{part.result}</code>
          </pre>
        </div>
      );
    }
    
    // List files - show file list
    if ((part.toolName === "list_files" || part.toolName === "list_directory") && 
        typeof part.result === "object" && 
        'files' in part.result) {
      return (
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
      );
    }
    
    // Bash command output
    if (part.toolName === "run_bash" && typeof part.result === "object" && 'output' in part.result) {
      return (
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
      );
    }
    
    // Memory search results
    if (part.toolName === "search_memory" && typeof part.result === "object" && 'results' in part.result) {
      return (
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
      );
    }
    
    // Default: show raw result
    return (
      <div className="rounded-md bg-muted/50 dark:bg-muted/30 p-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-muted-foreground">Result Details</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={handleCopy}
          >
            {copied ? <CheckCircle2 className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
          </Button>
        </div>
        <pre className="text-xs overflow-x-auto max-h-64 font-mono">
          {resultString}
        </pre>
      </div>
    );
  };

  return (
    <GenericMessagePart
      variant={part.isError ? "error" : "default"}
      statusIcon={part.isError ? <XCircle className="w-4 h-4 text-destructive" /> : <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-500" />}
      title={part.toolName}
      summary={getResultSummary()}
      badges={badges}
      actions={fileActions}
      expandable={resultString.length > 100 && !shouldHideExpanded()}
      expanded={isExpanded}
      onExpandedChange={setIsExpanded}
      expandedContent={getExpandedContent()}
    />
  );
}