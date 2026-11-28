import { Link2, Pencil, Plus, RotateCw, Video as VideoIcon, X } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DropZone, UploadRow, useUploadQueue } from "@/components/ui/chunked-upload";
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
  source: string;
  sourceLabel: string;
  poster: string | null;
  playback: string | null;
  duration: string;
  seconds: number;
  posterSecond: number;
  level: string;
  type: string | null;
  published: boolean;
  levelValue: string;
  typeId: number | null;
  packages: number;
  views: number;
};

type Choice = { value: string; label: string };

type Props = {
  kpis: Kpi[];
  rows: Row[];
  uploadUrl: string;
  csrfToken: string;
  levelChoices: Choice[];
  trainingTypes: Choice[];
  errors?: Record<string, { message: string }[]>;
  errorId?: number | null;
};

export default function Videos({
  kpis,
  rows,
  uploadUrl,
  csrfToken,
  levelChoices,
  trainingTypes,
  errors,
  errorId,
}: Props) {
  // Si el formulario volvio con errores, hay que reabrir el dialogo del que
  // salio: si no, el error viaja en las props y no lo ve nadie.
  const [abierto, setAbierto] = useState<"upload" | "link" | null>(
    errors && !errorId ? "link" : null,
  );
  const [editando, setEditando] = useState<Row | null>(
    errors && errorId ? rows.find((r) => r.id === errorId) ?? null : null,
  );
  const err = (campo: string) => errors?.[campo]?.[0]?.message;
  const cola = useUploadQueue();

  return (
    <>
    <ListSection<Row>
      title="Videos"
      description="La biblioteca de contenido que los usuarios ven en la app."
      actions={
        <>
          <Button variant="outline" size="sm" onClick={() => setAbierto("link")}>
            <Link2 />
            Agregar enlace
          </Button>
          <Button size="sm" onClick={() => setAbierto("upload")}>
            <Plus />
            Subir videos
          </Button>
        </>
      }
      kpis={kpis}
      tableIcon={<VideoIcon className="size-5" />}
      tableTitle="Biblioteca"
      searchPlaceholder="Buscar por nombre o tipo"
      haystack={(row) => `${row.name} ${row.description} ${row.type ?? ""} ${row.level}`}
      rows={rows}
      rowKey={(row) => row.id}
      noun="videos"
      minWidth="980px"
      columns={[
        { label: "Video" },
        { label: "Fuente" },
        { label: "Duración" },
        { label: "Nivel" },
        { label: "En paquetes" },
        { label: "Vistas" },
        { label: "Estado" },
        { label: "", className: "w-20" },
      ]}
      emptyIcon={<VideoIcon />}
      emptyTitle="Biblioteca vacía"
      emptyDetail="Todavía no hay ningún video cargado."
      renderRow={(row) => (
        <>
          <TableCell>
            <span className="flex items-center gap-3">
              <VideoThumb poster={row.poster} name={row.name} />
              <span className="min-w-0">
                <span className="block truncate text-sm font-medium text-foreground">
                  {row.name}
                </span>
                <span className="block max-w-xs truncate text-xs text-muted-foreground">
                  {row.type ?? "Sin tipo de entrenamiento"}
                </span>
              </span>
            </span>
          </TableCell>
          <TableCell>
            <Badge variant={row.source === "url" ? "info" : "neutral"}>
              {row.sourceLabel}
            </Badge>
            {/* Un video sin fuente no se puede reproducir: la fila lo dice. */}
            {!row.playback && (
              <span className="ml-2 text-xs text-destructive">sin fuente</span>
            )}
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm tabular-nums text-muted-foreground">
            {row.duration}
          </TableCell>
          <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
            {row.level}
          </TableCell>
          <TableCell className="text-sm tabular-nums text-foreground">
            {row.packages}
          </TableCell>
          <TableCell className="text-sm tabular-nums text-foreground">{row.views}</TableCell>
          <TableCell>
            <Badge dot variant={row.published ? "success" : "neutral"}>
              {row.published ? "Publicado" : "Borrador"}
            </Badge>
          </TableCell>
          <TableCell className="text-right">
            <Button variant="ghost" size="icon" className="size-8" onClick={() => setEditando(row)} aria-label={`Editar ${row.name}`}>
              <Pencil />
            </Button>
          </TableCell>
        </>
      )}
    />

    {/* Subir y pegar un enlace son dos gestos distintos: dos diálogos, cada
        uno con un solo trabajo, en vez de un formulario con un selector. */}
    <Dialog open={abierto === "upload"} onOpenChange={(v) => !v && setAbierto(null)}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Subir videos</DialogTitle>
          <DialogDescription>
            Elegí uno o varios. Se suben en segundo plano mientras seguís trabajando, y
            cada uno queda en la biblioteca como borrador para ponerle nombre y nivel.
          </DialogDescription>
        </DialogHeader>
        <DropZone
          onFiles={(files) => {
            if (cola.add(files) > 0) setAbierto(null);
          }}
        />
      </DialogContent>
    </Dialog>

    {/* La cola vive fuera del diálogo: cerrarlo no corta ninguna subida. */}
    {cola.items.length > 0 && (
      <section
        aria-label="Subidas de video"
        className="fixed inset-x-4 bottom-4 z-40 flex max-h-[70vh] flex-col rounded-lg border border-border bg-card shadow-lg sm:left-auto sm:right-6 sm:w-96"
      >
        <header className="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
          <p className="text-sm font-medium text-foreground">
            {cola.busy
              ? `Subiendo videos · ${cola.done} de ${cola.items.length}`
              : cola.failed
                ? `${cola.done} subidos, ${cola.failed} con error`
                : `${cola.done} ${cola.done === 1 ? "video subido" : "videos subidos"}`}
          </p>
          <span className="flex items-center gap-1">
            <Button type="button" variant="ghost" size="sm" onClick={() => setAbierto("upload")}>
              <Plus />
              Más
            </Button>
            {!cola.busy && (
              <Button type="button" variant="ghost" size="icon" className="size-8" aria-label="Cerrar" onClick={cola.clear}>
                <X />
              </Button>
            )}
          </span>
        </header>
        <ul className="divide-y divide-border overflow-y-auto px-4">
          {cola.items.map((item) => (
            <UploadRow
              key={item.key}
              uploadUrl={uploadUrl}
              csrfToken={csrfToken}
              item={item}
              active={cola.active.has(item.key)}
              onStatus={(status) => cola.setStatus(item.key, status)}
              onRemove={() => cola.remove(item.key)}
            />
          ))}
        </ul>
        {!cola.busy && cola.done > 0 && (
          <footer className="border-t border-border px-4 py-3">
            <Button type="button" size="sm" className="w-full" onClick={() => window.location.reload()}>
              <RotateCw />
              Ver los videos nuevos en la biblioteca
            </Button>
          </footer>
        )}
      </section>
    )}

    {/* Editar el video: es lo que saca un borrador recién subido del limbo. */}
    <Dialog open={editando !== null} onOpenChange={(v) => !v && setEditando(null)}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Editar video</DialogTitle>
          <DialogDescription>
            Un video en borrador no se puede agregar a un paquete hasta publicarlo.
          </DialogDescription>
        </DialogHeader>
        {editando && (
          <form method="post" className="flex flex-col gap-4">
            <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
            <input type="hidden" name="id" value={editando.id} />
            <input type="hidden" name="source" value={editando.source} />
            {editando.source === "url" && (
              <input type="hidden" name="url" value={editando.playback ?? ""} />
            )}
            <TextField name="name" label="Nombre" defaultValue={editando.name} error={err("name")} required />
            <Field name="description" label="Descripción" error={err("description")}>
              <textarea
                id="description"
                name="description"
                rows={2}
                defaultValue={editando.description}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </Field>
            <div className="flex flex-wrap gap-4">
              <TextField
                name="duration_seconds"
                label="Duración (segundos)"
                type="number"
                min={0}
                defaultValue={editando.seconds}
                hint="Si subiste el archivo, ponela a mano hasta que Cloudflare la informe."
                error={err("duration_seconds")}
              />
              <TextField
                name="poster_second"
                label="Miniatura (segundo)"
                type="number"
                min={1}
                defaultValue={editando.posterSecond}
                hint="En el segundo 1 casi nadie empezó: elegí uno donde se vea el movimiento."
                error={err("poster_second")}
              />
              <SelectField name="level" label="Nivel" defaultValue={editando.levelValue} options={levelChoices} error={err("level")} />
            </div>
            <SelectField
              name="training_type"
              label="Tipo de entrenamiento"
              defaultValue={editando.typeId ? String(editando.typeId) : ""}
              options={[{ value: "", label: "Sin tipo" }, ...trainingTypes]}
              error={err("training_type")}
            />
            <label className="flex items-center gap-2 text-sm text-muted-foreground">
              <input
                type="checkbox"
                name="is_published"
                defaultChecked={editando.published}
                className="size-4 rounded-sm border-border accent-[hsl(var(--primary))]"
              />
              Publicado (se puede agregar a paquetes)
            </label>
            <Button type="submit" size="sm" className="self-end">
              Guardar
            </Button>
          </form>
        )}
      </DialogContent>
    </Dialog>

    <Dialog open={abierto === "link"} onOpenChange={(v) => !v && setAbierto(null)}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Agregar un video por enlace</DialogTitle>
          <DialogDescription>
            Para videos que ya están en YouTube. La miniatura la toma de ahí.
          </DialogDescription>
        </DialogHeader>
        <form method="post" className="flex flex-col gap-4">
          <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
          <input type="hidden" name="source" value="url" />
          <TextField name="name" label="Nombre" error={err("name")} required />
          <TextField
            name="url"
            label="Enlace"
            type="url"
            placeholder="https://www.youtube.com/watch?v=..."
            error={err("url")}
            required
          />
          <div className="flex flex-wrap gap-4">
            <TextField
              name="duration_seconds"
              label="Duración (segundos)"
              type="number"
              min={0}
              defaultValue={0}
              error={err("duration_seconds")}
            />
            <SelectField name="level" label="Nivel" options={levelChoices} error={err("level")} />
          </div>
          <SelectField
            name="training_type"
            label="Tipo de entrenamiento"
            options={[{ value: "", label: "Sin tipo" }, ...trainingTypes]}
            error={err("training_type")}
          />
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <input
              type="checkbox"
              name="is_published"
              defaultChecked
              className="size-4 rounded-sm border-border accent-[hsl(var(--primary))]"
            />
            Publicado
          </label>
          <Button type="submit" size="sm" className="self-end">
            Agregar a la biblioteca
          </Button>
        </form>
      </DialogContent>
    </Dialog>
    </>
  );
}
