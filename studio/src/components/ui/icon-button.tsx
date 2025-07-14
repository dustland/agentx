import * as React from "react";
import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes } from "react";

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  index: number;
  icon?: React.ReactNode;
  label?: string;
  variant?: "default" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
}

export function IconButton({
  index,
  icon,
  label,
  className,
  variant = "default",
  size = "md",
  ...props
}: IconButtonProps) {
  const sizeClasses = {
    sm: "h-6 w-6 text-xs",
    md: "h-8 w-8 text-sm",
    lg: "h-10 w-10 text-base",
  };

  const variantClasses = {
    default: "bg-primary text-primary-foreground hover:bg-primary/90",
    outline:
      "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
    ghost: "hover:bg-accent hover:text-accent-foreground",
  };

  return (
    <button
      type="button"
      className={cn(
        "flex items-center justify-center rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      aria-label={label || `Element ${index}`}
      title={label || `Element ${index}`}
      {...props}
    >
      {icon || <span>{index}</span>}
    </button>
  );
}
