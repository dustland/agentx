"use client";

import { use, useState, useCallback, useEffect } from "react";
import { Workspace } from "@/components/project";
import { ChatLayout } from "@/components/chat";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/components/ui/resizable";
import { useChat } from "@/hooks/use-chat";
import { useProject, useProjectPlan } from "@/hooks/use-project";
import { useAppStore } from "@/store/app";

export default function XAgentPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { initialMessage, setInitialMessage } = useAppStore();

  // Use the XAgent hook to get executeProject
  const { executeProject } = useProject(id);

  // Use the plan hook to check if plan exists
  const { hasPlan } = useProjectPlan(id);

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
    projectId: id,
    onError: (error) => {
      console.error("Chat error:", error);
      // You could show a toast here
    },
  });

  // Send initial message if present
  useEffect(() => {
    // Only send initial message if we have one and messages have been loaded (not loading)
    if (initialMessage && !isMessagesLoading && messages.length === 0) {
      handleSubmit(initialMessage);
      setInitialMessage(null);
    }
  }, [
    initialMessage,
    messages.length,
    isMessagesLoading,
    handleSubmit,
    setInitialMessage,
  ]);

  // ChatLayout expects onSendMessage to be (message: string, mode?: "agent" | "chat") => void
  const handleSendMessage = (message: string, mode?: "agent" | "chat") => {
    // If no message and plan exists in agent mode, execute the plan
    if (!message && hasPlan && mode === "agent") {
      executeProject.mutate();
      return;
    }

    // Otherwise, pass the message with mode to handleSubmit
    handleSubmit(message, mode);
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
            onStop={stop}
            isLoading={isLoading}
            allowEmptyMessage={hasPlan}
          />
        </ResizablePanel>
        <ResizableHandle className="!bg-transparent" />
        <ResizablePanel defaultSize={45} minSize={20}>
          <Workspace
            projectId={id}
            onToolCallSelect={registerToolCallHandler}
          />
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}
