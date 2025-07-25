"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link } from "nextra-theme-docs";
import { useState, useEffect } from "react";

// Custom styled Link component that handles Nextra's CSS specificity
const StyledLink = ({
  href,
  children,
  lightColor,
  darkColor,
  className,
  ...props
}) => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check for dark mode
    const checkDarkMode = () => {
      setIsDark(document.documentElement.classList.contains("dark"));
    };

    checkDarkMode();

    // Watch for theme changes
    const observer = new MutationObserver(checkDarkMode);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => observer.disconnect();
  }, []);

  const color = isDark ? darkColor : lightColor;

  return (
    <Link href={href} style={{ color }} className={className} {...props}>
      {children}
    </Link>
  );
};
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
  Sparkles,
  Copy,
  Check,
} from "lucide-react";
import Image from "next/image";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";

// Enhanced bootstrap tabs with example code
const BootstrapTabs = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [copied, setCopied] = useState(false);

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const workflows = [
    {
      id: "writing",
      title: "Writing",
      icon: PenTool,
      description: "Research → Draft → Edit workflow",
      command: "pip install vibex\nvibex init my-research --template writing",
      agents: ["Researcher", "Writer", "Reviewer", "Web Designer"],
      exampleCode: `import asyncio
from vibex import start_task

async def main():
    # Start VibeX with your research team
    x = await start_task(
        "Write a comprehensive report on AI trends in 2025",
        "config/team.yaml"
    )
    
    # Enable parallel execution for 3-5x faster workflows
    x.set_parallel_execution(enabled=True, max_concurrent=4)

    print(f"Task ID: {x.task_id}")
    print(f"Workspace: {x.workspace.get_workspace_path()}")

    # Execute tasks with parallel processing
    while not x.is_complete:
        response = await x.step()  # Runs multiple tasks in parallel
        print(f"X: {response}")

    # Chat with your AI team for refinements
    response = await x.chat("Focus more on business applications")
    print(f"X: {response.text}")

    # Continue chatting for iterations
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
      command: "pip install vibex\nvibex init my-app --template coding",
      agents: ["Planner", "Developer", "Reviewer"],
      exampleCode: `import asyncio
from vibex import start_task

async def main():
    # Start VibeX with your development team
    x = await start_task(
        "Build a REST API for a todo application",
        "config/team.yaml"
    )
    
    # Enable parallel execution for faster development
    x.set_parallel_execution(enabled=True, max_concurrent=3)

    print(f"Task ID: {x.task_id}")
    print(f"Workspace: {x.workspace.get_workspace_path()}")

    # Execute tasks in parallel (e.g., API design + DB schema + tests)
    while not x.is_complete:
        response = await x.step()
        print(f"X: {response}")

    # Chat with your development team for changes
    response = await x.chat("Use FastAPI and SQLite instead")
    print(f"X: {response.text}")

    # Continue development with chat
    await x.chat("Add user authentication")
    await x.chat("Write comprehensive tests")

if __name__ == "__main__":
    asyncio.run(main())`,
    },
    {
      id: "ops",
      title: "Ops",
      icon: Cog,
      description: "Analyze → Execute → Monitor workflow",
      command: "pip install vibex\nvibex init my-automation --template ops",
      agents: ["Analyst", "Operator", "Monitor"],
      exampleCode: `import asyncio
from vibex import start_task

async def main():
    # Start VibeX with your operations team
    x = await start_task(
        "Automate daily server health monitoring",
        "config/team.yaml"
    )

    print(f"Task ID: {x.task_id}")
    print(f"Workspace: {x.workspace.get_workspace_path()}")

    # Execute the initial task
    while not x.is_complete:
        response = await x.step()
        print(f"X: {response}")

    # Chat with your ops team for adjustments
    response = await x.chat("Check disk usage and memory too")
    print(f"X: {response.text}")

    # Add monitoring with chat
    await x.chat("Set up alerts for high CPU usage")
    await x.chat("Generate a daily status report")

if __name__ == "__main__":
    asyncio.run(main())`,
    },
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Workflow Tabs - Clean and minimal styling */}
      <div className="flex items-center justify-center gap-1 mb-8 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
        {workflows.map((workflow, index) => {
          const isActive = activeTab === index;

          return (
            <button
              key={workflow.id}
              onClick={() => setActiveTab(index)}
              className={`flex items-center gap-2 px-6 py-3 text-sm font-medium rounded-lg transition-all duration-200 whitespace-nowrap ${
                isActive
                  ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-slate-700/50"
              }`}
            >
              <workflow.icon className="w-4 h-4" />
              {workflow.title}
            </button>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {/* CLI Command Block - Enhanced with better styling */}
          <div className="relative bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-900/50 rounded-xl p-6 mb-6 border border-slate-200/50 dark:border-slate-700/50 overflow-hidden">
            {/* Terminal decoration */}
            <div className="absolute top-3 left-4 flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-400/50"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-400/50"></div>
              <div className="w-3 h-3 rounded-full bg-green-400/50"></div>
            </div>

            {/* Command lines */}
            <div className="font-mono text-sm mt-6">
              {workflows[activeTab].command.split("\n").map((line, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-3 py-1"
                >
                  <span className="text-emerald-600 dark:text-emerald-400 select-none">
                    $
                  </span>
                  <span className="text-slate-700 dark:text-slate-300">
                    {line}
                  </span>
                </motion.div>
              ))}
            </div>

            {/* Copy button */}
            <button
              onClick={() => handleCopy(workflows[activeTab].command)}
              className="absolute top-4 right-4 p-2 rounded-lg bg-slate-200/50 dark:bg-slate-700/50 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              title="Copy command"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-600 dark:text-green-400" />
              ) : (
                <Copy className="w-4 h-4 text-slate-600 dark:text-slate-400" />
              )}
            </button>
          </div>

          {/* Enhanced Code Window - Claude-inspired */}
          <div className="bg-slate-900 rounded-lg border border-slate-700/50 overflow-hidden shadow-2xl">
            {/* Enhanced Window Header */}
            <div className="bg-slate-800/80 px-4 py-3 border-b border-slate-700/50 backdrop-blur-sm">
              <div className="flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
                <span className="text-sm font-medium text-slate-300">
                  main.py
                </span>
              </div>
            </div>

            {/* Enhanced Code Content */}
            <div className="p-4 bg-slate-900">
              <SyntaxHighlighter
                language="python"
                style={oneDark}
                customStyle={{
                  margin: 0,
                  padding: 0,
                  fontSize: "0.8rem",
                  lineHeight: "1.6",
                  background: "transparent",
                  fontFamily:
                    "'JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', monospace",
                }}
                showLineNumbers={true}
                lineNumberStyle={{
                  color: "#64748b",
                  paddingRight: "1rem",
                  fontSize: "0.75rem",
                }}
                className="!border-none"
                codeTagProps={{
                  style: {
                    background: "transparent",
                  },
                }}
              >
                {workflows[activeTab].exampleCode}
              </SyntaxHighlighter>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default function HomePage() {
  const features = [
    {
      icon: Zap,
      title: "Parallel Execution",
      description:
        "3-5x faster workflows with intelligent parallel task execution and dependency management.",
      href: "/docs/design/overview",
    },
    {
      icon: Users,
      title: "Multi-Agent Teams",
      description:
        "Specialized agents collaborate seamlessly with natural language handoffs.",
      href: "/docs/design/overview",
    },
    {
      icon: Brain,
      title: "Stateful Memory",
      description:
        "Long-term context retention with semantic search across conversations.",
      href: "/docs/design/state-and-context",
    },
    {
      icon: Wrench,
      title: "Extensible Tools",
      description: "Rich tool ecosystem with secure Docker sandbox execution.",
      href: "/docs/design/tool-execution",
    },
    {
      icon: BarChart3,
      title: "Full Observability",
      description:
        "Real-time monitoring, distributed tracing, and event streaming.",
      href: "#",
    },
    {
      icon: Settings,
      title: "Configuration-First",
      description: "Define complex workflows in YAML. No custom code required.",
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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      {/* Hero Section */}
      <section className="relative py-20 lg:py-32 overflow-hidden">
        {/* Subtle background decoration */}
        <div className="absolute inset-0 bg-gradient-to-b from-slate-50 to-white dark:from-slate-800 dark:to-slate-900"></div>

        {/* X-Pattern Background */}
        <div className="absolute inset-0 overflow-hidden">
          {/* Animated X patterns */}
          <svg
            className="absolute inset-0 w-full h-full"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <pattern
                id="x-pattern"
                x="0"
                y="0"
                width="120"
                height="120"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M30 30L50 50M50 30L30 50"
                  stroke="currentColor"
                  strokeWidth="1"
                  className="text-slate-200 dark:text-slate-700"
                  opacity="0.5"
                />
                <path
                  d="M90 30L110 50M110 30L90 50"
                  stroke="currentColor"
                  strokeWidth="1"
                  className="text-slate-200 dark:text-slate-700"
                  opacity="0.5"
                />
                <path
                  d="M30 90L50 110M50 90L30 110"
                  stroke="currentColor"
                  strokeWidth="1"
                  className="text-slate-200 dark:text-slate-700"
                  opacity="0.5"
                />
                <path
                  d="M90 90L110 110M110 90L90 110"
                  stroke="currentColor"
                  strokeWidth="1"
                  className="text-slate-200 dark:text-slate-700"
                  opacity="0.5"
                />
                {/* Center larger X */}
                <path
                  d="M50 50L70 70M70 50L50 70"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  className="text-blue-300 dark:text-blue-800"
                  opacity="0.3"
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#x-pattern)" />
          </svg>

          {/* Gradient overlay to fade the pattern */}
          <div className="absolute inset-0 bg-gradient-to-b from-white/80 via-white/60 to-white/90 dark:from-slate-900/80 dark:via-slate-900/60 dark:to-slate-900/90"></div>
        </div>

        {/* Floating X elements */}
        <motion.div
          animate={{
            rotate: [0, 90, 180, 270, 360],
            scale: [1, 1.1, 1, 0.9, 1],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: "linear",
          }}
          className="absolute top-20 left-[10%] w-24 h-24 opacity-10"
        >
          <svg viewBox="0 0 100 100" className="w-full h-full">
            <path
              d="M20 20L80 80M80 20L20 80"
              stroke="currentColor"
              strokeWidth="3"
              className="text-blue-500 dark:text-blue-400"
            />
          </svg>
        </motion.div>

        <motion.div
          animate={{
            rotate: [360, 270, 180, 90, 0],
            scale: [0.8, 1, 1.2, 1, 0.8],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear",
          }}
          className="absolute top-40 right-[15%] w-32 h-32 opacity-10"
        >
          <svg viewBox="0 0 100 100" className="w-full h-full">
            <path
              d="M20 20L80 80M80 20L20 80"
              stroke="currentColor"
              strokeWidth="4"
              className="text-purple-500 dark:text-purple-400"
            />
          </svg>
        </motion.div>

        {/* Glowing orbs with X shapes inside */}
        <motion.div
          animate={{ y: [-10, 10, -10], x: [-5, 5, -5] }}
          transition={{
            duration: 20,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut",
          }}
          className="absolute bottom-20 left-[20%] w-40 h-40"
        >
          <div className="relative w-full h-full">
            <div className="absolute inset-0 bg-blue-200 dark:bg-blue-900/30 rounded-full blur-3xl opacity-40"></div>
            <svg
              viewBox="0 0 100 100"
              className="absolute inset-4 w-32 h-32 opacity-20"
            >
              <path
                d="M25 25L75 75M75 25L25 75"
                stroke="currentColor"
                strokeWidth="2"
                className="text-blue-600 dark:text-blue-300"
              />
            </svg>
          </div>
        </motion.div>

        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="relative max-w-7xl mx-auto px-4 text-center"
        >
          <div className="max-w-4xl mx-auto">
            {/* Main heading */}
            <motion.h1
              variants={itemVariants}
              className="text-4xl md:text-6xl font-bold text-slate-900 dark:text-white mb-6"
            >
              Vibe-Working with Agentic Teams
            </motion.h1>

            <motion.p
              variants={itemVariants}
              className="text-xl text-slate-600 dark:text-slate-400 mb-8 max-w-3xl mx-auto"
            >
              Build collaborative, production-ready AI agent teams in minutes.
              Experience the future of work with VibeX.
            </motion.p>

            {/* CTA buttons */}
            <motion.div
              variants={itemVariants}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link
                href="/docs/getting-started"
                className="inline-flex items-center bg-blue-600 hover:bg-blue-700 !text-white font-bold px-8 py-4 rounded-lg transition-transform duration-200 hover:scale-105 shadow-lg no-underline"
              >
                Quick Start
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
              <StyledLink
                href="/docs/design/vibe-x"
                lightColor="#374151"
                darkColor="#d1d5db"
                className="inline-flex items-center border border-slate-300 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800 font-medium px-6 py-3 rounded-lg transition-transform duration-200 hover:scale-105"
              >
                Learn Vibe-X
                <ArrowRight className="w-4 h-4 ml-2" />
              </StyledLink>
            </motion.div>
          </div>
        </motion.div>

        {/* Curve decoration - part of hero section so grid extends through it */}
        <div className="absolute bottom-0 left-0 w-full overflow-hidden z-10">
          <svg
            className="relative block w-full h-12"
            viewBox="0 0 1200 120"
            preserveAspectRatio="none"
          >
            <path
              d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V120H0V0Z"
              fill="currentColor"
              className="text-white dark:text-slate-900"
            />
          </svg>
        </div>
      </section>

      {/* Vibe-X Philosophy */}
      <section className="relative py-20 bg-white dark:bg-slate-900 overflow-hidden">
        {/* Subtle X pattern for section background */}
        <div className="absolute inset-0 opacity-5">
          <svg
            className="absolute inset-0 w-full h-full"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <pattern
                id="vibe-x-pattern"
                x="0"
                y="0"
                width="60"
                height="60"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M15 15L25 25M25 15L15 25"
                  stroke="currentColor"
                  strokeWidth="0.5"
                  className="text-slate-400 dark:text-slate-600"
                />
                <path
                  d="M35 35L45 45M45 35L35 45"
                  stroke="currentColor"
                  strokeWidth="0.5"
                  className="text-slate-400 dark:text-slate-600"
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#vibe-x-pattern)" />
          </svg>
        </div>

        <div className="relative max-w-7xl mx-auto px-4">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            variants={containerVariants}
            className="grid md:grid-cols-3 gap-8"
          >
            <motion.div
              variants={itemVariants}
              className="relative bg-slate-50 dark:bg-slate-800/50 p-8 rounded-lg text-center overflow-hidden group hover:shadow-lg transition-shadow duration-300"
            >
              {/* X decoration in corner */}
              <div className="absolute -top-2 -right-2 w-12 h-12 opacity-10 group-hover:opacity-20 transition-opacity">
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <path
                    d="M20 20L80 80M80 20L20 80"
                    stroke="currentColor"
                    strokeWidth="8"
                    className="text-blue-600 dark:text-blue-400"
                  />
                </svg>
              </div>

              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mx-auto mb-6 relative">
                <Brain className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Transparent Processes
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Real-time visibility into AI decision-making with interruptible
                workflows. See what agents think and maintain full control.
              </p>
            </motion.div>

            <motion.div
              variants={itemVariants}
              className="relative bg-slate-50 dark:bg-slate-800/50 p-8 rounded-lg text-center overflow-hidden group hover:shadow-lg transition-shadow duration-300"
            >
              {/* X decoration in corner */}
              <div className="absolute -top-2 -right-2 w-12 h-12 opacity-10 group-hover:opacity-20 transition-opacity">
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <path
                    d="M20 20L80 80M80 20L20 80"
                    stroke="currentColor"
                    strokeWidth="8"
                    className="text-purple-600 dark:text-purple-400"
                  />
                </svg>
              </div>

              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mx-auto mb-6">
                <Users className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Human in the Loop
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Strategic human oversight with AI execution. Define boundaries,
                approve critical decisions, maintain ethical standards.
              </p>
            </motion.div>

            <motion.div
              variants={itemVariants}
              className="relative bg-slate-50 dark:bg-slate-800/50 p-8 rounded-lg text-center overflow-hidden group hover:shadow-lg transition-shadow duration-300"
            >
              {/* X decoration in corner */}
              <div className="absolute -top-2 -right-2 w-12 h-12 opacity-10 group-hover:opacity-20 transition-opacity">
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <path
                    d="M20 20L80 80M80 20L20 80"
                    stroke="currentColor"
                    strokeWidth="8"
                    className="text-green-600 dark:text-green-400"
                  />
                </svg>
              </div>

              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mx-auto mb-6">
                <DollarSign className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Cost-Aware Intelligence
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Intelligent model routing that balances capability with cost.
                Use DeepSeek for routine tasks, Claude for complex reasoning.
              </p>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Bootstrap Section */}
      <section className="relative py-24 bg-slate-50 dark:bg-slate-800/30 overflow-hidden">
        {/* Subtle background pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#f8fafc_1px,transparent_1px),linear-gradient(to_bottom,#f8fafc_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,#334155_1px,transparent_1px),linear-gradient(to_bottom,#334155_1px,transparent_1px)] bg-[size:80px_80px] opacity-30"></div>

        {/* Floating decoration */}
        <motion.div
          animate={{ y: [-20, 20, -20], rotate: [0, 180, 360] }}
          transition={{
            duration: 40,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut",
          }}
          className="absolute top-20 right-10 w-24 h-24 bg-blue-200 dark:bg-blue-900/30 rounded-full blur-2xl opacity-40"
        ></motion.div>

        <div className="relative max-w-7xl mx-auto px-4">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            variants={containerVariants}
            className="text-center mb-12"
          >
            <motion.h2
              variants={itemVariants}
              className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4"
            >
              Get Started in{" "}
              <span className="text-blue-600 dark:text-blue-400">Seconds</span>
            </motion.h2>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={{
              hidden: { opacity: 0, y: 30 },
              visible: {
                opacity: 1,
                y: 0,
                transition: { duration: 0.5, ease: "easeOut" },
              },
            }}
          >
            <BootstrapTabs />
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white dark:bg-slate-900">
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

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            variants={containerVariants}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-8"
          >
            {features.map((feature, index) => {
              const gradients = [
                "from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20",
                "from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20",
                "from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20",
                "from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20",
                "from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20",
                "from-cyan-50 to-blue-50 dark:from-cyan-900/20 dark:to-blue-900/20",
              ];
              const iconColors = [
                "text-blue-600 dark:text-blue-400",
                "text-purple-600 dark:text-purple-400",
                "text-emerald-600 dark:text-emerald-400",
                "text-orange-600 dark:text-orange-400",
                "text-violet-600 dark:text-violet-400",
                "text-cyan-600 dark:text-cyan-400",
              ];

              return (
                <motion.div
                  key={feature.title}
                  whileHover={{
                    y: -5,
                    transition: { type: "spring", stiffness: 300 },
                  }}
                  className="group relative"
                >
                  <div
                    className={`absolute inset-0 bg-gradient-to-br ${gradients[index]} rounded-xl blur-sm group-hover:blur-md transition-all duration-300 opacity-60 group-hover:opacity-80`}
                  ></div>
                  <div className="relative bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm p-6 rounded-xl border border-slate-200/50 dark:border-slate-700/50 h-full flex flex-col overflow-hidden">
                    {/* Subtle gradient overlay */}
                    <div
                      className={`absolute inset-0 bg-gradient-to-br ${gradients[index]} opacity-10`}
                    ></div>

                    {/* Content */}
                    <StyledLink
                      href={feature.href}
                      lightColor="#2563eb"
                      darkColor="#60a5fa"
                      className="relative text-sm font-medium no-underline"
                    >
                      <div className="flex items-center gap-3 mb-4">
                        <div
                          className={`w-10 h-10 bg-gradient-to-br ${gradients[index]} rounded-lg flex items-center justify-center shadow-sm`}
                        >
                          <feature.icon
                            className={`w-5 h-5 ${iconColors[index]}`}
                          />
                        </div>
                        {index === 0 && (
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-full">
                            New
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                        {feature.title}
                      </h3>
                      <p className="text-slate-600 dark:text-slate-400 text-sm flex-grow leading-relaxed">
                        {feature.description}
                      </p>
                      <div className="mt-4 flex items-center gap-2">
                        <span
                          className={`text-sm font-medium inline-flex items-center ${iconColors[index]} group-hover:gap-3 transition-all`}
                        >
                          Learn More{" "}
                          <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                        </span>
                      </div>
                    </StyledLink>

                    {/* Corner accent */}
                    <div className="absolute -top-1 -right-1 w-20 h-20 opacity-10 group-hover:opacity-20 transition-opacity">
                      <svg viewBox="0 0 100 100" className="w-full h-full">
                        <path
                          d="M50 10L90 50L50 90L10 50Z"
                          fill="currentColor"
                          className={iconColors[index]}
                        />
                      </svg>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* Real-World Applications */}
      <section className="py-20 bg-slate-50 dark:bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Real-World Applications
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              See how VibeX transforms work across industries.
            </p>
          </div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            variants={containerVariants}
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-8"
          >
            {useCases.map((useCase, index) => {
              const borderColors = [
                "border-blue-200 dark:border-blue-800",
                "border-purple-200 dark:border-purple-800",
                "border-emerald-200 dark:border-emerald-800",
                "border-orange-200 dark:border-orange-800",
              ];
              const iconBg = [
                "bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30",
                "bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30",
                "bg-gradient-to-br from-emerald-100 to-teal-100 dark:from-emerald-900/30 dark:to-teal-900/30",
                "bg-gradient-to-br from-orange-100 to-red-100 dark:from-orange-900/30 dark:to-red-900/30",
              ];
              const iconColors = [
                "text-blue-600 dark:text-blue-400",
                "text-purple-600 dark:text-purple-400",
                "text-emerald-600 dark:text-emerald-400",
                "text-orange-600 dark:text-orange-400",
              ];

              return (
                <motion.div
                  key={useCase.title}
                  variants={itemVariants}
                  whileHover={{ scale: 1.02 }}
                  className={`group relative text-center bg-white dark:bg-slate-800 p-8 rounded-xl border-2 ${borderColors[index]} hover:shadow-lg transition-all duration-300 overflow-hidden`}
                >
                  {/* Background pattern */}
                  <div className="absolute inset-0 opacity-5">
                    <div className="absolute top-0 right-0 w-32 h-32 transform translate-x-16 -translate-y-16">
                      <svg viewBox="0 0 100 100" className="w-full h-full">
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1"
                          className={iconColors[index]}
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="30"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1"
                          className={iconColors[index]}
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="20"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1"
                          className={iconColors[index]}
                        />
                      </svg>
                    </div>
                  </div>

                  <div className="relative">
                    <div
                      className={`w-16 h-16 ${iconBg[index]} rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm group-hover:shadow-md transition-shadow`}
                    >
                      <useCase.icon
                        className={`w-8 h-8 ${iconColors[index]}`}
                      />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                      {useCase.title}
                    </h3>
                    <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                      {useCase.description}
                    </p>
                  </div>

                  {/* Bottom accent line */}
                  <div
                    className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r ${iconBg[index]} transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300`}
                  ></div>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative py-20 bg-white dark:bg-slate-900">
        <div className="absolute inset-x-0 top-0 h-48 bg-gradient-to-b from-slate-50 dark:from-slate-800/50 to-transparent"></div>
        <div className="relative max-w-4xl mx-auto px-4">
          <div className="relative bg-gradient-to-br from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 rounded-2xl shadow-xl overflow-hidden p-12 text-center">
            {/* Large X pattern background */}
            <div className="absolute inset-0 opacity-10">
              <svg
                className="absolute inset-0 w-full h-full"
                xmlns="http://www.w3.org/2000/svg"
              >
                <defs>
                  <pattern
                    id="cta-x-pattern"
                    x="0"
                    y="0"
                    width="100"
                    height="100"
                    patternUnits="userSpaceOnUse"
                  >
                    <path
                      d="M20 20L80 80M80 20L20 80"
                      stroke="white"
                      strokeWidth="2"
                    />
                    <path
                      d="M0 50L50 100M50 0L100 50"
                      stroke="white"
                      strokeWidth="1"
                      opacity="0.5"
                    />
                    <path
                      d="M0 50L50 0M50 100L100 50"
                      stroke="white"
                      strokeWidth="1"
                      opacity="0.5"
                    />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#cta-x-pattern)" />
              </svg>
            </div>

            {/* Animated X elements */}
            <motion.div
              animate={{
                rotate: 360,
                scale: [1, 1.2, 1],
              }}
              transition={{
                rotate: { duration: 20, repeat: Infinity, ease: "linear" },
                scale: { duration: 4, repeat: Infinity, repeatType: "reverse" },
              }}
              className="absolute -top-20 -left-20 w-40 h-40 opacity-20"
            >
              <svg viewBox="0 0 100 100" className="w-full h-full">
                <path
                  d="M20 20L80 80M80 20L20 80"
                  stroke="white"
                  strokeWidth="4"
                />
              </svg>
            </motion.div>

            <motion.div
              animate={{
                rotate: -360,
                scale: [1.2, 1, 1.2],
              }}
              transition={{
                rotate: { duration: 25, repeat: Infinity, ease: "linear" },
                scale: { duration: 5, repeat: Infinity, repeatType: "reverse" },
              }}
              className="absolute -bottom-16 -right-16 w-56 h-56 opacity-15"
            >
              <svg viewBox="0 0 100 100" className="w-full h-full">
                <path
                  d="M10 10L90 90M90 10L10 90"
                  stroke="white"
                  strokeWidth="3"
                />
              </svg>
            </motion.div>
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.5 }}
              variants={containerVariants}
              className="relative"
            >
              <motion.h2
                variants={itemVariants}
                className="text-3xl md:text-4xl font-bold text-white mb-4"
              >
                Ready to Experience Vibe-X?
              </motion.h2>
              <motion.p
                variants={itemVariants}
                className="text-lg text-blue-100 max-w-2xl mx-auto mb-8"
              >
                Join the next generation of human-AI collaboration with
                transparent, cost-efficient, and truly collaborative intelligent
                systems.
              </motion.p>
              <motion.div
                variants={itemVariants}
                className="flex flex-col sm:flex-row gap-4 justify-center"
              >
                <StyledLink
                  href="/docs/tutorials/0-bootstrap"
                  lightColor="#2563eb"
                  darkColor="#2563eb"
                  className="inline-flex items-center bg-white font-bold px-8 py-4 rounded-lg transition-transform duration-200 hover:scale-105 shadow-lg no-underline"
                >
                  Start Building
                  <ArrowRight className="w-4 h-4 ml-2" />
                </StyledLink>
                <Link
                  href="https://github.com/dustland/vibex/tree/main/examples"
                  target="_blank"
                  style={{ color: "#ffffff" }}
                  className="inline-flex items-center border border-blue-400 font-medium px-6 py-3 rounded-lg transition-all duration-200 hover:scale-105 hover:bg-white/10 no-underline"
                >
                  View Examples
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative bg-gradient-to-b from-white to-slate-50 dark:from-slate-900 dark:to-slate-950 pt-20 pb-12 overflow-hidden">
        {/* Subtle X pattern background */}
        <div className="absolute inset-0 opacity-[0.02]">
          <svg
            className="absolute inset-0 w-full h-full"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <pattern
                id="footer-x-pattern"
                x="0"
                y="0"
                width="40"
                height="40"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M10 10L20 20M20 10L10 20"
                  stroke="currentColor"
                  strokeWidth="0.5"
                  className="text-slate-600"
                />
                <path
                  d="M20 20L30 30M30 20L20 30"
                  stroke="currentColor"
                  strokeWidth="0.5"
                  className="text-slate-600"
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#footer-x-pattern)" />
          </svg>
        </div>

        <div className="relative max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            {/* Brand Column */}
            <div className="md:col-span-1">
              <div className="flex items-center gap-3 mb-4">
                <div className="relative">
                  <Image
                    src={`/logo.png`}
                    alt="VibeX"
                    className="w-10 h-10"
                    width={40}
                    height={40}
                  />
                  <div className="absolute -inset-1 bg-blue-500/20 rounded-lg blur-sm"></div>
                </div>
                <span className="text-xl font-bold text-slate-900 dark:text-white">
                  VibeX
                </span>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                The framework for human-AI collaboration with intelligent
                parallel execution.
              </p>
              <div className="flex items-center gap-3">
                <a
                  href="https://github.com/dustland/vibex"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors group"
                >
                  <Github className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-white" />
                </a>
                <a
                  href="https://twitter.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors group"
                >
                  <svg
                    className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-white"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                </a>
              </div>
            </div>

            {/* Resources Column */}
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4 uppercase tracking-wider">
                Resources
              </h3>
              <ul className="space-y-3">
                <li>
                  <Link
                    href="/docs/getting-started"
                    className="text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors inline-flex items-center gap-1 group"
                  >
                    Getting Started
                    <ArrowRight className="w-3 h-3 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </Link>
                </li>
                <li>
                  <Link
                    href="/docs/design/overview"
                    className="text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors inline-flex items-center gap-1 group"
                  >
                    Architecture
                    <ArrowRight className="w-3 h-3 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </Link>
                </li>
                <li>
                  <Link
                    href="/docs/api"
                    className="text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors inline-flex items-center gap-1 group"
                  >
                    API Reference
                    <ArrowRight className="w-3 h-3 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </Link>
                </li>
                <li>
                  <Link
                    href="/docs/tutorials/0-bootstrap"
                    className="text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors inline-flex items-center gap-1 group"
                  >
                    Tutorials
                    <ArrowRight className="w-3 h-3 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </Link>
                </li>
              </ul>
            </div>

            {/* Community Column */}
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4 uppercase tracking-wider">
                Community
              </h3>
              <ul className="space-y-3">
                <li>
                  <a
                    href="https://github.com/dustland/vibex/discussions"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors inline-flex items-center gap-1 group"
                  >
                    GitHub Discussions
                    <ArrowRight className="w-3 h-3 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/dustland/vibex/issues"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors inline-flex items-center gap-1 group"
                  >
                    Report Issues
                    <ArrowRight className="w-3 h-3 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/dustland/vibex/blob/main/CONTRIBUTING.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors inline-flex items-center gap-1 group"
                  >
                    Contributing
                    <ArrowRight className="w-3 h-3 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </a>
                </li>
                <li>
                  <Link
                    href="/blog"
                    className="text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors inline-flex items-center gap-1 group"
                  >
                    Blog
                    <ArrowRight className="w-3 h-3 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </Link>
                </li>
              </ul>
            </div>

            {/* Quick Start Column */}
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4 uppercase tracking-wider">
                Quick Start
              </h3>
              <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-4 mb-4">
                <code className="text-sm font-mono text-slate-700 dark:text-slate-300">
                  pip install vibex
                </code>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-3">
                Get started in seconds with our Python package.
              </p>
              <Link
                href="/docs/getting-started"
                className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
              >
                View Documentation
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="pt-8 border-t border-slate-200 dark:border-slate-800">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                <span>&copy; {new Date().getFullYear()} VibeX.</span>
                <span className="hidden md:inline">•</span>
                <span className="hidden md:inline">Built with ❤️ by</span>
                <a
                  href="https://github.com/dustland"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  Dustland
                </a>
              </div>
              <div className="flex items-center gap-6 text-sm">
                <Link
                  href="/privacy"
                  className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  Privacy
                </Link>
                <Link
                  href="/terms"
                  className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  Terms
                </Link>
                <a
                  href="https://github.com/dustland/vibex/blob/main/LICENSE"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  License
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
