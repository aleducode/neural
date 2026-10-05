import { AlertTriangle, Bell, BellPlus, Search } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TablePagination } from "@/components/ui/data-table";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { Input } from "@/components/ui/input";
import { MemberAvatar } from "@/components/ui/member-avatar";
import { PageHeader } from "@/components/ui/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import { StatWidget, type Kpi } from "@/components/ui/stat-widget";
import { Table, TableCell, TableHead } from "@/components/ui/table";
import { Widget, WidgetHeader } from "@/components/ui/widget";
import { NotificationDetailDialog, toneFor } from "@/islands/NotificationDetail";
import { cn } from "@/lib/utils";

type Choice = { value: string; label: string };

type Row = {
  id: number;
  userId: number;
  userName: string;
  userInitials: string;
  userPhoto: string | null;
  title: string;
  body: string;
  type: string;
  status: string;
  statusLabel: string;
  created: string;
  attempts: number;
  failures: number;
};

type Props = {
  kpis: Kpi[];
  feedUrl: string;
  detailUrl: string;
  sendUrl: string;
  userDetailUrl: string;
  types: Choice[];
  statuses: Choice[];
};

export default function NotificationsTable({
  kpis,
  feedUrl,
  detailUrl,
  sendUrl,
  userDetailUrl,
  types,
  statuses,
}: Props) {
  const [rows, setRows] = useState<Row[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [type, setType] = useState("");
  const [status, setStatus] = useState("");
  const [abierta, setAbierta] = useState<number | null>(null);

  // La página la arma el servidor: son miles de filas y no caben en una isla.
  const cargar = useCallback(async () => {
    setLoading(true);
    const url = new URL(feedUrl, window.location.origin);
    url.searchParams.set("page", String(page));
    if (query.trim()) url.searchParams.set("q", query.trim());
    if (type) url.searchParams.set("type", type);
    if (status) url.searchParams.set("status", status);
    try {
      const response = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      const data = await response.json();
      setRows(data.results);
      setPages(data.pages);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }, [feedUrl, page, query, type, status]);

  // Cada tecla no puede ser una consulta: se espera a que pare de escribir.
  const primera = useRef(true);
  useEffect(() => {
    if (primera.current) {
      primera.current = false;
      cargar();
      return;
    }
    const id = window.setTimeout(cargar, 300);
    return () => window.clearTimeout(id);
  }, [cargar]);

  const filtrar = (set: (value: string) => void) => (value: string) => {
    set(value);
    setPage(1);
  };
  const porPagina = 30;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Notificaciones"
        description="Todo lo que el panel le mandó a los usuarios, y qué respondió Expo."
      >
        <Button size="sm" asChild>
          <a href={sendUrl}>
            <BellPlus />
            Enviar notificación
          </a>
        </Button>
      </PageHeader>

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => (
          <StatWidget {...kpi} key={kpi.key} />
        ))}
      </div>

      <Widget>
        <WidgetHeader icon={<Bell className="size-5" />} title="Historial de envíos">
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search
                className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
                aria-hidden="true"
              />
              <Input
                type="search"
                value={query}
                onChange={(event) => filtrar(setQuery)(event.target.value)}
                placeholder="Buscar por usuario o título"
                aria-label="Buscar por usuario o título"
                className="h-8 w-56 rounded-md pl-9 text-xs"
              />
            </div>
            <Filtro value={type} onChange={filtrar(setType)} options={types} label="Todos los tipos" />
            <Filtro value={status} onChange={filtrar(setStatus)} options={statuses} label="Todos los estados" />
          </div>
        </WidgetHeader>

        {loading && rows.length === 0 ? (
          <div className="flex flex-col gap-2 p-5">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : rows.length === 0 ? (
          <Empty>
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <Bell />
              </EmptyMedia>
              <EmptyTitle>Sin notificaciones</EmptyTitle>
              <EmptyDescription>
                {query || type || status
                  ? "Ningún envío coincide con los filtros."
                  : "Todavía no se envió ninguna notificación."}
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        ) : (
          <>
            <Table className={cn("min-w-[860px]", loading && "opacity-60")}>
              <thead>
                <tr>
                  <TableHead>Usuario</TableHead>
                  <TableHead>Notificación</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Enviada</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Detalle</TableHead>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.id}
                    className="border-b border-border transition-colors last:border-0 hover:bg-secondary"
                  >
                    <TableCell>
                      <a
                        href={userDetailUrl.replace("/0/", `/${row.userId}/`)}
                        className="flex items-center gap-2.5 no-underline"
                      >
                        <MemberAvatar
                          name={row.userName}
                          initials={row.userInitials}
                          photo={row.userPhoto}
                        />
                        <span className="truncate text-sm font-medium text-foreground">
                          {row.userName}
                        </span>
                      </a>
                    </TableCell>
                    <TableCell>
                      <span className="block max-w-xs truncate text-sm font-medium text-foreground">
                        {row.title}
                      </span>
                      <span className="block max-w-xs truncate text-xs text-muted-foreground">
                        {row.body}
                      </span>
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
                      {row.type}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm text-muted-foreground">
                      {row.created}
                    </TableCell>
                    <TableCell>
                      <span className="flex items-center gap-2">
                        <Badge dot variant={toneFor(row.status)}>
                          {row.statusLabel}
                        </Badge>
                        {/* La fila ya avisa del fallo: no hay que abrir el
                            modal para saber que algo salio mal. */}
                        {row.failures > 0 && (
                          <span
                            className="flex items-center gap-1 text-xs text-destructive"
                            title={`${row.failures} de ${row.attempts} dispositivos fallaron`}
                          >
                            <AlertTriangle className="size-3.5" />
                            {row.failures}/{row.attempts}
                          </span>
                        )}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="outline" size="sm" onClick={() => setAbierta(row.id)}>
                        Ver logs
                      </Button>
                    </TableCell>
                  </tr>
                ))}
              </tbody>
            </Table>

            <TablePagination
              from={(page - 1) * porPagina + 1}
              to={Math.min(page * porPagina, total)}
              total={total}
              page={page}
              pages={pages}
              pageSize={porPagina}
              onPage={setPage}
              noun="notificaciones"
            />
          </>
        )}
      </Widget>

      <NotificationDetailDialog
        id={abierta}
        detailUrl={detailUrl}
        userDetailUrl={userDetailUrl}
        onClose={() => setAbierta(null)}
      />
    </div>
  );
}

function Filtro({
  value,
  onChange,
  options,
  label,
}: {
  value: string;
  onChange: (value: string) => void;
  options: Choice[];
  label: string;
}) {
  return (
    <select
      value={value}
      onChange={(event) => onChange(event.target.value)}
      aria-label={label}
      className="h-8 rounded-md border border-input bg-background px-2 text-xs text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <option value="">{label}</option>
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
