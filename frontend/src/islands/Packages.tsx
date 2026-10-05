import { Library, Plus, Users } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Field, SelectField, TextField } from "@/components/ui/detail";
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
import { VideoThumb } from "@/components/ui/video-thumb";

type Row = {
  no: number;
  id: number;
  name: string;
  description: string;
  cover: string | null;
  kind: string;
  kindValue: string;
  videos: number;
  reach: number;
  targets: string[];
  published: boolean;
};

type Props = {
  kpis: Kpi[];
  rows: Row[];
  packageDetailUrl: string;
  csrfToken: string;
  kindChoices: { value: string; label: string }[];
  errors?: Record<string, { message: string }[]>;
};

export default function Packages({
  kpis,
  rows,
  packageDetailUrl,
  csrfToken,
  kindChoices,
  errors,
}: Props) {
  // Si el formulario volvio con errores, el dialogo tiene que abrirse solo:
  // si no, el usuario ve la lista intacta y no se entera de que fallo.
  const [creando, setCreando] = useState(Boolean(errors));
  const err = (campo: string) => errors?.[campo]?.[0]?.message;

  return (
    <>
    <ListSection<Row>
      title="Paquetes"
      description="Listas ordenadas de videos que se asignan a usuarios o a planes."
      actions={
        <Button size="sm" onClick={() => setCreando(true)}>
          <Plus />
          Nuevo paquete
        </Button>
      }
      kpis={kpis}
      tableIcon={<Library className="size-5" />}
      tableTitle="Paquetes de videos"
      searchPlaceholder="Buscar por nombre del paquete"
      haystack={(row) => `${row.name} ${row.description} ${row.targets.join(" ")}`}
      rows={rows}
      rowKey={(row) => row.id}
      noun="paquetes"
      minWidth="900px"
      columns={[
        { label: "Paquete" },
        { label: "Modalidad" },
        { label: "Videos" },
        { label: "Asignado a" },
        { label: "Alcance" },
        { label: "Estado" },
      ]}
      emptyIcon={<Library />}
      emptyTitle="Sin paquetes"
      emptyDetail="Creá uno para empezar a armar rutinas con los videos de la biblioteca."
      renderRow={(row) => (
        <>
          <TableCell>
            <a
              href={packageDetailUrl.replace("/0/", `/${row.id}/`)}
              className="flex items-center gap-3 no-underline"
            >
              <VideoThumb poster={row.cover} name={row.name} />
              <span className="min-w-0">
                <span className="block truncate text-sm font-medium text-foreground">
                  {row.name}
                </span>
                <span className="block max-w-xs truncate text-xs text-muted-foreground">
                  {row.description || "Sin descripción"}
                </span>
              </span>
            </a>
          </TableCell>
          <TableCell>
            <Badge variant={row.kindValue === "individual" ? "warning" : "info"}>
              {row.kind}
            </Badge>
          </TableCell>
          <TableCell className="text-sm tabular-nums text-foreground">{row.videos}</TableCell>
          <TableCell>
            {row.targets.length === 0 ? (
              <span className="text-xs text-destructive">Sin asignar</span>
            ) : (
              <span className="block max-w-xs truncate text-sm text-muted-foreground">
                {row.targets.join(" · ")}
              </span>
            )}
          </TableCell>
          <TableCell>
            <span className="flex items-center gap-1.5 text-sm tabular-nums text-foreground">
              <Users className="size-4 text-faint" aria-hidden="true" />
              {row.reach}
            </span>
          </TableCell>
          <TableCell>
            <Badge dot variant={row.published ? "success" : "neutral"}>
              {row.published ? "Publicado" : "Borrador"}
            </Badge>
          </TableCell>
        </>
      )}
    />

    {/* El backend ya aceptaba este POST; lo que faltaba era por donde hacerlo. */}
    <Dialog open={creando} onOpenChange={setCreando}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Nuevo paquete</DialogTitle>
          <DialogDescription>
            Al crearlo entrás al armador, donde le agregás los videos y elegís a quién
            se lo asignás.
          </DialogDescription>
        </DialogHeader>
        <form method="post" className="flex flex-col gap-4">
          <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
          <TextField name="name" label="Nombre" error={err("name")} required />
          <Field name="description" label="Descripción" error={err("description")}>
            <textarea
              id="description"
              name="description"
              rows={2}
              className="rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </Field>
          <SelectField
            name="kind"
            label="Modalidad"
            options={kindChoices}
            error={err("kind")}
          />
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <input
              type="checkbox"
              name="is_published"
              className="size-4 rounded-sm border-border accent-[hsl(var(--primary))]"
            />
            Publicado
          </label>
          <p className="text-xs text-muted-foreground">
            Un paquete sin publicar no le llega a nadie, aunque esté asignado.
          </p>
          <Button type="submit" size="sm" className="self-end">
            Crear y armar
          </Button>
        </form>
      </DialogContent>
    </Dialog>
    </>
  );
}
