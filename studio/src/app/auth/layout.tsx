"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";

interface AuthLayoutProps {
  children: React.ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Auth Header */}
      <div className="border-b bg-card">
        <div className="flex items-center justify-between px-4 h-14">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/logo.png" alt="AgentX" width={20} height={20} className="object-contain" />
            <span className="font-semibold">AgentX Studio</span>
          </Link>
        </div>
      </div>

      {/* Auth Content */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          {children}
        </div>
      </div>
    </div>
  );
}