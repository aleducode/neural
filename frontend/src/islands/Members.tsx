import { BellPlus, Users } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ListSection } from "@/components/ui/list-section";
import { PersonCell } from "@/components/ui/person-cell";
import { type Kpi } from "@/components/ui/stat-widget";
import { TableCell } from "@/components/ui/table";

type Tone = "success" | "warning" | "error" | "neutral";

type Member = {
  no: number;
  id: number;
  name: string;
  initials: string;
  photo: string | null;
  email: string;
  phone: string;
  plan: string;
  status: string;
  tone: Tone;
  joined: string | null;
  expires: string | null;
  lastCheckin: string;
};

type Props = {
  kpis: Kpi[];
  rows: Member[];
  userDetailUrl: string;
  sendUrl: string;
};

export default function Members({ kpis, rows, userDetailUrl, sendUrl }: Props) {
  return (
    <ListSection<Member>
      title="Usuarios"
      description="Todos los usuarios del gimnasio, su membresía y su actividad."
      actions={
        <Button size="sm" asChild>
          <a href={sendUrl}>
            <BellPlus />
            Enviar notificación
          </a>
        </Button>
      }
      kpis={kpis}
      tableIcon={<Users className="size-5" />}
      tableTitle="Listado de usuarios"
      searchPlaceholder="Buscar por nombre, email o teléfono"
      haystack={(row) => `${row.name} ${row.email} ${row.phone} ${row.plan}`}
      rows={rows}
      rowKey={(row) => row.id}
      noun="usuarios"
      minWidth="920px"
      columns={[
        { label: "No", className: "w-16" },
        { label: "Usuario" },
        { label: "Plan" },
        { label: "Estado" },
        { label: "Registro" },
        { label: "Vence" },
        { label: "Último check-in" },
      ]}
      emptyIcon={<Users />}
      emptyTitle="Sin usuarios"
      emptyDetail="Todavía no hay nadie registrado como usuario."
      renderRow={(row, index) => (
        <>
          <TableCell className="text-sm tabular-nums text-muted-foreground">{index}</TableCell>
          <PersonCell
            name={row.name}
            initials={row.initials}
            photo={row.photo}
            sub={row.email}
            href={userDetailUrl.replace("/0/", `/${row.id}/`)}
          />
          <TableCell className="whitespace-nowrap text-sm text-foreground">{row.plan}</TableCell>
          <TableCell>
            <Badge dot variant={row.tone}>
              {row.status}
            </Badge>
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
            {row.joined ?? "—"}
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
            {row.expires ?? "—"}
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
            {row.lastCheckin}
          </TableCell>
        </>
      )}
    />
  );
}
