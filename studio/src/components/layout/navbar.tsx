"use client";

import React from "react";
import { usePathname, useRouter } from "next/navigation";
import { Home, Bot, Workflow, Library, Monitor, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/common/theme-toggle";
import Image from "next/image";
import Link from "next/link";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface NavbarProps {
  className?: string;
}

export function Navbar({ className }: NavbarProps) {
  const router = useRouter();
  const pathname = usePathname();

  const navigationItems = [
    {
      label: "Home",
      icon: Home,
      href: "/",
      isActive: pathname === "/",
    },
    {
      label: "Tasks",
      icon: Workflow,
      href: "/tasks",
      isActive: pathname.includes("/tasks") && !pathname.match(/\/tasks\/[^\/]+$/),
    },
    {
      label: "Observability",
      icon: Monitor,
      href: "/observability",
      isActive: pathname.includes("/observability"),
    },
    {
      label: "Auth",
      icon: MessageSquare,
      href: "/auth/login",
      isActive: pathname.includes("/auth"),
    },
  ];

  return (
    <div
      className={cn("bg-card", className)}
      style={{ height: "var(--header-height, 57px)" }}
    >
      <div className="flex items-center justify-between px-4 h-full">
        {/* Left: Logo and Navigation */}
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/logo.png" alt="AgentX" width={20} height={20} className="object-contain" />
            <span className="font-semibold">
              Agent<span className="text-primary">X</span> Studio
            </span>
          </Link>

          {/* Navigation Items */}
          <Tabs
            value={pathname}
            onValueChange={(value) => router.push(value)}
            className="flex items-center gap-1"
          >
            <TabsList>
              {navigationItems.map((item) => (
                <TabsTrigger key={item.href} value={item.href}>
                  <item.icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        </div>

        {/* Right: Theme Toggle */}
        <div className="flex items-center gap-3">
          <ThemeToggle />
        </div>
      </div>
    </div>
  );
}