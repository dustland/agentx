"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function AgentPerformance() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent Performance</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          Agent performance metrics coming soon...
        </p>
      </CardContent>
    </Card>
  );
}