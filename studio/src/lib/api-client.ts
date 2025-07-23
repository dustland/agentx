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
} from "@/types/vibex";

export class VibeXAPIClient {
  private baseURL: string;
  private userId: string | null = null;
  private userPromise: Promise<void> | null = null;

  constructor(baseURL?: string) {
    this.baseURL =
      baseURL ||
      process.env.NEXT_PUBLIC_VIBEX_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:7770";

    // console.log("VibeX API client initialized with baseURL:", this.baseURL);
  }

  async init() {
    // Check if we're on the test page - use test user
    if (
      typeof window !== "undefined" &&
      window.location.pathname === "/test/hooks"
    ) {
      this.userId = "test-user-streaming";
      return;
    }

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
      // console.log("API client initialized with user:", this.userId);

      // If no user is found, redirect to login
      if (!user && typeof window !== "undefined") {
        const currentPath = window.location.pathname;
        // Only redirect if we're not already on the auth pages
        if (!currentPath.startsWith("/auth/")) {
          window.location.href = `/auth/login?redirect=${encodeURIComponent(
            currentPath
          )}`;
        }
      }
    } catch (error) {
      console.error("Failed to get current user:", error);
      this.userId = null;

      // Redirect to login on authentication error
      if (typeof window !== "undefined") {
        const currentPath = window.location.pathname;
        // Only redirect if we're not already on the auth pages
        if (!currentPath.startsWith("/auth/")) {
          window.location.href = `/auth/login?redirect=${encodeURIComponent(
            currentPath
          )}`;
        }
      }
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

    // Log request details for debugging
    console.log("API Request:", {
      url,
      method: options.method || "GET",
      userId: this.userId,
      headers: headers,
    });

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      // Handle 401 Unauthorized specifically
      if (response.status === 401 && typeof window !== "undefined") {
        const currentPath = window.location.pathname;
        // Only redirect if we're not already on the auth pages
        if (!currentPath.startsWith("/auth/")) {
          window.location.href = `/auth/login?redirect=${encodeURIComponent(
            currentPath
          )}`;
          // Throw error to stop further processing
          throw new Error("Unauthorized - redirecting to login");
        }
      }

      let errorText = "";
      try {
        errorText = await response.text();
      } catch (e) {
        errorText = "Failed to read error response";
      }
      
      const errorDetails = {
        status: response.status,
        statusText: response.statusText,
        error: errorText,
        url,
        userId: this.userId,
      };
      
      console.error("API Error:", errorDetails);
      
      // Create a more descriptive error message
      const errorMessage = errorText || response.statusText || `HTTP ${response.status}`;
      throw new Error(`API Error ${response.status}: ${errorMessage}`);
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
    const response = await this.request<{ tasks: TaskResponse[] }>("/tasks");
    // Backend returns { tasks: [...] }
    return {
      tasks: response.tasks || [],
      total: (response.tasks || []).length,
    };
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

  async getTaskPlan(taskId: string): Promise<ArtifactContent> {
    await this.init();
    return this.request<ArtifactContent>(`/tasks/${taskId}/plan`);
  }

  // Logs
  async getTaskLogs(
    taskId: string,
    options?: {
      limit?: number;
      offset?: number;
      tail?: boolean;
    }
  ): Promise<LogsResponse> {
    await this.init();
    const params = new URLSearchParams();
    if (options?.limit) params.append("limit", options.limit.toString());
    if (options?.offset) params.append("offset", options.offset.toString());
    if (options?.tail) params.append("tail", "true");

    const queryString = params.toString();
    return this.request<LogsResponse>(
      `/tasks/${taskId}/logs${queryString ? `?${queryString}` : ""}`
    );
  }

  // Real-time updates using Server-Sent Events
  subscribeToTaskUpdates(
    taskId: string,
    onUpdate: (event: StreamEvent) => void
  ): () => void {
    // Note: SSE doesn't support custom headers, so we need to pass user_id in URL for now
    // TODO: Consider using JWT tokens in the future for better security

    // SSE doesn't support custom headers, so we pass user_id as query parameter
    // If userId is not yet initialized, use "guest" as default
    const effectiveUserId = this.userId || "guest";
    const params = `?user_id=${encodeURIComponent(effectiveUserId)}`;
    console.log("[SSE] Creating connection for task:", taskId);
    console.log("[SSE] Using user ID:", effectiveUserId);
    console.log("[SSE] Current this.userId:", this.userId);

    let eventSource: EventSource;
    let isConnected = false;

    try {
      // For streaming, we need to connect directly to the backend, not through Next.js proxy
      // because EventSource doesn't work through Next.js rewrites
      const directBackendURL =
        process.env.NEXT_PUBLIC_VIBEX_BACKEND_URL || "http://localhost:7770";
      const streamUrl = `${directBackendURL}/tasks/${taskId}/stream${params}`;
      console.log("Creating EventSource for URL:", streamUrl);
      eventSource = new EventSource(streamUrl);
    } catch (error) {
      console.error("Failed to create EventSource:", error);
      // Return a no-op cleanup function
      return () => {};
    }

    eventSource.onopen = () => {
      console.log("SSE connection opened successfully for task:", taskId);
      isConnected = true;
    };

    eventSource.onmessage = (event) => {
      try {
        console.log("Raw SSE event received:", event);
        const data = JSON.parse(event.data);
        console.log("Parsed SSE data:", data);
        onUpdate(data);
      } catch (error) {
        console.error("Error parsing SSE data:", error, "Raw event:", event);
      }
    };

    eventSource.onerror = (error) => {
      console.warn("SSE connection error:", error);
      isConnected = false;

      // If the connection fails immediately, it might be a network issue
      // or the endpoint doesn't exist. Close the connection to prevent
      // infinite retry attempts.
      if (eventSource.readyState === EventSource.CLOSED) {
        // console.log("SSE connection closed by server");
      }
    };

    // Handle specific event types (keeping agent_message for backward compatibility)
    eventSource.addEventListener("agent_message", (event: MessageEvent) => {
      try {
        console.warn("[SSE] Received deprecated agent_message event");
        console.log("[SSE] agent_message event:", event);
        const data = JSON.parse(event.data);
        onUpdate({
          type: "agent_message",
          data: data,
          timestamp: new Date().toISOString(),
        });
      } catch (error) {
        console.error("Error handling agent_message:", error);
      }
    });

    eventSource.addEventListener("task_update", (event: MessageEvent) => {
      try {
        console.log("[SSE] task_update event:", event);
        const data = JSON.parse(event.data);
        onUpdate({
          type: "task_update",
          data: data,
          timestamp: new Date().toISOString(),
        });
      } catch (error) {
        console.error("Error handling task_update:", error);
      }
    });

    eventSource.addEventListener("tool_call", (event: MessageEvent) => {
      try {
        console.log("[SSE] tool_call event:", event);
        const data = JSON.parse(event.data);
        onUpdate({
          type: "tool_call",
          data: data,
          timestamp: new Date().toISOString(),
        });
      } catch (error) {
        console.error("Error handling tool_call:", error);
      }
    });

    eventSource.addEventListener("agent_status", (event: MessageEvent) => {
      try {
        console.log("[SSE] agent_status event:", event);
        const data = JSON.parse(event.data);
        onUpdate({
          type: "agent_status",
          data: data,
          timestamp: new Date().toISOString(),
        });
      } catch (error) {
        console.error("Error handling agent_status:", error);
      }
    });

    // Add listeners for new streaming events
    eventSource.addEventListener("message", (event: MessageEvent) => {
      try {
        console.log("[SSE] message event:", event);
        const data = JSON.parse(event.data);
        onUpdate({
          type: "message",
          data: data,
          timestamp: new Date().toISOString(),
        });
      } catch (error) {
        console.error("Error handling message:", error);
      }
    });

    eventSource.addEventListener("stream_chunk", (event: MessageEvent) => {
      try {
        console.log("[SSE] stream_chunk event:", event);
        const data = JSON.parse(event.data);
        onUpdate({
          type: "stream_chunk",
          data: data,
          timestamp: new Date().toISOString(),
        });
      } catch (error) {
        console.error("Error handling stream_chunk:", error);
      }
    });

    // Return cleanup function
    return () => {
      if (eventSource && eventSource.readyState !== EventSource.CLOSED) {
        eventSource.close();
      }
    };
  }

  // Messages
  async getMessages(taskId: string): Promise<MessagesResponse> {
    await this.init();
    return this.request<MessagesResponse>(`/tasks/${taskId}/messages`);
  }

  // Execute task plan
  async executeTaskPlan(taskId: string): Promise<{ message: string; task_id: string; status: string }> {
    await this.init();
    return this.request<{ message: string; task_id: string; status: string }>(
      `/tasks/${taskId}/execute`,
      {
        method: "POST",
      }
    );
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
        if (task.status === "completed" || task.status === "error") {
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
export const apiClient = new VibeXAPIClient();

// Hook for React components - returns the singleton instance
export function useAPI() {
  return apiClient;
}
