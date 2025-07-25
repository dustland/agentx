"use client";

import React, { useState, useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import {
  Activity,
  RefreshCwIcon,
  FileText,
  ChevronLeft,
  ChevronRight,
  Inbox,
  Terminal,
  FileStack,
} from "lucide-react";
import { AlertCircle, AlertTriangle, Info, Search } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useProjectLogs } from "@/hooks/use-project";

interface LogsProps {
  projectId: string;
}

export function Logs({ projectId }: LogsProps) {
  const [tailMode, setTailMode] = useState(true);
  const [offset, setOffset] = useState(0);
  const [autoScrollLogs, setAutoScrollLogs] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  const limit = 100;

  const {
    logs,
    hasMore,
    isLoading: loadingLogs,
    refetch,
  } = useProjectLogs(projectId, {
    limit,
    offset: tailMode ? 0 : offset,
    tail: tailMode,
  });

  const loadLogs = (newOffset?: number, newTailMode?: boolean) => {
    const useTail = newTailMode !== undefined ? newTailMode : tailMode;
    const useOffset = newOffset !== undefined ? newOffset : offset;

    if (!useTail) {
      setOffset(useOffset);
    }

    refetch();
  };

  // Auto-refresh logs every 2 seconds only in tail mode
  useEffect(() => {
    if (tailMode) {
      const interval = setInterval(() => refetch(), 2000);
      return () => clearInterval(interval);
    }
  }, [tailMode, refetch]);

  // Auto-scroll to bottom when new logs arrive or when first loading in tail mode
  useEffect(() => {
    if (autoScrollLogs && scrollRef.current && tailMode) {
      // Use setTimeout to ensure the content has been rendered
      setTimeout(() => {
        if (scrollRef.current) {
          scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
      }, 50);
    }
  }, [logs, autoScrollLogs, tailMode]);

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

  if (loadingLogs && logs.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <div className="text-center">
          <Inbox className="w-12 h-12 mx-auto mb-2 opacity-50 animate-pulse" />
          <p>Loading logs...</p>
        </div>
      </div>
    );
  }

  if (logs.length === 0 && !loadingLogs) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <div className="text-center">
          <Inbox className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No logs available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full relative">
      <div className="absolute top-2 right-2 z-10 flex items-center gap-1">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant="ghost"
                onClick={() => {
                  setTailMode(!tailMode);
                  loadLogs(0, !tailMode);
                }}
                className={`h-8 w-8 bg-background/80 backdrop-blur-sm border ${
                  tailMode ? "text-primary border-primary" : ""
                }`}
              >
                {tailMode ? (
                  <Terminal className="h-4 w-4" />
                ) : (
                  <FileStack className="h-4 w-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              {tailMode ? "Following latest logs" : "Paginated view"}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        {!tailMode && (
          <>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => {
                const newOffset = Math.max(0, offset - limit);
                loadLogs(newOffset, false);
              }}
              disabled={offset === 0 || loadingLogs}
              className="h-8 w-8 bg-background/80 backdrop-blur-sm border"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-xs text-muted-foreground px-2">
              {offset + 1}-{offset + logs.length}
            </span>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => {
                const newOffset = offset + limit;
                loadLogs(newOffset, false);
              }}
              disabled={!hasMore || loadingLogs}
              className="h-8 w-8 bg-background/80 backdrop-blur-sm border"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </>
        )}
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant="ghost"
                onClick={() => setAutoScrollLogs(!autoScrollLogs)}
                className={`h-8 w-8 bg-background/80 backdrop-blur-sm border ${
                  autoScrollLogs ? "text-primary border-primary" : ""
                }`}
              >
                <Activity className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              {autoScrollLogs ? "Auto-scroll enabled" : "Auto-scroll disabled"}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        <Button
          size="icon"
          variant="ghost"
          onClick={() => refetch()}
          disabled={loadingLogs}
          className="h-8 w-8 bg-background/80 backdrop-blur-sm border"
        >
          <RefreshCwIcon
            className={`h-4 w-4 ${loadingLogs ? "animate-spin" : ""}`}
          />
        </Button>
      </div>
      <ScrollArea className="h-full" ref={scrollRef}>
        <div className="p-4 space-y-1">
          {logs.map((log, idx) => {
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
                className="flex items-start gap-2 text-xs font-mono"
              >
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className={`flex-shrink-0 mt-0.5 ${getLogColor()}`}>
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
          })}
        </div>
      </ScrollArea>
    </div>
  );
}
