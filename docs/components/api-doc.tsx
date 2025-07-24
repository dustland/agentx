"use client";

import { useEffect, useState } from "react";

type ViewMode = "redoc" | "swagger";

export function ApiDoc() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>("redoc");

  useEffect(() => {
    // Check if the API server is accessible
    fetch("http://localhost:7770/openapi.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error("API server not accessible");
        }
        setIsLoading(false);
      })
      .catch(() => {
        setError(
          "Unable to connect to API server. Please ensure VibeX is running on port 7770."
        );
        setIsLoading(false);
      });
  }, []);

  // Detect theme changes
  useEffect(() => {
    const checkDarkMode = () => {
      setIsDarkMode(document.documentElement.classList.contains("dark"));
    };

    // Initial check
    checkDarkMode();

    // Watch for theme changes
    const observer = new MutationObserver(checkDarkMode);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => observer.disconnect();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-gray-100 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">
            Connecting to API server...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950 p-6">
        <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
          Connection Error
        </h3>
        <p className="text-red-700 dark:text-red-300 mb-4">{error}</p>
        <div className="bg-gray-900 dark:bg-gray-800 rounded p-3 font-mono text-sm text-gray-100">
          <span className="text-green-400">$</span> uv run start --port 7770
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* View Mode Switcher */}
      <div className="fixed top-20 right-4 z-50 flex gap-2 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg shadow-lg">
        <button
          onClick={() => setViewMode("redoc")}
          className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
            viewMode === "redoc"
              ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm"
              : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
          }`}
        >
          ReDoc
        </button>
        <button
          onClick={() => setViewMode("swagger")}
          className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
            viewMode === "swagger"
              ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm"
              : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
          }`}
        >
          Swagger UI
        </button>
      </div>

      {/* API Documentation Viewer */}
      <iframe
        key={`${viewMode}-${isDarkMode}`} // Force reload when theme changes
        src={
          viewMode === "redoc"
            ? isDarkMode
              ? "http://localhost:7770/redoc?theme=https://raw.githubusercontent.com/dilanx/redark/main/redark.json"
              : "http://localhost:7770/redoc"
            : "http://localhost:7770/docs"
        }
        className="w-full flex-1 border-0"
        style={{
          filter:
            isDarkMode && viewMode === "swagger"
              ? "invert(0.93) hue-rotate(180deg) contrast(0.9)"
              : "none",
          background: isDarkMode ? "#0a0a0a" : "white",
          minHeight: "calc(100vh - 64px)",
        }}
        title="VibeX API Documentation"
      />
    </div>
  );
}
