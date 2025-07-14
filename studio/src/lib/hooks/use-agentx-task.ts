import { useState, useCallback } from 'react';
import { useAgentXAPI, TaskResponse, TaskRequest } from '@/lib/api-client';

export function useAgentXTask() {
  const apiClient = useAgentXAPI();
  const [currentTask, setCurrentTask] = useState<TaskResponse | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const executeTask = useCallback(async (data: { objective: string; team_config: string }) => {
    try {
      setIsExecuting(true);
      setError(null);
      
      const taskRequest: TaskRequest = {
        config_path: getConfigPath(data.team_config),
        task_description: data.objective,
        context: {},
      };
      
      const newTask = await apiClient.createTask(taskRequest);
      setCurrentTask(newTask);
      
      // Start polling for updates
      const stopPolling = apiClient.pollTaskStatus(
        newTask.task_id, 
        (updatedTask) => {
          setCurrentTask(updatedTask);
          // Stop executing state when task completes
          if (updatedTask.status === 'completed' || updatedTask.status === 'failed') {
            setIsExecuting(false);
          }
        },
        2000
      );

      return { task: newTask, stopPolling };
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute task');
      setIsExecuting(false);
      throw err;
    }
  }, [apiClient]);

  const refetchTask = useCallback(async () => {
    if (!currentTask) return;
    
    try {
      const updatedTask = await apiClient.getTask(currentTask.task_id);
      setCurrentTask(updatedTask);
      return updatedTask;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refetch task');
    }
  }, [currentTask, apiClient]);

  return {
    executeTask,
    currentTask,
    isExecuting,
    error,
    refetchTask,
  };
}

function getConfigPath(teamConfig: string): string {
  const defaultConfig = process.env.NEXT_PUBLIC_DEFAULT_TEAM_CONFIG || 'examples/auto_writer/config/team.yaml';
  
  const configPaths: Record<string, string> = {
    'default': defaultConfig,
    'research': defaultConfig,
    'development': defaultConfig,
    'creative': defaultConfig,
  };
  
  return configPaths[teamConfig] || configPaths['default'];
}