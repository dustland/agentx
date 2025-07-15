"use client";

import React, { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  FileText,
  Code,
  Activity,
  Download,
  Copy,
  FileIcon,
  FolderIcon,
  ChevronRightIcon,
  WrenchIcon,
  RefreshCwIcon,
  XIcon,
  ScrollIcon,
  Brain,
  Database,
  ListIcon,
  Eye,
  Target,
  Clock,
  XCircle,
  AlertTriangle,
  Info,
  Bug,
} from "lucide-react";
import { useAgentXAPI } from "@/lib/api-client";
import { formatBytes, formatDate } from "@/lib/utils";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
  displayPath?: string;
}

interface ToolCall {
  id: string;
  agent_id: string;
  tool_name: string;
  parameters: any;
  result?: any;
  timestamp: string;
  status: "pending" | "completed" | "failed";
}

interface TaskSpacePanelProps {
  taskId: string;
  onToolCallSelect?: (handler: (toolCall: ToolCall) => void) => void;
}

export function TaskSpacePanel({
  taskId,
  onToolCallSelect,
}: TaskSpacePanelProps) {
  const apiClient = useAgentXAPI();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(
    null
  );
  const [selectedToolCall, setSelectedToolCall] = useState<ToolCall | null>(
    null
  );
  const [loadingArtifacts, setLoadingArtifacts] = useState(false);
  const [activeTab, setActiveTab] = useState("artifacts");
  const [logs, setLogs] = useState<string[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [autoScrollLogs, setAutoScrollLogs] = useState(true);
  const [memories, setMemories] = useState<any[]>([]);
  const [loadingMemories, setLoadingMemories] = useState(false);
  const [planContent, setPlanContent] = useState<string | null>(null);
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [hasPlan, setHasPlan] = useState(false);

  // Load artifacts
  useEffect(() => {
    if (!taskId) return;

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

        // Check for plan.json in root directory and load it if found
        const planArtifact = response.artifacts.find(
          (artifact: Artifact) =>
            artifact.path === "plan.json" && artifact.type === "file"
        );

        setHasPlan(!!planArtifact);

        // Only show plan tab if plan.json exists, but don't try to load it
        // to avoid 404 errors in console
        if (planArtifact) {
          setLoadingPlan(false);
          // We know the plan exists but won't load it until user clicks the tab
          // This avoids unnecessary 404 errors for files that may not be accessible
        } else {
          setPlanContent(null);
          setLoadingPlan(false);
        }
      } catch (error) {
        console.error("Failed to load artifacts:", error);
      } finally {
        setLoadingArtifacts(false);
      }
    };

    loadArtifacts();
  }, [taskId, apiClient]);

  // Load logs
  useEffect(() => {
    if (!taskId || activeTab !== "logs") return;

    const loadLogs = async () => {
      setLoadingLogs(true);
      try {
        const response = await apiClient.getTaskLogs(taskId);
        setLogs(response.logs);
      } catch (error) {
        console.error("Failed to load logs:", error);
      } finally {
        setLoadingLogs(false);
      }
    };

    loadLogs();

    // Refresh logs every 2 seconds when tab is active
    const interval = setInterval(loadLogs, 2000);
    return () => clearInterval(interval);
  }, [taskId, activeTab, apiClient]);

  // Load memories
  useEffect(() => {
    if (!taskId || activeTab !== "memory") return;

    const loadMemories = async () => {
      setLoadingMemories(true);
      try {
        const response = await apiClient.searchMemory(taskId, {
          query: "",
          limit: 100,
        });
        setMemories(response);
      } catch (error) {
        console.error("Failed to load memories:", error);
        // For now, show mock data if API fails
        setMemories([]);
      } finally {
        setLoadingMemories(false);
      }
    };

    loadMemories();
  }, [taskId, activeTab, apiClient]);

  // Load plan content function
  const loadPlan = async () => {
    setLoadingPlan(true);
    try {
      const planResponse = await apiClient.getArtifactContent(
        taskId,
        "plan.json"
      );
      setPlanContent(planResponse.content);
    } catch (error) {
      // Silently handle error - don't log to console
      setPlanContent(null);
    } finally {
      setLoadingPlan(false);
    }
  };

  // Load plan content when Plan tab is selected
  useEffect(() => {
    if (!taskId || activeTab !== "plan" || !hasPlan || planContent !== null)
      return;

    loadPlan();
  }, [taskId, activeTab, hasPlan, planContent, apiClient]);

  // Handle external tool call selection
  useEffect(() => {
    if (onToolCallSelect) {
      // Listen for tool call selections from the chat zone
      const handleToolCall = (toolCall: ToolCall) => {
        setSelectedToolCall(toolCall);
        setActiveTab("viewer");
      };

      // Register the handler
      onToolCallSelect(handleToolCall);
    }
  }, [onToolCallSelect]);

  // Load artifact content
  const loadArtifactContent = async (artifact: Artifact) => {
    try {
      const response = await apiClient.getArtifactContent(
        taskId,
        artifact.path
      );

      if (response.is_binary) {
        // Handle binary files
        setSelectedArtifact({
          ...artifact,
          content: "[Binary file - cannot display content]",
        });
      } else {
        setSelectedArtifact({
          ...artifact,
          content: response.content || "",
        });
      }
      setActiveTab("viewer");
    } catch (error) {
      console.error("Failed to load artifact content:", error);
    }
  };

  const getFileIcon = (path: string, type: string) => {
    if (type === "directory") return <FolderIcon className="w-4 h-4" />;
    if (path.endsWith(".py") || path.endsWith(".js") || path.endsWith(".ts")) {
      return <Code className="w-4 h-4" />;
    }
    return <FileIcon className="w-4 h-4" />;
  };

  const getFileLanguage = (path: string): string => {
    const ext = path.split(".").pop() || "";
    const langMap: Record<string, string> = {
      py: "python",
      js: "javascript",
      ts: "typescript",
      jsx: "jsx",
      tsx: "tsx",
      md: "markdown",
      json: "json",
      yaml: "yaml",
      yml: "yaml",
      html: "html",
      css: "css",
      sh: "bash",
      sql: "sql",
    };
    return langMap[ext] || "text";
  };

  return (
    <div className="h-full flex flex-col py-3 px-2">
      <Card className="flex-1 flex flex-col p-1 rounded-2xl">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="flex-1 flex flex-col"
        >
          {/* Shared Tab Header */}
          <CardHeader className="pb-2 pt-2">
            <div className="flex items-center justify-between">
              <TabsList className="h-8 bg-transparent">
                <TabsTrigger value="artifacts" className="text-xs gap-1 py-1">
                  <FileText className="h-3 w-3" />
                  Artifacts
                  {artifacts.length > 0 && (
                    <Badge
                      variant="secondary"
                      className="ml-1 h-3 px-1 text-xs"
                    >
                      {artifacts.length}
                    </Badge>
                  )}
                </TabsTrigger>
                <TabsTrigger value="viewer" className="text-xs gap-1 py-1">
                  <Eye className="h-3 w-3" />
                  Viewer
                  {(selectedArtifact || selectedToolCall) && (
                    <Badge
                      variant="secondary"
                      className="ml-1 h-3 px-1 text-xs"
                    >
                      •
                    </Badge>
                  )}
                </TabsTrigger>
                {hasPlan && (
                  <TabsTrigger value="plan" className="text-xs gap-1 py-1">
                    <Target className="h-3 w-3" />
                    Plan
                  </TabsTrigger>
                )}
                <TabsTrigger value="memory" className="text-xs gap-1 py-1">
                  <Brain className="h-3 w-3" />
                  Memory
                </TabsTrigger>
                <TabsTrigger value="logs" className="text-xs gap-1 py-1">
                  <ScrollIcon className="h-3 w-3" />
                  Logs
                  {logs.length > 0 && (
                    <Badge
                      variant="secondary"
                      className="ml-1 h-3 px-1 text-xs"
                    >
                      {logs.length}
                    </Badge>
                  )}
                </TabsTrigger>
              </TabsList>
              <div className="flex items-center gap-2">
                {/* Tab-specific actions */}
                {activeTab === "artifacts" && (
                  <Button size="sm" variant="ghost" disabled={loadingArtifacts}>
                    <RefreshCwIcon
                      className={`h-4 w-4 ${
                        loadingArtifacts ? "animate-spin" : ""
                      }`}
                    />
                  </Button>
                )}
                {activeTab === "plan" && (
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={loadingPlan}
                    onClick={loadPlan}
                  >
                    <RefreshCwIcon
                      className={`h-4 w-4 ${loadingPlan ? "animate-spin" : ""}`}
                    />
                  </Button>
                )}
                {activeTab === "viewer" && selectedArtifact && (
                  <>
                    <Button size="sm" variant="ghost">
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="ghost">
                      <Copy className="h-4 w-4" />
                    </Button>
                  </>
                )}
                {activeTab === "viewer" && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setSelectedArtifact(null);
                      setSelectedToolCall(null);
                    }}
                  >
                    <XIcon className="h-4 w-4" />
                  </Button>
                )}
                {activeTab === "memory" && (
                  <Button size="sm" variant="ghost" disabled={loadingMemories}>
                    <RefreshCwIcon
                      className={`h-4 w-4 ${
                        loadingMemories ? "animate-spin" : ""
                      }`}
                    />
                  </Button>
                )}
                {activeTab === "logs" && (
                  <>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setAutoScrollLogs(!autoScrollLogs)}
                      className={
                        autoScrollLogs
                          ? "text-primary"
                          : "text-muted-foreground"
                      }
                    >
                      <Activity className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="ghost" disabled={loadingLogs}>
                      <RefreshCwIcon
                        className={`h-4 w-4 ${
                          loadingLogs ? "animate-spin" : ""
                        }`}
                      />
                    </Button>
                  </>
                )}
              </div>
            </div>
          </CardHeader>
          {/* Artifacts Tab */}
          <TabsContent value="artifacts" className="flex-1 p-2 m-0">
            <ScrollArea className="h-[calc(100vh-280px)]">
              {artifacts.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">
                  <FileText className="w-6 h-6 mx-auto mb-2" />
                  <p>No artifacts generated yet</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {artifacts.map((artifact, idx) => (
                    <div
                      key={idx}
                      className="p-2 rounded-lg cursor-pointer hover:bg-accent/50 transition-colors border"
                      onClick={() =>
                        artifact.type === "file" &&
                        loadArtifactContent(artifact)
                      }
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 flex-1">
                          {getFileIcon(
                            artifact.displayPath || artifact.path,
                            artifact.type
                          )}
                          <span className="text-sm font-medium truncate">
                            {(artifact.displayPath || artifact.path)
                              .split("/")
                              .pop()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          {artifact.size && (
                            <span className="text-xs text-muted-foreground">
                              {formatBytes(artifact.size)}
                            </span>
                          )}
                          {artifact.type === "file" && (
                            <ChevronRightIcon className="w-4 h-4 text-muted-foreground" />
                          )}
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {artifact.displayPath || artifact.path}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          {/* Plan Tab */}
          {hasPlan && (
            <TabsContent value="plan" className="flex-1 p-2 m-0">
              <ScrollArea className="h-[calc(100vh-280px)]">
                {loadingPlan ? (
                  <div className="text-center py-6 text-muted-foreground">
                    <RefreshCwIcon className="w-6 h-6 mx-auto mb-2 animate-spin" />
                    <p>Loading plan...</p>
                  </div>
                ) : planContent ? (
                  <div className="relative">
                    <SyntaxHighlighter
                      language="json"
                      style={vscDarkPlus}
                      customStyle={{
                        margin: 0,
                        fontSize: "0.875rem",
                        borderRadius: "0.375rem",
                      }}
                    >
                      {planContent}
                    </SyntaxHighlighter>
                  </div>
                ) : (
                  <div className="text-center py-6 text-muted-foreground">
                    <ListIcon className="w-6 h-6 mx-auto mb-2" />
                    <p>No plan content available</p>
                  </div>
                )}
              </ScrollArea>
            </TabsContent>
          )}

          {/* Viewer Tab */}
          <TabsContent value="viewer" className="flex-1 p-2 m-0">
            <ScrollArea className="h-[calc(100vh-280px)]">
              {selectedToolCall ? (
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium mb-2">Agent</h4>
                    <Badge variant="outline">{selectedToolCall.agent_id}</Badge>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium mb-2">Parameters</h4>
                    <pre className="text-xs bg-muted p-3 rounded overflow-x-auto">
                      {JSON.stringify(selectedToolCall.parameters, null, 2)}
                    </pre>
                  </div>
                  {selectedToolCall.result && (
                    <div>
                      <h4 className="text-sm font-medium mb-2">Result</h4>
                      <pre className="text-xs bg-muted p-3 rounded overflow-x-auto">
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
                          : selectedToolCall.status === "failed"
                          ? "destructive"
                          : "secondary"
                      }
                    >
                      {selectedToolCall.status}
                    </Badge>
                  </div>
                </div>
              ) : selectedArtifact?.content ? (
                <div className="relative">
                  {selectedArtifact.path.endsWith(".md") ? (
                    <div className="prose prose-sm dark:prose-invert max-w-none">
                      <pre className="whitespace-pre-wrap">
                        {selectedArtifact.content}
                      </pre>
                    </div>
                  ) : (
                    <SyntaxHighlighter
                      language={getFileLanguage(selectedArtifact.path)}
                      style={vscDarkPlus}
                      customStyle={{
                        margin: 0,
                        fontSize: "0.875rem",
                        borderRadius: "0.375rem",
                      }}
                    >
                      {selectedArtifact.content}
                    </SyntaxHighlighter>
                  )}
                </div>
              ) : (
                <div className="text-center py-6 text-muted-foreground">
                  <FileText className="w-6 h-6 mx-auto mb-2" />
                  <p>Select an artifact or tool call to view details</p>
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          {/* Memory Tab */}
          <TabsContent value="memory" className="flex-1 p-2 m-0">
            <ScrollArea className="h-[calc(100vh-280px)]">
              {memories.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">
                  <Brain className="w-6 h-6 mx-auto mb-2 opacity-50" />
                  <p>No memories stored yet</p>
                  <p className="text-xs mt-2">
                    Memories will appear as agents store information during task
                    execution
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
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
          </TabsContent>

          {/* Logs Tab */}
          <TabsContent value="logs" className="flex-1 m-0">
            <div className="h-full flex flex-col">
              <ScrollArea className="flex-1">
                {logs.length === 0 ? (
                  <div className="text-center py-6 text-muted-foreground">
                    <ScrollIcon className="w-6 h-6 mx-auto mb-2" />
                    <p>No logs available yet</p>
                  </div>
                ) : (
                  <div className="font-mono text-xs space-y-0 p-2">
                    {logs.map((log, idx) => {
                      // Parse log entry components
                      const logMatch = log.match(
                        /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - ([^-]+) - (ERROR|WARN|INFO|DEBUG) - (.+)$/
                      );

                      if (logMatch) {
                        const [, timestamp, source, level, message] = logMatch;
                        const isError = level === "ERROR";
                        const isWarning = level === "WARN";
                        const isInfo = level === "INFO";
                        const isDebug = level === "DEBUG";

                        return (
                          <TooltipProvider key={idx}>
                            <div className="flex items-start gap-2 py-1 hover:bg-muted/50 rounded px-2 -mx-2">
                              {/* Time Icon */}
                              <div className="flex-shrink-0 mt-0.5">
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <Clock className="w-3 h-3 text-muted-foreground" />
                                  </TooltipTrigger>
                                  <TooltipContent>
                                    <p>{timestamp}</p>
                                  </TooltipContent>
                                </Tooltip>
                              </div>

                              {/* Source Icon */}
                              <div className="flex-shrink-0 mt-0.5">
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <Code className="w-3 h-3 text-muted-foreground" />
                                  </TooltipTrigger>
                                  <TooltipContent>
                                    <p>{source}</p>
                                  </TooltipContent>
                                </Tooltip>
                              </div>

                              {/* Level Icon */}
                              <div className="flex-shrink-0 mt-0.5">
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    {isError && (
                                      <XCircle className="w-3 h-3 text-red-500" />
                                    )}
                                    {isWarning && (
                                      <AlertTriangle className="w-3 h-3 text-yellow-500" />
                                    )}
                                    {isInfo && (
                                      <Info className="w-3 h-3 text-blue-500" />
                                    )}
                                    {isDebug && (
                                      <Bug className="w-3 h-3 text-gray-500" />
                                    )}
                                  </TooltipTrigger>
                                  <TooltipContent>
                                    <p>{level}</p>
                                  </TooltipContent>
                                </Tooltip>
                              </div>

                              {/* Message */}
                              <div
                                className={`
                                flex-1 whitespace-pre-wrap break-all
                                ${isError ? "text-red-500" : ""}
                                ${isWarning ? "text-yellow-500" : ""}
                                ${isInfo ? "text-blue-500" : ""}
                                ${isDebug ? "text-gray-500" : ""}
                                ${
                                  !isError && !isWarning && !isInfo && !isDebug
                                    ? "text-foreground"
                                    : ""
                                }
                              `}
                              >
                                {message}
                              </div>
                            </div>
                          </TooltipProvider>
                        );
                      } else {
                        // Fallback for logs that don't match the expected format
                        const isError =
                          log.toLowerCase().includes("error") ||
                          log.includes("ERROR");
                        const isWarning =
                          log.toLowerCase().includes("warn") ||
                          log.includes("WARN");
                        const isInfo =
                          log.toLowerCase().includes("info") ||
                          log.includes("INFO");
                        const isDebug =
                          log.toLowerCase().includes("debug") ||
                          log.includes("DEBUG");

                        return (
                          <div
                            key={idx}
                            className={`
                              whitespace-pre-wrap break-all py-1 px-2 hover:bg-muted/50 rounded
                              ${isError ? "text-red-500" : ""}
                              ${isWarning ? "text-yellow-500" : ""}
                              ${isInfo ? "text-blue-500" : ""}
                              ${isDebug ? "text-gray-500" : ""}
                              ${
                                !isError && !isWarning && !isInfo && !isDebug
                                  ? "text-foreground"
                                  : ""
                              }
                            `}
                          >
                            {log}
                          </div>
                        );
                      }
                    })}
                  </div>
                )}
              </ScrollArea>
            </div>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
}
