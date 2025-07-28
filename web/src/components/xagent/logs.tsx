"use client";

import React, { useState, useEffect, useRef } from "react";
// Removed ScrollArea import - using plain div for better scroll control
import { Button } from "@/components/ui/button";
import {
  Activity,
  RefreshCwIcon,
  FileText,
  ChevronLeft,
  ChevronRight,
  Terminal,
  FileStack,
  ScrollText,
} from "lucide-react";
import { EmptyState } from "./empty-state";
import { AlertCircle, AlertTriangle, Info, Search } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { useLogs } from "@/hooks/use-xagent";

interface LogsProps {
  xagentId: string;
}

export function Logs({ xagentId }: LogsProps) {
  const [tailMode, setTailMode] = useState(true);
  const [offset, setOffset] = useState(0);
  const [autoScrollLogs, setAutoScrollLogs] = useState(true);
  const [displayLimit, setDisplayLimit] = useState(100); // Limit displayed logs
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const limit = 100;

  const {
    logs,
    hasMore,
    isLoading: loadingLogs,
    refetch,
  } = useLogs(xagentId, {
    level: undefined,
    limit,
    enabled: true, // Only load when component is mounted
  });

  // Handle initial load completion - set a small delay to make tab switch feel instant
  useEffect(() => {
    if (!loadingLogs && logs && logs.length > 0 && isInitialLoad) {
      // Very short delay to allow tab switch, then show logs
      const timer = setTimeout(() => {
        setIsInitialLoad(false);
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [loadingLogs, logs, isInitialLoad]);

  // Reset display limit when switching to tail mode to show recent logs
  useEffect(() => {
    if (tailMode) {
      setDisplayLimit(100); // Reset to default when entering tail mode
    }
  }, [tailMode]);

  // Limit displayed logs to prevent DOM bloat - but always show logs after initial load
  const displayedLogs = logs
    ? tailMode
      ? logs.slice(-displayLimit) // Show last N logs in tail mode
      : logs.slice(offset, offset + displayLimit) // Show paginated logs
    : [];

  const loadLogs = (newOffset?: number, newTailMode?: boolean) => {
    const useTail = newTailMode !== undefined ? newTailMode : tailMode;
    const useOffset = newOffset !== undefined ? newOffset : offset;

    if (!useTail) {
      setOffset(useOffset);
    }

    refetch();
  };

  // Auto-refresh logs every 3 seconds only in tail mode
  useEffect(() => {
    if (tailMode && !isInitialLoad) {
      intervalRef.current = setInterval(() => {
        refetch();
      }, 3000); // Reduced frequency to prevent lag
    } else {
      // Clear interval when tail mode is disabled or during initial load
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [tailMode, refetch, isInitialLoad]);

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Auto-scroll to bottom in tail mode
  useEffect(() => {
    if (
      autoScrollLogs &&
      scrollRef.current &&
      tailMode &&
      !isInitialLoad &&
      displayedLogs.length > 0
    ) {
      const element = scrollRef.current;
      // Small delay to ensure DOM is updated, then scroll
      const timer = setTimeout(() => {
        element.scrollTop = element.scrollHeight;
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [displayedLogs, autoScrollLogs, tailMode, isInitialLoad]);

  // Initial scroll to bottom when first loading in tail mode
  useEffect(() => {
    if (
      tailMode &&
      !isInitialLoad &&
      autoScrollLogs &&
      scrollRef.current &&
      displayedLogs.length > 0
    ) {
      const element = scrollRef.current;
      // Ensure we scroll to bottom on first render
      setTimeout(() => {
        element.scrollTop = element.scrollHeight;
      }, 200);
    }
  }, [isInitialLoad, tailMode]); // Only run when initial load completes

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

  // Show loading immediately for instant tab switching
  if (isInitialLoad || loadingLogs || !logs) {
    return (
      <EmptyState
        icon={ScrollText}
        title="Loading logs..."
        isLoading={true}
        size="md"
      />
    );
  }

  if (!logs || (logs.length === 0 && !loadingLogs)) {
    return (
      <EmptyState
        icon={ScrollText}
        title="No logs available"
        description="Logs will appear here when agents start working"
        size="md"
      />
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
                className={`h-6 w-6 bg-background/80 backdrop-blur-sm border ${
                  tailMode ? "text-primary bg-primary/10" : ""
                }`}
              >
                {tailMode ? (
                  <Terminal className="h-3 w-3" />
                ) : (
                  <FileStack className="h-3 w-3" />
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
              className="h-6 w-6 bg-background/80 backdrop-blur-sm border"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-xs text-muted-foreground px-2">
              {offset + 1}-{offset + (logs?.length || 0)}
            </span>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => {
                const newOffset = offset + limit;
                loadLogs(newOffset, false);
              }}
              disabled={!hasMore || loadingLogs}
              className="h-6 w-6 bg-background/80 backdrop-blur-sm border"
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
                className={`h-6 w-6 bg-background/80 backdrop-blur-sm border ${
                  autoScrollLogs ? "text-primary bg-primary/10" : ""
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
          className="h-6 w-6 bg-background/80 backdrop-blur-sm border"
        >
          <RefreshCwIcon
            className={`h-4 w-4 ${loadingLogs ? "animate-spin" : ""}`}
          />
        </Button>
      </div>
      <div className="h-full overflow-y-auto overflow-x-auto" ref={scrollRef}>
        <div className="p-4 space-y-1 min-w-0">
          {/* Show truncation warning if logs are limited */}
          {logs && logs.length > displayLimit && tailMode && (
            <div className="text-xs text-muted-foreground text-center py-2 border-b mb-2">
              Showing last {displayedLogs.length} of {logs.length} logs
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setDisplayLimit((prev) => prev + 100)}
                className="ml-2 h-6 text-xs"
              >
                Load +100 more
              </Button>
            </div>
          )}

          {displayedLogs.map((log, idx) => {
            const parsed = parseLogEntry(log);
            const isError = parsed.level === "ERROR";
            const isWarning =
              parsed.level === "WARNING" || parsed.level === "WARN";
            const isInfo = parsed.level === "INFO";
            const isDebug = parsed.level === "DEBUG";

            const getLogIcon = () => {
              if (isError) return <AlertCircle className="w-4 h-4 shrink-0" />;
              if (isWarning)
                return <AlertTriangle className="w-4 h-4 shrink-0" />;
              if (isInfo) return <Info className="w-4 h-4 shrink-0" />;
              if (isDebug) return <Search className="w-4 h-4 shrink-0" />;
              return <FileText className="w-4 h-4 shrink-0" />;
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
                className="flex items-start gap-2 text-xs font-mono hover:bg-muted/50 py-0.5 px-2 -mx-2 rounded"
              >
                <HoverCard>
                  <HoverCardTrigger asChild>
                    <div
                      className={`flex items-center gap-2 flex-1 ${getLogColor()} font-mono truncate cursor-pointer`}
                    >
                      {/* Show timestamp and logger info inline for structure */}
                      {getLogIcon()}
                      {parsed.timestamp && (
                        <span className="">
                          {parsed.timestamp.split(" ")[1]}{" "}
                          {/* Show only time */}
                        </span>
                      )}
                      <span className="whitespace-nowrap overflow-hidden text-ellipsis">
                        {parsed.message}
                      </span>
                    </div>
                  </HoverCardTrigger>
                  <HoverCardContent
                    className="w-[600px] max-w-[90vw]"
                    align="start"
                  >
                    <div className="space-y-2">
                      <div className="text-xs text-muted-foreground space-y-1">
                        {parsed.timestamp && (
                          <div>
                            <span className="font-semibold">Time:</span>{" "}
                            {parsed.timestamp}
                          </div>
                        )}
                        {parsed.logger && (
                          <div>
                            <span className="font-semibold">Logger:</span>{" "}
                            {parsed.logger}
                          </div>
                        )}
                        <div>
                          <span className="font-semibold">Level:</span>{" "}
                          <span className={getLogColor()}>{parsed.level}</span>
                        </div>
                      </div>
                      <div className="pt-2 border-t">
                        <pre className="text-xs whitespace-pre-wrap break-all bg-muted p-2 rounded">
                          {parsed.message}
                        </pre>
                      </div>
                    </div>
                  </HoverCardContent>
                </HoverCard>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
