import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium",
  {
    variants: {
      variant: {
        neutral: "bg-muted text-muted-foreground",
        success: "bg-emerald-100 text-emerald-800",
        error: "bg-red-50 text-red-800",
        info: "bg-blue-50 text-blue-800",
      },
    },
    defaultVariants: { variant: "neutral" },
  },
);

const dotVariants = cva("h-2 w-2 rounded-full", {
  variants: {
    variant: {
      neutral: "bg-slate-400",
      success: "bg-emerald-500",
      error: "bg-red-500",
      info: "bg-blue-500",
    },
  },
  defaultVariants: { variant: "neutral" },
});

export function Badge({
  className,
  variant,
  dot = true,
  children,
}: React.HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants> & { dot?: boolean }) {
  return (
    <span className={cn(badgeVariants({ variant }), className)}>
      {dot && <span className={cn(dotVariants({ variant }))} />}
      {children}
    </span>
  );
}
