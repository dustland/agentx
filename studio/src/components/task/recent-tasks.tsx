'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { TaskStatus } from './task-status'
import { ArrowRight } from 'lucide-react'

export function RecentTasks() {
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['recent-tasks'],
    queryFn: () => api.listTasks({ limit: 10 }),
    refetchInterval: 30000,
  })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-muted rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Tasks</CardTitle>
        <CardDescription>Latest task executions across all teams</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {tasks?.map((task: any) => (
            <div
              key={task.task_id}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-sm">{task.id}</p>
                  <TaskStatus status={task.status} />
                </div>
                <p className="text-sm text-muted-foreground line-clamp-1">
                  {task.objective}
                </p>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span>Team: {task.team_config}</span>
                  <span>•</span>
                  <span>{new Date(task.created_at).toLocaleString()}</span>
                </div>
              </div>
              <Button variant="ghost" size="sm">
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}