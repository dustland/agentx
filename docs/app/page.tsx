"use client";

import React from "react";
import { motion } from "framer-motion";
import { Link } from "nextra-theme-docs";
import { useState, useEffect } from "react";
import {
  Users,
  Wrench,
  Brain,
  Zap,
  BarChart3,
  Settings,
  ArrowRight,
  Bot,
  GraduationCap,
  ChartColumnStacked,
  Rocket,
  PenTool,
  Code,
  Cog,
  Terminal,
  Github,
  DollarSign,
} from "lucide-react";
import Image from "next/image";

const basePath =
  process.env.NODE_ENV === "production" && process.env.GITHUB_ACTIONS === "true"
    ? "/agentx"
    : "";

// Simple typewriter for header - only essential animation
const TypewriterText = () => {
  const words = ["Writing", "Coding", "Ops"];
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [currentText, setCurrentText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentWord = words[currentWordIndex];
    let timeout: NodeJS.Timeout;

    if (!isDeleting && currentText.length < currentWord.length) {
      timeout = setTimeout(() => {
        setCurrentText(currentWord.slice(0, currentText.length + 1));
      }, 150);
    } else if (!isDeleting && currentText.length === currentWord.length) {
      timeout = setTimeout(() => {
        setIsDeleting(true);
      }, 2000);
    } else if (isDeleting && currentText.length > 0) {
      timeout = setTimeout(() => {
        setCurrentText(currentText.slice(0, -1));
      }, 100);
    } else if (isDeleting && currentText.length === 0) {
      setIsDeleting(false);
      setCurrentWordIndex((prev) => (prev + 1) % words.length);
    }

    return () => {
      if (timeout) clearTimeout(timeout);
    };
  }, [currentText, isDeleting, currentWordIndex]);

  return (
    <span className="text-blue-600 dark:text-blue-400">{currentText}</span>
  );
};

// Enhanced bootstrap tabs with example code
const BootstrapTabs = () => {
  const [activeTab, setActiveTab] = useState(0);

  const workflows = [
    {
      id: "writing",
      title: "Writing",
      icon: PenTool,
      description: "Research → Draft → Edit workflow",
      command: "agentx init my-research --template writing",
      agents: ["Researcher", "Writer", "Reviewer", "Web Designer"],
      exampleCode: `import asyncio
from agentx import start_task

async def main():
    # Start XAgent with your research team
    x = await start_task(
        "Write a comprehensive report on AI trends in 2025",
        "config/team.yaml"
    )

    # Chat with your AI team
    response = await x.chat("Focus on business applications")
    print(f"X: {response.text}")

    # Iterate and refine
    await x.chat("Add more visual charts and graphs")
    await x.chat("Create an executive summary")

if __name__ == "__main__":
    asyncio.run(main())`,
    },
    {
      id: "coding",
      title: "Coding",
      icon: Code,
      description: "Plan → Build → Test workflow",
      command: "agentx init my-app --template coding",
      agents: ["Planner", "Developer", "Reviewer"],
      exampleCode: `import asyncio
from agentx import start_task

async def main():
    # Start XAgent with your development team
    x = await start_task(
        "Build a REST API for a todo application",
        "config/team.yaml"
    )

    # Chat with your development team
    response = await x.chat("Use FastAPI and SQLite")
    print(f"X: {response.text}")

    # Continue development
    await x.chat("Add user authentication")
    await x.chat("Write comprehensive tests")

if __name__ == "__main__":
    asyncio.run(main())`,
    },
    {
      id: "operating",
      title: "Ops",
      icon: Cog,
      description: "Analyze → Execute → Monitor workflow",
      command: "agentx init my-automation --template operating",
      agents: ["Analyst", "Operator", "Monitor"],
      exampleCode: `import asyncio
from agentx import start_task

async def main():
    # Start XAgent with your operations team
    x = await start_task(
        "Automate daily server health monitoring",
        "config/team.yaml"
    )

    # Chat with your ops team
    response = await x.chat("Check disk usage and memory")
    print(f"X: {response.text}")

    # Add monitoring
    await x.chat("Set up alerts for high CPU usage")
    await x.chat("Generate a daily status report")

if __name__ == "__main__":
    asyncio.run(main())`,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Tab Navigation */}
      <div className="flex border-b border-slate-200 dark:border-slate-700 mb-8">
        {workflows.map((workflow, index) => (
          <button
            key={workflow.id}
            onClick={() => setActiveTab(index)}
            className={`flex items-center px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === index
                ? "border-blue-600 text-blue-600 dark:text-blue-400"
                : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
            }`}
          >
            <workflow.icon className="w-4 h-4 mr-2" />
            {workflow.title}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-6">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Description and Setup */}
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                {workflows[activeTab].title} Workflow
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                {workflows[activeTab].description}
              </p>
              <div className="space-y-3">
                <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  Your AI Team:
                </p>
                <div className="flex flex-wrap gap-2">
                  {workflows[activeTab].agents.map((agent) => (
                    <span
                      key={agent}
                      className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm rounded-full"
                    >
                      {agent}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* CLI Command */}
            <div>
              <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Get started with one command:
              </p>
              <div className="bg-slate-900 dark:bg-slate-900 rounded-lg p-4 font-mono text-sm">
                <div className="flex items-center gap-2 mb-2">
                  <Terminal className="w-4 h-4 text-slate-400" />
                  <span className="text-slate-400">Terminal</span>
                </div>
                <code className="text-green-400">
                  {workflows[activeTab].command}
                </code>
              </div>
            </div>

            {/* Features */}
            <div className="text-sm text-slate-600 dark:text-slate-400">
              <p className="font-medium text-slate-700 dark:text-slate-300 mb-2">
                What you get:
              </p>
              <ul className="space-y-1">
                <li>• Complete project structure</li>
                <li>• Pre-configured AI agents</li>
                <li>• Ready-to-run main.py</li>
                <li>• Cost-optimized model selection</li>
              </ul>
            </div>
          </div>

          {/* Right Column - Generated Code */}
          <div>
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Generated main.py (with XAgent):
            </p>
            <div className="bg-slate-900 dark:bg-slate-900 rounded-lg p-4 overflow-x-auto">
              <div className="flex items-center gap-2 mb-3">
                <Code className="w-4 h-4 text-slate-400" />
                <span className="text-slate-400 text-sm">main.py</span>
              </div>
              <pre className="text-xs text-slate-300 leading-relaxed">
                <code>{workflows[activeTab].exampleCode}</code>
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function HomePage() {
  const features = [
    {
      icon: Users,
      title: "Multi-Agent Orchestration",
      description:
        "Intelligent task distribution and coordination for complex workflows.",
      href: "/docs/design/overview",
    },
    {
      icon: Wrench,
      title: "Extensible Tools",
      description: "Native integrations and custom tool development framework.",
      href: "/docs/design/tool-execution",
    },
    {
      icon: Brain,
      title: "Persistent Memory",
      description:
        "Contextual retention and semantic search across agent networks.",
      href: "/docs/design/state-and-context",
    },
    {
      icon: Zap,
      title: "Event System",
      description:
        "Real-time coordination and scalable inter-agent communication.",
      href: "/docs/design/communication",
    },
    {
      icon: BarChart3,
      title: "Observability",
      description:
        "Distributed tracing and performance metrics for production.",
      href: "#",
    },
    {
      icon: Settings,
      title: "Configuration-Driven",
      description:
        "Simple YAML and Markdown configuration. Almost no code required.",
      href: "#",
    },
  ];

  const useCases = [
    {
      icon: Bot,
      title: "Agentic Applications",
      description:
        "Build intelligent applications with autonomous AI agents and human oversight.",
    },
    {
      icon: GraduationCap,
      title: "Research Automation",
      description:
        "Deploy collaborative research teams for data gathering and analysis.",
    },
    {
      icon: ChartColumnStacked,
      title: "Enterprise Operations",
      description:
        "Streamline business operations through intelligent automation.",
    },
    {
      icon: Rocket,
      title: "Creative Workflows",
      description:
        "Accelerate creative processes with AI-assisted ideation and content generation.",
    },
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      {/* Hero Section */}
      <section className="relative py-20 lg:py-32 overflow-hidden">
        {/* Subtle background decoration */}
        <div className="absolute inset-0 bg-gradient-to-b from-slate-50 to-white dark:from-slate-800 dark:to-slate-900"></div>

        {/* Simple grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#f1f5f9_1px,transparent_1px),linear-gradient(to_bottom,#f1f5f9_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:60px_60px] opacity-40"></div>

        {/* Subtle decorative elements */}
        <div className="absolute top-20 left-10 w-32 h-32 bg-blue-100 dark:bg-blue-900/20 rounded-full blur-3xl opacity-60"></div>
        <div className="absolute top-40 right-20 w-24 h-24 bg-purple-100 dark:bg-purple-900/20 rounded-full blur-3xl opacity-40"></div>
        <div className="absolute bottom-20 left-1/4 w-40 h-40 bg-slate-100 dark:bg-slate-800/30 rounded-full blur-3xl opacity-30"></div>

        <div className="relative max-w-7xl mx-auto px-4 text-center">
          <div className="max-w-4xl mx-auto">
            {/* Main heading */}
            <h1 className="text-4xl md:text-6xl font-bold text-slate-900 dark:text-white mb-6">
              Build Vibe-
              <TypewriterText /> Apps
              <br />
              <span className="text-2xl md:text-4xl text-slate-600 dark:text-slate-400">
                With AgentX
              </span>
            </h1>

            <p className="text-xl text-slate-600 dark:text-slate-400 mb-8 max-w-3xl mx-auto">
              The framework for human-AI collaboration that balances AI autonomy
              with human oversight. Transparent processes, cost-optimized
              intelligence, and professional workflows.
            </p>

            {/* CTA buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/docs/tutorials/0-bootstrap"
                className="inline-flex items-center bg-blue-600 hover:bg-blue-700 !text-white font-bold px-8 py-4 rounded-lg transition-colors shadow-lg no-underline"
              >
                Quick Start
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
              <Link
                href="/docs/design/vibe-x-philosophy"
                className="inline-flex items-center border border-slate-300 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium px-6 py-3 rounded-lg transition-colors"
              >
                Learn Vibe-X
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </div>
          </div>
        </div>

        {/* Curve decoration - part of hero section so grid extends through it */}
        <div className="absolute bottom-0 left-0 w-full overflow-hidden z-10">
          <svg
            className="relative block w-full h-12"
            viewBox="0 0 1200 120"
            preserveAspectRatio="none"
          >
            <path
              d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V120H0V0Z"
              fill="rgb(248, 250, 252)"
              className="dark:hidden"
            />
            <path
              d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V120H0V0Z"
              fill="rgba(30, 41, 59, 0.5)"
              className="hidden dark:block"
            />
          </svg>
        </div>
      </section>

      {/* Vibe-X Philosophy */}
      <section className="relative py-20 bg-slate-50 dark:bg-slate-800/50">
        <div className="relative max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">
              The Vibe-X Philosophy
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-3xl mx-auto">
              Beyond automation towards augmentation — where AI capabilities
              seamlessly integrate with human expertise.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Brain className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Transparent Processes
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Real-time visibility into AI decision-making with interruptible
                workflows. See what agents think and maintain full control.
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Human in the Loop
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Strategic human oversight with AI execution. Define boundaries,
                approve critical decisions, maintain ethical standards.
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mx-auto mb-4">
                <DollarSign className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Cost-Aware Intelligence
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Intelligent model routing that balances capability with cost.
                Use DeepSeek for routine tasks, Claude for complex reasoning.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Bootstrap Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Get Started in Seconds
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              Choose your workflow template and launch a complete AI team
              instantly.
            </p>
          </div>

          <BootstrapTabs />
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-slate-50 dark:bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Enterprise-Grade Features
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              Production-ready capabilities for sophisticated multi-agent
              architectures.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <motion.div
                key={feature.title}
                className="bg-white dark:bg-slate-800 p-6 rounded-lg border border-slate-200 dark:border-slate-700 hover:shadow-md transition-shadow"
                whileHover={{ y: -2 }}
                transition={{ duration: 0.2 }}
              >
                <div className="w-10 h-10 bg-slate-100 dark:bg-slate-700 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm mb-4">
                  {feature.description}
                </p>
                <Link
                  href={feature.href}
                  className="inline-flex items-center text-blue-600 dark:text-blue-400 text-sm font-medium hover:text-blue-700 dark:hover:text-blue-300 no-underline"
                >
                  Learn More
                  <ArrowRight className="w-3 h-3 ml-1" />
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="relative py-20">
        {/* Subtle diagonal lines decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-full">
            <svg
              className="absolute top-10 left-10 w-32 h-32 text-slate-100 dark:text-slate-800 opacity-50"
              viewBox="0 0 100 100"
            >
              <defs>
                <pattern
                  id="diagonalLines"
                  patternUnits="userSpaceOnUse"
                  width="10"
                  height="10"
                >
                  <path
                    d="M 0,10 l 10,-10 M -2.5,2.5 l 5,-5 M 7.5,12.5 l 5,-5"
                    stroke="currentColor"
                    strokeWidth="0.5"
                  />
                </pattern>
              </defs>
              <rect width="100" height="100" fill="url(#diagonalLines)" />
            </svg>
            <svg
              className="absolute bottom-20 right-20 w-24 h-24 text-slate-100 dark:text-slate-800 opacity-30"
              viewBox="0 0 100 100"
            >
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="currentColor"
                strokeWidth="0.5"
                strokeDasharray="5,5"
              />
              <circle
                cx="50"
                cy="50"
                r="30"
                fill="none"
                stroke="currentColor"
                strokeWidth="0.5"
                strokeDasharray="3,3"
              />
            </svg>
          </div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Real-World Applications
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              See how AgentX transforms work across industries.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {useCases.map((useCase) => (
              <div
                key={useCase.title}
                className="text-center p-6 rounded-lg border border-slate-200 dark:border-slate-700 hover:shadow-md transition-shadow"
              >
                <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <useCase.icon className="w-6 h-6 text-slate-600 dark:text-slate-400" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                  {useCase.title}
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm">
                  {useCase.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative py-20 bg-slate-900 dark:bg-slate-800 overflow-hidden">
        {/* Subtle accent decoration */}
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-px h-full bg-gradient-to-b from-transparent via-slate-700 to-transparent opacity-50"></div>
        <div className="absolute top-1/2 left-0 transform -translate-y-1/2 w-full h-px bg-gradient-to-r from-transparent via-slate-700 to-transparent opacity-30"></div>

        <div className="relative max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Experience Vibe-X?
          </h2>
          <p className="text-lg text-slate-300 mb-8">
            Join the next generation of human-AI collaboration with transparent,
            cost-efficient, and truly collaborative intelligent systems.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/docs/tutorials/0-bootstrap"
              className="inline-flex items-center bg-white text-slate-900 font-medium px-6 py-3 rounded-lg hover:bg-slate-100 transition-colors no-underline"
            >
              Start Building
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
            <Link
              href="https://github.com/dustland/agentx/tree/main/examples"
              target="_blank"
              className="inline-flex items-center border border-slate-600 text-white font-medium px-6 py-3 rounded-lg hover:bg-slate-800 transition-colors no-underline"
            >
              View Examples
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-50 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="flex items-center mb-4">
                <Image
                  src={`${basePath}/logo.png`}
                  alt="AgentX"
                  className="w-8 h-8 mr-3"
                  width={32}
                  height={32}
                />
                <span className="text-xl font-bold text-slate-900 dark:text-white">
                  AgentX
                </span>
              </div>
              <p className="text-slate-600 dark:text-slate-400 mb-4 max-w-md">
                Vibe-X philosophy in action. Build transparent, cost-efficient,
                and truly collaborative AI systems.
              </p>
              <Link
                href="https://github.com/dustland/agentx"
                target="_blank"
                className="inline-flex items-center text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 no-underline"
              >
                <Github className="w-5 h-5 mr-2" />
                GitHub
              </Link>
            </div>

            <div>
              <h3 className="font-semibold text-slate-900 dark:text-white mb-4">
                Documentation
              </h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link
                    href="/docs"
                    className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
                  >
                    Getting Started
                  </Link>
                </li>
                <li>
                  <Link
                    href="/docs/tutorials/0-bootstrap"
                    className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
                  >
                    Quick Start
                  </Link>
                </li>
                <li>
                  <Link
                    href="/docs/api"
                    className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
                  >
                    API Reference
                  </Link>
                </li>
                <li>
                  <Link
                    href="/docs/design"
                    className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
                  >
                    Design Philosophy
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-slate-900 dark:text-white mb-4">
                Resources
              </h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link
                    href="https://github.com/dustland/agentx/tree/main/examples"
                    target="_blank"
                    className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
                  >
                    Examples
                  </Link>
                </li>
                <li>
                  <Link
                    href="https://pypi.org/project/agentx-py/"
                    target="_blank"
                    className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
                  >
                    PyPI Package
                  </Link>
                </li>
                <li>
                  <Link
                    href="https://github.com/dustland/agentx/issues"
                    target="_blank"
                    className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
                  >
                    Report Issues
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between items-center">
            <div className="text-slate-500 dark:text-slate-400 text-sm">
              © {new Date().getFullYear()} Dustland.
            </div>
            <div className="text-slate-500 dark:text-slate-400 text-sm mt-2 md:mt-0">
              Made with ♥ for AI builders
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
