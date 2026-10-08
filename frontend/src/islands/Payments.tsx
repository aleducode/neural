import { CircleAlert, CreditCard, Phone } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { ListSection } from "@/components/ui/list-section";
import { PersonCell } from "@/components/ui/person-cell";
import { MemberAvatar } from "@/components/ui/member-avatar";
import { Widget, WidgetHeader } from "@/components/ui/widget";
import { type Kpi } from "@/components/ui/stat-widget";
import { TableCell } from "@/components/ui/table";

type Payment = {
  id: number;
  userId: number;
  reference: string;
  name: string;
  initials: string;
  photo: string | null;
  plan: string;
  method: string;
  amount: string;
  date: string;
  paid: boolean;
  status: string;
};

type Attempt = {
  id: number;
  name: string;
  initials: string;
  photo: string | null;
  email: string;
  phone: string;
  plan: string;
  attempts: number;
  last: string;
  solved: boolean;
};

type Props = {
  kpis: Kpi[];
  rows: Payment[];
  userDetailUrl: string;
  attempts: Attempt[];
  attemptsTotal: number;
  sinceNote: string;
};

export default function Payments({
  kpis,
  rows,
  userDetailUrl,
  attempts,
  attemptsTotal,
  sinceNote,
}: Props) {
  const sinResolver = attempts.filter((a) => !a.solved);

  return (
    <>
    <ListSection<Payment>
      title="Pagos"
      description="La plata que entró este mes, por dónde entró, y quién quiso pagar y no pudo."
      kpis={kpis}
      tableIcon={<CreditCard className="size-5" />}
      tableTitle="Pagos recibidos"
      searchPlaceholder="Buscar por usuario, referencia o plan"
      haystack={(row) => `${row.reference} ${row.name} ${row.plan} ${row.amount}`}
      rows={rows}
      rowKey={(row) => row.id}
      noun="pagos"
      minWidth="760px"
      columns={[
        { label: "Referencia" },
        { label: "Usuario" },
        { label: "Monto" },
        { label: "Medio" },
        { label: "Fecha" },
        { label: "Estado" },
      ]}
      emptyIcon={<CreditCard />}
      emptyTitle="Sin pagos recibidos"
      emptyDetail="Cuando recepción active un plan o alguien pague en línea, aparece acá."
      footnote={sinceNote}
      renderRow={(row) => (
        <>
          <TableCell className="whitespace-nowrap text-sm font-medium tabular-nums text-foreground">
            {row.reference}
          </TableCell>
          <PersonCell
            name={row.name}
            initials={row.initials}
            photo={row.photo}
            sub={row.plan}
            href={userDetailUrl.replace("/0/", `/${row.userId}/`)}
          />
          <TableCell className="whitespace-nowrap text-sm font-medium tabular-nums text-foreground">
            {row.amount}
          </TableCell>
          <TableCell className="whitespace-nowrap">
            <Badge variant={row.method === "Recepción" ? "neutral" : "info"}>
              {row.method}
            </Badge>
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
            {row.date}
          </TableCell>
          <TableCell>
            <Badge dot variant={row.paid ? "success" : "neutral"}>
              {row.status}
            </Badge>
          </TableCell>
        </>
      )}
    />

    {attempts.length > 0 && (
      <Widget>
        <WidgetHeader
          icon={<CircleAlert className="size-5" />}
          title="Quisieron pagar y no pudieron"
        >
          <span className="text-xs text-muted-foreground">
            {attemptsTotal.toLocaleString("es-CO")} intentos en total
          </span>
        </WidgetHeader>

        <p className="border-b border-border px-5 py-3 text-xs text-muted-foreground">
          La app genera la referencia pero todavía no abre la pasarela, así que
          el socio queda a mitad de camino. Los de arriba no tienen membresía:
          esos no están entrenando. Los de abajo se cansaron y pagaron en
          recepción.
        </p>

        <ul className="flex flex-col divide-y divide-border">
          {attempts.map((a) => (
            <li key={a.id} className="flex flex-wrap items-center gap-3 px-5 py-3">
              <MemberAvatar name={a.name} initials={a.initials} photo={a.photo} />
              <span className="min-w-0 flex-1">
                <a
                  href={userDetailUrl.replace("/0/", `/${a.id}/`)}
                  className="block truncate text-sm font-medium text-foreground no-underline"
                >
                  {a.name}
                </a>
                <span className="block truncate text-xs text-muted-foreground">
                  {a.plan} · {a.attempts} {a.attempts === 1 ? "intento" : "intentos"} ·
                  {" "}último el {a.last}
                </span>
              </span>

              {a.phone && (
                <a
                  href={`https://wa.me/${a.phone.replace(/[^0-9]/g, "")}`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex h-8 items-center gap-1.5 rounded-md border border-border px-3 text-xs font-medium text-foreground no-underline hover:bg-secondary"
                >
                  <Phone className="size-3.5" aria-hidden="true" />
                  Escribirle
                </a>
              )}

              <Badge dot variant={a.solved ? "success" : "warning"}>
                {a.solved ? "Ya tiene membresía" : "Sin membresía"}
              </Badge>
            </li>
          ))}
        </ul>

        {sinResolver.length > 0 && (
          <p className="border-t border-border bg-secondary px-5 py-3 text-xs text-muted-foreground">
            <span className="font-medium text-foreground">
              {sinResolver.length} {sinResolver.length === 1 ? "persona" : "personas"}
            </span>{" "}
            {sinResolver.length === 1 ? "quiso" : "quisieron"} pagar, no{" "}
            {sinResolver.length === 1 ? "pudo" : "pudieron"} y hoy no{" "}
            {sinResolver.length === 1 ? "entrena" : "entrenan"}.
          </p>
        )}
      </Widget>
    )}
    </>
  );
}
