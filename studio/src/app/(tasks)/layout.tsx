"use client";

import { useState, useCallback, useEffect } from "react";
import { Sidebar } from "@/components/layout/sidebar";

export default function TasksLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Initialize with default value to avoid hydration mismatch
  const [isSidebarPinned, setIsSidebarPinned] = useState(true);

  // Load pinned state from localStorage after mount
  useEffect(() => {
    const stored = localStorage.getItem("sidebar-pinned");
    if (stored !== null) {
      setIsSidebarPinned(stored === "true");
    }
  }, []);

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
      {isSidebarPinned ? (
        <Sidebar
          key="pinned-sidebar"
          className="flex-shrink-0"
          isFloating={false}
          onFloatingChange={handleFloatingChange}
        />
      ) : (
        <Sidebar
          key="floating-sidebar"
          isFloating={true}
          onFloatingChange={handleFloatingChange}
        />
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative bg-muted">
        {/* Page Content */}
        {children}
      </div>
    </div>
  );
}
