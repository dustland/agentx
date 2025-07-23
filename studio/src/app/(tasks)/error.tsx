"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle, RotateCcw, ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";

export default function TaskError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    // Log task-specific errors
    console.error("Task error:", error);
  }, [error]);

  return (
    <div
      className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-background via-muted to-background/80 animate-fadein"
      style={{ animation: "fadein 0.5s" }}
    >
      <style>{`
        @keyframes fadein {
          from { opacity: 0; transform: scale(0.97); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>
      <div className="bg-card shadow-2xl rounded-3xl px-10 py-12 w-full max-w-lg flex flex-col items-center space-y-7 border border-border animate-fadein">
        <div className="flex items-center justify-center w-20 h-20 rounded-full bg-yellow-100 mb-2 shadow-md">
          <AlertTriangle className="h-10 w-10 text-yellow-600" />
        </div>
        <h1 className="text-3xl font-extrabold text-center text-foreground">
          Something went wrong
        </h1>
        <p className="text-base text-muted-foreground text-center max-w-xs">
          Oops! We encountered an error while processing this task. This might
          be temporary. You can retry, or go back to your tasks.
        </p>
        <div className="flex gap-4 w-full justify-center mt-2">
          <Button
            onClick={() => router.push("/x")}
            variant="outline"
            className="flex-1 flex items-center gap-2"
            aria-label="Back to Tasks"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Tasks
          </Button>
          <Button
            onClick={reset}
            className="flex-1 flex items-center gap-2"
            aria-label="Retry"
            autoFocus
          >
            <RotateCcw className="w-4 h-4" />
            Retry
          </Button>
        </div>
        <button
          className="text-xs text-muted-foreground underline hover:text-foreground focus:outline-none mt-2"
          onClick={() => setShowDetails((v) => !v)}
          aria-expanded={showDetails}
        >
          {showDetails ? "Hide technical details" : "Show technical details"}
        </button>
        {showDetails && (
          <pre className="w-full bg-muted rounded-lg p-3 text-xs text-left overflow-x-auto border border-border max-h-40 mt-1">
            {error?.message || String(error)}
            {error?.digest ? `\nDigest: ${error.digest}` : ""}
          </pre>
        )}
      </div>
    </div>
  );
}
