import { create } from "zustand";
import { persist } from "zustand/middleware";
import { ChatMessage } from "@/types/chat";
import { Message, TaskStatus } from "@/types/agentx";
import { chatMessageToMessage, messageToChatMessage } from "@/lib/message-utils";

interface TaskData {
  id: string;
  messages: ChatMessage[]; // Keep as ChatMessage for backward compatibility
  newMessages?: Message[]; // New format messages
  status: TaskStatus;
  lastUpdated: Date;
}

interface TaskState {
  // Initial message to send when a task is created
  initialMessage: string | null;
  
  // Tasks data cache
  tasks: Record<string, TaskData>;

  // Actions
  setInitialMessage: (message: string) => void;
  clearInitialMessage: () => void;
  consumeInitialMessage: () => string | null; // Returns and clears the message
  
  // Task management
  getTask: (taskId: string) => TaskData | undefined;
  setTaskMessages: (taskId: string, messages: ChatMessage[]) => void;
  addTaskMessage: (taskId: string, message: ChatMessage) => void;
  setTaskStatus: (taskId: string, status: TaskData["status"]) => void;
  clearTask: (taskId: string) => void;
}

export const useTaskStore = create<TaskState>()(
  persist(
    (set, get) => ({
      initialMessage: null,
      tasks: {},

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
      
      setTaskMessages: (taskId: string, messages: ChatMessage[]) => {
        set((state) => ({
          tasks: {
            ...state.tasks,
            [taskId]: {
              ...state.tasks[taskId],
              id: taskId,
              messages,
              lastUpdated: new Date(),
            },
          },
        }));
      },
      
      addTaskMessage: (taskId: string, message: ChatMessage) => {
        set((state) => {
          const existingTask = state.tasks[taskId];
          return {
            tasks: {
              ...state.tasks,
              [taskId]: {
                ...existingTask,
                id: taskId,
                messages: [...(existingTask?.messages || []), message],
                lastUpdated: new Date(),
              },
            },
          };
        });
      },
      
      setTaskStatus: (taskId: string, status: TaskData["status"]) => {
        set((state) => ({
          tasks: {
            ...state.tasks,
            [taskId]: {
              ...state.tasks[taskId],
              id: taskId,
              status,
              lastUpdated: new Date(),
            },
          },
        }));
      },
      
      clearTask: (taskId: string) => {
        set((state) => {
          const { [taskId]: _, ...rest } = state.tasks;
          return { tasks: rest };
        });
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
            messages: task.messages.slice(-50), // Keep only last 50 messages
          };
          return acc;
        }, {} as Record<string, TaskData>),
      }),
    }
  )
);
