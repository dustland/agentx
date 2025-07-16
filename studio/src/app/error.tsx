'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertCircle } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="flex h-[calc(100vh-var(--header-height))] items-center justify-center p-6">
      <div className="max-w-md w-full space-y-6 text-center">
        <div className="flex justify-center">
          <div className="rounded-full bg-destructive/10 p-3">
            <AlertCircle className="h-6 w-6 text-destructive" />
          </div>
        </div>
        
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">
            Something went wrong!
          </h1>
          <p className="text-sm text-muted-foreground">
            An unexpected error occurred. We've been notified and are working to fix it.
          </p>
        </div>

        {process.env.NODE_ENV === 'development' && error.message && (
          <div className="rounded-lg bg-muted p-4 text-left">
            <p className="font-mono text-xs text-muted-foreground">
              {error.message}
            </p>
          </div>
        )}

        <div className="flex gap-3 justify-center">
          <Button
            onClick={() => window.location.href = '/'}
            variant="outline"
          >
            Go Home
          </Button>
          <Button onClick={reset}>
            Try Again
          </Button>
        </div>
      </div>
    </div>
  );
}