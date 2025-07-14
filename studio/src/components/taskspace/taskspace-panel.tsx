"use client";

import React, { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  ListIcon
} from "lucide-react";
import { useAgentXAPI } from "@/lib/api-client";
import { formatBytes, formatDate } from "@/lib/utils";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface Artifact {
  path: string;
  type: 'file' | 'directory';
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
}

interface ToolCall {
  id: string;
  agent_id: string;
  tool_name: string;
  parameters: any;
  result?: any;
  timestamp: string;
  status: 'pending' | 'completed' | 'error';
}

interface TaskSpacePanelProps {
  taskId: string;
  onToolCallSelect?: (handler: (toolCall: ToolCall) => void) => void;
}

export function TaskSpacePanel({ taskId, onToolCallSelect }: TaskSpacePanelProps) {
  const apiClient = useAgentXAPI();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null);
  const [selectedToolCall, setSelectedToolCall] = useState<ToolCall | null>(null);
  const [loadingArtifacts, setLoadingArtifacts] = useState(false);
  const [activeTab, setActiveTab] = useState("artifacts");
  const [logs, setLogs] = useState<string[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [autoScrollLogs, setAutoScrollLogs] = useState(true);
  const [memories, setMemories] = useState<any[]>([]);
  const [loadingMemories, setLoadingMemories] = useState(false);
  const [planContent, setPlanContent] = useState<string | null>(null);
  const [loadingPlan, setLoadingPlan] = useState(false);

  // Load artifacts
  useEffect(() => {
    if (!taskId) return;

    const loadArtifacts = async () => {
      setLoadingArtifacts(true);
      try {
        const response = await apiClient.getTaskArtifacts(taskId);
        setArtifacts(response.artifacts);
        
        // Check for plan.json
        const planArtifact = response.artifacts.find((artifact: Artifact) => 
          artifact.path === 'plan.json' && artifact.type === 'file'
        );
        
        if (planArtifact) {
          loadPlanContent();
        } else {
          setPlanContent(null);
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
    if (!taskId || activeTab !== 'logs') return;

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
    if (!taskId || activeTab !== 'memory') return;

    const loadMemories = async () => {
      setLoadingMemories(true);
      try {
        const response = await apiClient.searchMemory(taskId, { query: '', limit: 100 });
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

  // Load plan content
  const loadPlanContent = async () => {
    if (!taskId) return;
    
    setLoadingPlan(true);
    try {
      const response = await apiClient.getArtifactContent(taskId, 'plan.json');
      setPlanContent(response.content);
    } catch (error) {
      console.error("Failed to load plan content:", error);
      setPlanContent(null);
    } finally {
      setLoadingPlan(false);
    }
  };

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
      const response = await apiClient.getArtifactContent(taskId, artifact.path);
      
      if (response.is_binary) {
        // Handle binary files
        setSelectedArtifact({
          ...artifact,
          content: "[Binary file - cannot display content]"
        });
      } else {
        setSelectedArtifact({
          ...artifact,
          content: response.content || ''
        });
      }
      setActiveTab("viewer");
    } catch (error) {
      console.error("Failed to load artifact content:", error);
    }
  };

  const getFileIcon = (path: string, type: string) => {
    if (type === 'directory') return <FolderIcon className="w-4 h-4" />;
    if (path.endsWith('.py') || path.endsWith('.js') || path.endsWith('.ts')) {
      return <Code className="w-4 h-4" />;
    }
    return <FileIcon className="w-4 h-4" />;
  };

  const getFileLanguage = (path: string): string => {
    const ext = path.split('.').pop() || '';
    const langMap: Record<string, string> = {
      'py': 'python',
      'js': 'javascript',
      'ts': 'typescript',
      'jsx': 'jsx',
      'tsx': 'tsx',
      'md': 'markdown',
      'json': 'json',
      'yaml': 'yaml',
      'yml': 'yaml',
      'html': 'html',
      'css': 'css',
      'sh': 'bash',
      'sql': 'sql'
    };
    return langMap[ext] || 'text';
  };

  // Check if plan.json exists in artifacts
  const hasPlan = artifacts.some(artifact => artifact.path === 'plan.json' && artifact.type === 'file');

  return (
    <div className="h-full flex flex-col bg-card">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="px-4 pt-3">
          <TabsList className="h-9 bg-transparent">
            <TabsTrigger value="artifacts" className="text-xs gap-1.5">
              <FileText className="h-3 w-3" />
              Artifacts
              {artifacts.length > 0 && (
                <Badge variant="secondary" className="ml-1 h-4 px-1 text-xs">
                  {artifacts.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="viewer" className="text-xs gap-1.5">
              <Code className="h-3 w-3" />
              Viewer
              {(selectedArtifact || selectedToolCall) && (
                <Badge variant="secondary" className="ml-1 h-4 px-1 text-xs">
                  •
                </Badge>
              )}
            </TabsTrigger>
            {hasPlan && (
              <TabsTrigger value="plan" className="text-xs gap-1.5">
                <ListIcon className="h-3 w-3" />
                Plan
              </TabsTrigger>
            )}
            <TabsTrigger value="memory" className="text-xs gap-1.5">
              <Brain className="h-3 w-3" />
              Memory
            </TabsTrigger>
            <TabsTrigger value="logs" className="text-xs gap-1.5">
              <ScrollIcon className="h-3 w-3" />
              Logs
              {logs.length > 0 && (
                <Badge variant="secondary" className="ml-1 h-4 px-1 text-xs">
                  {logs.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>
        </div>

        {/* Artifacts Tab */}
        <TabsContent value="artifacts" className="flex-1 p-4 m-0">
          <Card className="h-full">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Taskspace Artifacts</CardTitle>
                <Button size="sm" variant="ghost" disabled={loadingArtifacts}>
                  <RefreshCwIcon className={`h-4 w-4 ${loadingArtifacts ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-300px)]">
                {artifacts.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <FileText className="w-8 h-8 mx-auto mb-2" />
                    <p>No artifacts generated yet</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {artifacts.map((artifact, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-lg cursor-pointer hover:bg-accent/50 transition-colors border"
                        onClick={() => artifact.type === 'file' && loadArtifactContent(artifact)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 flex-1">
                            {getFileIcon(artifact.path, artifact.type)}
                            <span className="text-sm font-medium truncate">
                              {artifact.path.split('/').pop()}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            {artifact.size && (
                              <span className="text-xs text-muted-foreground">
                                {formatBytes(artifact.size)}
                              </span>
                            )}
                            {artifact.type === 'file' && (
                              <ChevronRightIcon className="w-4 h-4 text-muted-foreground" />
                            )}
                          </div>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {artifact.path}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Plan Tab */}
        {hasPlan && (
          <TabsContent value="plan" className="flex-1 p-4 m-0">
            <Card className="h-full">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Task Plan</CardTitle>
                  <Button size="sm" variant="ghost" disabled={loadingPlan} onClick={loadPlanContent}>
                    <RefreshCwIcon className={`h-4 w-4 ${loadingPlan ? 'animate-spin' : ''}`} />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[calc(100vh-300px)]">
                  {loadingPlan ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <RefreshCwIcon className="w-8 h-8 mx-auto mb-2 animate-spin" />
                      <p>Loading plan...</p>
                    </div>
                  ) : planContent ? (
                    <div className="relative">
                      <SyntaxHighlighter
                        language="json"
                        style={vscDarkPlus}
                        customStyle={{
                          margin: 0,
                          fontSize: '0.875rem',
                          borderRadius: '0.375rem'
                        }}
                      >
                        {planContent}
                      </SyntaxHighlighter>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <ListIcon className="w-8 h-8 mx-auto mb-2" />
                      <p>No plan content available</p>
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {/* Viewer Tab */}
        <TabsContent value="viewer" className="flex-1 p-4 m-0">
          <Card className="h-full">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">
                  {selectedToolCall ? (
                    <div className="flex items-center gap-2">
                      <WrenchIcon className="w-4 h-4" />
                      Tool: {selectedToolCall.tool_name}
                    </div>
                  ) : selectedArtifact ? (
                    <div className="flex items-center gap-2">
                      {getFileIcon(selectedArtifact.path, selectedArtifact.type)}
                      {selectedArtifact.path.split('/').pop()}
                    </div>
                  ) : (
                    'Viewer'
                  )}
                </CardTitle>
                <div className="flex items-center gap-2">
                  {selectedArtifact && (
                    <>
                      <Button size="sm" variant="ghost">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="ghost">
                        <Copy className="h-4 w-4" />
                      </Button>
                    </>
                  )}
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
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-300px)]">
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
                          {typeof selectedToolCall.result === 'string' 
                            ? selectedToolCall.result 
                            : JSON.stringify(selectedToolCall.result, null, 2)}
                        </pre>
                      </div>
                    )}
                    <div>
                      <h4 className="text-sm font-medium mb-2">Status</h4>
                      <Badge variant={
                        selectedToolCall.status === 'completed' ? 'default' :
                        selectedToolCall.status === 'error' ? 'destructive' : 'secondary'
                      }>
                        {selectedToolCall.status}
                      </Badge>
                    </div>
                  </div>
                ) : selectedArtifact?.content ? (
                  <div className="relative">
                    {selectedArtifact.path.endsWith('.md') ? (
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <pre className="whitespace-pre-wrap">{selectedArtifact.content}</pre>
                      </div>
                    ) : (
                      <SyntaxHighlighter
                        language={getFileLanguage(selectedArtifact.path)}
                        style={vscDarkPlus}
                        customStyle={{
                          margin: 0,
                          fontSize: '0.875rem',
                          borderRadius: '0.375rem'
                        }}
                      >
                        {selectedArtifact.content}
                      </SyntaxHighlighter>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <FileText className="w-8 h-8 mx-auto mb-2" />
                    <p>Select an artifact or tool call to view details</p>
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Memory Tab */}
        <TabsContent value="memory" className="flex-1 p-4 m-0">
          <Card className="h-full">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Task Memory</CardTitle>
                <Button size="sm" variant="ghost" disabled={loadingMemories}>
                  <RefreshCwIcon className={`h-4 w-4 ${loadingMemories ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-300px)]">
                {memories.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>No memories stored yet</p>
                    <p className="text-xs mt-2">Memories will appear as agents store information during task execution</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {memories.map((memory, idx) => (
                      <Card key={idx} className="p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Database className="w-4 h-4 text-muted-foreground" />
                            <span className="font-medium text-sm">{memory.agent_id || 'System'}</span>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {memory.type || 'general'}
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
            </CardContent>
          </Card>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs" className="flex-1 p-4 m-0">
          <Card className="h-full">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Execution Logs</CardTitle>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setAutoScrollLogs(!autoScrollLogs)}
                    className={autoScrollLogs ? "text-primary" : "text-muted-foreground"}
                  >
                    <Activity className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="ghost" disabled={loadingLogs}>
                    <RefreshCwIcon className={`h-4 w-4 ${loadingLogs ? 'animate-spin' : ''}`} />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-300px)]">
                {logs.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <ScrollIcon className="w-8 h-8 mx-auto mb-2" />
                    <p>No logs available yet</p>
                  </div>
                ) : (
                  <div className="font-mono text-xs space-y-0.5">
                    {logs.map((log, idx) => {
                      // Parse log level and colorize
                      const isError = log.toLowerCase().includes('error') || log.includes('ERROR');
                      const isWarning = log.toLowerCase().includes('warn') || log.includes('WARN');
                      const isInfo = log.toLowerCase().includes('info') || log.includes('INFO');
                      const isDebug = log.toLowerCase().includes('debug') || log.includes('DEBUG');
                      
                      return (
                        <div
                          key={idx}
                          className={`
                            whitespace-pre-wrap break-all
                            ${isError ? 'text-red-500' : ''}
                            ${isWarning ? 'text-yellow-500' : ''}
                            ${isInfo ? 'text-blue-500' : ''}
                            ${isDebug ? 'text-gray-500' : ''}
                            ${!isError && !isWarning && !isInfo && !isDebug ? 'text-foreground' : ''}
                          `}
                        >
                          {log}
                        </div>
                      );
                    })}
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}