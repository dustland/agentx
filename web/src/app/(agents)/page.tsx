"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ChatInput } from "@/components/chat/input";
import { useUser } from "@/contexts/user";
import { useCallback } from "react";
import { useAppStore } from "@/store/app";
import { Card } from "@/components/ui/card";
import { useXAgents } from "@/hooks/use-xagent";
import { Badge } from "@/components/ui/badge";

export default function HomePage() {
  const router = useRouter();
  const { user } = useUser();
  const { setInitialMessage } = useAppStore();
  const { createXAgent } = useXAgents();
  const [isCreating, setIsCreating] = useState(false);

  // Sample goals with team-based configurations
  const sampleGoals = [
    {
      id: 1,
      title: "AI Tools Market Analysis",
      description:
        "Research the current AI productivity tools market, compare top 5 competitors, and identify opportunities for differentiation",
      config: "auto_writer",
    },
    {
      id: 2,
      title: "Python Code Documentation",
      description:
        "Generate comprehensive documentation for a Python REST API project including API endpoints, data models, and usage examples",
      config: "simple_team",
    },
    {
      id: 3,
      title: "SaaS Blog Content Strategy",
      description:
        "Create a 3-month content calendar for a B2B SaaS startup focusing on SEO-optimized topics in the project management space",
      config: "handoff_demo",
    },
    {
      id: 4,
      title: "E-commerce Competitor Analysis",
      description:
        "Analyze top 5 sustainable fashion e-commerce brands, their pricing strategies, marketing channels, and unique selling propositions",
      config: "extractor",
    },
    {
      id: 5,
      title: "Mobile App Launch Plan",
      description:
        "Develop a go-to-market strategy for a fitness tracking mobile app including pre-launch, launch week, and post-launch activities",
      config: "auto_writer",
    },
    {
      id: 6,
      title: "Technical Blog Optimization",
      description:
        "Audit a developer blog for SEO, readability, and engagement, then provide actionable recommendations for improvement",
      config: "simple_team",
    },
  ];

  const handleCreateXAgent = useCallback(
    (prompt: string) => {
      if (!prompt.trim()) return;

      setIsCreating(true);

      // Phase 1: Set initial message in store (for Phase 2 on agent page)
      setInitialMessage(prompt);

      // Phase 1: Create XAgent (just create it, don't start yet)
      createXAgent.mutate(
        {
          goal: prompt, // Pass the prompt as the goal
          configPath: "examples/simple_chat/config/team.yaml",
          context: { source: "studio_homepage" },
        },
        {
          onSuccess: (response) => {
            console.log("XAgent created successfully:", response);
            const agentId = response.xagent_id;

            if (!agentId) {
              throw new Error("No agent ID returned from API");
            }

            // Phase 1: Navigate to the agent page (Phase 2 will happen there)
            router.push(`/x/${agentId}`);
          },
          onError: (error) => {
            console.error("Failed to create task:", error);

            // Clear initial message on error
            setInitialMessage(null);

            // Check if it's a backend error
            if (
              error instanceof Error &&
              error.message.includes("name 'os' is not defined")
            ) {
              alert(
                "Backend service is currently experiencing issues. The task creation feature is temporarily disabled."
              );
            } else if (
              error instanceof Error &&
              error.message.includes("404")
            ) {
              alert(
                "Task service not found. Please check if the backend is running."
              );
            } else {
              alert("Failed to create task. Please try again.");
            }
          },
          onSettled: () => {
            setIsCreating(false);
          },
        }
      );
    },
    [createXAgent, router, setInitialMessage]
  );

  const handleSampleGoalClick = (goal: any) => {
    const prompt = `${goal.title}: ${goal.description}`;
    handleCreateXAgent(prompt);
  };

  return (
    <div className="flex-1 flex flex-col overflow-y-auto">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Hero Section - Center vertically in viewport */}
        <div className="flex-1 flex items-center justify-center px-6 py-12">
          <div className="w-full max-w-4xl">
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
              onSendMessage={handleCreateXAgent}
              isLoading={isCreating}
              placeholder="Describe what would you like me to do..."
            />
          </div>
        </div>

        {/* Sample Tasks Section - Below the fold */}
        <div className="px-6 pb-12">
          <div className="max-w-4xl mx-auto">
            <div className="mb-6">
              <h2 className="text-lg font-medium mb-6">
                Choose a goal to achieve
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {sampleGoals.map((goal) => {
                return (
                  <Card
                    key={goal.id}
                    className="group flex flex-col rounded-2xl p-4 hover:border-foreground/30 transition-all duration-200 relative"
                  >
                    <div className="space-y-2 flex-1">
                      <h3 className="font-medium text-sm text-foreground">
                        {goal.title}
                      </h3>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {goal.description}
                      </p>
                    </div>

                    {/* Start Button - appears on hover */}
                    <div className="flex justify-between pt-4">
                      <Badge variant="outline" className="text-xs">
                        {goal.config}
                      </Badge>
                      <Button
                        size="sm"
                        variant="default"
                        className="h-7 px-3 text-xs"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSampleGoalClick(goal);
                        }}
                      >
                        Start X
                      </Button>
                    </div>
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
