"use client";

import { use, useState, useEffect, useCallback } from "react";
import { TaskSpacePanel } from "@/components/taskspace/taskspace-panel";
import { ChatLayout } from "@/components/chat";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/components/ui/resizable";
import { useAgentXAPI } from "@/lib/api-client";
import { ChatMessage, TaskStatus } from "@/types/chat";
import {
  Message,
  TaskStatus as AgentXTaskStatus,
  StreamEvent,
  AgentMessageEvent,
  ToolCallStartEvent,
  ToolCallResultEvent,
  TaskUpdateEvent,
  getMessageText,
} from "@/types/agentx";
import { nanoid } from "nanoid";
import { useTaskStore } from "@/store/task";
import { useMessages } from "@/hooks/use-messages";
import { useRouter } from "next/navigation";

export default function TaskPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const {
    consumeInitialMessage,
    getTask,
    setTaskInfo: updateTaskInfo,
    setTaskMessages,
    addTaskMessage,
    setTaskStatus: updateTaskStatus,
  } = useTaskStore();
  const apiClient = useAgentXAPI();
  const router = useRouter();

  const [selectedToolCall, setSelectedToolCall] = useState<any>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [taskNotFound, setTaskNotFound] = useState(false);

  // Initialize from task store if available
  const cachedTask = getTask(id);

  // Initialize all states from cache or defaults to prevent flickering
  const [messages, setMessages] = useState<ChatMessage[]>(
    cachedTask?.messages || []
  );
  const [taskStatus, setTaskStatus] = useState<TaskStatus>(
    cachedTask?.status || "pending"
  );
  const [taskInfo, setTaskInfo] = useState<any>(cachedTask || null);

  // Only show loading if we don't have cached data
  const [isLoading, setIsLoading] = useState(!cachedTask);

  // Sync messages to store when they change
  useEffect(() => {
    if (messages.length > 0) {
      setTaskMessages(id, messages);
    }
  }, [messages, id, setTaskMessages]);

  // Sync status to store when it changes
  useEffect(() => {
    updateTaskStatus(id, taskStatus);
  }, [taskStatus, id, updateTaskStatus]);

  // Load task info and set up streaming
  useEffect(() => {
    if (isInitialized) return; // Prevent multiple initializations

    const loadTask = async () => {
      try {
        // Only show loading if we don't have cached data
        if (!cachedTask) {
          setIsLoading(true);
        }

        console.log("Loading task with ID:", id);

        // Load task info
        const task = await apiClient.getTask(id);

        console.log("Task loaded successfully:", task);

        // Batch state updates to prevent flickering
        setTaskInfo(task);
        setTaskStatus(task.status || "pending");
        updateTaskInfo(id, task);

        // Only load messages if we don't have cached ones
        if (!cachedTask?.messages || cachedTask.messages.length === 0) {
          try {
            const messagesResponse = await apiClient.getMessages(id);
            if (
              messagesResponse.messages &&
              messagesResponse.messages.length > 0
            ) {
              const formattedMessages = messagesResponse.messages
                .filter((msg) => msg.role !== "tool") // Filter out tool messages
                .map((msg) => ({
                  id: msg.id,
                  role: msg.role as "user" | "assistant" | "system",
                  content: getMessageText(msg),
                  timestamp: new Date(msg.timestamp),
                  status: "complete" as const,
                  metadata: msg.metadata,
                }));
              setMessages(formattedMessages);
            }
          } catch (error) {
            console.log(
              "No existing messages or messages endpoint not available"
            );
          }
        }

        setIsLoading(false);
        setIsInitialized(true);

        // Set up streaming for new updates - with error handling
        try {
          const cleanup = apiClient.subscribeToTaskUpdates(
            id,
            (event: StreamEvent) => {
              console.log("Task update:", event);

              switch (event.event) {
                case "agent_message": {
                  const data = event.data as AgentMessageEvent;
                  const message: ChatMessage = {
                    id: nanoid(),
                    role: data.agent_id === "user" ? "user" : "assistant",
                    content: data.message,
                    timestamp: new Date(),
                    status: "complete",
                    metadata: {
                      agentId: data.agent_id,
                      ...data.metadata,
                    },
                  };
                  setMessages((prev) => [...prev, message]);
                  addTaskMessage(id, message); // Also add to store
                  break;
                }

                case "tool_call_start": {
                  const data = event.data as ToolCallStartEvent;
                  // Could update UI to show tool is running
                  console.log("Tool call started:", data);
                  break;
                }

                case "tool_call_result": {
                  const data = event.data as ToolCallResultEvent;
                  // Could update UI to show tool result
                  console.log("Tool call result:", data);
                  break;
                }

                case "agent_status": {
                  const data = event.data;
                  setTaskStatus(
                    data.status === "working" ? "running" : "pending"
                  );
                  break;
                }

                case "task_update": {
                  const data = event.data as TaskUpdateEvent;
                  setTaskStatus(data.status);
                  break;
                }

                case "log_entry": {
                  // Handled in taskspace panel
                  break;
                }

                case "artifact_created":
                case "artifact_updated": {
                  // Handled in taskspace panel
                  break;
                }

                default:
                  console.log("Unhandled event type:", event.event);
              }
            }
          );

          return cleanup;
        } catch (error) {
          console.error("Failed to set up SSE connection:", error);
          // Continue without SSE - the app should still work for existing messages
          console.log("Continuing without real-time updates");

          // Set up polling as fallback
          const pollInterval = setInterval(async () => {
            try {
              const messagesResponse = await apiClient.getMessages(id);
              if (
                messagesResponse.messages &&
                messagesResponse.messages.length > 0
              ) {
                const formattedMessages = messagesResponse.messages
                  .filter((msg) => msg.role !== "tool")
                  .map((msg) => ({
                    id: msg.id,
                    role: msg.role as "user" | "assistant" | "system",
                    content: getMessageText(msg),
                    timestamp: new Date(msg.timestamp),
                    status: "complete" as const,
                    metadata: msg.metadata,
                  }));

                // Only update if messages have changed
                setMessages((prev) => {
                  if (prev.length !== formattedMessages.length) {
                    return formattedMessages;
                  }
                  return prev;
                });
              }
            } catch (error) {
              console.error("Failed to poll for messages:", error);
            }
          }, 2000); // Poll every 2 seconds

          return () => clearInterval(pollInterval);
        }
      } catch (error) {
        console.error("Failed to load task:", error);
        console.error("Error details:", {
          message: error instanceof Error ? error.message : String(error),
          taskId: id,
        });

        setIsLoading(false);
        setIsInitialized(true);

        // If task not found, show error state
        if (
          error instanceof Error &&
          (error.message.includes("404") ||
            error.message.includes("Task not found"))
        ) {
          console.log("Task not found, showing error state");
          setTaskNotFound(true);

          // Debug: Try to list existing tasks to help with troubleshooting
          try {
            const tasksResponse = await apiClient.getTasks();
            console.log(
              "Available tasks:",
              tasksResponse.tasks.map((t) => ({
                id: t.task_id,
                status: t.status,
              }))
            );
          } catch (debugError) {
            console.log("Could not fetch available tasks:", debugError);
          }
        }
      }
    };

    const cleanupPromise = loadTask();

    return () => {
      cleanupPromise.then((cleanup) => cleanup && cleanup());
    };
  }, [id, isInitialized]); // Removed user, userLoading from dependencies

  const handleSendMessage = useCallback(
    async (message: string) => {
      // Add user message optimistically
      const userMessage: ChatMessage = {
        id: nanoid(),
        role: "user",
        content: message,
        timestamp: new Date(),
        status: "complete",
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        // Send message to backend
        await apiClient.sendMessage(id, message);
        setTaskStatus("running");
      } catch (error) {
        console.error("Failed to send message:", error);
        // You might want to show an error toast here
      }
    },
    [id, apiClient]
  );

  // Send initial message if provided (consume from store)
  useEffect(() => {
    const initialMessage = consumeInitialMessage();
    if (initialMessage && messages.length === 0 && isInitialized) {
      handleSendMessage(initialMessage);
    }
  }, [
    messages.length,
    consumeInitialMessage,
    handleSendMessage,
    isInitialized,
  ]);

  const handlePauseResume = () => {
    setTaskStatus((prev) => (prev === "running" ? "pending" : "running"));
  };

  const handleShare = () => {
    // TODO: Implement share functionality
    console.log("Share task");
  };

  const handleMoreActions = () => {
    // TODO: Implement more actions menu
    console.log("More actions");
  };

  // Show error state if task not found (after useEffect hooks have run)
  if (taskNotFound) {
    return (
      <div className="flex-1 flex items-center justify-center w-full h-full">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold text-muted-foreground">
            Task Not Found
          </h2>
          <p className="text-muted-foreground max-w-md">
            The task "{id}" doesn't exist or may have been deleted. This can
            happen if:
          </p>
          <ul className="text-sm text-muted-foreground space-y-1 max-w-md">
            <li>• The task was created in a previous session</li>
            <li>• The backend was restarted and lost task data</li>
            <li>• The task ID in the URL is invalid</li>
          </ul>
          <div className="flex gap-2 justify-center mt-6">
            <button
              onClick={() => router.push("/")}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Go to Homepage
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 border border-border rounded-md hover:bg-muted"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ResizablePanelGroup direction="horizontal" className="flex-1">
      {/* Left Panel - Chat Interface */}
      <ResizablePanel defaultSize={40} minSize={40} maxSize={80}>
        <ChatLayout
          taskId={id}
          taskName={
            taskInfo?.task_description || taskInfo?.title || `Task ${id}`
          }
          taskStatus={taskStatus}
          messages={messages}
          onSendMessage={handleSendMessage}
          onPauseResume={handlePauseResume}
          onShare={handleShare}
          onMoreActions={handleMoreActions}
          isLoading={isLoading}
        />
      </ResizablePanel>

      {/* Resize Handle */}
      <ResizableHandle className="!bg-transparent hover:!bg-border/50 transition-colors" />

      {/* Right Panel - TaskSpace */}
      <ResizablePanel defaultSize={60} minSize={20}>
        <TaskSpacePanel
          taskId={id}
          onToolCallSelect={(handler) => {
            // When a tool call is clicked in chat, pass it to taskspace
            if (selectedToolCall && typeof handler === "function") {
              handler(selectedToolCall);
              setSelectedToolCall(null);
            }
          }}
        />
      </ResizablePanel>
    </ResizablePanelGroup>
  );
}
