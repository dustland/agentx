"use client";

import React, { useState, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, RefreshCwIcon, ScrollIcon } from "lucide-react";
import { useAgentXAPI } from "@/lib/api-client";
import {
  AlertCircle,
  Info,
  AlertTriangle,
  Search,
  FileText,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface LogsProps {
  taskId: string;
}

export function Logs({ taskId }: LogsProps) {
  const apiClient = useAgentXAPI();
  const [logs, setLogs] = useState<string[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [autoScrollLogs, setAutoScrollLogs] = useState(true);

  // Load logs function
  const loadLogs = async () => {
    if (!taskId) return;

    setLoadingLogs(true);
    try {
      const response = await apiClient.getTaskLogs(taskId);
      setLogs(response.logs || []);
    } catch (error) {
      console.error("Failed to load logs:", error);
    } finally {
      setLoadingLogs(false);
    }
  };

  // Load logs initially and set up refresh interval
  useEffect(() => {
    if (!taskId) return;

    loadLogs();

    // Refresh logs every 2 seconds when tab is active
    const interval = setInterval(loadLogs, 2000);
    return () => clearInterval(interval);
  }, [taskId]);

  const parseLogEntry = (log: string) => {
    // Match pattern: YYYY-MM-DD HH:MM:SS - logger.name - LEVEL - message
    const logPattern =
      /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - ([^-]+) - ([A-Z]+) - (.+)$/;
    const match = log.match(logPattern);

    if (match) {
      const [, timestamp, logger, level, message] = match;
      return {
        timestamp: timestamp.trim(),
        logger: logger.trim(),
        level: level.trim(),
        message: message.trim(),
        original: log,
      };
    }

    // Fallback for logs that don't match the pattern
    return {
      timestamp: "",
      logger: "",
      level: "INFO",
      message: log,
      original: log,
    };
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-4 border-b">
        <h3 className="text-lg font-semibold">Logs</h3>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setAutoScrollLogs(!autoScrollLogs)}
            className={
              autoScrollLogs ? "text-primary" : "text-muted-foreground"
            }
          >
            <Activity className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={loadLogs}
            disabled={loadingLogs}
          >
            <RefreshCwIcon
              className={`h-4 w-4 ${loadingLogs ? "animate-spin" : ""}`}
            />
          </Button>
        </div>
      </div>
      <ScrollArea className="flex-1 min-h-0">
        <div className="p-4 space-y-1">
          {logs.length === 0 ? (
            <div className="text-center py-6 text-muted-foreground">
              <FileText className="w-6 h-6 mx-auto mb-2 opacity-50" />
              <p>No logs available</p>
            </div>
          ) : (
            logs.map((log, idx) => {
              const parsed = parseLogEntry(log);
              const isError = parsed.level === "ERROR";
              const isWarning =
                parsed.level === "WARNING" || parsed.level === "WARN";
              const isInfo = parsed.level === "INFO";
              const isDebug = parsed.level === "DEBUG";

              const getLogIcon = () => {
                if (isError) return <AlertCircle className="w-4 h-4" />;
                if (isWarning) return <AlertTriangle className="w-4 h-4" />;
                if (isInfo) return <Info className="w-4 h-4" />;
                if (isDebug) return <Search className="w-4 h-4" />;
                return <FileText className="w-4 h-4" />;
              };

              const getLogColor = () => {
                if (isError) return "text-red-500";
                if (isWarning) return "text-amber-600 dark:text-amber-400";
                if (isInfo) return "text-blue-500";
                if (isDebug) return "text-gray-500";
                return "text-foreground";
              };

              const tooltipContent = [
                parsed.timestamp && `Time: ${parsed.timestamp}`,
                parsed.logger && `Logger: ${parsed.logger}`,
                `Level: ${parsed.level}`,
              ]
                .filter(Boolean)
                .join("\n");

              return (
                <div
                  key={idx}
                  className="flex items-start gap-2 text-sm font-mono"
                >
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div
                          className={`flex-shrink-0 mt-0.5 ${getLogColor()}`}
                        >
                          {getLogIcon()}
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <pre className="text-xs whitespace-pre-wrap">
                          {tooltipContent}
                        </pre>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                  <span className={`flex-1 ${getLogColor()}`}>
                    {parsed.message}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
