"use client";

import { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useMessages } from "@/hooks/use-messages";
import { Bot, User, Wrench } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface AgentMessagesProps {
  taskId: string;
}

export function AgentMessages({ taskId }: AgentMessagesProps) {
  const { messages, isLoading } = useMessages(taskId);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <ScrollArea className="h-[600px] pr-4" ref={scrollRef}>
      <div className="space-y-4">
        {messages.map((message) => (
          <Card key={message.id} className="p-4">
            <div className="flex items-start gap-3">
              <Avatar className="h-8 w-8">
                <div className="flex items-center justify-center w-full h-full bg-primary/10">
                  {message.agent === "user" ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </div>
              </Avatar>

              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm">{message.agent}</span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                  {message.tool_calls && message.tool_calls.length > 0 && (
                    <Badge variant="outline" className="text-xs">
                      <Wrench className="h-3 w-3 mr-1" />
                      {message.tool_calls.length} tool
                      {message.tool_calls.length > 1 ? "s" : ""}
                    </Badge>
                  )}
                </div>

                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                </div>

                {message.tool_calls && message.tool_calls.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {message.tool_calls.map((tool, idx) => (
                      <div key={idx} className="text-xs bg-muted p-2 rounded">
                        <span className="font-mono">{tool.name}</span>
                        {tool.args && (
                          <pre className="mt-1 text-xs opacity-70">
                            {JSON.stringify(tool.args, null, 2)}
                          </pre>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </ScrollArea>
  );
}
