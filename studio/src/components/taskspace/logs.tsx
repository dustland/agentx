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
} from "lucide-react";
import { AlertCircle, AlertTriangle, Info, Search } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { formatBytes } from "@/lib/utils";
import { useTask } from "@/hooks/use-task";

interface LogsProps {
  taskId: string;
}

export function Logs({ taskId }: LogsProps) {
  const { getLogs } = useTask(taskId);
  const [logs, setLogs] = useState<string[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [autoScrollLogs, setAutoScrollLogs] = useState(true);
  const [tailMode, setTailMode] = useState(true);
  const [offset, setOffset] = useState(0);
  const [fileSize, setFileSize] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const limit = 100;

  const loadLogs = async (newOffset?: number, newTailMode?: boolean) => {
    if (!taskId) return;

    setLoadingLogs(true);
    try {
      const useTail = newTailMode !== undefined ? newTailMode : tailMode;
      const useOffset = newOffset !== undefined ? newOffset : offset;

      const response = await getLogs({
        limit,
        offset: useTail ? 0 : useOffset,
        tail: useTail,
      });

      setLogs(response.logs || []);
      setFileSize(response.file_size || 0);
      setHasMore(response.has_more || false);

      if (!useTail) {
        setOffset(useOffset);
      }
    } catch (error) {
      // console.error("Failed to load logs:", error);
    } finally {
      setLoadingLogs(false);
    }
  };

  // Load logs when component mounts or taskId changes
  useEffect(() => {
    if (taskId) {
      loadLogs();
    }

    // Auto-refresh logs every 2 seconds only in tail mode
    if (tailMode) {
      const interval = setInterval(() => loadLogs(), 2000);
      return () => clearInterval(interval);
    }
  }, [taskId, tailMode]);

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
        {fileSize > 0 && (
          <span className="text-xs text-muted-foreground mr-2">
            {formatBytes(fileSize)}
          </span>
        )}
        <Button
          size="sm"
          variant={tailMode ? "default" : "ghost"}
          onClick={() => {
            setTailMode(!tailMode);
            loadLogs(0, !tailMode);
          }}
          className="h-7 px-2 text-xs"
        >
          {tailMode ? "Tail" : "Page"}
        </Button>
        {!tailMode && (
          <>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                const newOffset = Math.max(0, offset - limit);
                loadLogs(newOffset, false);
              }}
              disabled={offset === 0 || loadingLogs}
              className="h-7 w-7 p-0"
            >
              <ChevronLeft className="h-3 w-3" />
            </Button>
            <span className="text-xs text-muted-foreground px-1">
              {offset + 1}-{offset + logs.length}
            </span>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                const newOffset = offset + limit;
                loadLogs(newOffset, false);
              }}
              disabled={!hasMore || loadingLogs}
              className="h-7 w-7 p-0"
            >
              <ChevronRight className="h-3 w-3" />
            </Button>
          </>
        )}
        <Button
          size="sm"
          variant="ghost"
          onClick={() => setAutoScrollLogs(!autoScrollLogs)}
          className={
            autoScrollLogs
              ? "text-primary h-7 w-7 p-0"
              : "text-muted-foreground h-7 w-7 p-0"
          }
          title={
            autoScrollLogs ? "Auto-scroll enabled" : "Auto-scroll disabled"
          }
        >
          <Activity className="h-3 w-3" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => loadLogs()}
          disabled={loadingLogs}
          className="h-7 w-7 p-0"
        >
          <RefreshCwIcon
            className={`h-3 w-3 ${loadingLogs ? "animate-spin" : ""}`}
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
