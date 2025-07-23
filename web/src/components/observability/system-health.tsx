"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useObservability } from "@/hooks/use-observability";
import { Activity, Cpu, HardDrive, Wifi } from "lucide-react";

export function SystemHealth() {
  const { systemHealth } = useObservability();

  const mockHealth = {
    api: { status: "healthy", latency: 45 },
    database: { status: "healthy", connections: 12 },
    memory: { used: 68, total: 100 },
    cpu: { usage: 35 },
  };

  return (
    <div className="h-full bg-card flex flex-col">
      {/* System Health Header */}
      <div
        className="border-b bg-card"
        style={{ height: "var(--header-height)" }}
      >
        <div className="flex items-center justify-between px-4 h-full">
          <h2 className="font-semibold">System Monitor</h2>
        </div>
      </div>

      {/* System Health Body */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>
              Real-time system health monitoring
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Wifi className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">API Server</span>
                  </div>
                  <Badge variant="default" className="bg-green-500 text-white">
                    Healthy
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Latency: {mockHealth.api.latency}ms
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Database</span>
                  </div>
                  <Badge variant="default" className="bg-green-500 text-white">
                    Healthy
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Active connections: {mockHealth.database.connections}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resource Usage</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-muted-foreground" />
                  <span>CPU Usage</span>
                </div>
                <span>{mockHealth.cpu.usage}%</span>
              </div>
              <Progress value={mockHealth.cpu.usage} className="h-2" />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4 text-muted-foreground" />
                  <span>Memory Usage</span>
                </div>
                <span>{mockHealth.memory.used}%</span>
              </div>
              <Progress value={mockHealth.memory.used} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
