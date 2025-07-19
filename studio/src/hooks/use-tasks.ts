import { useEffect, useCallback } from "react";
import { useAgentXAPI } from "@/lib/api-client";
import { useTaskStore } from "@/store/task";
import { Task as TaskResponse } from "@/types/agentx";

export function useTasks() {
  const apiClient = useAgentXAPI();
  const {
    tasksList,
    tasksListLoading,
    tasksListError,
    lastTasksListFetch,
    setTasksList,
    setTasksListLoading,
    setTasksListError,
    updateTaskInList,
    removeTaskFromList,
  } = useTaskStore();

  // Check if we should refresh (cache for 30 seconds)
  const shouldRefresh = useCallback(() => {
    if (!lastTasksListFetch) return true;
    const thirtySecondsAgo = new Date(Date.now() - 30 * 1000);
    return lastTasksListFetch < thirtySecondsAgo;
  }, [lastTasksListFetch]);

  // Load tasks from API
  const loadTasks = useCallback(async (force = false) => {
    // Skip if already loading or cache is fresh (unless forced)
    if (tasksListLoading || (!force && !shouldRefresh())) {
      return;
    }

    try {
      setTasksListLoading(true);
      setTasksListError(null);
      
      const response = await apiClient.getTasks();
      
      // Convert API response to our TaskData format
      const tasksData = (response.tasks || []).map((task: TaskResponse) => ({
        id: task.task_id,
        status: task.status,
        lastUpdated: new Date(),
        task_description: task.task_description,
        config_path: task.config_path,
        created_at: task.created_at,
        updated_at: task.updated_at,
        completed_at: task.completed_at,
        error: task.error,
        result: task.result,
        user_id: task.user_id,
        context: task.context,
        messages: [], // Will be loaded when task is opened
      }));
      
      setTasksList(tasksData);
    } catch (error) {
      console.error("Failed to load tasks:", error);
      setTasksListError(error instanceof Error ? error.message : "Failed to load tasks");
    } finally {
      setTasksListLoading(false);
    }
  }, [apiClient, tasksListLoading, shouldRefresh, setTasksList, setTasksListLoading, setTasksListError]);

  // Delete a task
  const deleteTask = useCallback(async (taskId: string) => {
    try {
      await apiClient.deleteTask(taskId);
      removeTaskFromList(taskId);
      return true;
    } catch (error) {
      console.error("Failed to delete task:", error);
      return false;
    }
  }, [apiClient, removeTaskFromList]);

  // Update task status
  const updateTaskStatus = useCallback((taskId: string, status: TaskResponse['status']) => {
    updateTaskInList(taskId, { status });
  }, [updateTaskInList]);

  // Auto-load tasks on mount
  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  // Set up polling for real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      loadTasks();
    }, 10000); // Poll every 10 seconds

    return () => clearInterval(interval);
  }, [loadTasks]);

  return {
    tasks: tasksList,
    loading: tasksListLoading,
    error: tasksListError,
    loadTasks,
    deleteTask,
    updateTaskStatus,
    refetch: () => loadTasks(true), // Force refresh
  };
}