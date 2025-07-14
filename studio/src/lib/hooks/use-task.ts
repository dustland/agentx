import { useState, useEffect, useCallback } from 'react';
import { useAgentXAPI, TaskResponse, TaskRequest } from '@/lib/api-client';

export interface TaskAgent {
  id: string;
  name: string;
  role: string;
  status: 'idle' | 'working' | 'completed' | 'error';
  progress: number;
  lastAction: string;
}

export interface TaskMessage {
  id: string;
  agentId?: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
}

export interface UseTaskOptions {
  autoStart?: boolean;
  configPath?: string;
  pollingInterval?: number;
}

export function useTask(taskId: string, options: UseTaskOptions = {}) {
  const apiClient = useAgentXAPI();
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [agents, setAgents] = useState<TaskAgent[]>([]);
  const [messages, setMessages] = useState<TaskMessage[]>([]);

  // Default agents structure (will be replaced by actual agent data)
  const defaultAgents: TaskAgent[] = [
    {
      id: 'researcher',
      name: 'Research Agent',
      role: 'Data Collection & Analysis',
      status: 'idle',
      progress: 0,
      lastAction: 'Ready to start',
    },
    {
      id: 'writer',
      name: 'Content Agent',
      role: 'Content Generation',
      status: 'idle',
      progress: 0,
      lastAction: 'Waiting for research',
    },
    {
      id: 'reviewer',
      name: 'Quality Agent',
      role: 'Review & Optimization',
      status: 'idle',
      progress: 0,
      lastAction: 'Standby',
    },
  ];

  // Load task data
  const loadTask = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const taskData = await apiClient.getTask(taskId);
      setTask(taskData);
      
      // Initialize agents if not already done
      if (agents.length === 0) {
        setAgents(defaultAgents);
      }
      
      // Add system message for task creation
      if (messages.length === 0) {
        setMessages([{
          id: '1',
          type: 'system',
          content: `Task ${taskId} loaded with status: ${taskData.status}`,
          timestamp: new Date(),
        }]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load task');
    } finally {
      setLoading(false);
    }
  }, [taskId, apiClient, agents.length, messages.length]);

  // Create a new task
  const createTask = useCallback(async (description: string, context?: Record<string, any>) => {
    try {
      setLoading(true);
      setError(null);
      
      const taskRequest: TaskRequest = {
        config_path: options.configPath || 'examples/auto_writer/config/team.yaml',
        task_description: description,
        context,
      };
      
      const newTask = await apiClient.createTask(taskRequest);
      setTask(newTask);
      setAgents(defaultAgents);
      
      setMessages([{
        id: '1',
        type: 'system',
        content: `Task created: ${description}`,
        timestamp: new Date(),
      }]);
      
      return newTask;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiClient, options.configPath]);

  // Update agent status based on task status
  const updateAgentsFromTask = useCallback((taskData: TaskResponse) => {
    setAgents(prev => {
      switch (taskData.status) {
        case 'running':
          return prev.map((agent, index) => ({
            ...agent,
            status: index === 0 ? 'working' : 'idle',
            lastAction: index === 0 ? 'Processing task...' : 'Waiting for previous step',
            progress: index === 0 ? 25 : 0,
          }));
        case 'completed':
          return prev.map(agent => ({
            ...agent,
            status: 'completed',
            lastAction: 'Task completed',
            progress: 100,
          }));
        case 'failed':
          return prev.map(agent => ({
            ...agent,
            status: 'error',
            lastAction: 'Task failed',
            progress: 0,
          }));
        default:
          return prev;
      }
    });
  }, []);

  // Handle task updates
  const handleTaskUpdate = useCallback((updatedTask: TaskResponse) => {
    setTask(updatedTask);
    updateAgentsFromTask(updatedTask);
    
    // Add status update message
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      type: 'system',
      content: `Task status updated: ${updatedTask.status}`,
      timestamp: new Date(),
    }]);
  }, [updateAgentsFromTask]);

  // Start polling for updates
  useEffect(() => {
    if (!task || !taskId) return;

    const stopPolling = apiClient.pollTaskStatus(taskId, handleTaskUpdate, options.pollingInterval);
    return () => {
      if (stopPolling && typeof stopPolling === 'function') {
        stopPolling();
      }
    };
  }, [task, taskId, apiClient, handleTaskUpdate, options.pollingInterval]);

  // Initial load
  useEffect(() => {
    if (taskId) {
      loadTask();
    }
  }, [taskId, loadTask]);

  // Add memory to task
  const addMemory = useCallback(async (content: string, metadata?: Record<string, any>) => {
    try {
      await apiClient.addMemory(taskId, { content, metadata });
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        type: 'system',
        content: `Added content to task memory`,
        timestamp: new Date(),
      }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add memory');
    }
  }, [taskId, apiClient]);

  // Search task memory
  const searchMemory = useCallback(async (query: string, limit?: number) => {
    try {
      return await apiClient.searchMemory(taskId, { query, limit });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search memory');
      return [];
    }
  }, [taskId, apiClient]);

  // Delete task
  const deleteTask = useCallback(async () => {
    try {
      await apiClient.deleteTask(taskId);
      setTask(null);
      setAgents([]);
      setMessages([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  }, [taskId, apiClient]);

  return {
    task,
    loading,
    error,
    agents,
    messages,
    createTask,
    loadTask,
    addMemory,
    searchMemory,
    deleteTask,
    setMessages,
  };
}