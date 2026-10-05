import { CalendarCheck, CalendarDays } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ListSection } from "@/components/ui/list-section";
import { PersonCell } from "@/components/ui/person-cell";
import { type Kpi } from "@/components/ui/stat-widget";
import { TableCell } from "@/components/ui/table";

type Tone = "success" | "warning" | "error" | "neutral";

type Booking = {
  id: number;
  userId: number;
  reference: string;
  name: string;
  initials: string;
  photo: string | null;
  email: string;
  klass: string;
  date: string | null;
  isToday: boolean;
  time: string;
  status: string;
  tone: Tone;
};

type Props = {
  kpis: Kpi[];
  rows: Booking[];
  period: string;
  userDetailUrl: string;
  calendarUrl: string;
};

export default function Bookings({ kpis, rows, period, userDetailUrl, calendarUrl }: Props) {
  return (
    <ListSection<Booking>
      title="Reservas"
      description="Quién reservó qué clase, cuándo y en qué estado quedó."
      actions={
        <Button variant="outline" size="sm" asChild>
          <a href={calendarUrl}>
            <CalendarDays />
            Ver calendario
          </a>
        </Button>
      }
      kpis={kpis}
      tableIcon={<CalendarCheck className="size-5" />}
      tableTitle="Listado de reservas"
      searchPlaceholder="Buscar por usuario, clase o referencia"
      haystack={(row) => `${row.reference} ${row.name} ${row.email} ${row.klass}`}
      rows={rows}
      rowKey={(row) => row.id}
      noun="reservas"
      minWidth="880px"
      columns={[
        { label: "Referencia" },
        { label: "Usuario" },
        { label: "Clase" },
        { label: "Fecha" },
        { label: "Horario" },
        { label: "Estado" },
      ]}
      emptyIcon={<CalendarCheck />}
      emptyTitle="Sin reservas en el periodo"
      emptyDetail="Nadie reservó una clase dentro de esta ventana de fechas."
      footnote={`La tabla muestra la ventana ${period}. Fuera de ahí hay historia que no se carga en esta pantalla.`}
      renderRow={(row) => (
        <>
          <TableCell className="whitespace-nowrap text-sm font-medium tabular-nums text-foreground">
            {row.reference}
          </TableCell>
          <PersonCell
            name={row.name}
            initials={row.initials}
            photo={row.photo}
            sub={row.email}
            href={userDetailUrl.replace("/0/", `/${row.userId}/`)}
          />
          <TableCell className="text-sm text-foreground">{row.klass}</TableCell>
          <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
            {row.isToday ? (
              <Badge dot variant="success">
                Hoy
              </Badge>
            ) : (
              (row.date ?? "—")
            )}
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm tabular-nums text-foreground">
            {row.time}
          </TableCell>
          <TableCell>
            <Badge dot variant={row.tone}>
              {row.status}
            </Badge>
          </TableCell>
        </>
      )}
    />
  );
}
