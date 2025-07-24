import { Loader2 } from "lucide-react";

export default function RootLoading() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">Loading VibeX...</p>
      </div>
    </div>
  );
}
