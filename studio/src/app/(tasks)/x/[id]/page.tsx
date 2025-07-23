"use client";

import { use, useState, useCallback, useEffect } from "react";
import { TaskSpacePanel } from "@/components/taskspace/panel";
import { ChatLayout } from "@/components/chat";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/components/ui/resizable";
import { useChat } from "@/hooks/use-chat";
import { useAppStore } from "@/store/app";

export default function TaskPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { initialMessage, setInitialMessage } = useAppStore();

  // Use the chat hook for chat functionality
  const {
    messages,
    input,
    isLoading,
    isMessagesLoading,
    handleInputChange,
    handleSubmit,
    stop,
    setInput,
  } = useChat({
    taskId: id,
    onError: (error) => {
      console.error("Chat error:", error);
      // You could show a toast here
    },
  });

  // Send initial message if present
  useEffect(() => {
    if (initialMessage && messages.length === 0) {
      handleSubmit(initialMessage);
      setInitialMessage(null);
    }
  }, [initialMessage, messages.length, handleSubmit, setInitialMessage]);

  const handlePauseResume = () => {
    // TODO: Implement pause/resume functionality
    console.log("Pause/Resume clicked");
  };

  // ChatLayout expects onSendMessage to be (message: string) => void
  const handleSendMessage = (message: string) => {
    // Pass the message directly to handleSubmit
    handleSubmit(message);
  };

  // Callback registration function for tool call selection
  const registerToolCallHandler = useCallback(
    (handler: (toolCall: any) => void) => {
      // Store the handler if needed, or just use it directly
      // For now, we don't need to do anything with selected tool calls
    },
    []
  );

  return (
    <div className="flex-1 flex flex-col h-screen">
      <ResizablePanelGroup
        direction="horizontal"
        className="flex-1 overflow-hidden"
      >
        <ResizablePanel defaultSize={55} minSize={30}>
          <ChatLayout
            messages={messages}
            onSendMessage={handleSendMessage}
            taskStatus={isLoading ? "running" : "pending"}
            onStop={stop}
            onPauseResume={handlePauseResume}
            isLoading={isLoading}
            taskId={id}
            taskName="Task"
            onShare={() => {}}
            onMoreActions={() => {}}
          />
        </ResizablePanel>
        <ResizableHandle className="!bg-transparent" />
        <ResizablePanel defaultSize={45} minSize={20}>
          <TaskSpacePanel
            taskId={id}
            onToolCallSelect={registerToolCallHandler}
          />
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}
