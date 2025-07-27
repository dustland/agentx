"use client";

import React, { createContext, useContext, ReactNode } from "react";
import { useXAgent } from "@/hooks/use-xagent";

interface XAgentContextType {
  // Data
  xagent: any;
  messages: any[];
  artifacts: any;

  // Loading states
  isLoading: boolean;
  isMessagesLoading: boolean;
  isLoadingArtifacts: boolean;

  // Error states
  error: any;
  messagesError: any;
  artifactsError: any;

  // Chat functionality
  input: string;
  handleSubmit: (message: string, mode?: "chat" | "agent") => void;
  handleInputChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
  setInput: (value: string) => void;

  // Chat loading state
  isSendingMessage: boolean;

  // Mutations
  deleteXAgent: any;
}

const XAgentContext = createContext<XAgentContextType | undefined>(undefined);

export function XAgentProvider({
  children,
  xagentId,
}: {
  children: ReactNode;
  xagentId: string;
}) {
  const xagentData = useXAgent(xagentId);

  return (
    <XAgentContext.Provider value={xagentData}>
      {children}
    </XAgentContext.Provider>
  );
}

export function useXAgentContext() {
  const context = useContext(XAgentContext);
  if (context === undefined) {
    throw new Error("useXAgentContext must be used within a XAgentProvider");
  }
  return context;
}
