import { Layers, Pencil, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Field, TextField } from "@/components/ui/detail";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
  priceRaw: number;
  durationDays: number;
  sessions: number;
};

type Props = {
  kpis: Kpi[];
  rows: Plan[];
  csrfToken: string;
  errors?: Record<string, { message: string }[]>;
  errorId?: number | null;
};

export default function Plans({ kpis, rows, csrfToken, errors, errorId }: Props) {
  // Si el formulario rebota, se reabre donde salio: con el dialogo cerrado el
  // error viaja en las props y no lo ve nadie.
  const [editando, setEditando] = useState<Plan | null>(
    errors && errorId ? rows.find((r) => r.id === errorId) ?? null : null,
  );
  const [creando, setCreando] = useState(Boolean(errors && !errorId));
  const err = (campo: string) => errors?.[campo]?.[0]?.message;

  return (
    <>
    <ListSection<Plan>
      title="Planes"
      description="El catálogo de membresías, qué cuesta cada una y cuánta gente la tiene."
      actions={
        <Button size="sm" onClick={() => setCreando(true)}>
          <Plus />
          Nuevo plan
        </Button>
      }
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
        { label: "", className: "w-24" },
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
          <TableCell>
            <span className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setEditando(row)}
                aria-label={`Editar ${row.name}`}
                className="flex size-8 items-center justify-center rounded-md border border-border text-foreground hover:bg-secondary"
              >
                <Pencil className="size-4" />
              </button>
              {/* Borrar va por formulario: el servidor decide si se puede,
                  porque un plan en uso arrastra cosas en cascada. */}
              <form method="post" onSubmit={(e) => {
                if (!confirm(`¿Borrar el plan «${row.name}»?`)) e.preventDefault();
              }}>
                <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
                <input type="hidden" name="action" value="delete" />
                <input type="hidden" name="id" value={row.id} />
                <button
                  type="submit"
                  aria-label={`Borrar ${row.name}`}
                  className="flex size-8 items-center justify-center rounded-md border border-border text-destructive hover:bg-secondary"
                >
                  <Trash2 className="size-4" />
                </button>
              </form>
            </span>
          </TableCell>
        </>
      )}
    />

    <FormularioPlan
      abierto={creando}
      cerrar={() => setCreando(false)}
      plan={null}
      csrfToken={csrfToken}
      err={err}
    />
    <FormularioPlan
      abierto={editando !== null}
      cerrar={() => setEditando(null)}
      plan={editando}
      csrfToken={csrfToken}
      err={err}
    />
    </>
  );
}

/**
 * Alta y edición de un plan.
 *
 * La duración es el campo que más importa: de ahí sale la fecha de
 * vencimiento cuando recepción activa el plan, que antes se escribía a mano y
 * salía mal en una de cada cuatro membresías.
 */
function FormularioPlan({
  abierto,
  cerrar,
  plan,
  csrfToken,
  err,
}: {
  abierto: boolean;
  cerrar: () => void;
  plan: Plan | null;
  csrfToken: string;
  err: (campo: string) => string | undefined;
}) {
  return (
    <Dialog open={abierto} onOpenChange={(v) => !v && cerrar()}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>{plan ? `Editar «${plan.name}»` : "Nuevo plan"}</DialogTitle>
          <DialogDescription>
            La duración define hasta cuándo vale el plan cuando se lo activás a
            alguien. No hace falta escribir la fecha de vencimiento nunca más.
          </DialogDescription>
        </DialogHeader>
        <form method="post" className="flex flex-col gap-4">
          <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
          {plan && <input type="hidden" name="id" value={plan.id} />}

          <TextField
            name="name"
            label="Nombre"
            defaultValue={plan?.name ?? ""}
            error={err("name")}
            required
          />
          <Field name="description" label="Descripción" error={err("description")}>
            <textarea
              id="description"
              name="description"
              rows={2}
              defaultValue={plan?.description ?? ""}
              className="rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </Field>

          <div className="flex flex-wrap gap-4">
            <TextField
              name="price"
              label="Precio"
              type="number"
              min={0}
              step={1000}
              defaultValue={plan?.priceRaw ?? 0}
              error={err("price")}
            />
            <TextField
              name="duration"
              label="Duración (días)"
              type="number"
              min={1}
              defaultValue={plan?.durationDays ?? 30}
              hint="30 mensualidad · 90 trimestre · 180 semestre"
              error={err("duration")}
            />
            <TextField
              name="sessions"
              label="Sesiones"
              type="number"
              min={0}
              defaultValue={plan?.sessions ?? 0}
              hint="0 = por tiempo. Mayor que 0 = tiquetera."
              error={err("sessions")}
            />
          </div>

          <Button type="submit" size="sm" className="self-end">
            {plan ? "Guardar cambios" : "Crear plan"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
