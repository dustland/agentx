import { Skeleton } from '@/components/ui/skeleton';

export default function TasksLoading() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header skeleton */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-96" />
      </div>

      {/* Task list skeleton */}
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="border rounded-lg p-6 space-y-3">
            <div className="flex items-center justify-between">
              <Skeleton className="h-6 w-64" />
              <Skeleton className="h-5 w-20" />
            </div>
            <Skeleton className="h-4 w-full max-w-lg" />
            <div className="flex gap-2">
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-8 w-24" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}