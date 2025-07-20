"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface UserAvatarProps {
  username?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function UserAvatar({
  username = "Guest",
  size = "md",
  className,
}: UserAvatarProps) {
  // Generate a consistent color based on username
  const getAvatarColor = (name: string) => {
    const colors = [
      "bg-orange-500/50",
      "bg-green-500/50",
      "bg-emerald-500/50",
      "bg-teal-500/50",
      "bg-amber-500/50",
      "bg-purple-500/50",
      "bg-fuchsia-500/50",
      "bg-pink-500/50",
      "bg-yellow-500/50",
      "bg-lime-500/50",
      "bg-cyan-500/50",
      "bg-sky-500/50",
      "bg-indigo-500/50",
      "bg-violet-500",
      "bg-rose-500/50",
    ];

    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }

    return colors[Math.abs(hash) % colors.length];
  };

  const sizeClasses = {
    sm: "h-7 w-7 text-xs",
    md: "h-9 w-9 text-sm",
    lg: "h-11 w-11 text-base",
  };

  const initials = username
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div
      className={cn(
        "rounded-full flex items-center justify-center font-medium text-white",
        getAvatarColor(username),
        sizeClasses[size],
        className
      )}
    >
      {initials}
    </div>
  );
}
