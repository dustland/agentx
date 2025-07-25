"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChat } from "@/hooks/use-chat";
import { useProject } from "@/hooks/use-project";
import { Loader2, Send, Zap, MessageSquare, Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

export default function HooksTestPage() {
  const [projectId, setProjectId] = useState<string>("");
  const [customMessage, setCustomMessage] = useState<string>(
    "Tell me a joke about programming in exactly 3 sentences."
  );
  const [isCreatingTask, setIsCreatingTask] = useState(false);
  const [streamEvents, setStreamEvents] = useState<any[]>([]);

  // Only use hooks when we have a valid projectId
  const projectHook = useProject(projectId || "dummy-task-id");
  const chatHook = useChat({
    taskId: projectId || "dummy-task-id",
    onError: (error) => console.error("Chat error:", error),
  });

  // Disable hooks when no projectId
  const isHooksActive = !!projectId;

  // Track streaming events from chat hook
  useEffect(() => {
    if (!projectId || projectId === "dummy-task-id") return;

    console.log("[TEST] Setting up monitoring for project:", projectId);

    // The useTask hook already handles subscriptions internally
    // We can track messages and streaming state through the chat hook

    return () => {
      console.log("[TEST] Cleaning up monitoring");
      projectHook.stop();
    };
  }, [projectId, projectHook]);

  // Track message changes for streaming events
  useEffect(() => {
    // Since useChat doesn't expose streaming messages directly,
    // we'll track changes in the messages array
    if (chatHook.messages.length > 0) {
      const lastMessage = chatHook.messages[chatHook.messages.length - 1];
      console.log("[TEST] Messages updated, last message:", lastMessage);
    }
  }, [chatHook.messages]);

  const createTestProject = async () => {
    setIsCreatingTask(true);
    try {
      // Directly call the backend API with a test user ID
      const response = await fetch("http://localhost:7770/tasks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-ID": "test-user-streaming", // Test user ID
        },
        body: JSON.stringify({
          config_path: "examples/simple_chat/config/team.yaml",
          task_description: "Chat with me",
          initial_message: "Hi! I'm ready to chat.",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setProjectId(data.task_id);
      setStreamEvents([]);
    } catch (error) {
      console.error("Failed to create task:", error);
      toast(
        "Failed to create task. Please make sure the backend is running on http://localhost:7770"
      );
    } finally {
      setIsCreatingTask(false);
    }
  };

  const sendTestMessage = async () => {
    if (!projectId || !customMessage.trim()) return;
    console.log("[TEST] Sending message:", customMessage);
    console.log("[TEST] Project ID:", projectId);
    setStreamEvents([]);

    try {
      await chatHook.handleSubmit(customMessage);
      console.log("[TEST] Message sent successfully");
    } catch (error) {
      console.error("[TEST] Error sending message:", error);
    }
  };

  const StreamingVisualizer = () => {
    // Since we don't have direct access to streaming messages,
    // we'll show the loading state when messages are being sent
    if (!chatHook.isLoading) return null;

    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-sm font-medium">Processing Message</span>
        </div>

        <div className="p-4 bg-muted/50 rounded-lg border border-primary/20">
          <div className="text-sm mb-2 text-muted-foreground">
            Waiting for response...
          </div>
          <div className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">AI is thinking...</span>
          </div>
        </div>
      </div>
    );
  };

  const EventLog = () => {
    return (
      <ScrollArea className="h-[300px]">
        <div className="space-y-2 pr-4">
          {streamEvents.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No events yet. Send a message to see streaming events.
            </p>
          ) : (
            streamEvents
              .slice(-50)
              .reverse()
              .map((event, idx) => (
                <div
                  key={idx}
                  className={cn(
                    "p-2 rounded text-xs font-mono",
                    event.type === "chunk"
                      ? "bg-blue-500/10"
                      : "bg-green-500/10"
                  )}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Badge
                      variant={event.type === "chunk" ? "secondary" : "default"}
                      className="text-xs"
                    >
                      {event.type}
                    </Badge>
                    <span className="text-muted-foreground">
                      {event.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                        fractionalSecondDigits: 3,
                      })}
                    </span>
                  </div>
                  {event.type === "chunk" ? (
                    <div>
                      <span className="text-muted-foreground">chunk: </span>
                      <span className="text-primary">"{event.data.chunk}"</span>
                      {event.data.is_final && (
                        <Badge variant="outline" className="ml-2 text-xs">
                          FINAL
                        </Badge>
                      )}
                    </div>
                  ) : (
                    <div>
                      <span className="text-muted-foreground">message: </span>
                      <span>
                        {event.data.role} -{" "}
                        {event.data.content.substring(0, 50)}...
                      </span>
                    </div>
                  )}
                </div>
              ))
          )}
        </div>
      </ScrollArea>
    );
  };

  const Stats = () => {
    const chunkCount = streamEvents.filter((e) => e.type === "chunk").length;
    const avgChunkLength =
      chunkCount > 0
        ? streamEvents
            .filter((e) => e.type === "chunk")
            .reduce((acc, e) => acc + e.data.chunk.length, 0) / chunkCount
        : 0;

    console.log("[STATS] Messages:", chatHook.messages.length);
    console.log("[STATS] Stream events:", streamEvents.length);
    console.log("[STATS] Is loading:", chatHook.isLoading);

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{chatHook.messages.length}</div>
            <p className="text-xs text-muted-foreground">Total Messages</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">{chunkCount}</div>
            <p className="text-xs text-muted-foreground">Stream Chunks</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">
              {avgChunkLength.toFixed(1)}
            </div>
            <p className="text-xs text-muted-foreground">Avg Chunk Size</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold">
              {chatHook.isLoading ? "Active" : "Idle"}
            </div>
            <p className="text-xs text-muted-foreground">Stream Status</p>
          </CardContent>
        </Card>
      </div>
    );
  };

  return (
    <div className="container max-w-6xl py-8 mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Zap className="w-8 h-8 text-primary" />
          Real-time Streaming Test
        </h1>
        <p className="text-muted-foreground mt-2">
          Watch messages stream in real-time, character by character
        </p>
      </div>

      {/* Setup */}
      {!projectId && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Setup Test Environment</CardTitle>
            <CardDescription>
              Create a test task to start streaming tests
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={createTestProject}
              disabled={isCreatingTask}
              size="lg"
              className="w-full"
            >
              {isCreatingTask ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating Task...
                </>
              ) : (
                <>
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Create Test Task
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {projectId && (
        <>
          {/* Current Task Info */}
          <div className="mb-6 flex items-center justify-between p-4 bg-muted/50 rounded-lg">
            <div>
              <span className="text-sm text-muted-foreground">
                Test Project ID:{" "}
              </span>
              <code className="font-mono text-sm">{projectId}</code>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setProjectId("");
                setStreamEvents([]);
              }}
            >
              Reset
            </Button>
          </div>

          {/* Stats */}
          <div className="mb-6">
            <Stats />
          </div>

          {/* Test Controls */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Send Test Message</CardTitle>
              <CardDescription>
                Send a message and watch it stream back
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  value={customMessage}
                  onChange={(e) => setCustomMessage(e.target.value)}
                  placeholder="Enter test message..."
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      sendTestMessage();
                    }
                  }}
                />
                <Button
                  onClick={sendTestMessage}
                  disabled={chatHook.isLoading || !customMessage.trim()}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex gap-2 mt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setCustomMessage("Tell me a short joke about debugging.")
                  }
                >
                  Joke
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCustomMessage("Count from 1 to 5.")}
                >
                  Count
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCustomMessage("What is React?")}
                >
                  React
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Live Streaming View */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  Live Streaming View
                </CardTitle>
                <CardDescription>
                  Real-time display of streaming content
                </CardDescription>
              </CardHeader>
              <CardContent>
                <StreamingVisualizer />
                {!chatHook.isLoading && (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No active stream. Send a message to start streaming.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Event Log */}
            <Card>
              <CardHeader>
                <CardTitle>Stream Event Log</CardTitle>
                <CardDescription>
                  Raw streaming events (newest first)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <EventLog />
              </CardContent>
            </Card>
          </div>

          {/* Messages Display */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Complete Messages</CardTitle>
              <CardDescription>
                All messages including streaming ones
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px]">
                <div className="space-y-2 pr-4">
                  {chatHook.messages.map((message, idx) => (
                    <div
                      key={message.id || idx}
                      className={cn(
                        "p-3 rounded-lg",
                        message.role === "user"
                          ? "bg-primary/10 ml-8"
                          : "bg-muted mr-8"
                      )}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="text-xs">
                          {message.role}
                        </Badge>
                        {message.status === "streaming" && (
                          <Badge
                            variant="default"
                            className="text-xs animate-pulse"
                          >
                            STREAMING
                          </Badge>
                        )}
                        <span className="text-xs text-muted-foreground">
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-sm whitespace-pre-wrap">
                        {message.content}
                        {message.status === "streaming" && (
                          <span className="inline-flex items-center ml-2">
                            <span className="w-1.5 h-4 bg-current rounded-sm animate-pulse" />
                            <span className="w-1.5 h-4 bg-current rounded-sm animate-pulse animation-delay-150 ml-0.5" />
                            <span className="w-1.5 h-4 bg-current rounded-sm animate-pulse animation-delay-300 ml-0.5" />
                          </span>
                        )}
                      </p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
