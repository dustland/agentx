import { AgentXAPIClient } from "./api-client";
import { getCurrentUser } from "./auth";

export class AuthenticatedAgentXAPIClient extends AgentXAPIClient {
  private userId: string | null = null;
  private userPromise: Promise<void> | null = null;

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

  async getTaskLogs(taskId: string, tail?: number) {
    await this.init();
    return super.getTaskLogs(taskId, tail, this.userId || undefined);
  }

  async deleteTask(taskId: string) {
    await this.init();
    return super.deleteTask(taskId);
  }
}

// Export authenticated client instance
export const authApiClient = new AuthenticatedAgentXAPIClient();
