/**
 * Dynamic imports for heavy components
 * Reduces initial bundle size by loading components only when needed
 */

import dynamic from 'next/dynamic';
import { Skeleton } from '@/components/ui/skeleton';

// Loading component for markdown
const MarkdownSkeleton = () => (
  <div className="space-y-2">
    <Skeleton className="h-4 w-full" />
    <Skeleton className="h-4 w-[90%]" />
    <Skeleton className="h-4 w-[80%]" />
  </div>
);

// Dynamic import for ReactMarkdown
export const DynamicMarkdown = dynamic(
  () => import('react-markdown'),
  {
    loading: () => <MarkdownSkeleton />,
    ssr: true, // Enable SSR if needed
  }
);

// Example: Dynamic import for a chart library (when you add one)
export const DynamicChart = dynamic(
  () => import('@/components/charts/task-chart').then(mod => mod.TaskChart),
  {
    loading: () => <Skeleton className="h-[300px] w-full" />,
    ssr: false, // Charts usually don't need SSR
  }
);

// Example: Dynamic import for code editor
export const DynamicCodeEditor = dynamic(
  () => import('@/components/editor/code-editor').then(mod => mod.CodeEditor),
  {
    loading: () => <Skeleton className="h-[400px] w-full" />,
    ssr: false,
  }
);