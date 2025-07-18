"use client";

import { useState, useCallback } from "react";
import { Sidebar } from "@/components/layout/sidebar";

export default function TasksLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Initialize sidebar state synchronously to prevent flickering
  const [isSidebarPinned, setIsSidebarPinned] = useState(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("sidebar-pinned");
      return stored !== null ? stored === "true" : true;
    }
    return true;
  });

  const handleFloatingChange = useCallback((floating: boolean) => {
    // Only update if the state actually needs to change
    setIsSidebarPinned((prev) => {
      const newValue = !floating;
      if (prev !== newValue) {
        localStorage.setItem("sidebar-pinned", newValue.toString());
        return newValue;
      }
      return prev;
    });
  }, []);

  return (
    <div className="h-screen flex">
      {/* Sidebar - conditionally render based on pinned state */}
      {isSidebarPinned && (
        <Sidebar
          className="flex-shrink-0"
          isFloating={false}
          onFloatingChange={handleFloatingChange}
        />
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Floating Sidebar */}
        {!isSidebarPinned && (
          <Sidebar isFloating={true} onFloatingChange={handleFloatingChange} />
        )}

        {/* Page Content */}
        {children}
      </div>
    </div>
  );
}
