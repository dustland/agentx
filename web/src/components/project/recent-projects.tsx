"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function RecentProjects() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Projects</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          Recent tasks list coming soon...
        </p>
      </CardContent>
    </Card>
  );
}