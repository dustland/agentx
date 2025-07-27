import {
  CreateXAgentRequest,
  XAgent,
  XAgentListResponse,
  MemoryContent,
  MemorySearchRequest,
} from "@/types/vibex";
import { useMemo } from "react";
import { useUser } from "@/contexts/user-context";

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
    // For now, return empty array since there's no list endpoint
    // TODO: Implement proper artifacts listing endpoint
    return [];
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

    eventSource.onmessage = (event) => {
      console.log("[SSE] Raw event received:", event);
      console.log("[SSE] Event data:", event.data);
      console.log("[SSE] Event type:", event.type);
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Parsed data:", data);
        onUpdate(data);
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
