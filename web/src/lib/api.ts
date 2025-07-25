const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/vibex'

export interface Task {
  id: string
  objective: string
  status: 'pending' | 'planning' | 'executing' | 'completed' | 'failed'
  team_config: string
  plan?: any
  created_at: string
  updated_at: string
  result?: any
}

export interface Message {
  id: string
  project_id: string
  agent: string
  content: string
  timestamp: string
  tool_calls?: any[]
}

export interface Artifact {
  name: string
  content_type: string
  size: number
  created_at: string
  url: string
}

export interface Metrics {
  totalTasks: number
  tasksToday: number
  avgDuration: number
  successRate: number
  activeAgents: number
}

class ApiClient {
  private async fetch(endpoint: string, options?: RequestInit) {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  // Project operations
  async createProject(data: { objective: string; team_config: string }) {
    return this.fetch('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getProject(projectId: string) {
    return this.fetch(`/projects/${projectId}`)
  }

  async listProjects(params?: { limit?: number; offset?: number }) {
    const query = new URLSearchParams(params as any).toString()
    return this.fetch(`/projects?${query}`)
  }

  // Message operations
  async getMessages(projectId: string) {
    return this.fetch(`/projects/${projectId}/messages`)
  }

  streamMessages(projectId: string, onMessage: (message: Message) => void) {
    const eventSource = new EventSource(`${API_URL}/projects/${projectId}/messages/stream`)
    
    eventSource.onmessage = (event) => {
      const message = JSON.parse(event.data)
      onMessage(message)
    }

    eventSource.onerror = () => {
      eventSource.close()
    }

    return () => eventSource.close()
  }

  // Artifact operations
  async getArtifacts(projectId: string) {
    return this.fetch(`/projects/${projectId}/artifacts`)
  }

  async downloadArtifact(projectId: string, artifactName: string) {
    const response = await fetch(`${API_URL}/projects/${projectId}/artifacts/${artifactName}`)
    return response.blob()
  }

  // Metrics operations
  async getMetrics() {
    return this.fetch('/metrics')
  }

  async getAgentPerformance() {
    return this.fetch('/metrics/agents')
  }

  async getSystemHealth() {
    return this.fetch('/health')
  }
}

export const api = new ApiClient()