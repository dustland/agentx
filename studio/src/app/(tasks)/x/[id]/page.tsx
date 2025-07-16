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
import { useTaskStore } from "@/lib/stores/task-store";
import { useUser } from "@/contexts/user-context";
import { useMessages } from "@/hooks/use-messages";

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
  const { user } = useUser();
  const apiClient = useAgentXAPI();

  const [selectedToolCall, setSelectedToolCall] = useState<any>(null);
  const [isInitialized, setIsInitialized] = useState(false);

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

        // Load task info
        const task = await apiClient.getTask(id);

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

        // Set up streaming for new updates
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
        console.error("Failed to load task:", error);
        setIsLoading(false);
        setIsInitialized(true);
      }
    };

    const cleanupPromise = loadTask();

    return () => {
      cleanupPromise.then((cleanup) => cleanup && cleanup());
    };
  }, [id, isInitialized]); // Add isInitialized to prevent multiple runs

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
