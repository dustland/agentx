"use client";

import { Button } from "@/components/ui/button";
import { MoonIcon, SunIcon, GithubIcon } from "lucide-react";
import { useTheme } from "@/hooks/use-theme";
import Image from "next/image";

export function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="border-b bg-white/50 dark:bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Image
            src="/logo.svg"
            alt="VibeX Logo"
            width={40}
            height={40}
            className="rounded-lg"
          />
          <span className="font-semibold text-lg">VibeX</span>
        </div>

        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="w-9 h-9"
          >
            {theme === "dark" ? (
              <SunIcon className="h-4 w-4" />
            ) : (
              <MoonIcon className="h-4 w-4" />
            )}
          </Button>

          <Button variant="ghost" size="icon" asChild className="w-9 h-9">
            <a
              href="https://github.com/dustland/vibex"
              target="_blank"
              rel="noopener noreferrer"
            >
              <GithubIcon className="h-4 w-4" />
            </a>
          </Button>
        </div>
      </div>
    </header>
  );
}
