import React from "react";
import { cn } from "@/lib/utils";

interface JsonViewerProps {
  data: any;
  className?: string;
  maxHeight?: string;
}

export function JsonViewer({
  data,
  className,
  maxHeight = "200px",
}: JsonViewerProps) {
  const jsonString = JSON.stringify(data, null, 2);

  return (
    <div className={cn("relative", className)}>
      <pre
        className={cn(
          "text-xs font-mono bg-muted/50 border rounded-md p-3 overflow-auto",
          "text-muted-foreground whitespace-pre-wrap break-words"
        )}
        style={{ maxHeight }}
      >
        {jsonString}
      </pre>
    </div>
  );
}
