'use client';

// This is where the current page.tsx logic would go
// Only the interactive parts need to be client components

interface Task {
  id: string;
  title: string;
  status: string;
}

interface TasksClientProps {
  initialTasks: Task[];
}

export function TasksClient({ initialTasks }: TasksClientProps) {
  // All the client-side logic from the current page.tsx would go here
  // useQuery, useState, event handlers, etc.
  
  return (
    <div>
      <h1>Tasks</h1>
      {/* The existing UI components */}
    </div>
  );
}