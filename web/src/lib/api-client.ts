import {
  CreateXAgentRequest,
  TaskRun,
  TaskRunListResponse,
  MemoryContent,
  MemorySearchRequest,
} from "@/types/vibex";
import { useMemo } from "react";

export class VibeXAPIClient {
  private baseURL: string;
  private userId: string | null = null;

  constructor(
    baseURL: string = process.env.NEXT_PUBLIC_API_BASE_URL ||
      "http://localhost:7777"
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
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.userId) {
      headers["X-User-ID"] = this.userId;
    }

    const response = await fetch(url, {
      ...options,
      headers,
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
  ): Promise<TaskRun> {
    const requestBody: CreateXAgentRequest = {
      goal: goal,
      config_path: configPath,
      context: context,
    };
    return this.post<TaskRun>("/agents", requestBody);
  }

  async listXAgents(): Promise<TaskRunListResponse> {
    return this.get<TaskRunListResponse>("/agents");
  }

  async getXAgent(agentId: string): Promise<TaskRun> {
    return this.get<TaskRun>(`/agents/${agentId}`);
  }

  async deleteXAgent(agentId: string): Promise<{ message: string }> {
    return this.delete(`/agents/${agentId}`);
  }

  // Legacy aliases for backward compatibility
  async getProject(projectId: string): Promise<TaskRun> {
    return this.getXAgent(projectId);
  }

  async getProjectArtifacts(projectId: string): Promise<{ artifacts: any[] }> {
    // This would need to be implemented to list all artifacts
    // For now, return empty array
    return { artifacts: [] };
  }

  // Chat
  async sendMessage(agentId: string, message: string): Promise<any> {
    const requestBody = { agent_id: agentId, content: message };
    return this.post(`/chat`, requestBody);
  }

  async getMessages(agentId: string): Promise<{ messages: any[] }> {
    return this.get(`/agents/${agentId}/messages`);
  }

  // Agent Resources
  async getArtifact(
    agentId: string,
    artifactPath: string
  ): Promise<{ artifact_path: string; content: any }> {
    return this.get(`/agents/${agentId}/artifacts/${artifactPath}`);
  }

  async getLogs(agentId: string): Promise<{ logs: any[] }> {
    return this.get(`/agents/${agentId}/logs`);
  }

  async getPlan(agentId: string): Promise<{ plan: any }> {
    return this.get(`/agents/${agentId}/plan`);
  }

  // Streaming
  subscribeToXAgentUpdates(
    agentId: string,
    onUpdate: (data: any) => void,
    onError: (error: any) => void
  ) {
    const effectiveUserId = this.userId || "guest";
    const params = `?user_id=${encodeURIComponent(effectiveUserId)}`;
    const eventSource = new EventSource(
      `${this.baseURL}/agents/${agentId}/stream${params}`
    );

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
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
}

// React hook for using the API client
export function useAPI(): VibeXAPIClient {
  return useMemo(() => new VibeXAPIClient(), []);
}
