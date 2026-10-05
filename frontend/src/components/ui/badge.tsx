import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Badge del diseño (nodo «Badge» #EY7t3): alto 20, radio 16, padding [2,8,2,6],
 * texto 12/500. Con `dot`, el punto de 6px a la izquierda.
 *
 * Los colores salen de los pares de estado del .pen, no de la paleta cruda de
 * Tailwind: un bg-emerald-100 suelto no cambia en modo oscuro.
 */
const badgeVariants = cva(
  "inline-flex h-5 shrink-0 items-center gap-1 rounded-full px-2 text-xs font-medium",
  {
    variants: {
      variant: {
        neutral: "bg-accent text-foreground",
        success: "bg-positive-soft text-positive",
        error: "bg-negative-soft text-negative",
        warning: "bg-warning-soft text-warning",
        info: "bg-secondary text-muted-foreground",
      },
    },
    defaultVariants: { variant: "neutral" },
  },
);

function Badge({
  className,
  variant,
  dot = false,
  children,
  ...props
}: React.HTMLAttributes<HTMLSpanElement> &
  VariantProps<typeof badgeVariants> & { dot?: boolean }) {
  return (
    <span className={cn(badgeVariants({ variant }), dot && "pl-1.5", className)} {...props}>
      {dot && <span className="size-1.5 rounded-full bg-current" aria-hidden="true" />}
      {children}
    </span>
  );
}

export { Badge, badgeVariants };
