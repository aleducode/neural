import { Bell, ChevronLeft, ChevronRight, Search } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableCell, TableHead, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/utils";

type Choice = { value: string; label: string };

type Row = {
  id: number;
  userId: number;
  userName: string;
  userInitials: string;
  title: string;
  body: string;
  type: string;
  status: string;
  statusLabel: string;
  created: string;
};

type Props = {
  feedUrl: string;
  userDetailUrl: string;
  types: Choice[];
  statuses: Choice[];
};

function badgeFor(status: string) {
  if (status === "sent" || status === "delivered") return "success" as const;
  if (status === "failed") return "error" as const;
  if (status === "read") return "info" as const;
  return "neutral" as const;
}

export default function NotificationsTable({
  feedUrl,
  userDetailUrl,
  types,
  statuses,
}: Props) {
  const [query, setQuery] = useState("");
  const [type, setType] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);

  const [rows, setRows] = useState<Row[]>([]);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  // Una peticion en vuelo a la vez: si el usuario sigue tecleando, la
  // respuesta vieja no puede pisar a la nueva.
  const request = useRef(0);

  const load = useCallback(async () => {
    const ticket = ++request.current;
    setLoading(true);
    setFailed(false);

    const params = new URLSearchParams({ page: String(page) });
    if (query.trim()) params.set("q", query.trim());
    if (type) params.set("type", type);
    if (status) params.set("status", status);

    try {
      const response = await fetch(`${feedUrl}?${params}`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin",
      });
      if (!response.ok) throw new Error(String(response.status));
      const data = await response.json();
      if (ticket !== request.current) return;
      setRows(data.results);
      setPages(data.pages);
      setTotal(data.total);
    } catch {
      if (ticket !== request.current) return;
      setFailed(true);
    } finally {
      if (ticket === request.current) setLoading(false);
    }
  }, [feedUrl, page, query, type, status]);

  // Debounce solo para lo que se escribe; los selects responden al instante.
  useEffect(() => {
    const timer = setTimeout(load, query ? 300 : 0);
    return () => clearTimeout(timer);
  }, [load, query]);

  function reset(apply: () => void) {
    apply();
    setPage(1);
  }

  const selectClass =
    "h-9 rounded-md border border-input bg-background px-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring";

  return (
    <div className="rounded-lg border border-border bg-background">
      <div className="flex flex-wrap items-center gap-3 border-b border-border px-6 py-5">
        <div className="relative w-full max-w-xs">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(event) => reset(() => setQuery(event.target.value))}
            placeholder="Buscar por usuario o título..."
            className="pl-9"
            aria-label="Buscar notificaciones"
          />
        </div>

        <select
          className={selectClass}
          value={type}
          onChange={(event) => reset(() => setType(event.target.value))}
          aria-label="Filtrar por tipo"
        >
          <option value="">Todos los tipos</option>
          {types.map((choice) => (
            <option key={choice.value} value={choice.value}>
              {choice.label}
            </option>
          ))}
        </select>

        <select
          className={selectClass}
          value={status}
          onChange={(event) => reset(() => setStatus(event.target.value))}
          aria-label="Filtrar por estado"
        >
          <option value="">Todos los estados</option>
          {statuses.map((choice) => (
            <option key={choice.value} value={choice.value}>
              {choice.label}
            </option>
          ))}
        </select>

        <span className="ml-auto text-xs text-muted-foreground">
          {loading ? "Cargando..." : `${total.toLocaleString("es-CO")} notificaciones`}
        </span>
      </div>

      {failed ? (
        <div className="px-8 py-16 text-center">
          <p className="mb-4 text-sm text-muted-foreground">
            No se pudo cargar el historial.
          </p>
          <Button variant="outline" size="sm" onClick={load}>
            Reintentar
          </Button>
        </div>
      ) : rows.length === 0 && !loading ? (
        <div className="px-8 py-16 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted text-muted-foreground">
            <Bell className="h-6 w-6" />
          </div>
          <h5 className="mb-2 text-base font-semibold text-foreground">
            No se encontraron notificaciones
          </h5>
          <p className="text-sm text-muted-foreground">
            {query ? `No hay resultados para "${query}"` : "No hay notificaciones con estos filtros"}
          </p>
        </div>
      ) : (
        <>
          <div className={cn("transition-opacity", loading && "opacity-50")}>
            <Table>
              <thead>
                <tr>
                  <TableHead>Usuario</TableHead>
                  <TableHead>Notificación</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Fecha</TableHead>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>
                      <a
                        href={userDetailUrl.replace("/0/", `/${row.userId}/`)}
                        className="flex items-center gap-3 no-underline"
                      >
                        <span className="flex h-10 w-10 flex-none items-center justify-center rounded-full bg-emerald-500 text-sm font-semibold text-white">
                          {row.userInitials}
                        </span>
                        <span className="truncate text-sm font-medium text-foreground">
                          {row.userName}
                        </span>
                      </a>
                    </TableCell>
                    <TableCell>
                      <div className="max-w-[280px]">
                        <div className="truncate text-sm font-medium text-foreground">
                          {row.title}
                        </div>
                        <div className="truncate text-xs text-muted-foreground">{row.body}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="inline-flex rounded border border-border bg-muted px-2 py-0.5 text-[0.6875rem] font-medium text-muted-foreground">
                        {row.type}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge variant={badgeFor(row.status)}>{row.statusLabel}</Badge>
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
                      {row.created}
                    </TableCell>
                  </TableRow>
                ))}
              </tbody>
            </Table>
          </div>

          {pages > 1 && (
            <div className="flex items-center justify-center gap-2 px-6 py-4">
              <Button
                variant="outline"
                size="icon"
                onClick={() => setPage(page - 1)}
                disabled={page <= 1 || loading}
                aria-label="Página anterior"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="px-2 text-sm text-muted-foreground">
                {page} de {pages}
              </span>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setPage(page + 1)}
                disabled={page >= pages || loading}
                aria-label="Página siguiente"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
