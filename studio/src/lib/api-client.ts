import type {
  CreateTaskRequest,
  Task as TaskResponse,
  TaskListResponse,
  MemoryContent,
  MemorySearchRequest,
  MemorySearchResult,
  Message,
  MessagesResponse,
  SendMessageRequest,
  StreamEvent,
  Artifact,
  ArtifactContent,
  LogsResponse,
} from "@/types/agentx";

export class AgentXAPIClient {
  private baseURL: string;
  private userId: string | null = null;
  private userPromise: Promise<void> | null = null;

  constructor(baseURL?: string) {
    this.baseURL =
      baseURL ||
      process.env.NEXT_PUBLIC_AGENTX_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:7770";
  }

  async init() {
    // If we already have a user or are in the process of getting one, don't call again
    if (this.userId !== null || this.userPromise) {
      if (this.userPromise) {
        await this.userPromise;
      }
      return;
    }

    // Cache the promise to prevent multiple concurrent calls
    this.userPromise = this.fetchUser();
    await this.userPromise;
    this.userPromise = null;
  }

  private async fetchUser() {
    try {
      // Import getCurrentUser dynamically to avoid circular dependencies
      const { getCurrentUser } = await import("./auth");
      const user = await getCurrentUser();
      this.userId = user?.id || null;
    } catch (error) {
      console.error("Failed to get current user:", error);
      this.userId = null;
    }
  }

  // Method to clear cached user (useful for logout)
  clearUser() {
    this.userId = null;
    this.userPromise = null;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    // Build headers with authentication
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    // Add user ID to headers if available
    if (this.userId) {
      (headers as any)["X-User-ID"] = this.userId;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error ${response.status}: ${error}`);
    }

    return response.json();
  }

  // Task Management
  async createTask(taskRequest: CreateTaskRequest): Promise<TaskResponse> {
    await this.init();
    return this.request<TaskResponse>("/tasks", {
      method: "POST",
      body: JSON.stringify(taskRequest),
    });
  }

  async getTasks(): Promise<TaskListResponse> {
    await this.init();
    const tasks = await this.request<TaskResponse[]>("/tasks");
    // Backend returns array directly, wrap it for compatibility
    return { tasks, total: tasks.length };
  }

  async getTask(taskId: string): Promise<TaskResponse> {
    await this.init();
    return this.request<TaskResponse>(`/tasks/${taskId}`);
  }

  async deleteTask(taskId: string): Promise<void> {
    await this.init();
    await this.request(`/tasks/${taskId}`, {
      method: "DELETE",
    });
  }

  // Memory Management
  async addMemory(taskId: string, content: MemoryContent): Promise<void> {
    await this.init();
    await this.request(`/tasks/${taskId}/memory`, {
      method: "POST",
      body: JSON.stringify(content),
    });
  }

  async searchMemory(
    taskId: string,
    searchRequest: MemorySearchRequest
  ): Promise<MemorySearchResult[]> {
    await this.init();
    return this.request<MemorySearchResult[]>(
      `/tasks/${taskId}/memory?${new URLSearchParams({
        query: searchRequest.query,
        ...(searchRequest.limit && { limit: searchRequest.limit.toString() }),
      })}`
    );
  }

  async clearMemory(taskId: string): Promise<void> {
    await this.init();
    await this.request(`/tasks/${taskId}/memory`, {
      method: "DELETE",
    });
  }

  // Health & Monitoring
  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>("/health");
  }

  async getMonitoringData(): Promise<any> {
    return this.request("/monitor");
  }

  // Artifacts
  async getTaskArtifacts(taskId: string): Promise<{ artifacts: Artifact[] }> {
    await this.init();
    return this.request<{ artifacts: Artifact[] }>(
      `/tasks/${taskId}/artifacts`
    );
  }

  async getArtifactContent(
    taskId: string,
    filePath: string
  ): Promise<ArtifactContent> {
    await this.init();
    return this.request<ArtifactContent>(
      `/tasks/${taskId}/artifacts/${encodeURIComponent(filePath)}`
    );
  }

  // Logs
  async getTaskLogs(taskId: string, tail?: number): Promise<LogsResponse> {
    await this.init();
    const params = tail ? `?tail=${tail}` : "";
    return this.request<LogsResponse>(`/tasks/${taskId}/logs${params}`);
  }

  // Real-time updates using Server-Sent Events
  subscribeToTaskUpdates(
    taskId: string,
    onUpdate: (event: StreamEvent) => void
  ): () => void {
    // Note: SSE doesn't support custom headers, so we need to pass user_id in URL for now
    // TODO: Consider using JWT tokens in the future for better security
    const params = this.userId
      ? `?user_id=${encodeURIComponent(this.userId)}`
      : "";
    const eventSource = new EventSource(
      `${this.baseURL}/tasks/${taskId}/stream${params}`
    );

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onUpdate(data);
      } catch (error) {
        console.error("Error parsing SSE data:", error);
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE connection error:", error);
    };

    // Return cleanup function
    return () => {
      eventSource.close();
    };
  }

  // Messages
  async getMessages(taskId: string): Promise<MessagesResponse> {
    await this.init();
    return this.request<MessagesResponse>(`/tasks/${taskId}/messages`);
  }

  // Send message to task
  async sendMessage(
    taskId: string,
    message: string | SendMessageRequest
  ): Promise<void> {
    await this.init();
    const payload =
      typeof message === "string" ? { content: message } : message;

    await this.request(`/tasks/${taskId}/chat`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Poll for task updates (fallback for when SSE is not available)
  pollTaskStatus(
    taskId: string,
    onUpdate: (task: TaskResponse) => void,
    interval: number = 2000
  ): () => void {
    let isPolling = true;

    const poll = async () => {
      try {
        if (!isPolling) return;

        const task = await this.getTask(taskId);
        onUpdate(task);

        // Stop polling if task is complete
        if (task.status === "completed" || task.status === "failed") {
          isPolling = false;
          return;
        }

        // Schedule next poll
        setTimeout(poll, interval);
      } catch (error) {
        console.error("Error polling task status:", error);
        // Continue polling even on error
        if (isPolling) {
          setTimeout(poll, interval * 2); // Backoff on error
        }
      }
    };

    // Start polling
    poll();

    // Return stop function
    return () => {
      isPolling = false;
    };
  }
}

// Export a singleton instance
export const apiClient = new AgentXAPIClient();

// Hook for React components - returns the singleton instance
export function useAgentXAPI() {
  return apiClient;
}
