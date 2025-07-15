"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  BotIcon,
  UserIcon,
  ActivityIcon,
  CheckCircleIcon,
  AlertCircleIcon,
} from "lucide-react";
import { formatDate } from "@/lib/utils";

interface AgentMessage {
  id: string;
  agent_id: string;
  message: string;
  timestamp: string;
  metadata?: any;
}

interface AgentStatus {
  agent_id: string;
  status: string;
  progress: number;
}

interface ToolCall {
  id: string;
  agent_id: string;
  tool_name: string;
  parameters: any;
  result?: any;
  timestamp: string;
  status: "pending" | "completed" | "error";
}

interface AgentStreamProps {
  taskId: string;
  apiUrl?: string;
  onToolCall?: (toolCall: ToolCall) => void;
}

export function AgentStream({
  taskId,
  apiUrl = process.env.NEXT_PUBLIC_AGENTX_API_URL || "http://localhost:7770",
  onToolCall,
}: AgentStreamProps) {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [agentStatuses, setAgentStatuses] = useState<
    Record<string, AgentStatus>
  >({});
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!taskId) return;

    // Create SSE connection
    const eventSource = new EventSource(`${apiUrl}/tasks/${taskId}/stream`);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      console.log("Connected to task stream:", taskId);
    };

    eventSource.onerror = (error) => {
      console.error("SSE error:", error);
      setIsConnected(false);
    };

    // Handle agent messages
    eventSource.addEventListener("agent_message", (event) => {
      try {
        const data = JSON.parse(event.data);
        const message: AgentMessage = {
          id: event.lastEventId || Date.now().toString(),
          agent_id: data.agent_id,
          message: data.message,
          timestamp: new Date().toISOString(),
          metadata: data.metadata,
        };
        setMessages((prev) => [...prev, message]);

        // Auto-scroll to bottom
        setTimeout(() => {
          scrollRef.current?.scrollIntoView({ behavior: "smooth" });
        }, 100);
      } catch (err) {
        console.error("Failed to parse agent message:", err);
      }
    });

    // Handle agent status updates
    eventSource.addEventListener("agent_status", (event) => {
      try {
        const data = JSON.parse(event.data);
        setAgentStatuses((prev) => ({
          ...prev,
          [data.agent_id]: data,
        }));
      } catch (err) {
        console.error("Failed to parse agent status:", err);
      }
    });

    // Handle task updates
    eventSource.addEventListener("task_update", (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Task update:", data);
      } catch (err) {
        console.error("Failed to parse task update:", err);
      }
    });

    // Handle tool calls
    eventSource.addEventListener("tool_call", (event) => {
      try {
        const data = JSON.parse(event.data);
        const toolCall: ToolCall = {
          id: event.lastEventId || Date.now().toString(),
          agent_id: data.agent_id,
          tool_name: data.tool_name,
          parameters: data.parameters,
          result: data.result,
          timestamp: new Date().toISOString(),
          status: data.status || "pending",
        };
        setToolCalls((prev) => [...prev, toolCall]);
        onToolCall?.(toolCall);
      } catch (err) {
        console.error("Failed to parse tool call:", err);
      }
    });

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    };
  }, [taskId, apiUrl]);

  const getAgentColor = (agentId: string) => {
    const colors = [
      "bg-blue-500",
      "bg-green-500",
      "bg-purple-500",
      "bg-pink-500",
      "bg-yellow-500",
      "bg-indigo-500",
    ];
    const index = agentId.charCodeAt(0) % colors.length;
    return colors[index];
  };

  const getAgentInitials = (agentId: string) => {
    return agentId.slice(0, 2).toUpperCase();
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            Agent Messages
            {isConnected && (
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            )}
          </CardTitle>
          <Badge variant={isConnected ? "default" : "secondary"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
        </div>

        {/* Agent Status Bar */}
        <div className="flex gap-2 mt-3 flex-wrap">
          {Object.entries(agentStatuses).map(([agentId, status]) => (
            <Badge key={agentId} variant="outline" className="text-xs">
              <div
                className={`w-2 h-2 rounded-full mr-1 ${
                  status.status === "working"
                    ? "bg-blue-500 animate-pulse"
                    : status.status === "completed"
                    ? "bg-green-500"
                    : "bg-gray-500"
                }`}
              />
              {agentId}: {status.status} ({status.progress}%)
            </Badge>
          ))}
        </div>
      </CardHeader>

      <CardContent className="flex-1 p-0">
        <ScrollArea className="h-[500px] px-4">
          <div className="space-y-4 py-4">
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                <ActivityIcon className="w-8 h-8 mx-auto mb-2 animate-pulse" />
                <p>Waiting for agent messages...</p>
              </div>
            ) : (
              messages.map((message) => (
                <div key={message.id} className="flex gap-3">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className={getAgentColor(message.agent_id)}>
                      {getAgentInitials(message.agent_id)}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">
                        {message.agent_id}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatDate(new Date(message.timestamp))}
                      </span>
                      {message.metadata?.error && (
                        <AlertCircleIcon className="w-3 h-3 text-red-500" />
                      )}
                    </div>

                    <div className="text-sm whitespace-pre-wrap">
                      {message.message}
                    </div>

                    {message.metadata?.step && (
                      <Badge variant="secondary" className="text-xs">
                        Step {message.metadata.step}
                      </Badge>
                    )}

                    {/* Display tool calls inline */}
                    {message.metadata?.tool_calls &&
                      message.metadata.tool_calls.map(
                        (tool: any, idx: number) => (
                          <Card
                            key={idx}
                            className="mt-2 p-2 bg-secondary/20 cursor-pointer hover:bg-secondary/30"
                            onClick={() => {
                              const toolCall: ToolCall = {
                                id: `${message.id}-tool-${idx}`,
                                agent_id: message.agent_id,
                                tool_name: tool.name,
                                parameters: tool.parameters,
                                result: tool.result,
                                timestamp: message.timestamp,
                                status: tool.result ? "completed" : "pending",
                              };
                              onToolCall?.(toolCall);
                            }}
                          >
                            <div className="flex items-center gap-2 text-xs">
                              <Badge variant="outline" className="text-xs">
                                {tool.name}
                              </Badge>
                              <span className="text-muted-foreground">
                                Click to view details
                              </span>
                            </div>
                          </Card>
                        )
                      )}
                  </div>
                </div>
              ))
            )}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
