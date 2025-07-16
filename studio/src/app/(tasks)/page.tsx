"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Plus,
  Paperclip,
  FileText,
  BarChart3,
  Code,
  Users,
  Image,
  Video,
  Globe,
  Presentation,
  RefreshCw,
  ArrowUp,
} from "lucide-react";
import { generateId } from "@/lib/utils";
import NextImage from "next/image";
import { useAgentXAPI } from "@/lib/api-client";
import { useUser } from "@/contexts/user-context";
import { UserAvatar } from "@/components/ui/user-avatar";
import { useCallback } from "react";
import { useTaskStore } from "@/lib/stores/task-store";

export default function HomePage() {
  const router = useRouter();
  const { user } = useUser();
  const apiClient = useAgentXAPI();
  const { setInitialMessage } = useTaskStore();
  const [taskInput, setTaskInput] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  // Sample tasks with team-based configurations
  const sampleTasks = [
    {
      id: 1,
      title: "Market Research Report",
      description: "Analyze market trends and create comprehensive report",
      config: "auto_writer",
      icon: BarChart3,
      color: "bg-blue-500",
    },
    {
      id: 2,
      title: "Code Review & Documentation",
      description: "Review codebase and generate technical documentation",
      config: "simple_team",
      icon: Code,
      color: "bg-green-500",
    },
    {
      id: 3,
      title: "Content Strategy Planning",
      description: "Develop content strategy and editorial calendar",
      config: "handoff_demo",
      icon: FileText,
      color: "bg-purple-500",
    },
    {
      id: 4,
      title: "Competitive Analysis",
      description: "Research competitors and identify market opportunities",
      config: "extractor",
      icon: Users,
      color: "bg-orange-500",
    },
    {
      id: 5,
      title: "Product Launch Plan",
      description: "Create comprehensive product launch strategy",
      config: "auto_writer",
      icon: Presentation,
      color: "bg-pink-500",
    },
    {
      id: 6,
      title: "Website Content Audit",
      description: "Analyze website content and suggest improvements",
      config: "simple_team",
      icon: Globe,
      color: "bg-cyan-500",
    },
  ];

  const createTask = useCallback(
    async (prompt: string) => {
      if (!prompt.trim()) return;

      setIsCreating(true);
      try {
        // Create task with empty description - the prompt becomes the first message
        const response = await apiClient.createTask({
          task_description: "",
          config_path: "examples/simple_chat/config/team.yaml",
          context: { source: "studio_homepage" },
        });
        const taskId = response.task_id;

        // Store the initial message to be sent when the task page loads
        setInitialMessage(prompt);

        // Navigate to the task page
        router.push(`/x/${taskId}`);
      } catch (error) {
        console.error("Failed to create task:", error);
      } finally {
        setIsCreating(false);
      }
    },
    [apiClient, router, setInitialMessage]
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createTask(taskInput);
  };

  const handleSampleTaskClick = (task: any) => {
    const prompt = `${task.title}: ${task.description}`;
    createTask(prompt);
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b bg-card">
        <div className="flex items-center gap-3">
          <NextImage
            src="/logo.png"
            alt="AgentX"
            width={32}
            height={32}
            className="object-contain"
          />
          <div>
            <h1 className="text-2xl font-bold">
              Agent<span className="text-primary">X</span>
            </h1>
            <p className="text-sm text-muted-foreground">
              Multi-Agent AI Platform
            </p>
          </div>
        </div>
        {user && (
          <div className="flex items-center gap-3">
            <UserAvatar username={user.username} size="lg" />
            <div>
              <p className="text-sm font-medium">{user.username}</p>
              <p className="text-xs text-muted-foreground">
                {user.email || "No email"}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-6 space-y-8">
          {/* Welcome Section */}
          <div className="text-center space-y-4">
            <h2 className="text-3xl font-bold">
              What would you like to work on today?
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Describe your task and let our AI agents collaborate to get it
              done efficiently.
            </p>
          </div>

          {/* Task Input */}
          <Card className="bg-background border-2">
            <CardContent className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                  <Input
                    placeholder="Describe your task... (e.g., 'Research the latest AI trends and write a comprehensive report')"
                    value={taskInput}
                    onChange={(e) => setTaskInput(e.target.value)}
                    className="pr-12 h-12 text-base"
                    disabled={isCreating}
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      disabled={isCreating}
                    >
                      <Paperclip className="h-4 w-4" />
                    </Button>
                    <Button
                      type="submit"
                      size="sm"
                      className="h-8 w-8 p-0 rounded-full"
                      disabled={!taskInput.trim() || isCreating}
                    >
                      {isCreating ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <ArrowUp className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Sample Tasks */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold">Sample Tasks</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sampleTasks.map((task) => {
                const Icon = task.icon;
                return (
                  <Card
                    key={task.id}
                    className="cursor-pointer transition-all duration-200 hover:border-primary group bg-background"
                    onClick={() => handleSampleTaskClick(task)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div
                          className={`p-2 rounded-lg ${task.color} text-white`}
                        >
                          <Icon className="h-5 w-5" />
                        </div>
                        <Badge
                          variant="secondary"
                          className="text-xs font-mono"
                        >
                          {task.config}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex-1">
                        <CardTitle className="text-base mb-2 group-hover:text-primary transition-colors">
                          {task.title}
                        </CardTitle>
                        <CardDescription className="text-sm">
                          {task.description}
                        </CardDescription>
                      </div>
                      <div className="pt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button size="sm" variant="outline" className="w-full">
                          <Plus className="h-4 w-4 mr-2" />
                          Start Task
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
