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

// Define the Artifact interface to match workspace
interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
  displayPath?: string;
}

interface ToolCall {
  id: string;
  xagent_id: string;
  tool_name: string;
  parameters: any;
  result?: any;
  timestamp: string;
  status: "pending" | "completed" | "error";
}

function XAgentPageContent({ id }: { id: string }) {
  const { initialMessage, setInitialMessage } = useAppStore();

  // Use the XAgent context for all functionality
  const { messages, isMessagesLoading, handleSubmit } = useXAgentContext();

  // State for workspace artifact selection
  const [workspaceArtifactHandler, setWorkspaceArtifactHandler] = useState<
    ((artifact: Artifact) => void) | null
  >(null);

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
    (handler: (toolCall: ToolCall) => void) => {
      // Store the handler if needed, or just use it directly
      // For now, we don't need to do anything with selected tool calls
    },
    []
  );

  // Callback registration function for artifact selection
  const registerArtifactHandler = useCallback(
    (handler: (artifact: Artifact) => void) => {
      setWorkspaceArtifactHandler(() => handler);
    },
    []
  );

  return (
    <div className="h-screen w-full flex flex-col">
      <ResizablePanelGroup
        direction="horizontal"
        className="flex-1 min-h-0 w-full"
      >
        <ResizablePanel defaultSize={55} minSize={30}>
          <ChatLayout onArtifactSelect={workspaceArtifactHandler} />
        </ResizablePanel>
        <ResizableHandle className="!bg-transparent" />
        <ResizablePanel defaultSize={45} minSize={20}>
          <Workspace
            xagentId={id}
            onToolCallSelect={registerToolCallHandler}
            onArtifactHandlerRegister={registerArtifactHandler}
          />
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
