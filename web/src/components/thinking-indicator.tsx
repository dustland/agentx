import { Loader2 } from "lucide-react";

export function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-2 text-muted-foreground mt-2">
      <Loader2 className="w-3 h-3 animate-spin" />
      <span className="text-xs">Thinking...</span>
    </div>
  );
}
