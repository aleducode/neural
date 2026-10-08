import { CreditCard } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { ListSection } from "@/components/ui/list-section";
import { PersonCell } from "@/components/ui/person-cell";
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

type Props = { kpis: Kpi[]; rows: Payment[]; userDetailUrl: string };

export default function Payments({ kpis, rows, userDetailUrl }: Props) {
  return (
    <ListSection<Payment>
      title="Pagos"
      description="Las referencias de pago que pasaron por Bold y en qué quedaron."
      kpis={kpis}
      tableIcon={<CreditCard className="size-5" />}
      tableTitle="Listado de pagos"
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
      emptyTitle="Sin pagos registrados"
      emptyDetail="Todavía no hay ninguna referencia de pago en el sistema."
      footnote="«Recepción» son los cobros registrados al activar un plan en el panel; «En línea», los de Bold."
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
  );
}
