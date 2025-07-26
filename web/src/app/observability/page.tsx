"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ActivityIcon, CheckCircleIcon, Activity, Wifi } from "lucide-react";
import { RecentProjects } from "@/components/xagent/recent-projects";
import { useObservability } from "@/hooks/use-observability";

export default function ObservabilityPage() {
  const { systemHealth, isLoading } = useObservability();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-6 space-y-6 overflow-auto">
      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <CheckCircleIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemHealth?.status === "healthy" ? "Healthy" : "Unknown"}
            </div>
            <p className="text-xs text-muted-foreground">
              Version {systemHealth?.version || "loading..."}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            <ActivityIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemHealth?.active_agents || 0}
            </div>
            <p className="text-xs text-muted-foreground">Currently running</p>
          </CardContent>
        </Card>
      </div>

      {/* System Monitoring */}
      <Tabs defaultValue="health" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="health">System Health</TabsTrigger>
          <TabsTrigger value="agents">Recent Agents</TabsTrigger>
        </TabsList>

        <TabsContent value="health" className="space-y-4 mt-4">
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
                      <span className="text-sm font-medium">
                        {systemHealth?.service_name || "VibeX API"}
                      </span>
                    </div>
                    <Badge
                      variant="default"
                      className={
                        systemHealth?.status === "healthy"
                          ? "bg-green-500 text-white"
                          : "bg-red-500 text-white"
                      }
                    >
                      {systemHealth?.status || "Unknown"}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Version: {systemHealth?.version || "loading..."}
                  </p>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Activity className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">Active Agents</span>
                    </div>
                    <Badge variant="default" className="bg-blue-500 text-white">
                      {systemHealth?.active_agents || 0}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Last updated:{" "}
                    {systemHealth?.timestamp
                      ? new Date(systemHealth.timestamp).toLocaleTimeString()
                      : "N/A"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>API Endpoints</CardTitle>
              <CardDescription>Available service endpoints</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {systemHealth?.api_endpoints?.map((endpoint: string) => (
                  <div
                    key={endpoint}
                    className="flex items-center gap-2 text-sm"
                  >
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <code className="text-xs bg-muted px-2 py-1 rounded">
                      {endpoint}
                    </code>
                  </div>
                )) || (
                  <p className="text-sm text-muted-foreground">
                    No endpoints available
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agents" className="space-y-4 mt-4">
          <RecentProjects />
        </TabsContent>
      </Tabs>
    </div>
  );
}
