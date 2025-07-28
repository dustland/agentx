"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import {
  ChevronRight,
  ChevronDown,
  XCircle,
  FileCode,
  CheckCircle2,
  Copy,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { GenericMessagePart } from "./generic-message-part";
import { ToolCall, ToolResult } from "./tool-message-parts";

// Types matching Vercel AI SDK structure
export interface TextPart {
  type: "text";
  text: string;
}

export interface ToolCallPart {
  type: "tool-call";
  toolCallId: string;
  toolName: string;
  args: Record<string, any>;
  // UI-specific fields for streaming status
  status?: "pending" | "running" | "completed" | "failed";
  duration?: number;
}

export interface ToolResultPart {
  type: "tool-result";
  toolCallId: string;
  toolName: string;
  result: any;
  isError?: boolean;
  duration?: number;
}

export interface ImagePart {
  type: "image";
  image: string; // URL or base64
  mimeType?: string;
}

export interface FilePart {
  type: "file";
  data: string; // URL or base64
  mimeType: string;
}

export interface StepStartPart {
  type: "step-start";
  stepId: string;
  stepName?: string;
}

export interface ReasoningPart {
  type: "reasoning";
  content: string;
}

export interface ErrorPart {
  type: "error";
  error: string;
  errorCode?: string;
}

export type MessagePart =
  | TextPart
  | ToolCallPart
  | ToolResultPart
  | ImagePart
  | FilePart
  | StepStartPart
  | ReasoningPart
  | ErrorPart;

interface Artifact {
  path: string;
  type: "file" | "directory";
  size?: number;
  content?: string;
  created_at?: string;
  modified_at?: string;
  displayPath?: string;
}

interface MessagePartsProps {
  parts: MessagePart[];
  isStreaming?: boolean;
  onArtifactSelect?: ((artifact: Artifact) => void) | null;
}

// Text Part Component
function TextPartComponent({ part }: { part: TextPart }) {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  
  if (!part.text) return null;

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  // For simple text without markdown, render directly without wrapper
  const isSimpleText = !part.text.includes('\n') && 
    !part.text.includes('#') && 
    !part.text.includes('`') && 
    !part.text.includes('[') && 
    !part.text.includes('*') &&
    part.text.length < 200;

  if (isSimpleText) {
    return (
      <div className="text-sm leading-relaxed py-1">
        {part.text}
      </div>
    );
  }

  // For complex text with markdown, use the full renderer
  return (
    <div className="text-sm leading-relaxed">
      <ReactMarkdown
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const isInline = !className;
            const codeString = String(children).replace(/\n$/, "");
            
            return !isInline && match ? (
              <div className="relative my-2 group">
                <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0"
                    onClick={() => handleCopyCode(codeString)}
                  >
                    {copiedCode === codeString ? (
                      <CheckCircle2 className="h-3 w-3" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{
                    fontSize: '0.875rem',
                    padding: '1rem',
                    paddingRight: '3rem',
                    borderRadius: '0.375rem',
                  }}
                >
                  {codeString}
                </SyntaxHighlighter>
              </div>
            ) : (
              <code
                className={cn(
                  "bg-muted px-1.5 py-0.5 rounded-md text-xs font-mono",
                  className
                )}
                {...props}
              >
                {children}
              </code>
            );
          },
          p: ({ children }) => <p className="mb-2">{children}</p>,
          ul: ({ children }) => <ul className="list-disc list-inside mb-2 ml-3">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 ml-3">{children}</ol>,
          li: ({ children }) => <li className="mb-1">{children}</li>,
          h1: ({ children }) => <h1 className="text-lg font-semibold mb-2 mt-3">{children}</h1>,
          h2: ({ children }) => <h2 className="text-base font-semibold mb-2 mt-3">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-semibold mb-1.5 mt-2">{children}</h3>,
        }}
      >
        {part.text}
      </ReactMarkdown>
    </div>
  );
}

// Tool message part wrappers - delegating to the new components
function ToolCallPartComponent({ 
  part,
  onArtifactSelect 
}: { 
  part: ToolCallPart;
  onArtifactSelect?: ((artifact: Artifact) => void) | null;
}) {
  return <ToolCall part={part} onArtifactSelect={onArtifactSelect} />;
}

function ToolResultPartComponent({
  part,
  onArtifactSelect,
}: {
  part: ToolResultPart;
  onArtifactSelect?: ((artifact: Artifact) => void) | null;
}) {
  return <ToolResult part={part} onArtifactSelect={onArtifactSelect} />;
}

// Reasoning Part Component
function ReasoningPartComponent({ part }: { part: ReasoningPart }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <GenericMessagePart
      variant="muted"
      icon={FileCode}
      title="Agent reasoning..."
      titleClassName="italic"
      expandable={true}
      expanded={isExpanded}
      onExpandedChange={setIsExpanded}
      expandedContent={
        <div className="text-sm text-muted-foreground italic">
          {part.content}
        </div>
      }
    />
  );
}

// Step Start Component - keeping original design as it's unique
function StepStartPartComponent({ part }: { part: StepStartPart }) {
  return (
    <div className="flex items-center gap-2 my-3 text-muted-foreground">
      <div className="flex-1 h-px bg-border" />
      <span className="text-xs font-medium px-2">
        {part.stepName || `Step ${part.stepId}`}
      </span>
      <div className="flex-1 h-px bg-border" />
    </div>
  );
}

// Image Part Component
function ImagePartComponent({ part }: { part: ImagePart }) {
  const [isExpanded, setIsExpanded] = useState(true);

  const badges = part.mimeType ? [{ label: part.mimeType, variant: "outline" as const }] : [];

  return (
    <GenericMessagePart
      title="Image"
      badges={badges}
      expandable={true}
      expanded={isExpanded}
      onExpandedChange={setIsExpanded}
      expandedContent={
        <img
          src={part.image}
          alt="Message image"
          className="max-w-full rounded-md border"
        />
      }
    />
  );
}

// Error Part Component
function ErrorPartComponent({ part }: { part: ErrorPart }) {
  const badges = part.errorCode ? [{ label: part.errorCode, variant: "destructive" as const }] : [];
  
  return (
    <GenericMessagePart
      variant="error"
      statusIcon={<XCircle className="w-4 h-4 text-destructive" />}
      title="Error"
      badges={badges}
      expandedContent={
        <div className="text-sm text-destructive">
          {part.error}
        </div>
      }
      expanded={true}
    />
  );
}

// Main component
export function MessageParts({
  parts,
  isStreaming,
  onArtifactSelect,
}: MessagePartsProps) {
  if (!parts || parts.length === 0) return null;

  return (
    <div className="space-y-1">
      {parts.map((part, index) => {
        const key = `part-${index}-${part.type}`;

        switch (part.type) {
          case "text":
            return <TextPartComponent key={key} part={part} />;
          case "tool-call":
            return (
              <ToolCallPartComponent 
                key={key} 
                part={part as ToolCallPart} 
                onArtifactSelect={onArtifactSelect}
              />
            );
          case "tool-result":
            return (
              <ToolResultPartComponent
                key={key}
                part={part as ToolResultPart}
                onArtifactSelect={onArtifactSelect}
              />
            );
          case "reasoning":
            return (
              <ReasoningPartComponent key={key} part={part as ReasoningPart} />
            );
          case "step-start":
            return (
              <StepStartPartComponent key={key} part={part as StepStartPart} />
            );
          case "image":
            return <ImagePartComponent key={key} part={part as ImagePart} />;
          case "error":
            return <ErrorPartComponent key={key} part={part as ErrorPart} />;
          default:
            return null;
        }
      })}
    </div>
  );
}