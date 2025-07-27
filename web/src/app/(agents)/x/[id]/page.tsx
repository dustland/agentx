"use client";

import { use, useState, useCallback, useEffect } from "react";
import { Workspace } from "@/components/xagent";
import { ChatLayout } from "@/components/chat";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/components/ui/resizable";
import { XAgentProvider, useXAgentContext } from "@/contexts/xagent";
import { useAppStore } from "@/store/app";

function XAgentPageContent({ id }: { id: string }) {
  const { initialMessage, setInitialMessage } = useAppStore();

  // Use the XAgent context for all functionality
  const { messages, isMessagesLoading, handleSubmit } = useXAgentContext();

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
          <ChatLayout />
        </ResizablePanel>
        <ResizableHandle className="!bg-transparent" />
        <ResizablePanel defaultSize={45} minSize={20}>
          <Workspace xagentId={id} onToolCallSelect={registerToolCallHandler} />
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}

export default function XAgentPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  return (
    <XAgentProvider xagentId={id}>
      <XAgentPageContent id={id} />
    </XAgentProvider>
  );
}
