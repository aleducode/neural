import {
  BadgeCheck,
  CalendarClock,
  CalendarDays,
  CircleX,
  Clock3,
  Flame,
  Library,
  Layers,
  Percent,
  Receipt,
  ScanLine,
  Trophy,
  UserPlus,
  Users,
  Video,
  Wallet,
  type LucideIcon,
} from "lucide-react";

import { DeltaPill } from "@/components/ui/widget";

/**
 * Widget de métrica del diseño (nodo «Widget» #BnCaH):
 * caja de icono 36x36 radio 10 en verde con el glifo oscuro, etiqueta 14,
 * valor 18/600 y la píldora de variación alineada abajo a la derecha.
 */

// Las claves son las que manda metrics.py; el icono no viaja desde el servidor.
const ICONS: Record<string, LucideIcon> = {
  users: Users,
  wallet: Wallet,
  "badge-check": BadgeCheck,
  "scan-line": ScanLine,
  "calendar-clock": CalendarClock,
  "calendar-days": CalendarDays,
  "user-plus": UserPlus,
  "circle-x": CircleX,
  flame: Flame,
  percent: Percent,
  receipt: Receipt,
  layers: Layers,
  trophy: Trophy,
  video: Video,
  library: Library,
  clock: Clock3,
};

export type Kpi = {
  key: string;
  icon: string;
  label: string;
  value: string;
  delta: number | null;
  basis: string;
};

export function StatWidget({ icon, label, value, delta, basis }: Kpi) {
  const Icon = ICONS[icon] ?? Users;

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-border bg-card px-4 pb-3.5 pt-4 shadow-widget">
      <span className="flex size-9 items-center justify-center rounded-[10px] bg-primary text-primary-foreground shadow-icon-box">
        <Icon className="size-5" strokeWidth={1.67} aria-hidden="true" />
      </span>

      <div className="flex items-end justify-between gap-3">
        <div className="min-w-0">
          <div className="truncate text-sm text-muted-foreground">{label}</div>
          <div className="mt-1 truncate text-lg font-semibold tabular-nums text-foreground">
            {value}
          </div>
        </div>
        <DeltaPill delta={delta} basis={basis} />
      </div>
    </div>
  );
}
