import * as React from "react";
import { cn } from "@/lib/utils";

export const Table = ({ className, ...props }: React.HTMLAttributes<HTMLTableElement>) => (
  <div className="w-full overflow-x-auto">
    <table className={cn("w-full border-collapse", className)} {...props} />
  </div>
);

// ThHTMLAttributes y no HTMLAttributes: si no, `scope` no tipa y una tabla
// deja de decirle al lector de pantalla a que pertenece cada celda.
export const TableHead = ({
  className,
  scope = "col",
  ...props
}: React.ThHTMLAttributes<HTMLTableCellElement>) => (
  <th
    scope={scope}
    className={cn(
      "h-10 border-b border-border bg-secondary px-3 text-left text-sm font-medium text-muted-foreground first:pl-5 last:pr-5",
      className,
    )}
    {...props}
  />
);

export const TableRow = ({ className, ...props }: React.HTMLAttributes<HTMLTableRowElement>) => (
  <tr className={cn("transition-colors hover:bg-secondary", className)} {...props} />
);

export const TableCell = ({ className, ...props }: React.HTMLAttributes<HTMLTableCellElement>) => (
  <td
    className={cn("h-16 border-b border-border px-3 align-middle first:pl-5 last:pr-5", className)}
    {...props}
  />
);
