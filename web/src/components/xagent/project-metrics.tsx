"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ProjectMetrics() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Task Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          Task metrics visualization coming soon...
        </p>
      </CardContent>
    </Card>
  );
}