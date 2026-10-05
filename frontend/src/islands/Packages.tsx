import { Library, Users } from "lucide-react";

import { Badge } from "@/components/ui/badge";
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

type Props = { kpis: Kpi[]; rows: Row[]; packageDetailUrl: string };

export default function Packages({ kpis, rows, packageDetailUrl }: Props) {
  return (
    <ListSection<Row>
      title="Paquetes"
      description="Listas ordenadas de videos que se asignan a usuarios o a planes."
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
  );
}
