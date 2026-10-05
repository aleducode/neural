import { Layers } from "lucide-react";

import { ListSection } from "@/components/ui/list-section";
import { type Kpi } from "@/components/ui/stat-widget";
import { TableCell } from "@/components/ui/table";

type Plan = {
  id: number;
  name: string;
  description: string;
  price: string;
  duration: string;
  perMonth: string;
  members: number;
  share: number;
  revenue: string;
};

type Props = { kpis: Kpi[]; rows: Plan[] };

export default function Plans({ kpis, rows }: Props) {
  return (
    <ListSection<Plan>
      title="Planes"
      description="El catálogo de membresías, qué cuesta cada una y cuánta gente la tiene."
      kpis={kpis}
      tableIcon={<Layers className="size-5" />}
      tableTitle="Catálogo de planes"
      searchPlaceholder="Buscar por nombre del plan"
      haystack={(row) => `${row.name} ${row.description}`}
      rows={rows}
      rowKey={(row) => row.id}
      noun="planes"
      minWidth="820px"
      columns={[
        { label: "Plan" },
        { label: "Precio" },
        { label: "Duración" },
        { label: "Equivale al mes" },
        { label: "Usuarios" },
        { label: "Recaudado (12 meses)" },
      ]}
      emptyIcon={<Layers />}
      emptyTitle="Sin planes cargados"
      emptyDetail="No hay ningún NeuralPlan creado todavía."
      renderRow={(row) => (
        <>
          <TableCell>
            <span className="block text-sm font-medium text-foreground">{row.name}</span>
            <span className="block max-w-xs truncate text-xs text-muted-foreground">
              {row.description}
            </span>
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm font-medium tabular-nums text-foreground">
            {row.price}
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
            {row.duration}
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm tabular-nums text-muted-foreground">
            {row.perMonth}
          </TableCell>
          <TableCell>
            {/* La barra lleva el color; el numero y el porcentaje van en tinta. */}
            <span className="flex items-center gap-2">
              <span className="h-1.5 w-20 overflow-hidden rounded-full bg-secondary">
                <span
                  className="block h-full rounded-full bg-primary"
                  style={{ width: `${Math.max(row.share, 2)}%` }}
                />
              </span>
              <span className="text-sm tabular-nums text-foreground">{row.members}</span>
              <span className="text-xs tabular-nums text-muted-foreground">{row.share}%</span>
            </span>
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm tabular-nums text-foreground">
            {row.revenue}
          </TableCell>
        </>
      )}
    />
  );
}
