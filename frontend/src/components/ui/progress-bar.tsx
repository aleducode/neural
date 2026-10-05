import { cn } from "@/lib/utils";

/**
 * Barra de progreso de consumo. El color va en la barra y el número en tinta;
 * el verde lleno es «terminado» y lo dice también el texto al lado.
 */
export function ProgressBar({
  percent,
  done,
  className,
  width = "w-24",
}: {
  percent: number;
  done?: boolean;
  className?: string;
  width?: string;
}) {
  return (
    <span className={cn("flex items-center gap-2", className)}>
      <span className={cn("h-1.5 flex-none overflow-hidden rounded-full bg-accent", width)}>
        <span
          className={cn(
            "block h-full rounded-full",
            done ? "bg-positive" : percent > 0 ? "bg-primary" : "bg-transparent",
          )}
          style={{ width: `${Math.max(Math.min(percent, 100), percent > 0 ? 3 : 0)}%` }}
        />
      </span>
      <span className="text-xs tabular-nums text-muted-foreground">{percent}%</span>
    </span>
  );
}
