import * as React from "react";
import { cn } from "@/lib/utils";

export const Table = ({ className, ...props }: React.HTMLAttributes<HTMLTableElement>) => (
  <div className="w-full overflow-x-auto">
    <table className={cn("w-full border-collapse", className)} {...props} />
  </div>
);

export const TableHead = ({ className, ...props }: React.HTMLAttributes<HTMLTableCellElement>) => (
  <th
    className={cn(
      "border-b border-border bg-secondary px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground first:pl-6 last:pr-6",
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
    className={cn("border-b border-border px-4 py-4 align-middle first:pl-6 last:pr-6", className)}
    {...props}
  />
);
