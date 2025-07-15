/**
 * Comprehensive types for AgentX API matching the backend schema
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
export type MessageContent = TextContent | ImageContent | ToolCallContent | ToolResultContent;

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

// Task-related types
export interface Task {
  task_id: string;
  status: TaskStatus;
  config_path: string;
  task_description?: string;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  error?: string;
  result?: Record<string, any>;
  user_id?: string;
  context?: Record<string, any>;
}

export type TaskStatus = "pending" | "running" | "completed" | "failed";

// API request/response types
export interface CreateTaskRequest {
  config_path: string;
  task_description?: string;
  context?: Record<string, any>;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

export interface MessagesResponse {
  messages: Message[];
}

export interface SendMessageRequest {
  content: string | MessageContent | MessageContent[];
  role?: MessageRole;
  name?: string;
}

// Streaming event types
export type StreamEventType = 
  | "agent_message"
  | "tool_call_start"
  | "tool_call_result"
  | "agent_status"
  | "task_update"
  | "artifact_created"
  | "artifact_updated"
  | "memory_updated"
  | "log_entry"
  | "error";

export interface StreamEvent {
  event: StreamEventType;
  data: any;
  timestamp?: string;
}

// Specific stream event data types
export interface AgentMessageEvent {
  agent_id: string;
  message: string;
  content?: MessageContent | MessageContent[];
  metadata?: MessageMetadata;
}

export interface ToolCallStartEvent {
  agent_id: string;
  tool_call_id: string;
  tool_name: string;
  args: Record<string, any>;
}

export interface ToolCallResultEvent {
  agent_id: string;
  tool_call_id: string;
  tool_name: string;
  result: any;
  is_error?: boolean;
}

export interface AgentStatusEvent {
  agent_id: string;
  status: "idle" | "thinking" | "working" | "waiting";
  message?: string;
}

export interface TaskUpdateEvent {
  status: TaskStatus;
  message?: string;
  progress?: number;
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
  metadata?: Record<string, any>;
}

export interface MemorySearchRequest {
  query: string;
  limit?: number;
}

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
  task_id: string;
  logs: string[];
  total_lines: number;
}

// Helper functions to work with messages
export function isTextContent(content: MessageContent): content is TextContent {
  return content.type === "text";
}

export function isToolCallContent(content: MessageContent): content is ToolCallContent {
  return content.type === "tool-call";
}

export function isToolResultContent(content: MessageContent): content is ToolResultContent {
  return content.type === "tool-result";
}

export function getMessageText(message: Message): string {
  if (typeof message.content === "string") {
    return message.content;
  }
  
  if (Array.isArray(message.content)) {
    return message.content
      .filter(isTextContent)
      .map(c => c.text)
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