export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  status?: "streaming" | "complete" | "failed";
  metadata?: {
    agentId?: string;
    agentName?: string;
    toolCalls?: Array<{
      name: string;
      status: "running" | "completed" | "failed";
      parameters?: any;
      result?: any;
    }>;
  };
}

export type TaskStatus = "pending" | "running" | "completed" | "failed";

export interface StreamEvent {
  type: "message" | "tool_call" | "status_update" | "failed";
  data: any;
  timestamp: Date;
}
