import { CalendarDays, ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { cn } from "@/lib/utils";

/**
 * «23. Calendar View - Month».
 *
 * Rejilla de semanas completas: celdas de 128, numero del dia a la derecha en
 * 14, y un chip por clase con una barrita de color a la izquierda. El verde es
 * una clase con cupo; el ambar, una llena. El chip tambien lo dice con texto,
 * asi que el color no es la unica pista.
 */

type Klass = {
  id: number;
  name: string;
  time: string | null;
  taken: number;
  places: number;
  full: boolean;
};

type Day = {
  date: string;
  day: number;
  inMonth: boolean;
  isToday: boolean;
  classes: Klass[];
};

type Month = { year: number; month: number };

type Props = {
  title: string;
  weekdays: string[];
  days: Day[];
  prev: Month;
  next: Month;
  today: Month;
  calendarUrl: string;
};

const MAX_CHIPS = 3;

export default function CalendarMonth({
  title,
  weekdays,
  days,
  prev,
  next,
  today,
  calendarUrl,
}: Props) {
  const url = (m: Month) => `${calendarUrl}?year=${m.year}&month=${m.month}`;
  const totalClases = days.filter((d) => d.inMonth).reduce((n, d) => n + d.classes.length, 0);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Calendario"
        description={`${totalClases} clases programadas en ${title.toLowerCase()}.`}
      >
        <Button variant="outline" size="sm" asChild>
          <a href={url(today)}>
            <CalendarDays />
            Hoy
          </a>
        </Button>
      </PageHeader>

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" className="size-8" asChild>
            <a href={url(prev)} aria-label="Mes anterior">
              <ChevronLeft />
            </a>
          </Button>
          <Button variant="outline" size="icon" className="size-8" asChild>
            <a href={url(next)} aria-label="Mes siguiente">
              <ChevronRight />
            </a>
          </Button>
          <h2 className="text-base font-medium text-foreground">{title}</h2>
        </div>

        <ul className="flex items-center gap-4 text-xs text-muted-foreground">
          <li className="flex items-center gap-1.5">
            <span className="h-3 w-0.5 rounded-full bg-primary" aria-hidden="true" />
            Con cupo
          </li>
          <li className="flex items-center gap-1.5">
            <span
              className="h-3 w-0.5 rounded-full bg-[hsl(var(--warning))]"
              aria-hidden="true"
            />
            Llena
          </li>
        </ul>
      </div>

      <div className="overflow-x-auto">
        <div className="min-w-[840px] overflow-hidden rounded-lg border border-border bg-card shadow-widget">
          <div className="grid grid-cols-7">
            {weekdays.map((weekday) => (
              <div
                key={weekday}
                className="flex h-10 items-center justify-center border-b border-border text-sm font-medium text-faint"
              >
                {weekday}
              </div>
            ))}

            {days.map((day) => (
              <div
                key={day.date}
                className={cn(
                  "flex h-32 flex-col gap-2 border-b border-r border-border p-3 last:border-r-0",
                  day.inMonth ? "bg-card" : "bg-secondary",
                )}
              >
                <div className="flex items-center justify-end">
                  <span
                    className={cn(
                      "text-sm tabular-nums",
                      day.isToday &&
                        "flex size-6 items-center justify-center rounded-full bg-primary font-medium text-primary-foreground",
                      !day.isToday && day.inMonth && "text-foreground",
                      !day.isToday && !day.inMonth && "text-faint",
                    )}
                  >
                    {day.day}
                  </span>
                </div>

                <div className="flex min-h-0 flex-1 flex-col gap-1 overflow-hidden">
                  {day.classes.slice(0, MAX_CHIPS).map((klass) => (
                    <span
                      key={klass.id}
                      title={`${klass.name} · ${klass.time ?? ""} · ${klass.taken}/${klass.places} cupos`}
                      className={cn(
                        "relative flex h-6 items-center gap-1 overflow-hidden rounded-sm px-2 text-[0.625rem] text-foreground",
                        klass.full ? "bg-warning-soft" : "bg-positive-soft",
                      )}
                    >
                      <span
                        className={cn(
                          "absolute left-0 h-3.5 w-0.5 rounded-full",
                          klass.full ? "bg-[hsl(var(--warning))]" : "bg-primary",
                        )}
                        aria-hidden="true"
                      />
                      <span className="truncate pl-1">
                        {klass.time} {klass.name}
                      </span>
                      <span className="ml-auto shrink-0 tabular-nums">
                        {klass.taken}/{klass.places}
                      </span>
                    </span>
                  ))}

                  {day.classes.length > MAX_CHIPS && (
                    <span className="text-[0.625rem] font-medium text-foreground">
                      +{day.classes.length - MAX_CHIPS} más
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
