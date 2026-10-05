import { cn } from "@/lib/utils";

/**
 * Barra de ocupación del diseño: pista de 96x6 y el porcentaje al lado.
 *
 * El color va en la barra y el número en tinta, nunca al revés. El ámbar marca
 * "casi llena", pero el porcentaje lo dice igual: el color no es la única pista.
 */
export function OccupancyBar({
  value,
  className,
}: {
  value: number | null;
  className?: string;
}) {
  if (value === null || value === undefined) {
    return <span className="text-sm text-muted-foreground">Sin sesiones</span>;
  }

  const pct = Math.min(Math.max(value, 0), 100);
  return (
    <span className={cn("flex items-center gap-2", className)}>
      <span className="h-1.5 w-24 flex-none overflow-hidden rounded-full bg-accent">
        <span
          className={cn(
            "block h-full rounded-full",
            pct >= 85 ? "bg-[hsl(var(--warning))]" : "bg-primary",
          )}
          style={{ width: `${Math.max(pct, 2)}%` }}
        />
      </span>
      <span className="text-sm tabular-nums text-foreground">{value}%</span>
    </span>
  );
}
