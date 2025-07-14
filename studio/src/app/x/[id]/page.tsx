"use client";

import { use, useState, useEffect } from "react";
import { TaskSidebar } from "@/components/layout/task-sidebar";
import { TaskSpacePanel } from "@/components/taskspace/taskspace-panel";
import { ChatLayout } from "@/components/chat";
import { cn } from "@/lib/utils";
import { 
  ResizablePanelGroup, 
  ResizablePanel, 
  ResizableHandle 
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
  
  const [isSidebarPinned, setIsSidebarPinned] = useState(true);
  const [selectedToolCall, setSelectedToolCall] = useState<any>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [taskStatus, setTaskStatus] = useState<TaskStatus>("idle");
  const [taskInfo, setTaskInfo] = useState<any>(null);

  // Load task info
  useEffect(() => {
    const loadTask = async () => {
      try {
        const task = await apiClient.getTask(id);
        setTaskInfo(task);
        setTaskStatus(task.status || "idle");
      } catch (error) {
        console.error("Failed to load task:", error);
      }
    };
    loadTask();
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
    setMessages(prev => [...prev, userMessage]);
    
    // TODO: Send to backend and handle streaming response
    setTaskStatus("running");
  };

  const handlePauseResume = () => {
    setTaskStatus(prev => prev === "running" ? "paused" : "running");
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

  return (
    <>
      {/* Main Layout Container */}
      <div className="h-screen flex bg-muted/30">
        {/* Sidebar - only renders when pinned */}
        {isSidebarPinned && (
          <TaskSidebar 
            className="flex-shrink-0"
            isFloating={false}
            onFloatingChange={setIsSidebarPinned}
          />
        )}
        
        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden relative">
          {/* Floating Sidebar */}
          {isSidebarFloating && (
            <TaskSidebar 
              isFloating={true}
              onFloatingChange={setIsSidebarPinned}
            />
          )}
          
          {/* Task Execution Area */}
          <ResizablePanelGroup direction="horizontal" className="flex-1">
              {/* Left Panel - Chat Interface */}
              <ResizablePanel defaultSize={60} minSize={40} maxSize={80}>
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
              <ResizablePanel defaultSize={40} minSize={20}>
                <TaskSpacePanel 
                  taskId={id}
                  onToolCallSelect={(handler) => {
                    // When a tool call is clicked in chat, pass it to taskspace
                    if (selectedToolCall && typeof handler === 'function') {
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