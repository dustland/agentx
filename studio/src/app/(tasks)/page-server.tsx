// Example of Server Component pattern for tasks page
import { Metadata } from 'next';
import { TasksClient } from './tasks-client';

export const metadata: Metadata = {
  title: 'Tasks',
  description: 'View and manage your AgentX tasks',
};

// Server Component - runs on server, can fetch data directly
export default async function TasksPage() {
  // This would be your actual data fetching
  // const tasks = await fetchTasksFromAPI();
  
  // For now, we'll pass empty data to show the pattern
  const initialTasks = [];

  return <TasksClient initialTasks={initialTasks} />;
}