'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Avatar } from '@/components/ui/avatar'
import { Bot } from 'lucide-react'

const mockAgents = [
  { name: 'Researcher', tasks: 145, successRate: 95, avgTime: 12 },
  { name: 'Writer', tasks: 132, successRate: 92, avgTime: 18 },
  { name: 'Designer', tasks: 89, successRate: 88, avgTime: 25 },
  { name: 'Reviewer', tasks: 156, successRate: 97, avgTime: 8 },
]

export function AgentPerformance() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent Performance</CardTitle>
        <CardDescription>Individual agent metrics and statistics</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {mockAgents.map((agent) => (
            <div key={agent.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Avatar className="h-8 w-8">
                    <div className="flex items-center justify-center w-full h-full bg-primary/10">
                      <Bot className="h-4 w-4" />
                    </div>
                  </Avatar>
                  <div>
                    <p className="font-medium">{agent.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {agent.tasks} tasks completed
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <Badge variant="outline">{agent.avgTime}m avg</Badge>
                  <Badge 
                    variant={agent.successRate >= 95 ? 'default' : 'secondary'}
                    className={agent.successRate >= 95 ? 'bg-green-500 text-white' : ''}
                  >
                    {agent.successRate}% success
                  </Badge>
                </div>
              </div>
              <Progress value={agent.successRate} className="h-2" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}