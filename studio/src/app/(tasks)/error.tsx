'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';
import { useRouter } from 'next/navigation';

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
    console.error('Task error:', error);
  }, [error]);

  return (
    <div className="flex h-full items-center justify-center p-6">
      <div className="max-w-md w-full space-y-6 text-center">
        <div className="flex justify-center">
          <div className="rounded-full bg-yellow-500/10 p-3">
            <AlertTriangle className="h-6 w-6 text-yellow-600" />
          </div>
        </div>
        
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">
            Task Error
          </h1>
          <p className="text-sm text-muted-foreground">
            We encountered an error while processing this task.
          </p>
        </div>

        <div className="flex gap-3 justify-center">
          <Button
            onClick={() => router.push('/x')}
            variant="outline"
          >
            Back to Tasks
          </Button>
          <Button onClick={reset}>
            Retry
          </Button>
        </div>
      </div>
    </div>
  );
}