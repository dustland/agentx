"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function RecentTasks() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Tasks</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          Recent tasks list coming soon...
        </p>
      </CardContent>
    </Card>
  );
}