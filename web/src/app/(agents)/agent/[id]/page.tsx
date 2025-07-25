"use client";

import { use, useState, useCallback, useEffect } from "react";
import { Workspace } from "@/components/project";
import { ChatLayout } from "@/components/chat";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/components/ui/resizable";
import { useXAgent, usePlan } from "@/hooks/use-xagent";
import { useAppStore } from "@/store/app";

export default function XAgentPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { initialMessage, setInitialMessage } = useAppStore();

  // Use the XAgent hook for all functionality
  const {
    messages,
    input,
    isLoading,
    isMessagesLoading,
    handleInputChange,
    handleSubmit,
    setInput,
    isSendingMessage,
  } = useXAgent(id);

  // Use the plan hook to check if plan exists
  const { plan } = usePlan(id);

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

  // ChatLayout expects onSendMessage to be (message: string, mode?: "chat" | "agent") => void
  const handleSendMessage = (message: string, mode?: "chat" | "agent") => {
    // Convert "agent" mode to "command" for the API
    const apiMode = mode === "agent" ? "command" : mode;
    handleSubmit(message, apiMode);
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
            allowEmptyMessage={!!plan}
          />
        </ResizablePanel>
        <ResizableHandle className="!bg-transparent" />
        <ResizablePanel defaultSize={45} minSize={20}>
          <Workspace xagentId={id} onToolCallSelect={registerToolCallHandler} />
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}
