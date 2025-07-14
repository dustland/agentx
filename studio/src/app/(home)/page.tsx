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
  Search,
  Plus,
  Mic,
  Paperclip,
  FileText,
  BarChart3,
  Code,
  Users,
  Settings,
  Moon,
  Sun,
  Image,
  Video,
  Globe,
  Presentation,
  RefreshCw,
  ChevronDown,
  ArrowUp,
} from "lucide-react";
import { generateId } from "@/lib/utils";
import NextImage from "next/image";
import { useTheme } from "next-themes";

export default function HomePage() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [taskInput, setTaskInput] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const categories = [
    { name: "Recommend", active: true, icon: RefreshCw },
    { name: "Featured", active: false },
    { name: "Research", active: false },
    { name: "Data", active: false },
    { name: "Edu", active: false },
    { name: "Productivity", active: false },
    { name: "Programming", active: false },
  ];

  const sampleTasks = [
    {
      title: "AI Agent Character Creation",
      description:
        "Design and develop custom AI agent personalities with unique traits and capabilities",
      contentType: "Image",
      icon: Image,
      prompt:
        "Create a comprehensive AI agent character with unique personality traits, capabilities, and visual design for interactive applications.",
    },
    {
      title: "15-Second Product Demo Video",
      description:
        "Create engaging product demonstration videos with professional narration and visuals",
      contentType: "Video",
      icon: Video,
      prompt:
        "Produce a compelling 15-second product demo video showcasing key features with professional voiceover and visual effects.",
    },
    {
      title: "Marketing Presentation for Management Review",
      description:
        "Develop comprehensive marketing strategy presentations with data-driven insights",
      contentType: "Slides",
      icon: Presentation,
      prompt:
        "Create a professional marketing presentation for management review including market analysis, strategy recommendations, and performance metrics.",
    },
    {
      title: "Technical Documentation Site",
      description:
        "Build comprehensive technical documentation websites with interactive examples",
      contentType: "Webpage",
      icon: Globe,
      prompt:
        "Develop a complete technical documentation website with interactive code examples, API references, and user guides.",
    },
    {
      title: "Data Visualization Dashboard",
      description:
        "Create interactive dashboards for complex data analysis and business intelligence",
      contentType: "Video",
      icon: Video,
      prompt:
        "Build an interactive data visualization dashboard with real-time analytics and customizable reporting features.",
    },
    {
      title: "Code Architecture Analysis",
      description:
        "Analyze and optimize software architecture patterns for scalability and performance",
      contentType: "Slides",
      icon: Presentation,
      prompt:
        "Conduct comprehensive code architecture analysis with recommendations for scalability improvements and performance optimization.",
    },
    {
      title: "AI Training Dataset Creation",
      description:
        "Generate and curate high-quality training datasets for machine learning models",
      contentType: "Webpage",
      icon: Globe,
      prompt:
        "Create comprehensive AI training datasets with proper labeling, validation, and documentation for machine learning applications.",
    },
    {
      title: "Interactive Learning Module",
      description:
        "Develop engaging educational content with interactive elements and assessments",
      contentType: "Image",
      icon: Image,
      prompt:
        "Design interactive learning modules with multimedia content, quizzes, and progress tracking for educational platforms.",
    },
    {
      title: "Business Process Automation",
      description:
        "Streamline complex business workflows with intelligent automation solutions",
      contentType: "Slides",
      icon: Presentation,
      prompt:
        "Design and implement business process automation workflows with intelligent decision-making and error handling capabilities.",
    },
  ];

  const createTask = async (description: string) => {
    if (!description.trim()) return;

    setIsCreating(true);
    try {
      const taskId = generateId();
      router.push(
        `/x/${taskId}?description=${encodeURIComponent(description)}`
      );
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
    createTask(task.prompt);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <NextImage
                src="/logo.png"
                alt="AgentX"
                width={32}
                height={32}
                className="object-contain"
              />
              <span className="text-xl font-semibold">AgentX Studio</span>
            </div>

            <div className="flex items-center space-x-4">
              <Badge variant="outline">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>3
                Agents Active
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              >
                {theme === "dark" ? (
                  <Sun className="h-4 w-4" />
                ) : (
                  <Moon className="h-4 w-4" />
                )}
              </Button>
              <Button variant="ghost" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* Welcome Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Hello Hugh</h1>
          <p className="text-xl text-muted-foreground mb-8">
            What can I do for you?
          </p>

          {/* Main Input */}
          <form onSubmit={handleTaskInputSubmit} className="relative mb-8">
            <div className="relative max-w-3xl mx-auto">
              <div className="relative bg-card border border-border rounded-3xl shadow-sm hover:shadow-md transition-shadow">
                <Input
                  value={taskInput}
                  onChange={(e) => setTaskInput(e.target.value)}
                  placeholder="Assign a task or ask anything"
                  className="h-16 pl-16 pr-40 text-lg bg-transparent border-0 rounded-3xl focus:ring-0 focus:border-0 focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground/60"
                  disabled={isCreating}
                />
                <Search className="absolute left-6 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground/60" />
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="p-2 h-8 w-8 rounded-full hover:bg-muted/50"
                  >
                    <Paperclip className="w-4 h-4 text-muted-foreground/60" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="p-2 h-8 w-8 rounded-full hover:bg-muted/50"
                  >
                    <Mic className="w-4 h-4 text-muted-foreground/60" />
                  </Button>
                  <Button
                    type="submit"
                    size="sm"
                    className="px-4 h-8 rounded-full bg-foreground text-background hover:bg-foreground/90 ml-2"
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

        {/* Category Filters */}
        <div className="flex justify-center items-center space-x-3 mb-8">
          {categories.map((category, index) => (
            <Badge
              key={index}
              variant={category.active ? "default" : "outline"}
              className={`cursor-pointer px-4 py-2 text-sm ${
                category.active
                  ? "bg-foreground text-background hover:bg-foreground/90"
                  : "hover:bg-muted"
              }`}
            >
              {category.icon && <category.icon className="w-3 h-3 mr-1" />}
              {category.name}
            </Badge>
          ))}
          <Button variant="ghost" size="sm" className="p-2">
            <ChevronDown className="w-4 h-4" />
          </Button>
        </div>

        {/* Disclaimer */}
        <p className="text-center text-xs text-muted-foreground mb-8">
          All community content is voluntarily shared by users and will not be
          displayed without consent.
        </p>

        {/* Sample Tasks Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sampleTasks.map((task, index) => (
            <Card
              key={index}
              className="cursor-pointer transition-colors duration-200 border-0 bg-muted/30 hover:bg-muted/50"
              onClick={() => handleSampleTaskClick(task)}
            >
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium text-foreground leading-tight mb-2">
                      {task.title}
                    </h3>
                  </div>
                  <div className="flex items-center text-muted-foreground text-sm">
                    <task.icon className="w-4 h-4 mr-2" />
                    <span>{task.contentType}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Bottom Action */}
        <div className="flex justify-center mt-12">
          <Button
            onClick={() => createTask("I need help with a custom task")}
            className="px-8 py-3"
            disabled={isCreating}
          >
            <Plus className="w-4 h-4 mr-2" />
            Start Custom Task
          </Button>
        </div>
      </main>
    </div>
  );
}
