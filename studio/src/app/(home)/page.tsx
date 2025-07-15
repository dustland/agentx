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
import { TaskSidebar } from "@/components/layout/task-sidebar";
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
  const [isSidebarPinned, setIsSidebarPinned] = useState(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("sidebar-pinned");
      return stored !== null ? stored === "true" : true;
    }
    return true;
  });

  const sampleTasks = [
    {
      title: "Research Assistant Chat",
      description:
        "Chat with an AI assistant that can search the web for current information and provide helpful responses",
      teamConfig: "simple_chat",
      icon: Users,
      prompt:
        "Hello! I'm your research assistant with web search capabilities. What would you like to know about today?",
      configPath: "examples/simple_chat/config/team.yaml",
    },
    {
      title: "15-Second Product Demo Video",
      description:
        "Create engaging product demonstration videos with professional narration and visuals",
      teamConfig: "auto_writer",
      icon: Video,
      prompt:
        "Produce a compelling 15-second product demo video showcasing key features with professional voiceover and visual effects.",
      configPath: "examples/auto_writer/config/team.yaml",
    },
    {
      title: "Marketing Presentation for Management Review",
      description:
        "Develop comprehensive marketing strategy presentations with data-driven insights",
      teamConfig: "simple_team",
      icon: Presentation,
      prompt:
        "Create a professional marketing presentation for management review including market analysis, strategy recommendations, and performance metrics.",
      configPath: "examples/simple_team/config/team.yaml",
    },
    {
      title: "Technical Documentation Site",
      description:
        "Build comprehensive technical documentation websites with interactive examples",
      teamConfig: "auto_writer",
      icon: Globe,
      prompt:
        "Develop a complete technical documentation website with interactive code examples, API references, and user guides.",
      configPath: "examples/auto_writer/config/team.yaml",
    },
    {
      title: "Data Visualization Dashboard",
      description:
        "Create interactive dashboards for complex data analysis and business intelligence",
      teamConfig: "simple_team",
      icon: BarChart3,
      prompt:
        "Build an interactive data visualization dashboard with real-time analytics and customizable reporting features.",
      configPath: "examples/simple_team/config/team.yaml",
    },
    {
      title: "Code Architecture Analysis",
      description:
        "Analyze and optimize software architecture patterns for scalability and performance",
      teamConfig: "simple_chat",
      icon: Code,
      prompt:
        "Conduct comprehensive code architecture analysis with recommendations for scalability improvements and performance optimization.",
      configPath: "examples/simple_chat/config/team.yaml",
    },
    {
      title: "AI Training Dataset Creation",
      description:
        "Generate and curate high-quality training datasets for machine learning models",
      teamConfig: "extractor",
      icon: FileText,
      prompt:
        "Create comprehensive AI training datasets with proper labeling, validation, and documentation for machine learning applications.",
      configPath: "examples/extractor/config/team.yaml",
    },
    {
      title: "Interactive Learning Module",
      description:
        "Develop engaging educational content with interactive elements and assessments",
      teamConfig: "auto_writer",
      icon: Image,
      prompt:
        "Design interactive learning modules with multimedia content, quizzes, and progress tracking for educational platforms.",
      configPath: "examples/auto_writer/config/team.yaml",
    },
    {
      title: "Business Process Automation",
      description:
        "Streamline complex business workflows with intelligent automation solutions",
      teamConfig: "simple_team",
      icon: RefreshCw,
      prompt:
        "Design and implement business process automation workflows with intelligent decision-making and error handling capabilities.",
      configPath: "examples/simple_team/config/team.yaml",
    },
  ];

  const createTask = async (description: string, configPath?: string) => {
    if (!description.trim()) return;

    setIsCreating(true);
    try {
      // Store the initial message in Zustand store
      setInitialMessage(description);

      // Create task via API
      const taskResponse = await apiClient.createTask({
        config_path: configPath || "examples/simple_chat/config/team.yaml",
        task_description: "", // Empty description, will use chat message instead
        context: { source: "studio_homepage" },
      });

      // Navigate to task page (initial message will be consumed from store)
      router.push(`/x/${taskResponse.task_id}`);
    } catch (error) {
      console.error("Error creating task:", error);
      setIsCreating(false);
    }
  };

  const handleTaskInputSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createTask(taskInput);
  };

  const handleSampleTaskClick = (task: any) => {
    createTask(task.prompt, task.configPath);
  };

  const handleFloatingChange = useCallback((floating: boolean) => {
    // Only update if the state actually needs to change
    setIsSidebarPinned((prev) => {
      const newValue = !floating;
      if (prev !== newValue) {
        localStorage.setItem("sidebar-pinned", newValue.toString());
        return newValue;
      }
      return prev;
    });
  }, []);

  return (
    <div className="h-screen flex bg-muted/40">
      {/* Sidebar - always render but control visibility through props */}
      <TaskSidebar
        className={isSidebarPinned ? "flex-shrink-0" : ""}
        isFloating={!isSidebarPinned}
        onFloatingChange={handleFloatingChange}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {/* Main Content */}
        <main className="flex-1 overflow-auto bg-muted/40">
          <div className="max-w-6xl mx-auto px-6 py-12">
            {/* Welcome Section */}
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold mb-4">
                Hello {user?.username || "Guest"}
              </h1>
              <p className="text-xl text-muted-foreground mb-8">
                What can I do for you?
              </p>

              {/* Main Input */}
              <form onSubmit={handleTaskInputSubmit} className="relative mb-8">
                <div className="relative max-w-3xl mx-auto">
                  <div className="relative bg-background border border-border rounded-3xl shadow-sm hover:shadow-md transition-shadow">
                    <Input
                      value={taskInput}
                      onChange={(e) => setTaskInput(e.target.value)}
                      placeholder="Assign a task or ask anything"
                      className="h-16 pl-16 pr-20 text-lg bg-transparent border-0 rounded-3xl focus:ring-0 focus:border-0 focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground/60"
                      disabled={isCreating}
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute left-6 top-1/2 transform -translate-y-1/2 p-2 h-8 w-8 rounded-full hover:bg-muted/50"
                    >
                      <Paperclip className="w-4 h-4 text-muted-foreground/60" />
                    </Button>
                    <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
                      <Button
                        type="submit"
                        size="sm"
                        className="h-8 w-8 rounded-full bg-foreground text-background hover:bg-foreground/90 ml-2 p-0"
                        disabled={!taskInput.trim() || isCreating}
                      >
                        {isCreating ? (
                          <div className="w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <ArrowUp className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              </form>
            </div>

            {/* Disclaimer */}
            <p className="text-center text-xs text-muted-foreground mb-8">
              All community content is voluntarily shared by users and will not
              be displayed without consent.
            </p>

            {/* Sample Tasks Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sampleTasks.map((task, index) => (
                <Card
                  key={index}
                  className="group cursor-pointer transition-all duration-200 border border-border hover:border-muted-foreground bg-background relative shadow-none"
                  onClick={() => handleSampleTaskClick(task)}
                >
                  <CardContent className="p-6 h-full flex flex-col">
                    <div className="flex-1 space-y-4">
                      <div className="flex-1">
                        <h3 className="font-medium text-foreground leading-tight mb-2">
                          {task.title}
                        </h3>
                        <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                          {task.description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex items-center text-muted-foreground text-sm">
                        <task.icon className="w-4 h-4 mr-2" />
                        <span>{task.teamConfig}</span>
                      </div>
                      <Button
                        size="sm"
                        className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 h-8 px-3 text-xs"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSampleTaskClick(task);
                        }}
                      >
                        Start Task
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
