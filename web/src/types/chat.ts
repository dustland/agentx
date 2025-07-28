import type { MessagePart } from "@/components/chat/message-parts";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  status?: "streaming" | "complete" | "error";
  parts?: MessagePart[];
  metadata?: {
    agentId?: string;
    agentName?: string;
    toolCalls?: Array<{
      name: string;
      status: "running" | "completed" | "error";
      parameters?: any;
      result?: any;
    }>;
  };
}

export type TaskStatus = "pending" | "running" | "completed" | "error";

export interface StreamEvent {
  type: "message" | "tool_call" | "status_update" | "failed";
  data: any;
  timestamp: Date;
}
