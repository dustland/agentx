'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useObservability } from '@/lib/hooks/use-observability'

const mockData = [
  { name: 'Mon', tasks: 12, avgDuration: 15 },
  { name: 'Tue', tasks: 19, avgDuration: 18 },
  { name: 'Wed', tasks: 15, avgDuration: 14 },
  { name: 'Thu', tasks: 25, avgDuration: 20 },
  { name: 'Fri', tasks: 22, avgDuration: 16 },
  { name: 'Sat', tasks: 8, avgDuration: 12 },
  { name: 'Sun', tasks: 10, avgDuration: 13 },
]

export function TaskMetrics() {
  const { metrics } = useObservability()

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Task Volume</CardTitle>
          <CardDescription>Number of tasks executed per day</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="name" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip />
              <Bar dataKey="tasks" fill="hsl(var(--primary))" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Average Duration</CardTitle>
          <CardDescription>Task completion time in minutes</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="name" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="avgDuration"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}