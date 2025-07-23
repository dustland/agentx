import { create } from "zustand";
import { persist } from "zustand/middleware";
import { ChatMessage } from "@/types/chat";
import { Message, TaskStatus } from "@/types/agentx";
import {
  chatMessageToMessage,
  messageToChatMessage,
} from "@/lib/message-utils";

interface TaskData {
  id: string;
  messages: ChatMessage[]; // Keep as ChatMessage for backward compatibility
  newMessages?: Message[]; // New format messages
  status: TaskStatus;
  lastUpdated: Date;
  // Task info fields for caching
  task_description?: string;
  config_path?: string;
  created_at?: string;
  updated_at?: string;
  completed_at?: string;
  error?: string;
  result?: Record<string, any>;
  user_id?: string;
  context?: Record<string, any>;
}

interface TaskState {
  // Initial message to send when a task is created
  initialMessage: string | null;

  // Tasks data cache
  tasks: Record<string, TaskData>;

  // Task list management
  tasksList: TaskData[];
  tasksListLoading: boolean;
  tasksListError: string | null;
  lastTasksListFetch: Date | null;

  // Actions
  setInitialMessage: (message: string) => void;
  clearInitialMessage: () => void;
  consumeInitialMessage: () => string | null; // Returns and clears the message

  // Task management
  getTask: (taskId: string) => TaskData | undefined;
  setTaskInfo: (taskId: string, taskInfo: any) => void;
  setTaskMessages: (taskId: string, messages: ChatMessage[]) => void;
  addTaskMessage: (taskId: string, message: ChatMessage) => void;
  setTaskStatus: (taskId: string, status: TaskData["status"]) => void;
  clearTask: (taskId: string) => void;
  
  // Task list management
  setTasksList: (tasks: TaskData[]) => void;
  setTasksListLoading: (loading: boolean) => void;
  setTasksListError: (error: string | null) => void;
  updateTaskInList: (taskId: string, updates: Partial<TaskData>) => void;
  removeTaskFromList: (taskId: string) => void;
}

export const useTaskStore = create<TaskState>()(
  persist(
    (set, get) => ({
      initialMessage: null,
      tasks: {},
      tasksList: [],
      tasksListLoading: false,
      tasksListError: null,
      lastTasksListFetch: null,

      setInitialMessage: (message: string) => {
        set({ initialMessage: message });
      },

      clearInitialMessage: () => {
        set({ initialMessage: null });
      },

      consumeInitialMessage: () => {
        const message = get().initialMessage;
        if (message) {
          set({ initialMessage: null });
        }
        return message;
      },

      getTask: (taskId: string) => {
        return get().tasks[taskId];
      },

      setTaskInfo: (taskId: string, taskInfo: any) => {
        set((state) => {
          const existingTask = state.tasks[taskId];
          return {
            tasks: {
              ...state.tasks,
              [taskId]: {
                ...existingTask,
                id: taskId,
                ...taskInfo,
                lastUpdated: new Date(),
              },
            },
          };
        });
      },

      setTaskMessages: (taskId: string, messages: ChatMessage[]) => {
        set((state) => {
          const existingTask = state.tasks[taskId];
          return {
            tasks: {
              ...state.tasks,
              [taskId]: {
                ...existingTask,
                id: taskId,
                messages,
                status: existingTask?.status || "pending",
                lastUpdated: new Date(),
              },
            },
          };
        });
      },

      addTaskMessage: (taskId: string, message: ChatMessage) => {
        set((state) => {
          const existingTask = state.tasks[taskId];
          const existingMessages = existingTask?.messages || [];
          
          // Check for duplicate messages by content and role within a short time window
          const isDuplicate = existingMessages.some(m => 
            m.role === message.role && 
            m.content === message.content &&
            Math.abs(new Date(m.timestamp).getTime() - new Date(message.timestamp).getTime()) < 5000 // 5 second window
          );
          
          if (isDuplicate) {
            console.log("Skipping duplicate message:", message);
            return state;
          }
          
          return {
            tasks: {
              ...state.tasks,
              [taskId]: {
                ...existingTask,
                id: taskId,
                messages: [...existingMessages, message],
                lastUpdated: new Date(),
              },
            },
          };
        });
      },

      setTaskStatus: (taskId: string, status: TaskData["status"]) => {
        set((state) => {
          const existingTask = state.tasks[taskId];
          return {
            tasks: {
              ...state.tasks,
              [taskId]: {
                ...existingTask,
                id: taskId,
                messages: existingTask?.messages || [],
                status,
                lastUpdated: new Date(),
              },
            },
          };
        });
      },

      clearTask: (taskId: string) => {
        set((state) => {
          const { [taskId]: _, ...rest } = state.tasks;
          return { tasks: rest };
        });
      },

      // Task list management methods
      setTasksList: (tasks: TaskData[]) => {
        set({ 
          tasksList: tasks,
          lastTasksListFetch: new Date()
        });
      },

      setTasksListLoading: (loading: boolean) => {
        set({ tasksListLoading: loading });
      },

      setTasksListError: (error: string | null) => {
        set({ tasksListError: error });
      },

      updateTaskInList: (taskId: string, updates: Partial<TaskData>) => {
        set((state) => ({
          tasksList: state.tasksList.map(task => 
            task.id === taskId ? { ...task, ...updates } : task
          )
        }));
      },

      removeTaskFromList: (taskId: string) => {
        set((state) => ({
          tasksList: state.tasksList.filter(task => task.id !== taskId)
        }));
      },
    }),
    {
      name: "task-store",
      // Persist initial message and task data
      partialize: (state) => ({
        initialMessage: state.initialMessage,
        // Only persist task status and last 50 messages per task to avoid storage limits
        tasks: Object.entries(state.tasks).reduce((acc, [id, task]) => {
          acc[id] = {
            ...task,
            messages: task.messages?.slice(-50) || [], // Keep only last 50 messages
          };
          return acc;
        }, {} as Record<string, TaskData>),
      }),
    }
  )
);
