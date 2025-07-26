"use client";

import { Sidebar } from "@/components/layout/sidebar";

export default function TasksLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative bg-muted">
        {/* Page Content */}
        {children}
      </div>
    </div>
  );
}
