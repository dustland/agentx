"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChatInput } from "@/components/chat/chat-input";
import { generateId } from "@/lib/utils";
import { useAgentXAPI } from "@/lib/api-client";
import { useUser } from "@/contexts/user-context";
import { useCallback } from "react";
import { useTaskStore } from "@/store/task";

export default function HomePage() {
  const router = useRouter();
  const { user } = useUser();
  const apiClient = useAgentXAPI();
  const { setInitialMessage } = useTaskStore();
  const [isCreating, setIsCreating] = useState(false);

  // Sample tasks with team-based configurations
  const sampleTasks = [
    {
      id: 1,
      title: "Market Research Report",
      description: "Analyze market trends and create comprehensive report",
      config: "auto_writer",
    },
    {
      id: 2,
      title: "Code Review & Documentation",
      description: "Review codebase and generate technical documentation",
      config: "simple_team",
    },
    {
      id: 3,
      title: "Content Strategy Planning",
      description: "Develop content strategy and editorial calendar",
      config: "handoff_demo",
    },
    {
      id: 4,
      title: "Competitive Analysis",
      description: "Research competitors and identify market opportunities",
      config: "extractor",
    },
    {
      id: 5,
      title: "Product Launch Plan",
      description: "Create comprehensive product launch strategy",
      config: "auto_writer",
    },
    {
      id: 6,
      title: "Website Content Audit",
      description: "Analyze website content and suggest improvements",
      config: "simple_team",
    },
  ];

  const createTask = useCallback(
    async (prompt: string) => {
      if (!prompt.trim()) return;

      setIsCreating(true);
      try {
        console.log("Creating task with prompt:", prompt);

        // Create task with empty description - the prompt becomes the first message
        const response = await apiClient.createTask({
          task_description: "",
          config_path: "examples/simple_chat/config/team.yaml",
          context: { source: "studio_homepage" },
        });

        console.log("Task created successfully:", response);
        const taskId = response.task_id;

        if (!taskId) {
          throw new Error("No task ID returned from API");
        }

        // Store the initial message to be sent when the task page loads
        setInitialMessage(prompt);

        // Navigate to the task page
        router.push(`/x/${taskId}`);
      } catch (error) {
        console.error("Failed to create task:", error);

        // Check if it's a backend error
        if (
          error instanceof Error &&
          error.message.includes("name 'os' is not defined")
        ) {
          alert(
            "Backend service is currently experiencing issues. The task creation feature is temporarily disabled."
          );
        } else if (error instanceof Error && error.message.includes("404")) {
          alert(
            "Task service not found. Please check if the backend is running."
          );
        } else {
          alert("Failed to create task. Please try again.");
        }
      } finally {
        setIsCreating(false);
      }
    },
    [apiClient, router, setInitialMessage]
  );

  const handleSampleTaskClick = (task: any) => {
    const prompt = `${task.title}: ${task.description}`;
    createTask(prompt);
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto px-6">
          {/* Hero Section */}
          <div className="flex flex-col items-center justify-center min-h-[50vh] py-12">
            <div className="text-center space-y-4 mb-8">
              <h1 className="text-3xl font-medium text-foreground">
                Hello {user?.username || "there"}
              </h1>
              <p className="text-base text-muted-foreground">
                What can I do for you?
              </p>
            </div>

            {/* Simple Task Input */}
            <ChatInput
              onSendMessage={createTask}
              isLoading={isCreating}
              placeholder="Ask me anything..."
            />
          </div>

          {/* Sample Tasks Section */}
          <div className="pb-12">
            <div className="mb-6">
              <h2 className="text-lg font-medium mb-6">Recommended</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {sampleTasks.map((task) => {
                return (
                  <div
                    key={task.id}
                    className="group cursor-pointer border border-border rounded-2xl p-4 hover:border-foreground/30 transition-all duration-200 relative"
                    onClick={() => handleSampleTaskClick(task)}
                  >
                    <div className="space-y-2">
                      <h3 className="font-medium text-sm text-foreground">
                        {task.title}
                      </h3>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {task.description}
                      </p>
                    </div>

                    {/* Start Button - appears on hover */}
                    <div className="absolute bottom-2 right-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <Button
                        size="sm"
                        variant="secondary"
                        className="h-7 px-3 text-xs"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSampleTaskClick(task);
                        }}
                      >
                        Start Task
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
