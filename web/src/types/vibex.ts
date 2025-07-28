/**
 * Comprehensive types for VibeX API matching the backend schema
 * Inspired by Vercel AI SDK's message structure
 */

// Base message content types
export type TextContent = {
  type: "text";
  text: string;
};

export type ImageContent = {
  type: "image";
  image: string | Uint8Array; // URL or base64 encoded image
  mimeType?: string;
};

export type ToolCallContent = {
  type: "tool-call";
  toolCallId: string;
  toolName: string;
  args: Record<string, any>;
};

export type ToolResultContent = {
  type: "tool-result";
  toolCallId: string;
  toolName: string;
  result: any;
  isError?: boolean;
};

// Union type for all content types
export type MessageContent =
  | TextContent
  | ImageContent
  | ToolCallContent
  | ToolResultContent;

// Message roles
export type MessageRole = "system" | "user" | "assistant" | "tool";

// Core message interface
export interface Message {
  id: string;
  role: MessageRole;
  content: string | MessageContent | MessageContent[];
  name?: string; // For multi-agent scenarios
  timestamp: string;
  metadata?: MessageMetadata;
}

// Message metadata
export interface MessageMetadata {
  agentId?: string;
  agentName?: string;
  model?: string;
  finishReason?: "stop" | "length" | "tool-calls" | "content-filter" | "error";
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

// Tool definition
export interface Tool {
  type: "function";
  function: {
    name: string;
    description?: string;
    parameters?: Record<string, any>; // JSON Schema
  };
}

// Project-related types
export interface Project {
  project_id: string;
  name?: string;
  goal?: string;
  status: ProjectStatus;
  config_path: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  error?: string;
  result?: Record<string, any>;
  user_id?: string;
  context?: Record<string, any>;
  plan?: Plan;
}

export type ProjectStatus = "pending" | "running" | "completed" | "error";

// Plan and Task types (tasks are execution units within a plan)
export interface Plan {
  tasks: Task[];
  created_at?: string;
  updated_at?: string;
  version: number;
}

export interface Task {
  id: string;
  action: string;
  status: TaskStatus;
  dependencies: string[];
  result?: string;
  assigned_to?: string;
}

export type TaskStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "error";

export interface CreateXAgentRequest {
  goal: string;
  config_path: string;
  context?: object;
  user_id?: string;
}

export interface XAgent {
  xagent_id: string;
  name?: string;
  status: TaskStatus;
  goal?: string;
  result?: any;
  error?: string;
  created_at?: string;
  completed_at?: string;
  user_id?: string;
  config_path?: string;
  context?: any;
  plan?: any;
}

export interface XAgentListResponse {
  xagents: XAgent[];
}

// API request/response types
export interface CreateProjectRequest {
  goal: string;
  config_path: string;
  context?: Record<string, any>;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

export interface MessagesResponse {
  messages: Message[];
}

export interface SendMessageRequest {
  content: string | MessageContent | MessageContent[];
  role?: MessageRole;
  name?: string;
  mode?: "agent" | "chat"; // Execution mode: agent (multi-agent with plan) or chat (direct response)
}

// Streaming event types
export type StreamEventType =
  | "message" // Complete Message object
  | "agent_message" // Legacy format (deprecated)
  | "tool_call" // Tool call events
  | "tool_call_start"
  | "tool_call_result"
  | "agent_status"
  | "project_update"
  | "task_progress" // Progress of individual tasks within the project
  | "artifact_created"
  | "artifact_updated"
  | "memory_updated"
  | "log_entry"
  | "error";

export interface StreamEvent {
  type: StreamEventType;
  data: any;
  timestamp?: string;
}

// Specific stream event data types
export interface AgentMessageEvent {
  xagent_id: string;
  message: string;
  message_id?: string;
  timestamp?: string;
  content?: MessageContent | MessageContent[];
  metadata?: MessageMetadata;
}

export interface ToolCallStartEvent {
  xagent_id: string;
  tool_call_id: string;
  tool_name: string;
  args: Record<string, any>;
}

export interface ToolCallResultEvent {
  xagent_id: string;
  tool_call_id: string;
  tool_name: string;
  result: any;
  is_error?: boolean;
}

export interface AgentStatusEvent {
  xagent_id: string;
  status: "idle" | "thinking" | "working" | "waiting";
  message?: string;
}

export interface ProjectUpdateEvent {
  status: ProjectStatus;
  message?: string;
  progress?: number;
}

export interface TaskProgressEvent {
  task_id: string;
  task_name: string;
  status: TaskStatus;
  message?: string;
}

export interface StreamChunkEvent {
  message_id: string;
  chunk: string;
  is_final: boolean;
  timestamp: string;
  error?: string; // Optional error message
}

// Artifact types
export interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  created_at?: string;
  updated_at?: string;
  displayPath?: string; // Frontend-specific display path
}

export interface ArtifactContent {
  path: string;
  content: string | null;
  is_binary?: boolean;
  size: number;
}

// Memory types
export interface MemoryContent {
  content: string;
  metadata?: {
    timestamp?: string;
    source?: string;
    [key: string]: any;
  };
}

export interface MemorySearchRequest {
  xagent_id: string;
  query: string;
  limit?: number;
}

// Backward compatibility aliases
export type TaskRun = XAgent;
export type TaskRunListResponse = XAgentListResponse;

export interface MemorySearchResult {
  content: string;
  score: number;
  metadata?: Record<string, any>;
}

// Log types
export interface LogEntry {
  timestamp: string;
  level: "DEBUG" | "INFO" | "WARN" | "ERROR";
  source: string;
  message: string;
  metadata?: Record<string, any>;
}

export interface LogsResponse {
  logs: string[];
  total: number;
  offset: number;
  limit: number;
  file_size?: number;
  mode?: "full" | "chunked" | "tail";
  has_more?: boolean;
}

// Helper functions to work with messages
export function isTextContent(content: MessageContent): content is TextContent {
  return content.type === "text";
}

export function isToolCallContent(
  content: MessageContent
): content is ToolCallContent {
  return content.type === "tool-call";
}

export function isToolResultContent(
  content: MessageContent
): content is ToolResultContent {
  return content.type === "tool-result";
}

export function getMessageText(message: Message): string {
  if (typeof message.content === "string") {
    return message.content;
  }

  if (Array.isArray(message.content)) {
    return message.content
      .filter(isTextContent)
      .map((c) => c.text)
      .join("\n");
  }

  if (isTextContent(message.content)) {
    return message.content.text;
  }

  return "";
}

export function getToolCalls(message: Message): ToolCallContent[] {
  if (!message.content || typeof message.content === "string") {
    return [];
  }

  if (Array.isArray(message.content)) {
    return message.content.filter(isToolCallContent);
  }

  if (isToolCallContent(message.content)) {
    return [message.content];
  }

  return [];
}

export function getToolResults(message: Message): ToolResultContent[] {
  if (!message.content || typeof message.content === "string") {
    return [];
  }

  if (Array.isArray(message.content)) {
    return message.content.filter(isToolResultContent);
  }

  if (isToolResultContent(message.content)) {
    return [message.content];
  }

  return [];
}
