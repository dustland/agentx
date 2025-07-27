export function TypingIndicator() {
  return (
    <div className="flex items-center space-x-1 mt-3 pt-2 border-t border-border/50">
      <div className="flex items-center space-x-1.5">
        <span className="w-2.5 h-2.5 bg-primary/70 rounded-full typing-dot"></span>
        <span className="w-2.5 h-2.5 bg-primary/70 rounded-full typing-dot"></span>
        <span className="w-2.5 h-2.5 bg-primary/70 rounded-full typing-dot"></span>
      </div>
    </div>
  );
}
