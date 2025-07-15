"use client";

import { use, useState, useEffect, useCallback } from "react";
import { TaskSidebar } from "@/components/layout/task-sidebar";
import { TaskSpacePanel } from "@/components/taskspace/taskspace-panel";
import { ChatLayout } from "@/components/chat";
import { cn } from "@/lib/utils";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/components/ui/resizable";
import { useAgentXAPI } from "@/lib/api-client";
import { ChatMessage, TaskStatus } from "@/types/chat";
import { nanoid } from "nanoid";

export default function TaskPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const { id } = use(params);
  const { description } = use(searchParams);
  const apiClient = useAgentXAPI();

  const [isSidebarPinned, setIsSidebarPinned] = useState(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("sidebar-pinned");
      return stored !== null ? stored === "true" : true;
    }
    return true;
  });
  const [selectedToolCall, setSelectedToolCall] = useState<any>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [taskStatus, setTaskStatus] = useState<TaskStatus>("pending");
  const [taskInfo, setTaskInfo] = useState<any>(null);

  // Load task info and set up streaming
  useEffect(() => {
    const loadTask = async () => {
      try {
        const task = await apiClient.getTask(id);
        setTaskInfo(task);
        setTaskStatus(task.status || "pending");

        // Set up streaming for task updates
        const cleanup = apiClient.subscribeToTaskUpdates(id, (data) => {
          console.log("Task update:", data);

          if (data.event === "agent_message") {
            const message: ChatMessage = {
              id: nanoid(),
              role: data.data.agent_id === "user" ? "user" : "assistant",
              content: data.data.message,
              timestamp: new Date(),
              status: "complete",
              metadata: data.data.metadata,
            };
            setMessages((prev) => [...prev, message]);
          } else if (data.event === "agent_status") {
            setTaskStatus(
              data.data.status === "working" ? "running" : "pending"
            );
          } else if (data.event === "task_update") {
            setTaskStatus(data.data.status);
          }
        });

        return cleanup;
      } catch (error) {
        console.error("Failed to load task:", error);
      }
    };

    const cleanupPromise = loadTask();

    return () => {
      cleanupPromise.then((cleanup) => cleanup && cleanup());
    };
  }, [id]);

  const handleSendMessage = (message: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: nanoid(),
      role: "user",
      content: message,
      timestamp: new Date(),
      status: "complete",
    };
    setMessages((prev) => [...prev, userMessage]);

    // TODO: Send to backend and handle streaming response
    setTaskStatus("running");
  };

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

  // Check if sidebar is floating based on viewport or user preference
  const isSidebarFloating = !isSidebarPinned;

  const handleFloatingChange = useCallback((floating: boolean) => {
    // Only update if the state actually needs to change
    setIsSidebarPinned((prev) => {
      const newValue = !floating;
      if (prev !== newValue) {
        localStorage.setItem("sidebar-pinned", newValue.toString());
        return newValue;
      }
      return prev;
    });
  }, []);

  return (
    <>
      {/* Main Layout Container */}
      <div className="h-screen flex bg-muted/50">
        {/* Sidebar - only renders when pinned */}
        {isSidebarPinned && (
          <TaskSidebar
            className="flex-shrink-0"
            isFloating={false}
            onFloatingChange={handleFloatingChange}
          />
        )}

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden relative">
          {/* Floating Sidebar */}
          {isSidebarFloating && (
            <TaskSidebar
              isFloating={true}
              onFloatingChange={handleFloatingChange}
            />
          )}

          {/* Task Execution Area */}
          <ResizablePanelGroup direction="horizontal" className="flex-1">
            {/* Left Panel - Chat Interface */}
            <ResizablePanel defaultSize={40} minSize={40} maxSize={80}>
              <ChatLayout
                taskId={id}
                taskName={taskInfo?.title || `Task ${id}`}
                taskStatus={taskStatus}
                messages={messages}
                onSendMessage={handleSendMessage}
                onPauseResume={handlePauseResume}
                onShare={handleShare}
                onMoreActions={handleMoreActions}
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
        </div>
      </div>
    </>
  );
}
