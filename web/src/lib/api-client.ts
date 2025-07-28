import {
  CreateXAgentRequest,
  XAgent,
  XAgentListResponse,
  MemoryContent,
  MemorySearchRequest,
} from "@/types/vibex";
import { useMemo } from "react";
import { useUser } from "@/contexts/user";

export class VibexClient {
  private baseURL: string;
  private userId: string | null = null;

  constructor(
    baseURL: string = process.env.NEXT_PUBLIC_VIBEX_API_URL || "/api/vibex"
  ) {
    this.baseURL = baseURL;
  }

  setUserId(userId: string) {
    this.userId = userId;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "X-User-ID": this.userId || "guest", // Always include a user ID
      ...((options.headers as Record<string, string>) || {}),
    };

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: "include", // Include cookies for authentication
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error ${response.status}: ${errorText}`);
    }

    return response.json();
  }

  private async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  private async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  private async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }

  // XAgent Management
  async createXAgent(
    goal: string,
    configPath: string,
    context?: object
  ): Promise<XAgent> {
    const requestBody: CreateXAgentRequest = {
      goal: goal,
      config_path: configPath,
      context: context,
    };
    return this.post<XAgent>("/xagents", requestBody);
  }

  async listXAgents(): Promise<XAgentListResponse> {
    return this.get<XAgentListResponse>("/xagents");
  }

  async getXAgent(agentId: string): Promise<XAgent> {
    return this.get<XAgent>(`/xagents/${agentId}`);
  }

  async deleteXAgent(agentId: string): Promise<{ message: string }> {
    return this.delete(`/xagents/${agentId}`);
  }

  // Chat
  async sendMessage(xagentId: string, message: string): Promise<any> {
    const requestBody = { xagent_id: xagentId, content: message };
    return this.post(`/chat`, requestBody);
  }

  async getMessages(agentId: string): Promise<{ messages: any[] }> {
    return this.get(`/xagents/${agentId}/messages`);
  }

  // Agent Resources
  async listArtifacts(agentId: string): Promise<any[]> {
    const data = await this.request<{ artifacts: any[] }>(
      `/xagents/${agentId}/artifacts`
    );
    return data.artifacts || [];
  }

  async getArtifact(
    agentId: string,
    artifactPath: string
  ): Promise<{ artifact_path: string; content: any }> {
    return this.get(`/xagents/${agentId}/artifacts/${artifactPath}`);
  }

  async getLogs(agentId: string): Promise<{ logs: any[] }> {
    return this.get(`/xagents/${agentId}/logs`);
  }

  // Streaming
  subscribeToXAgentUpdates(
    agentId: string,
    onUpdate: (data: any) => void,
    onError: (error: any) => void
  ) {
    const effectiveUserId = this.userId || "guest";
    const params = `?user_id=${encodeURIComponent(effectiveUserId)}`;
    const url = `${this.baseURL}/xagents/${agentId}/stream${params}`;

    console.log("[SSE] Connecting to:", url);
    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      console.log("[SSE] Connection opened for agent:", agentId);
      console.log("[SSE] Connection URL:", url);
    };

    // Handle specific event types

    eventSource.addEventListener("message", (event) => {
      console.log("[SSE] Message event received:", event);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Message data:", data);
        onUpdate({ event: "message", data });
      } catch (error) {
        console.error("Error parsing message data:", error);
        onError(error);
      }
    });

    eventSource.addEventListener("agent_status", (event) => {
      console.log("[SSE] Agent status event received:", event);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Agent status data:", data);
        onUpdate({ event: "agent_status", data });
      } catch (error) {
        console.error("Error parsing agent status data:", error);
        onError(error);
      }
    });

    eventSource.addEventListener("task_update", (event) => {
      console.log("[SSE] Task update event received:", event);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Task update data:", data);
        onUpdate({ event: "task_update", data });
      } catch (error) {
        console.error("Error parsing task update data:", error);
        onError(error);
      }
    });

    eventSource.addEventListener("artifact_update", (event) => {
      console.log("[SSE] Artifact update event received:", event);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Artifact update data:", data);
        onUpdate({ event: "artifact_update", data });
      } catch (error) {
        console.error("Error parsing artifact update data:", error);
        onError(error);
      }
    });

    eventSource.addEventListener("project_update", (event) => {
      console.log("[SSE] Project update event received:", event);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Project update data:", data);
        onUpdate({ event: "project_update", data });
      } catch (error) {
        console.error("Error parsing project update data:", error);
        onError(error);
      }
    });

    // Tool call streaming events
    eventSource.addEventListener("tool_call_start", (event) => {
      console.log("[SSE] Tool call start event received:", event);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Tool call start data:", data);
        onUpdate({ event: "tool_call_start", data });
      } catch (error) {
        console.error("Error parsing tool call start data:", error);
        onError(error);
      }
    });

    eventSource.addEventListener("tool_call_result", (event) => {
      console.log("[SSE] Tool call result event received:", event);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Tool call result data:", data);
        onUpdate({ event: "tool_call_result", data });
      } catch (error) {
        console.error("Error parsing tool call result data:", error);
        onError(error);
      }
    });

    eventSource.addEventListener("tool_call_delta", (event) => {
      console.log("[SSE] Tool call delta event received:", event);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Tool call delta data:", data);
        onUpdate({ event: "tool_call_delta", data });
      } catch (error) {
        console.error("Error parsing tool call delta data:", error);
        onError(error);
      }
    });

    eventSource.addEventListener("message_part", (event) => {
      console.log("[SSE] Message part event received:", event);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Message part data:", data);
        onUpdate({ event: "message_part", data });
      } catch (error) {
        console.error("Error parsing message part data:", error);
        onError(error);
      }
    });

    // New message part streaming events
    eventSource.addEventListener("message_start", (event) => {
      console.log("[SSE] Message start event received:", event);
      try {
        const data = JSON.parse(event.data);
        onUpdate({ event: "message_start", data });
      } catch (error) {
        console.error("Error parsing message start data:", error);
        onError(error);
      }
    });

    eventSource.addEventListener("part_delta", (event) => {
      console.log("[SSE] Part delta event received:", event);
      try {
        const data = JSON.parse(event.data);
        onUpdate({ event: "part_delta", data });
      } catch (error) {
        console.error("Error parsing part delta data:", error);
        onError(error);
      }
    });

    eventSource.addEventListener("part_complete", (event) => {
      console.log("[SSE] Part complete event received:", event);
      try {
        const data = JSON.parse(event.data);
        onUpdate({ event: "part_complete", data });
      } catch (error) {
        console.error("Error parsing part complete data:", error);
        onError(error);
      }
    });

    eventSource.addEventListener("message_complete", (event) => {
      console.log("[SSE] Message complete event received:", event);
      try {
        const data = JSON.parse(event.data);
        onUpdate({ event: "message_complete", data });
      } catch (error) {
        console.error("Error parsing message complete data:", error);
        onError(error);
      }
    });

    // Handle generic messages (fallback)
    eventSource.onmessage = (event) => {
      console.log("[SSE] Generic message event received:", event);
      console.log("[SSE] Event data:", event.data);
      console.log("[SSE] Event type:", event.type);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Parsed data:", data);
        onUpdate({ event: "generic", data });
      } catch (error) {
        console.error("Error parsing SSE data:", error);
        onError(error);
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE connection error:", error);
      onError(error);
    };

    return eventSource;
  }

  // Memory
  async searchMemory(request: MemorySearchRequest): Promise<MemoryContent[]> {
    return this.post<MemoryContent[]>("/memory/search", request);
  }

  // System Health
  async getSystemHealth(): Promise<any> {
    return this.get("/health");
  }
}

// React hook for using the API client
export function useApi(): VibexClient {
  const { user } = useUser();

  return useMemo(() => {
    const vibex = new VibexClient();
    if (user?.id) {
      vibex.setUserId(user.id);
    }
    return vibex;
  }, [user?.id]);
}
