"use client";

import * as React from "react";
import { Moon, Sun, Laptop } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

export function ThemeToggle() {
  const { setTheme, theme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  // Avoid hydration mismatch by only rendering after mount
  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="h-7 w-7 flex items-center justify-center cursor-pointer">
        <div className="h-4 w-4" /> {/* Placeholder to maintain layout */}
      </div>
    );
  }

  // Determine which icon to show based on current theme
  const getCurrentIcon = () => {
    if (resolvedTheme === "dark") {
      return <Moon className="h-4 w-4" />;
    } else {
      return <Sun className="h-4 w-4" />;
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <div className="h-7 w-7 flex items-center justify-center cursor-pointer hover:text-primary transition-colors">
          {getCurrentIcon()}
          <span className="sr-only">Toggle theme</span>
        </div>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40 space-y-1">
        {[
          { theme: "light", icon: <Sun className="mr-2 h-4 w-4" /> },
          { theme: "dark", icon: <Moon className="mr-2 h-4 w-4" /> },
          { theme: "system", icon: <Laptop className="mr-2 h-4 w-4" /> },
        ].map((item) => (
          <DropdownMenuItem
            key={item.theme}
            onClick={() => setTheme(item.theme)}
            className={cn(
              "flex items-center gap-2",
              theme === item.theme && "bg-accent text-accent-foreground"
            )}
          >
            {item.icon}
            <span>{item.theme}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
