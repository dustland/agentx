"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cards, Callout } from "nextra/components";
import { Link } from "nextra-theme-docs";
import { useState, useEffect } from "react";
import {
  Users,
  Wrench,
  Brain,
  Zap,
  BarChart3,
  Settings,
  Sparkles,
  Rocket,
  Github,
  ArrowRight,
  ChartColumnStacked,
  GraduationCap,
  Bot,
  DollarSign,
  PenTool,
  Code,
  Cog,
  Terminal,
} from "lucide-react";

// Floating particles animation
const ParticleField = () => {
  const [particles, setParticles] = useState<
    Array<{ id: number; x: number; y: number; delay: number }>
  >([]);

  useEffect(() => {
    const newParticles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 2,
    }));
    setParticles(newParticles);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute w-1 h-1 bg-blue-400/30 rounded-full"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
          }}
          animate={{
            y: [0, -100, 0],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            delay: particle.delay,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
};

// Icon wrapper for consistent styling
const IconWrapper = ({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) => <div className={`inline-flex ${className}`}>{children}</div>;

// Optimized typewriter with Vibe-X focused words
const AnimatedText = () => {
  const words = ["Writing", "Coding", "Operating"];
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [currentText, setCurrentText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    const currentWord = words[currentWordIndex];
    let timeout: NodeJS.Timeout;

    if (!isDeleting && currentText.length < currentWord.length) {
      // Typing
      timeout = setTimeout(() => {
        setCurrentText(currentWord.slice(0, currentText.length + 1));
      }, 150);
    } else if (!isDeleting && currentText.length === currentWord.length) {
      // Pause before deleting
      timeout = setTimeout(() => {
        setIsDeleting(true);
      }, 3000);
    } else if (isDeleting && currentText.length > 0) {
      // Deleting
      timeout = setTimeout(() => {
        setCurrentText(currentText.slice(0, -1));
      }, 75);
    } else if (isDeleting && currentText.length === 0) {
      // Move to next word
      setIsDeleting(false);
      setCurrentWordIndex((prev) => (prev + 1) % words.length);
    }

    return () => {
      if (timeout) clearTimeout(timeout);
    };
  }, [currentText, isDeleting, currentWordIndex]);

  // Cursor blinking
  useEffect(() => {
    const cursorInterval = setInterval(() => {
      setShowCursor((prev) => !prev);
    }, 530);
    return () => clearInterval(cursorInterval);
  }, []);

  return (
    <div className="flex items-center h-full">
      <span className="text-emerald-400 font-mono">Vibe-</span>
      <span className="text-white font-mono whitespace-nowrap">
        {currentText}
      </span>
      <span
        className={`inline-block w-0.5 ml-1 bg-emerald-400 transition-opacity duration-150 ${
          showCursor ? "opacity-100" : "opacity-0"
        }`}
        style={{ height: "1em" }}
      />
    </div>
  );
};

// Interactive Bootstrap Tabs Component
const BootstrapTabs = () => {
  const [activeTab, setActiveTab] = useState(0);

  const workflows = [
    {
      id: "writing",
      title: "Writing",
      icon: PenTool,
      color: "blue",
      description: "Research → Draft → Edit workflow",
      command: "agentx init --template writing --model deepseek",
      features: [
        "Research automation",
        "Content structuring",
        "Quality review",
      ],
      agents: ["Researcher", "Writer", "Editor"],
    },
    {
      id: "coding",
      title: "Coding",
      icon: Code,
      color: "purple",
      description: "Plan → Build → Test workflow",
      command: "agentx init --template coding --model deepseek",
      features: [
        "Code generation",
        "Testing automation",
        "Architecture design",
      ],
      agents: ["Architect", "Developer", "Tester"],
    },
    {
      id: "operating",
      title: "Operating",
      icon: Cog,
      color: "emerald",
      description: "Analyze → Execute → Monitor workflow",
      command: "agentx init --template operating --model deepseek",
      features: [
        "System automation",
        "Real-world actions",
        "Impact monitoring",
      ],
      agents: ["Analyst", "Operator", "Monitor"],
    },
  ];

  const getColorClasses = (
    color: string,
    variant: "bg" | "text" | "border" | "ring"
  ) => {
    const colorMap = {
      blue: {
        bg: "bg-blue-500",
        text: "text-blue-600",
        border: "border-blue-200",
        ring: "ring-blue-500/20",
      },
      purple: {
        bg: "bg-purple-500",
        text: "text-purple-600",
        border: "border-purple-200",
        ring: "ring-purple-500/20",
      },
      emerald: {
        bg: "bg-emerald-500",
        text: "text-emerald-600",
        border: "border-emerald-200",
        ring: "ring-emerald-500/20",
      },
    };
    return colorMap[color]?.[variant] || "";
  };

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex justify-center">
        <div className="inline-flex rounded-xl bg-slate-100 dark:bg-slate-800 p-1">
          {workflows.map((workflow, index) => (
            <button
              key={workflow.id}
              onClick={() => setActiveTab(index)}
              className={`
                relative flex items-center px-6 py-3 rounded-lg text-sm font-medium transition-all duration-200
                ${
                  activeTab === index
                    ? `${getColorClasses(
                        workflow.color,
                        "bg"
                      )} text-white shadow-lg`
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                }
              `}
            >
              <workflow.icon className="w-4 h-4 mr-2" />
              {workflow.title}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="space-y-6"
        >
          {/* Command Terminal with Team Display */}
          <motion.div
            className="rounded-lg bg-slate-950 dark:bg-slate-950 p-6 shadow-inner"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <div className="flex items-center mb-4">
              <div className="flex space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              <span className="ml-4 text-xs text-slate-400">Terminal</span>
            </div>

            <code className="text-sm text-emerald-400 font-mono block text-left">
              $ pip install agentx-py
            </code>
            <code className="text-sm text-emerald-400 font-mono block text-left">
              $ {workflows[activeTab].command}
            </code>
            <code className="text-sm text-slate-400 font-mono block text-left mt-2">
              # Creates optimized {workflows[activeTab].title.toLowerCase()}{" "}
              workflow with 3 specialized agents
            </code>

            {/* Team Members Row */}
            <div className="mt-6 pt-4 border-t border-slate-700">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400 font-mono">
                  Generated Team:
                </span>
                <div className="flex items-center space-x-4">
                  {workflows[activeTab].agents.map((agent, i) => (
                    <div key={i} className="flex items-center space-x-2">
                      <div
                        className={`w-8 h-8 ${getColorClasses(
                          workflows[activeTab].color,
                          "bg"
                        )} rounded-full flex items-center justify-center`}
                      >
                        <Users className="w-4 h-4 text-white" />
                      </div>
                      <span className="text-xs text-slate-300 font-mono">
                        {agent}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Workflow Description */}
          <div
            className={`p-6 rounded-xl border-2 ${getColorClasses(
              workflows[activeTab].color,
              "border"
            )} bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-900`}
          >
            <h3
              className={`text-xl font-bold mb-3 ${getColorClasses(
                workflows[activeTab].color,
                "text"
              )} dark:text-white`}
            >
              {workflows[activeTab].title}
            </h3>
            <p className="text-slate-600 dark:text-slate-300 mb-4">
              {workflows[activeTab].description}
            </p>
            <div className="grid grid-cols-3 gap-4">
              {workflows[activeTab].features.map((feature, i) => (
                <div
                  key={i}
                  className="flex items-center text-sm text-slate-600 dark:text-slate-400"
                >
                  <span
                    className={`w-1.5 h-1.5 ${getColorClasses(
                      workflows[activeTab].color,
                      "bg"
                    )} rounded-full mr-2`}
                  ></span>
                  {feature}
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default function HomePage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const features = [
    {
      icon: Users,
      title: "Multi-Agent Orchestration",
      description:
        "Intelligent task distribution and dynamic load balancing for complex multi-agent workflows.",
      href: "/docs/design/overview",
    },
    {
      icon: Wrench,
      title: "Extensible Tools",
      description:
        "Native integrations for web APIs, file systems, databases, and custom tool development.",
      href: "/docs/design/tool-execution",
    },
    {
      icon: Brain,
      title: "Persistent Memory",
      description:
        "Contextual retention, semantic search, and distributed state persistence across agent networks.",
      href: "/docs/design/state-and-context",
    },
    {
      icon: Zap,
      title: "Events",
      description:
        "Real-time coordination, fault tolerance, and scalable inter-agent communication infrastructure.",
      href: "/docs/design/communication",
    },
    {
      icon: BarChart3,
      title: "Observability",
      description:
        "Distributed tracing, performance metrics, and intelligent debugging for production deployments.",
      href: "#",
    },
    {
      icon: Settings,
      title: "Configuration-Driven",
      description:
        "Configure agents and teams through simple YAML and Markdown. Almost no code required.",
      href: "#",
    },
  ];

  const vibeXWorkflows = [
    {
      icon: PenTool,
      title: "Vibe-Writing",
      description:
        "From idea to polished document. Collaborative research, drafting, and editing workflows with intelligent content generation and human oversight.",
      color: "blue",
      features: [
        "Research automation",
        "Content structuring",
        "Quality review",
      ],
    },
    {
      icon: Code,
      title: "Vibe-Coding",
      description:
        "From requirement to application. AI-assisted development with architecture planning, implementation, and testing in seamless collaboration.",
      color: "purple",
      features: [
        "Code generation",
        "Testing automation",
        "Architecture design",
      ],
    },
    {
      icon: Cog,
      title: "Vibe-Operating",
      description:
        "From insight to real-world impact. Agents that don't just analyze but act on digital and physical systems with human-defined boundaries.",
      color: "emerald",
      features: [
        "System automation",
        "Real-world actions",
        "Impact monitoring",
      ],
    },
  ];

  const realWorldScenarios = [
    {
      icon: Bot,
      title: "Agentic Applications",
      description:
        "Build intelligent applications where AI agents autonomously handle complex workflows while maintaining human oversight for critical decisions.",
    },
    {
      icon: GraduationCap,
      title: "Academic Research",
      description:
        "Deploy collaborative research teams that systematically gather data, conduct analysis, and synthesize findings across multiple domains and sources.",
    },
    {
      icon: ChartColumnStacked,
      title: "Enterprise Operations",
      description:
        "Streamline business operations through intelligent automation, real-time monitoring, and adaptive process optimization at scale.",
    },
    {
      icon: Rocket,
      title: "Creative Innovation",
      description:
        "Accelerate creative processes through AI-assisted ideation, content generation, and iterative design workflows for marketing and product development.",
    },
  ];

  return (
    <div
      className={`
        relative min-h-screen overflow-hidden
        bg-gradient-to-br from-slate-50 via-white to-blue-50 
        dark:from-slate-950 dark:via-slate-900 dark:to-blue-950
      `}
    >
      {/* Animated background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(120,119,198,0.3),rgba(255,255,255,0))]" />
        <ParticleField />
      </div>

      {/* Hero Section */}
      <motion.div
        className="relative z-10"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <div className="mx-auto max-w-7xl px-4 pt-20 pb-16 text-center lg:pt-32">
          <div className="mx-auto max-w-4xl">
            {/* Announcement Badge */}
            <motion.div
              variants={itemVariants}
              className="mb-8 flex justify-center"
            >
              <motion.div
                className="group relative overflow-hidden rounded-full px-4 py-2 text-sm leading-6 text-slate-600 ring-1 ring-slate-900/10 hover:ring-slate-900/20 dark:text-slate-400 dark:ring-slate-800 dark:hover:ring-slate-700 transition-all duration-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  layoutId="badge-bg"
                />
                <span className="relative flex items-center gap-2">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Introducing Vibe-X: Human-AI Collaboration Philosophy
                  <Link
                    href="/docs/design/vibe-x-philosophy"
                    className="font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                  >
                    Learn More <ArrowRight className="w-3 h-3 ml-1 inline" />
                  </Link>
                </span>
              </motion.div>
            </motion.div>

            {/* Main Title */}
            <motion.h1
              variants={itemVariants}
              className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-mono font-bold text-white text-center leading-tight max-w-4xl mx-auto whitespace-nowrap"
            >
              <span>Build </span>
              <span className="inline-block bg-slate-800/50 backdrop-blur-sm rounded-2xl px-4 sm:px-6 py-2 border border-slate-600/30 mx-1 sm:mx-2">
                <AnimatedText />
              </span>
              <span> Apps</span>
            </motion.h1>

            <motion.div
              variants={itemVariants}
              className="text-2xl sm:text-3xl lg:text-4xl mt-8"
              animate={{
                backgroundPosition: ["0%", "100%", "0%"],
              }}
              transition={{
                duration: 8,
                repeat: Infinity,
                ease: "linear",
              }}
            >
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent bg-[length:200%] animate-gradient">
                with Human-AI Collaboration
              </span>
            </motion.div>

            {/* Subtitle */}
            <motion.p
              variants={itemVariants}
              className="mt-6 text-xl leading-8 text-slate-600 dark:text-slate-300 sm:text-2xl max-w-3xl mx-auto"
            >
              The framework that embodies the perfect balance: AI autonomy with
              human oversight, transparent processes, and cost-optimized
              intelligence for professional workflows
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              variants={itemVariants}
              className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-6"
            >
              {/* Primary CTA Button */}
              <motion.div
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link
                  href="/docs/tutorials/0-bootstrap"
                  className="group relative inline-flex items-center overflow-hidden rounded-xl bg-gradient-to-r from-blue-500 via-purple-600 to-indigo-600 px-8 py-4 text-lg font-bold text-white shadow-2xl transition-all duration-300 hover:shadow-purple-500/25 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700"
                >
                  <Terminal className="mr-3 h-5 w-5 group-hover:rotate-12 transition-transform duration-300" />
                  Quick Start
                  <ArrowRight className="ml-3 h-5 w-5 group-hover:translate-x-1 transition-transform duration-300" />
                </Link>
              </motion.div>

              {/* Secondary CTA Button */}
              <motion.div
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link
                  href="/docs/design/vibe-x-philosophy"
                  className="group inline-flex items-center rounded-xl bg-white/10 dark:bg-slate-800/50 backdrop-blur-xl border border-white/20 dark:border-slate-700/50 px-8 py-4 text-lg font-semibold text-slate-700 dark:text-white shadow-xl hover:bg-white/20 dark:hover:bg-slate-700/50 transition-all duration-300"
                >
                  <Brain className="mr-3 h-5 w-5 group-hover:rotate-12 transition-transform duration-300" />
                  Explore Vibe-X
                  <ArrowRight className="ml-3 h-5 w-5 group-hover:translate-x-1 transition-transform duration-300" />
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Vibe-X Philosophy Section - Enhanced */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="relative z-10 py-24 bg-gradient-to-br from-slate-100 via-blue-50 to-purple-50 dark:from-slate-800 dark:via-slate-900 dark:to-slate-800 overflow-hidden"
      >
        {/* Background Pattern Effects */}
        <div className="absolute inset-0">
          {/* Floating geometric shapes */}
          <div className="absolute top-20 left-10 w-32 h-32 bg-blue-200/20 rounded-full blur-xl animate-pulse" />
          <div
            className="absolute top-40 right-20 w-24 h-24 bg-purple-200/20 rounded-full blur-lg animate-pulse"
            style={{ animationDelay: "1s" }}
          />
          <div
            className="absolute bottom-32 left-1/4 w-40 h-40 bg-indigo-200/15 rounded-full blur-2xl animate-pulse"
            style={{ animationDelay: "2s" }}
          />
          <div
            className="absolute bottom-20 right-1/3 w-28 h-28 bg-violet-200/20 rounded-full blur-xl animate-pulse"
            style={{ animationDelay: "0.5s" }}
          />

          {/* Subtle grid pattern */}
          <div
            className="absolute inset-0 opacity-5"
            style={{
              backgroundImage: `radial-gradient(circle at 1px 1px, rgba(99, 102, 241, 0.3) 1px, transparent 0)`,
              backgroundSize: "40px 40px",
            }}
          />

          {/* Gradient overlays */}
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-transparent to-purple-500/5" />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-indigo-500/3 to-transparent" />
        </div>

        <div className="mx-auto max-w-7xl px-4 relative z-10">
          <motion.div
            className="text-center mb-20"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-5xl md:text-6xl font-bold text-slate-900 dark:text-white text-center mb-6">
              The Vibe-X Philosophy
            </h2>
            <p className="text-2xl text-slate-700 dark:text-slate-300 max-w-4xl mx-auto leading-relaxed">
              Beyond automation towards augmentation — where AI capabilities
              seamlessly integrate with human expertise for optimal
              collaboration
            </p>
          </motion.div>

          {/* Three Core Pillars with Glass Effect */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Transparent Processes */}
            <motion.div
              className="group relative p-10 h-full min-h-[400px] flex flex-col backdrop-blur-xl shadow-2xl"
              style={{
                background: `linear-gradient(45deg, rgba(59, 130, 246, 0.04), rgba(59, 130, 246, 0.08), rgba(59, 130, 246, 0.02))`,
                border: "1px solid rgba(59, 130, 246, 0.2)",
                backdropFilter: "blur(18px)",
                boxShadow:
                  "0 16px 50px 0 rgba(59, 130, 246, 0.08), inset 0 3px 0 rgba(255,255,255,0.15)",
                transform: "rotate(1deg)",
                borderRadius: "30px 10px 30px 10px",
              }}
              whileHover={{
                scale: 1.02,
                rotate: -0.5,
              }}
              transition={{ duration: 0.3 }}
            >
              <div className="flex flex-col h-full items-center text-center relative z-10">
                <div className="mb-8 mx-auto">
                  <Brain
                    className="w-16 h-16 opacity-80"
                    style={{
                      color: "#3b82f6",
                      filter: "drop-shadow(0 2px 4px rgba(59, 130, 246, 0.2))",
                    }}
                  />
                </div>
                <h3 className="text-2xl font-bold mb-6 text-center text-slate-800 dark:text-white">
                  Transparent Processes
                </h3>
                <p className="text-slate-700 dark:text-slate-200 leading-relaxed text-center flex-grow opacity-90">
                  Real-time visibility into AI decision-making with
                  interruptible workflows. See what agents think, intervene when
                  needed, and maintain full control.
                </p>
              </div>
            </motion.div>

            {/* Human in the Loop */}
            <motion.div
              className="group relative p-10 h-full min-h-[400px] flex flex-col backdrop-blur-xl shadow-2xl"
              style={{
                background: `linear-gradient(45deg, rgba(139, 92, 246, 0.04), rgba(139, 92, 246, 0.08), rgba(139, 92, 246, 0.02))`,
                border: "1px solid rgba(139, 92, 246, 0.2)",
                backdropFilter: "blur(18px)",
                boxShadow:
                  "0 16px 50px 0 rgba(139, 92, 246, 0.08), inset 0 3px 0 rgba(255,255,255,0.15)",
                transform: "rotate(-1deg)",
                borderRadius: "30px 10px 30px 10px",
              }}
              whileHover={{
                scale: 1.02,
                rotate: 0.5,
              }}
              transition={{ duration: 0.3 }}
            >
              <div className="flex flex-col h-full items-center text-center relative z-10">
                <div className="mb-8 mx-auto">
                  <Users
                    className="w-16 h-16 opacity-80"
                    style={{
                      color: "#8b5cf6",
                      filter: "drop-shadow(0 2px 4px rgba(139, 92, 246, 0.2))",
                    }}
                  />
                </div>
                <h3 className="text-2xl font-bold mb-6 text-center text-slate-800 dark:text-white">
                  Human in the Loop
                </h3>
                <p className="text-slate-700 dark:text-slate-200 leading-relaxed text-center flex-grow opacity-90">
                  Strategic human oversight with AI execution. Define
                  boundaries, approve critical decisions, and maintain ethical
                  standards while AI handles the toil.
                </p>
              </div>
            </motion.div>

            {/* Cost-Aware Intelligence */}
            <motion.div
              className="group relative p-10 h-full min-h-[400px] flex flex-col backdrop-blur-xl shadow-2xl"
              style={{
                background: `linear-gradient(45deg, rgba(16, 185, 129, 0.04), rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.02))`,
                border: "1px solid rgba(16, 185, 129, 0.2)",
                backdropFilter: "blur(18px)",
                boxShadow:
                  "0 16px 50px 0 rgba(16, 185, 129, 0.08), inset 0 3px 0 rgba(255,255,255,0.15)",
                transform: "rotate(0.5deg)",
                borderRadius: "30px 10px 30px 10px",
              }}
              whileHover={{
                scale: 1.02,
                rotate: -0.5,
              }}
              transition={{ duration: 0.3 }}
            >
              <div className="flex flex-col h-full items-center text-center relative z-10">
                <div className="mb-8 mx-auto">
                  <DollarSign
                    className="w-16 h-16 opacity-80"
                    style={{
                      color: "#10b981",
                      filter: "drop-shadow(0 2px 4px rgba(16, 185, 129, 0.2))",
                    }}
                  />
                </div>
                <h3 className="text-2xl font-bold mb-6 text-center text-slate-800 dark:text-white">
                  Cost-Aware Intelligence
                </h3>
                <p className="text-slate-700 dark:text-slate-200 leading-relaxed text-center flex-grow opacity-90">
                  Intelligent model routing that balances capability with cost.
                  Use DeepSeek for routine tasks, Claude for complex reasoning —
                  economically sustainable AI.
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Features Section */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="relative z-10 py-24"
      >
        <div className="mx-auto max-w-7xl px-4">
          <motion.div
            className="text-center mb-20"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-5xl md:text-6xl font-bold text-slate-900 dark:text-white text-center mb-6">
              Enterprise-Grade Features
            </h2>
            <p className="text-2xl text-slate-600 dark:text-slate-300 max-w-4xl mx-auto leading-relaxed">
              Production-ready capabilities for building sophisticated
              multi-agent architectures
            </p>
          </motion.div>

          {/* Minimal Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <motion.div
                  className="group relative p-6 border border-slate-200 dark:border-slate-700 rounded-xl hover:border-slate-300 dark:hover:border-slate-600 transition-all duration-200"
                  whileHover={{ y: -2 }}
                  transition={{ duration: 0.2 }}
                >
                  {/* Minimal Icon */}
                  <div className="w-12 h-12 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-slate-600 dark:text-slate-400" />
                  </div>

                  {/* Content */}
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-4">
                    {feature.description}
                  </p>

                  {/* Minimal CTA */}
                  <Link
                    href={feature.href}
                    className="inline-flex items-center text-xs font-medium text-slate-500 dark:text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors group"
                  >
                    Learn More
                    <ArrowRight className="ml-1 h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </motion.div>
              </motion.div>
            ))}
          </div>

          {/* Architecture CTA */}
          <div className="text-center mt-20">
            <p className="text-lg text-slate-600 dark:text-slate-400 mb-8">
              Ready to understand how it all works together?
            </p>
            <Link
              href="/docs/design"
              className="inline-flex items-center bg-slate-500 dark:bg-white/20 hover:bg-slate-300 dark:hover:bg-white/30 text-white font-semibold px-8 py-4 rounded-xl transition-colors duration-200 shadow-lg hover:shadow-xl"
            >
              <Sparkles className="mr-3 h-5 w-5" />
              Explore the Design
              <ArrowRight className="ml-3 h-5 w-5" />
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Real-World Applications - Beautiful floating card layout restored */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="relative z-10 py-24"
      >
        <div className="mx-auto max-w-7xl px-4">
          <motion.div
            className="text-center mb-20"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-5xl md:text-6xl font-bold text-slate-900 dark:text-white text-center mb-6">
              Real-World Applications
            </h2>
            <p className="text-2xl text-slate-600 dark:text-slate-300 max-w-4xl mx-auto leading-relaxed">
              See how AgentX transforms work across industries with intelligent
              automation and human collaboration
            </p>
          </motion.div>

          {/* Floating Card Layout - Desktop Only */}
          <div className="hidden lg:block relative max-w-7xl mx-auto min-h-[600px]">
            {realWorldScenarios.map((scenario, index) => {
              const positions = [
                { top: "5%", left: "10%", rotate: "-3deg", zIndex: 4 },
                { top: "20%", right: "5%", rotate: "2deg", zIndex: 3 },
                {
                  top: "40%",
                  left: "30%",
                  rotate: "-1deg",
                  zIndex: 2,
                },
                {
                  top: "15%",
                  left: "50%",
                  rotate: "1deg",
                  zIndex: 1,
                },
              ];

              const colors = [
                {
                  bg: "from-blue-50 to-blue-100",
                  border: "border-blue-200",
                  text: "text-blue-900",
                  accent: "bg-blue-500",
                },
                {
                  bg: "from-purple-50 to-purple-100",
                  border: "border-purple-200",
                  text: "text-purple-900",
                  accent: "bg-purple-500",
                },
                {
                  bg: "from-emerald-50 to-emerald-100",
                  border: "border-emerald-200",
                  text: "text-emerald-900",
                  accent: "bg-emerald-500",
                },
                {
                  bg: "from-orange-50 to-orange-100",
                  border: "border-orange-200",
                  text: "text-orange-900",
                  accent: "bg-orange-500",
                },
              ];

              return (
                <motion.div
                  key={scenario.title}
                  className="absolute w-96 h-80"
                  style={{
                    top: positions[index].top,
                    left: positions[index].left,
                    right: positions[index].right,
                    transform: `rotate(${positions[index].rotate})`,
                    zIndex: positions[index].zIndex,
                  }}
                  initial={{ opacity: 0, y: 50, rotate: 0 }}
                  whileInView={{
                    opacity: 1,
                    y: 0,
                    rotate: parseInt(
                      positions[index].rotate.replace("deg", "")
                    ),
                  }}
                  viewport={{ once: true }}
                  transition={{
                    duration: 0.8,
                    delay: index * 0.2,
                    type: "spring",
                  }}
                  whileHover={{
                    scale: 1.08,
                    rotate: 0,
                    zIndex: 20,
                    y: -10,
                  }}
                >
                  <div
                    className="relative w-full h-full backdrop-blur-xl rounded-3xl p-8 shadow-2xl"
                    style={{
                      background:
                        colors[index].accent
                          .replace("bg-", "")
                          .replace("-500", "") === "blue"
                          ? `linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.05))`
                          : colors[index].accent
                              .replace("bg-", "")
                              .replace("-500", "") === "purple"
                          ? `linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(139, 92, 246, 0.05))`
                          : colors[index].accent
                              .replace("bg-", "")
                              .replace("-500", "") === "emerald"
                          ? `linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05))`
                          : `linear-gradient(135deg, rgba(249, 115, 22, 0.15), rgba(249, 115, 22, 0.05))`,
                      border:
                        colors[index].accent
                          .replace("bg-", "")
                          .replace("-500", "") === "blue"
                          ? "1px solid rgba(59, 130, 246, 0.3)"
                          : colors[index].accent
                              .replace("bg-", "")
                              .replace("-500", "") === "purple"
                          ? "1px solid rgba(139, 92, 246, 0.3)"
                          : colors[index].accent
                              .replace("bg-", "")
                              .replace("-500", "") === "emerald"
                          ? "1px solid rgba(16, 185, 129, 0.3)"
                          : "1px solid rgba(249, 115, 22, 0.3)",
                      backdropFilter: "blur(20px)",
                      boxShadow:
                        colors[index].accent
                          .replace("bg-", "")
                          .replace("-500", "") === "blue"
                          ? "0 8px 32px 0 rgba(59, 130, 246, 0.2), inset 0 1px 0 rgba(255,255,255,0.3)"
                          : colors[index].accent
                              .replace("bg-", "")
                              .replace("-500", "") === "purple"
                          ? "0 8px 32px 0 rgba(139, 92, 246, 0.2), inset 0 1px 0 rgba(255,255,255,0.3)"
                          : colors[index].accent
                              .replace("bg-", "")
                              .replace("-500", "") === "emerald"
                          ? "0 8px 32px 0 rgba(16, 185, 129, 0.2), inset 0 1px 0 rgba(255,255,255,0.3)"
                          : "0 8px 32px 0 rgba(249, 115, 22, 0.2), inset 0 1px 0 rgba(255,255,255,0.3)",
                    }}
                  >
                    {/* Corner accent with glass effect */}
                    <div
                      className="absolute top-0 right-0 w-20 h-20 rounded-bl-3xl rounded-tr-3xl"
                      style={{
                        background:
                          colors[index].accent
                            .replace("bg-", "")
                            .replace("-500", "") === "blue"
                            ? `linear-gradient(135deg, rgba(59, 130, 246, 0.25), transparent)`
                            : colors[index].accent
                                .replace("bg-", "")
                                .replace("-500", "") === "purple"
                            ? `linear-gradient(135deg, rgba(139, 92, 246, 0.25), transparent)`
                            : colors[index].accent
                                .replace("bg-", "")
                                .replace("-500", "") === "emerald"
                            ? `linear-gradient(135deg, rgba(16, 185, 129, 0.25), transparent)`
                            : `linear-gradient(135deg, rgba(249, 115, 22, 0.25), transparent)`,
                      }}
                    />

                    {/* Engraved Icon */}
                    <div className="mb-6">
                      <scenario.icon
                        className="w-12 h-12 opacity-70"
                        style={{
                          color:
                            colors[index].accent
                              .replace("bg-", "")
                              .replace("-500", "") === "blue"
                              ? "#3b82f6"
                              : colors[index].accent
                                  .replace("bg-", "")
                                  .replace("-500", "") === "purple"
                              ? "#8b5cf6"
                              : colors[index].accent
                                  .replace("bg-", "")
                                  .replace("-500", "") === "emerald"
                              ? "#10b981"
                              : "#f97316",
                          filter:
                            "drop-shadow(0 1px 2px rgba(0,0,0,0.1)) drop-shadow(0 -1px 1px rgba(255,255,255,0.3))",
                        }}
                      />
                    </div>

                    {/* Content with glass-friendly colors */}
                    <h3 className="text-2xl font-bold mb-4 text-slate-800 dark:text-white">
                      {scenario.title}
                    </h3>
                    <p className="text-slate-700 dark:text-slate-200 text-base leading-relaxed opacity-90">
                      {scenario.description}
                    </p>

                    {/* Glass decorative dots */}
                    <div className="absolute bottom-6 right-6 flex space-x-1.5">
                      <div
                        className="w-2 h-2 rounded-full backdrop-blur-sm border border-white/30"
                        style={{
                          background: `linear-gradient(135deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1))`,
                        }}
                      />
                      <div
                        className="w-2 h-2 rounded-full backdrop-blur-sm border border-white/30"
                        style={{
                          background: `linear-gradient(135deg, rgba(255,255,255,0.4), rgba(255,255,255,0.2))`,
                        }}
                      />
                      <div
                        className="w-2 h-2 rounded-full backdrop-blur-sm border border-white/30"
                        style={{
                          background: `linear-gradient(135deg, rgba(255,255,255,0.5), rgba(255,255,255,0.3))`,
                        }}
                      />
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Mobile List Layout */}
          <div className="lg:hidden grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {realWorldScenarios.map((scenario, index) => {
              const colors = [
                {
                  bg: "from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20",
                  border: "border-blue-200 dark:border-blue-700",
                  text: "text-blue-900 dark:text-blue-100",
                  accent: "bg-blue-500",
                },
                {
                  bg: "from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20",
                  border: "border-purple-200 dark:border-purple-700",
                  text: "text-purple-900 dark:text-purple-100",
                  accent: "bg-purple-500",
                },
                {
                  bg: "from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20",
                  border: "border-emerald-200 dark:border-emerald-700",
                  text: "text-emerald-900 dark:text-emerald-100",
                  accent: "bg-emerald-500",
                },
                {
                  bg: "from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20",
                  border: "border-orange-200 dark:border-orange-700",
                  text: "text-orange-900 dark:text-orange-100",
                  accent: "bg-orange-500",
                },
              ];

              return (
                <motion.div
                  key={scenario.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className={`p-6 rounded-2xl bg-gradient-to-br ${colors[index].bg} border ${colors[index].border} hover:shadow-lg transition-all duration-300`}
                >
                  <div className="flex items-start space-x-4">
                    <div
                      className={`flex-shrink-0 w-12 h-12 ${colors[index].accent} rounded-xl flex items-center justify-center`}
                    >
                      <scenario.icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3
                        className={`text-xl font-bold mb-2 ${colors[index].text}`}
                      >
                        {scenario.title}
                      </h3>
                      <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                        {scenario.description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Final CTA */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
        className="relative z-10 py-24"
      >
        <div className="mx-auto max-w-4xl px-4 text-center">
          <motion.div
            className="rounded-3xl bg-gradient-to-br from-blue-600 to-purple-600 p-12 shadow-2xl"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.3 }}
          >
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Experience Vibe-X?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join the next generation of human-AI collaboration with
              transparent, cost-efficient, and truly collaborative intelligent
              systems
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link
                  href="/docs/tutorials/0-bootstrap"
                  className="inline-flex items-center bg-white text-blue-600 font-semibold py-3 px-8 rounded-lg shadow-lg hover:bg-blue-50 transition-colors duration-200"
                >
                  Start Building
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link
                  href="https://github.com/dustland/agentx/tree/main/examples"
                  target="_blank"
                  className="inline-flex items-center text-white font-semibold py-3 px-8 rounded-lg border border-white/20 hover:bg-white/10 transition-colors duration-200"
                >
                  View Examples
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
