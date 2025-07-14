export interface TaskRequest {
  config_path: string;
  task_description: string;
  context?: Record<string, any>;
}

export interface TaskResponse {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: Record<string, any>;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export interface TaskListResponse {
  tasks: TaskResponse[];
  total: number;
}

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

export class AgentXAPIClient {
  private baseURL: string;

  constructor(baseURL?: string) {
    this.baseURL = baseURL || process.env.NEXT_PUBLIC_AGENTX_API_URL || 'http://localhost:8000';
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error ${response.status}: ${error}`);
    }

    return response.json();
  }

  // Task Management
  async createTask(taskRequest: TaskRequest): Promise<TaskResponse> {
    return this.request<TaskResponse>('/tasks', {
      method: 'POST',
      body: JSON.stringify(taskRequest),
    });
  }

  async getTasks(userId?: string): Promise<TaskListResponse> {
    const params = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    return this.request<TaskListResponse>(`/tasks${params}`);
  }

  async getTask(taskId: string, userId?: string): Promise<TaskResponse> {
    const params = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    return this.request<TaskResponse>(`/tasks/${taskId}${params}`);
  }

  async deleteTask(taskId: string): Promise<void> {
    await this.request(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  // Memory Management
  async addMemory(taskId: string, content: MemoryContent): Promise<void> {
    await this.request(`/tasks/${taskId}/memory`, {
      method: 'POST',
      body: JSON.stringify(content),
    });
  }

  async searchMemory(
    taskId: string,
    searchRequest: MemorySearchRequest
  ): Promise<MemorySearchResult[]> {
    return this.request<MemorySearchResult[]>(
      `/tasks/${taskId}/memory?${new URLSearchParams({
        query: searchRequest.query,
        ...(searchRequest.limit && { limit: searchRequest.limit.toString() }),
      })}`
    );
  }

  async clearMemory(taskId: string): Promise<void> {
    await this.request(`/tasks/${taskId}/memory`, {
      method: 'DELETE',
    });
  }

  // Health & Monitoring
  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }

  async getMonitoringData(): Promise<any> {
    return this.request('/monitor');
  }

  // Artifacts
  async getTaskArtifacts(taskId: string, userId?: string): Promise<{ artifacts: any[] }> {
    const params = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    return this.request<{ artifacts: any[] }>(`/tasks/${taskId}/artifacts${params}`);
  }

  async getArtifactContent(taskId: string, filePath: string): Promise<{
    path: string;
    content: string | null;
    is_binary?: boolean;
    size: number;
  }> {
    return this.request(`/tasks/${taskId}/artifacts/${encodeURIComponent(filePath)}`);
  }

  // Logs
  async getTaskLogs(taskId: string, tail?: number): Promise<{
    task_id: string;
    logs: string[];
    total_lines: number;
  }> {
    const params = tail ? `?tail=${tail}` : '';
    return this.request(`/tasks/${taskId}/logs${params}`);
  }

  // Real-time updates using Server-Sent Events
  subscribeToTaskUpdates(taskId: string, onUpdate: (data: any) => void): () => void {
    const eventSource = new EventSource(`${this.baseURL}/tasks/${taskId}/stream`);
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onUpdate(data);
      } catch (error) {
        console.error('Error parsing SSE data:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
    };

    // Return cleanup function
    return () => {
      eventSource.close();
    };
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
        if (task.status === 'completed' || task.status === 'failed') {
          isPolling = false;
          return;
        }

        // Schedule next poll
        setTimeout(poll, interval);
      } catch (error) {
        console.error('Error polling task status:', error);
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

// Export a default instance
export const apiClient = new AgentXAPIClient();

// Hook for React components
export function useAgentXAPI(baseURL?: string) {
  return new AgentXAPIClient(baseURL);
}