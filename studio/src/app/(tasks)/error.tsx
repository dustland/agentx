"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";
import { useRouter } from "next/navigation";

export default function TaskError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  useEffect(() => {
    // Log task-specific errors
    console.error("Task error:", error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="bg-card shadow-lg rounded-2xl px-8 py-10 w-full max-w-md flex flex-col items-center space-y-6">
        <div className="flex items-center justify-center w-16 h-16 rounded-full bg-yellow-100 mb-2">
          <AlertTriangle className="h-8 w-8 text-yellow-600" />
        </div>
        <h1 className="text-2xl font-bold text-center">Task Error</h1>
        <p className="text-base text-muted-foreground text-center">
          We encountered an error while processing this task.
        </p>
        <div className="flex gap-4 w-full justify-center mt-2">
          <Button
            onClick={() => router.push("/x")}
            variant="outline"
            className="flex-1"
          >
            Back to Tasks
          </Button>
          <Button onClick={reset} className="flex-1">
            Retry
          </Button>
        </div>
      </div>
    </div>
  );
}
