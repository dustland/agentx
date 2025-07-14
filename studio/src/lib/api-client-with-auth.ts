import { AgentXAPIClient } from './api-client';
import { getCurrentUser } from './auth';

export class AuthenticatedAgentXAPIClient extends AgentXAPIClient {
  private userId: string | null = null;

  async init() {
    const user = await getCurrentUser();
    this.userId = user?.id || null;
  }

  async createTask(taskRequest: any) {
    await this.init();
    return super.createTask({
      ...taskRequest,
      user_id: this.userId,
    });
  }

  async getTasks() {
    await this.init();
    return super.getTasks(this.userId || undefined);
  }

  async getTask(taskId: string) {
    await this.init();
    return super.getTask(taskId, this.userId || undefined);
  }

  async getTaskArtifacts(taskId: string) {
    await this.init();
    return super.getTaskArtifacts(taskId, this.userId || undefined);
  }
}

// Export authenticated client instance
export const authApiClient = new AuthenticatedAgentXAPIClient();