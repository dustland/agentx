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
import { Button } from "nextra/components";

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
      command:
        "pip install agentx-py\nagentx init my-research --template writing",
      agents: ["Researcher", "Writer", "Reviewer", "Web Designer"],
      exampleCode: `import asyncio
from agentx import start_task

async def main():
    # Start XAgent with your research team
    x = await start_task(
        "Write a comprehensive report on AI trends in 2025",
        "config/team.yaml"
    )

    print(f"Task ID: {x.task_id}")
    print(f"Workspace: {x.workspace.get_workspace_path()}")

    # Execute the initial task
    while not x.is_complete:
        response = await x.step()
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
      command: "pip install agentx-py\nagentx init my-app --template coding",
      agents: ["Planner", "Developer", "Reviewer"],
      exampleCode: `import asyncio
from agentx import start_task

async def main():
    # Start XAgent with your development team
    x = await start_task(
        "Build a REST API for a todo application",
        "config/team.yaml"
    )

    print(f"Task ID: {x.task_id}")
    print(f"Workspace: {x.workspace.get_workspace_path()}")

    # Execute the initial task
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
      command:
        "pip install agentx-py\nagentx init my-automation --template ops",
      agents: ["Analyst", "Operator", "Monitor"],
      exampleCode: `import asyncio
from agentx import start_task

async def main():
    # Start XAgent with your operations team
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
      {/* Workflow Tabs - Polished with rounded corners and auto width */}
      <div className="flex items-center justify-center gap-1 mb-8 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
        {workflows.map((workflow, index) => (
          <button
            key={workflow.id}
            onClick={() => setActiveTab(index)}
            className={`flex items-center gap-2 px-6 py-3 text-sm font-medium rounded-lg transition-all duration-200 whitespace-nowrap ${
              activeTab === index
                ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-slate-700/50"
            }`}
          >
            <workflow.icon className="w-4 h-4" />
            {workflow.title}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {/* CLI Command Block - With command indicators for each line */}
          <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 mb-6 border border-slate-200/50 dark:border-slate-700/50">
            <div className="font-mono text-sm text-slate-700 dark:text-slate-300">
              {workflows[activeTab].command.split("\n").map((line, index) => (
                <div key={index} className="flex items-center gap-3">
                  <span className="text-slate-500 dark:text-slate-400">
                    &gt;_
                  </span>
                  <span>{line}</span>
                </div>
              ))}
            </div>
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

        {/* Simple grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#f1f5f9_1px,transparent_1px),linear-gradient(to_bottom,#f1f5f9_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:60px_60px] opacity-40"></div>

        {/* Floating decorative elements */}
        <motion.div
          animate={{ y: [-10, 10, -10], x: [-5, 5, -5] }}
          transition={{
            duration: 20,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut",
          }}
          className="absolute top-20 left-10 w-32 h-32 bg-blue-100 dark:bg-blue-900/20 rounded-full blur-3xl opacity-60"
        ></motion.div>
        <motion.div
          animate={{ y: [15, -15, 15], x: [8, -8, 8] }}
          transition={{
            duration: 25,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut",
          }}
          className="absolute top-40 right-20 w-24 h-24 bg-purple-100 dark:bg-purple-900/20 rounded-full blur-3xl opacity-40"
        ></motion.div>
        <motion.div
          animate={{ y: [-5, 5, -5], x: [10, -10, 10] }}
          transition={{
            duration: 30,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut",
          }}
          className="absolute bottom-20 left-1/4 w-40 h-40 bg-slate-100 dark:bg-slate-800/30 rounded-full blur-3xl opacity-30"
        ></motion.div>

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
              Build Vibe-
              <TypewriterText /> Apps
              <br />
              <span className="text-2xl md:text-4xl text-slate-600 dark:text-slate-400">
                With AgentX
              </span>
            </motion.h1>

            <motion.p
              variants={itemVariants}
              className="text-xl text-slate-600 dark:text-slate-400 mb-8 max-w-3xl mx-auto"
            >
              The framework for human-AI collaboration that balances AI autonomy
              with human oversight. Transparent processes, cost-optimized
              intelligence, and professional workflows.
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
      <section className="py-20 bg-white dark:bg-slate-900">
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
              className="bg-slate-50 dark:bg-slate-800/50 p-8 rounded-lg text-center"
            >
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mx-auto mb-6">
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
              className="bg-slate-50 dark:bg-slate-800/50 p-8 rounded-lg text-center"
            >
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
              className="bg-slate-50 dark:bg-slate-800/50 p-8 rounded-lg text-center"
            >
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
            {features.map((feature) => (
              <motion.div
                key={feature.title}
                whileHover={{
                  y: -5,
                  boxShadow:
                    "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
                }}
                className="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-lg border border-slate-200 dark:border-slate-700 h-full flex flex-col"
              >
                <StyledLink
                  href={feature.href}
                  lightColor="#2563eb"
                  darkColor="#60a5fa"
                  className="text-sm font-medium no-underline"
                >
                  <div className="w-10 h-10 bg-slate-100 dark:bg-slate-700 rounded-lg flex items-center justify-center mb-4">
                    <feature.icon className="w-5 h-5 text-slate-600 dark:text-slate-300" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 text-sm flex-grow">
                    {feature.description}
                  </p>
                  <div className="mt-4">
                    <span
                      style={{ color: "#2563eb" }}
                      className="text-sm font-medium inline-flex items-center"
                    >
                      Learn More <ArrowRight className="w-4 h-4 ml-1" />
                    </span>
                  </div>
                </StyledLink>
              </motion.div>
            ))}
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
              See how AgentX transforms work across industries.
            </p>
          </div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            variants={containerVariants}
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-8"
          >
            {useCases.map((useCase) => (
              <motion.div
                key={useCase.title}
                variants={itemVariants}
                className="text-center bg-white dark:bg-slate-800 p-8 rounded-lg border border-slate-200 dark:border-slate-700"
              >
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-6">
                  <useCase.icon className="w-8 h-8 text-slate-500 dark:text-slate-400" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                  {useCase.title}
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm">
                  {useCase.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative py-20 bg-white dark:bg-slate-900">
        <div className="absolute inset-x-0 top-0 h-48 bg-gradient-to-b from-slate-50 dark:from-slate-800/50 to-transparent"></div>
        <div className="relative max-w-4xl mx-auto px-4">
          <div className="relative bg-blue-600 dark:bg-blue-700 rounded-2xl shadow-xl overflow-hidden p-12 text-center">
            <div className="absolute -top-10 -left-10 w-40 h-40 bg-white/10 rounded-full"></div>
            <div className="absolute -bottom-16 -right-5 w-56 h-56 bg-white/10 rounded-full"></div>
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
                  href="https://github.com/dustland/agentx/tree/main/examples"
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
      <footer className="bg-white dark:bg-slate-900 pt-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8 pb-8">
            <div className="flex items-center gap-3">
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
            <div className="flex items-center gap-6">
              <a
                href="https://github.com/dustland/agentx"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-white transition-colors"
              >
                <Github className="w-6 h-6" />
              </a>
              <Link
                href="/docs/getting-started"
                style={{ color: "#475569" }}
                className="text-sm font-medium transition-colors hover:text-blue-600"
              >
                Documentation
              </Link>
              <Link
                href="/docs/tutorials/0-bootstrap"
                style={{ color: "#475569" }}
                className="text-sm font-medium transition-colors hover:text-blue-600"
              >
                Examples
              </Link>
            </div>
          </div>
          <div className="py-8 border-t border-slate-200 dark:border-slate-700 text-center text-sm text-slate-500 dark:text-slate-400">
            <p>
              &copy; {new Date().getFullYear()} AgentX. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
