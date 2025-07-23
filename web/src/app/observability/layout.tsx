"use client";

import React from "react";
import { Navbar } from "@/components/layout/navbar";

interface ObservabilityLayoutProps {
  children: React.ReactNode;
}

export default function ObservabilityLayout({ children }: ObservabilityLayoutProps) {
  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <div className="flex-1 overflow-auto">{children}</div>
    </div>
  );
}