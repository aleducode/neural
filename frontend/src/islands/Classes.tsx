import { CalendarDays, Dumbbell } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ListSection } from "@/components/ui/list-section";
import { OccupancyBar } from "@/components/ui/occupancy-bar";
import { type Kpi } from "@/components/ui/stat-widget";
import { TableCell } from "@/components/ui/table";

type Klass = {
  no: number;
  id: number;
  name: string;
  typeId: number;
  kind: string;
  day: string;
  isToday: boolean;
  time: string;
  duration: string;
  places: number;
  bookings: number;
  sessions: number;
  occupancy: number | null;
};

type Props = { kpis: Kpi[]; rows: Klass[]; calendarUrl: string; classDetailUrl: string };

export default function Classes({ kpis, rows, calendarUrl, classDetailUrl }: Props) {
  return (
    <ListSection<Klass>
      title="Clases"
      description="Los horarios del gimnasio, su cupo y cuánto se piden."
      actions={
        <Button variant="outline" size="sm" asChild>
          <a href={calendarUrl}>
            <CalendarDays />
            Ver calendario
          </a>
        </Button>
      }
      kpis={kpis}
      tableIcon={<Dumbbell className="size-5" />}
      tableTitle="Listado de horarios"
      searchPlaceholder="Buscar por clase o día"
      haystack={(row) => `${row.name} ${row.kind} ${row.day} ${row.time}`}
      rows={rows}
      rowKey={(row) => row.id}
      noun="horarios"
      minWidth="1000px"
      columns={[
        { label: "No", className: "w-16" },
        { label: "Clase" },
        { label: "Tipo" },
        { label: "Día" },
        { label: "Horario" },
        { label: "Duración" },
        { label: "Cupos" },
        { label: "Reservas (30 días)" },
        { label: "Ocupación (30 días)" },
      ]}
      emptyIcon={<Dumbbell />}
      emptyTitle="Sin horarios"
      emptyDetail="Todavía no hay ninguna clase programada."
      renderRow={(row, index) => (
        <>
          <TableCell className="text-sm tabular-nums text-muted-foreground">{index}</TableCell>
          <TableCell>
            <a
              href={classDetailUrl.replace("/0/", `/${row.id}/`)}
              className="text-sm font-medium text-foreground no-underline hover:underline"
            >
              {row.name}
            </a>
          </TableCell>
          <TableCell>
            <Badge variant={row.kind === "Grupal" ? "info" : "neutral"}>{row.kind}</Badge>
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm text-foreground">
            {row.isToday ? (
              <Badge dot variant="success">
                {row.day} · hoy
              </Badge>
            ) : (
              row.day
            )}
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm tabular-nums text-foreground">
            {row.time}
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
            {row.duration}
          </TableCell>
          <TableCell className="text-sm tabular-nums text-foreground">{row.places}</TableCell>
          <TableCell className="text-sm tabular-nums text-foreground">{row.bookings}</TableCell>
          <TableCell>
            <OccupancyBar value={row.occupancy} />
          </TableCell>
        </>
      )}
    />
  );
}
