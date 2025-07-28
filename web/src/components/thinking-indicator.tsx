import { Loader2 } from "lucide-react";

export function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-1.5 text-muted-foreground/60 mt-1">
      <Loader2 className="w-3 h-3 animate-spin" />
      <span className="text-[11px] italic">Thinking...</span>
    </div>
  );
}
