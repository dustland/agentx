"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { useObservability } from "@/hooks/use-observability";
import { Activity, CheckCircle, Clock, AlertTriangle } from "lucide-react";
import Link from "next/link";

interface ObservabilityLayoutProps {
  children: React.ReactNode;
}

export default function ObservabilityLayout({
  children,
}: ObservabilityLayoutProps) {
  const { systemHealth, isLoading, refetch } = useObservability();

  return (
    <div className="h-screen flex">
      {/* Sidebar */}
      <Sidebar
        title="System Monitor"
        isLoading={isLoading}
        showRefreshButton={true}
        onRefresh={refetch}
        placeholder={
          <div className="text-center text-muted-foreground">
            <div className="bg-muted/30 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <p className="text-sm font-medium mb-1">No system data</p>
            <p className="text-xs opacity-75">
              Unable to load system information
            </p>
          </div>
        }
      >
        <div className="p-6 space-y-8">
          {/* System Health Overview */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-foreground">
              System Health
            </h3>

            <div className="space-y-2">
              {[
                {
                  label: "Status",
                  value:
                    systemHealth?.status === "healthy" ? "Healthy" : "Unknown",
                  icon:
                    systemHealth?.status === "healthy"
                      ? CheckCircle
                      : AlertTriangle,
                  color:
                    systemHealth?.status === "healthy"
                      ? "text-green-600"
                      : "text-red-600",
                  bgColor:
                    systemHealth?.status === "healthy"
                      ? "bg-green-50 dark:bg-green-950/20"
                      : "bg-red-50 dark:bg-red-950/20",
                },
                {
                  label: "Active Agents",
                  value: systemHealth?.active_agents || 0,
                  icon: Activity,
                  color: "text-blue-600",
                  bgColor: "bg-blue-50 dark:bg-blue-950/20",
                },
                {
                  label: "Version",
                  value: systemHealth?.version || "Unknown",
                  icon: CheckCircle,
                  color: "text-gray-600",
                  bgColor: "bg-gray-50 dark:bg-gray-950/20",
                },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <div
                    key={item.label}
                    className="p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${item.bgColor}`}>
                        <Icon className={`h-4 w-4 ${item.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground">
                          {item.label}
                        </p>
                        <p className="text-sm text-muted-foreground mt-0.5">
                          {item.value}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Navigation Links */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-foreground">
              Monitoring
            </h3>

            <div className="space-y-2">
              {[
                {
                  title: "System Overview",
                  description: "Health metrics and performance",
                  href: "/observability",
                  icon: Activity,
                },
                {
                  title: "Service Status",
                  description: "API endpoints and availability",
                  href: "/observability",
                  icon: CheckCircle,
                },
                {
                  title: "Performance",
                  description: "Response times and diagnostics",
                  href: "/observability",
                  icon: Clock,
                },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <Link key={item.title} href={item.href}>
                    <div className="p-3 rounded-lg bg-muted/20 hover:bg-muted/40 transition-all duration-200 group cursor-pointer">
                      <div className="flex items-start gap-3">
                        <div className="p-1.5 rounded-md bg-muted/50 group-hover:bg-accent/50 transition-colors">
                          <Icon className="h-4 w-4 text-muted-foreground group-hover:text-foreground" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-foreground group-hover:text-foreground">
                            {item.title}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {item.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>

          {/* System Information */}
          {systemHealth && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-foreground">
                System Info
              </h3>

              <div className="p-4 rounded-lg bg-muted/30">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      Service
                    </span>
                    <span className="text-sm font-medium text-foreground">
                      {systemHealth.service_name || "VibeX API"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      Updated
                    </span>
                    <span className="text-sm font-medium text-foreground">
                      {systemHealth.timestamp
                        ? new Date(systemHealth.timestamp).toLocaleTimeString(
                            [],
                            {
                              hour: "2-digit",
                              minute: "2-digit",
                            }
                          )
                        : "N/A"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </Sidebar>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative bg-muted">
        {/* Page Content */}
        {children}
      </div>
    </div>
  );
}
