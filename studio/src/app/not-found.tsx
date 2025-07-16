import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Home, Search } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex h-[calc(100vh-var(--header-height))] items-center justify-center p-6">
      <div className="max-w-md w-full space-y-6 text-center">
        <div className="space-y-2">
          <h1 className="text-6xl font-bold text-primary">404</h1>
          <h2 className="text-2xl font-semibold tracking-tight">
            Page not found
          </h2>
          <p className="text-sm text-muted-foreground">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        <div className="flex gap-3 justify-center">
          <Button asChild variant="outline">
            <Link href="/">
              <Home className="mr-2 h-4 w-4" />
              Go Home
            </Link>
          </Button>
          <Button asChild>
            <Link href="/x">
              <Search className="mr-2 h-4 w-4" />
              Browse Tasks
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}